"""Load: camada RAW — cópia fiel das fontes dentro do warehouse.

Mesma regra do notebook da Aula 06:
- todas as colunas de origem entram como VARCHAR (all_varchar / schema-on-read);
- nenhuma limpeza, tipagem ou remoção de duplicata;
- só acrescentamos metadados de linhagem: _source_file, _ingested_at, _row_id, _batch_id.

Tabelas:
- raw.denuncias_simuladas — fonte 1 (CSV simulado; contém nome_denunciante: a minimização
  acontece na passagem para a Bronze, a raw é o "seguro" de reprocessamento);
- raw.denuncias_app       — fonte 2 (exportação da API; vazia quando a API não está disponível);
- raw.log_cargas          — histórico de cargas (auditoria), uma linha por fonte e lote.

Estratégia de carga: full refresh (CREATE OR REPLACE) a cada execução, porque ambas as
fontes são exportações completas. Isso torna o pipeline idempotente.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from .config import PipelineConfig
from .dominio import COLUNAS_EXPORTACAO_API, COLUNAS_FONTE_SIMULADA, FONTE_API, FONTE_SIMULADA
from .warehouse import contar, ident

log = logging.getLogger("acessacidade_pipeline")

TABELA_SIMULADA = "raw.denuncias_simuladas"
TABELA_APP = "raw.denuncias_app"
TABELA_LOG = "raw.log_cargas"
METADADOS = ("_source_file", "_ingested_at", "_row_id", "_batch_id")


def _caminho_relativo(caminho: Path, cfg: PipelineConfig) -> str:
    try:
        return "data/" + Path(caminho).resolve().relative_to(Path(cfg.data_dir).resolve()).as_posix()
    except ValueError:
        return Path(caminho).name


def _ler_csv_varchar(con: duckdb.DuckDBPyConnection, caminho: Path) -> pd.DataFrame:
    """Lê o CSV com o leitor do DuckDB, tudo como texto (all_varchar), preservando a ordem."""
    return con.execute(
        "SELECT * FROM read_csv(?, all_varchar = true, header = true, delim = ',', quote = '\"', "
        "escape = '\"')",  # UTF-8 é o padrão do DuckDB (encoding= só existe a partir da 1.2)
        [str(caminho)],
    ).df()


def _gravar_raw(con, tabela: str, df: pd.DataFrame, colunas_origem: list[str], source_file: str,
                batch_id: str, ingested_at: datetime) -> int:
    df = df.copy()
    df["_source_file"] = source_file
    df["_ingested_at"] = pd.Timestamp(ingested_at)
    # _row_id = posição da linha no arquivo de origem (1 = primeira linha de dados)
    df["_row_id"] = range(1, len(df) + 1)
    df["_batch_id"] = batch_id
    selecao = ", ".join(f"CAST({ident(c)} AS VARCHAR) AS {ident(c)}" for c in colunas_origem)
    con.register("_df_raw", df)
    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE {tabela} AS
            SELECT {selecao},
                   CAST(_source_file AS VARCHAR) AS _source_file,
                   CAST(_ingested_at AS TIMESTAMP) AS _ingested_at,
                   CAST(_row_id AS BIGINT)        AS _row_id,
                   CAST(_batch_id AS VARCHAR)     AS _batch_id
            FROM _df_raw
            ORDER BY _row_id
        """)
    finally:
        con.unregister("_df_raw")
    return contar(con, tabela)


def carregar_raw_simulada(con, cfg: PipelineConfig, batch_id: str, ingested_at: datetime) -> int:
    df = _ler_csv_varchar(con, cfg.samples_csv)
    faltando = [c for c in COLUNAS_FONTE_SIMULADA if c not in df.columns]
    if faltando:
        raise ValueError(f"Fonte simulada fora do formato esperado; colunas ausentes: {faltando}")
    return _gravar_raw(con, TABELA_SIMULADA, df, list(df.columns), _caminho_relativo(cfg.samples_csv, cfg),
                       batch_id, ingested_at)


def carregar_raw_app(con, cfg: PipelineConfig, arquivo_api: str | Path | None, batch_id: str,
                     ingested_at: datetime) -> int:
    if arquivo_api:
        df = _ler_csv_varchar(con, Path(arquivo_api))
        faltando = [c for c in COLUNAS_EXPORTACAO_API if c not in df.columns]
        if faltando:
            raise ValueError(f"Exportação da API fora do contrato 4.7; colunas ausentes: {faltando}")
        origem = _caminho_relativo(Path(arquivo_api), cfg)
    else:
        # Sem API nesta execução: tabela vazia com o mesmo esquema (o union da Bronze continua válido).
        df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_EXPORTACAO_API})
        origem = "(api indisponível nesta execução)"
    return _gravar_raw(con, TABELA_APP, df, list(df.columns), origem, batch_id, ingested_at)


def registrar_cargas(con, batch_id: str, ingested_at: datetime, cargas: list[dict]) -> None:
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABELA_LOG} (
            _batch_id VARCHAR, fonte VARCHAR, tabela VARCHAR, arquivo VARCHAR,
            linhas BIGINT, status VARCHAR, mensagem VARCHAR, carregado_em TIMESTAMP
        )
    """)
    con.execute(f"DELETE FROM {TABELA_LOG} WHERE _batch_id = ?", [batch_id])
    for c in cargas:
        con.execute(
            f"INSERT INTO {TABELA_LOG} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [batch_id, c["fonte"], c["tabela"], c["arquivo"], c["linhas"], c["status"], c["mensagem"],
             ingested_at],
        )


def carregar_raw(con, cfg: PipelineConfig, batch_id: str, ingested_at: datetime,
                 arquivo_api: str | Path | None, status_api: str = "PULADA", mensagem_api: str = "") -> dict:
    """Carrega as duas fontes na RAW e registra o lote. Devolve contagens por fonte."""
    n_sim = carregar_raw_simulada(con, cfg, batch_id, ingested_at)
    n_app = carregar_raw_app(con, cfg, arquivo_api, batch_id, ingested_at)
    registrar_cargas(con, batch_id, ingested_at, [
        {"fonte": FONTE_SIMULADA, "tabela": TABELA_SIMULADA, "arquivo": _caminho_relativo(cfg.samples_csv, cfg),
         "linhas": n_sim, "status": "OK", "mensagem": "Fonte simulada carregada sem transformação."},
        {"fonte": FONTE_API, "tabela": TABELA_APP,
         "arquivo": _caminho_relativo(Path(arquivo_api), cfg) if arquivo_api else None,
         "linhas": n_app, "status": status_api, "mensagem": mensagem_api},
    ])
    log.info("[raw] %s: %d linhas | %s: %d linhas", TABELA_SIMULADA, n_sim, TABELA_APP, n_app)
    return {"linhas_raw_simuladas": n_sim, "linhas_raw_app": n_app, "linhas_raw": n_sim + n_app}
