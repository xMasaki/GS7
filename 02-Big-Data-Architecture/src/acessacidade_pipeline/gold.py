"""Camada GOLD — agregados prontos para o dashboard do AcessaCidade e para BI.

Todas as tabelas Gold usam apenas registros com `registro_valido = true` da Silver (RN-13)
e não contêm dados pessoais nem texto livre (sem descrição, sem logradouro, sem nome).

Tabelas:
- gold.denuncias_por_bairro      (bairro, total, possiveis_buracos, impede_passagem, com_fotografia, percentual)
- gold.denuncias_por_categoria   (categoria, rotulo, total, possiveis_buracos, percentual)
- gold.denuncias_por_periodo     (granularidade mensal|semanal, periodo, inicio_periodo, total, possiveis_buracos)
- gold.denuncias_por_status      (status, rotulo, total, percentual)
- gold.resultado_visao           (classificacao, rotulo, total, percentual)
- gold.qualidade_registros       (metrica, valor, descricao)

Saídas em arquivo: data/processed/gold/<tabela>.csv e gold_snapshot.json (contrato 4.8).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import PipelineConfig
from .dominio import FONTE_API, FONTE_SIMULADA
from .raw import TABELA_APP, TABELA_SIMULADA
from .warehouse import contar

log = logging.getLogger("acessacidade_pipeline")

TABELAS_GOLD = (
    "denuncias_por_bairro",
    "denuncias_por_categoria",
    "denuncias_por_periodo",
    "denuncias_por_status",
    "resultado_visao",
    "qualidade_registros",
)

_VALIDOS = "(SELECT * FROM silver.denuncias WHERE registro_valido)"


def calcular_qualidade(con) -> dict:
    """Indicadores de qualidade no formato do contrato 4.8 (+ 3 campos extras de transparência).

    - linhas_raw: linhas das duas fontes na RAW;
    - linhas_bronze / duplicatas_removidas: após a dedup TÉCNICA (linhas 100% idênticas);
    - datas_invalidas: registros (pós-bronze) com data ausente, irreconhecível ou implausível (RN-09);
    - coordenadas_invalidas: coordenada informada mas inválida (bronze) ou fora do Brasil (RN-10);
    - campos_obrigatorios_ausentes: registros (pós-bronze) com ao menos um campo obrigatório vazio;
    - percentual_registros_validos: registros válidos / denúncias únicas da Silver x 100 (RN-12).
    """
    n_raw = contar(con, TABELA_SIMULADA) + contar(con, TABELA_APP)
    n_bronze = contar(con, "bronze.denuncias")
    todos_silver = ("(SELECT flag_data_invalida, flag_coordenada_invalida, flag_coordenada_fora_area "
                    "FROM silver.denuncias UNION ALL SELECT flag_data_invalida, flag_coordenada_invalida, "
                    "flag_coordenada_fora_area FROM silver.denuncias_duplicadas)")
    n_silver = contar(con, "silver.denuncias")
    n_validos = contar(con, "silver.denuncias", "registro_valido")
    return {
        "linhas_raw": n_raw,
        "linhas_bronze": n_bronze,
        "duplicatas_removidas": n_raw - n_bronze,
        "datas_invalidas": contar(con, todos_silver, "flag_data_invalida"),
        "coordenadas_invalidas": contar(con, todos_silver, "flag_coordenada_invalida OR flag_coordenada_fora_area"),
        "campos_obrigatorios_ausentes": contar(con, "bronze.denuncias", "flag_campo_obrigatorio_ausente"),
        "percentual_registros_validos": round(100.0 * n_validos / n_silver, 1) if n_silver else 0.0,
        # extras (não exigidos pelo contrato, úteis para o painel e para a banca)
        "linhas_silver": n_silver,
        "duplicatas_negocio_removidas": contar(con, "silver.denuncias_duplicadas"),
        "registros_validos": n_validos,
    }


DESCRICOES_QUALIDADE = {
    "linhas_raw": "Linhas carregadas na RAW (todas as fontes, sem transformação)",
    "linhas_bronze": "Linhas na BRONZE após remover duplicatas técnicas",
    "duplicatas_removidas": "Duplicatas técnicas removidas (linhas 100% idênticas na origem)",
    "datas_invalidas": "Registros com data ausente, não reconhecida ou implausível (RN-09)",
    "coordenadas_invalidas": "Registros com coordenada inválida ou fora do Brasil (RN-10)",
    "campos_obrigatorios_ausentes": "Registros com ao menos um campo obrigatório vazio",
    "percentual_registros_validos": "Percentual de denúncias únicas que atendem à regra de registro válido (RN-12)",
    "linhas_silver": "Denúncias únicas na SILVER após a deduplicação de negócio",
    "duplicatas_negocio_removidas": "Quase-duplicatas removidas na SILVER (mesmo endereço + tipo + dia, RN-11)",
    "registros_validos": "Denúncias únicas válidas, usadas nos agregados Gold",
}


def construir_gold(con) -> dict:
    con.execute(f"""
        CREATE OR REPLACE TABLE gold.denuncias_por_bairro AS
        SELECT bairro,
               count(*)                                                        AS total,
               count(*) FILTER (WHERE visao_classificacao = 'POSSIBLE_POTHOLE') AS possiveis_buracos,
               count(*) FILTER (WHERE impacto = 'IMPEDE_PASSAGEM')              AS impede_passagem,
               count(*) FILTER (WHERE possui_imagem)                            AS com_fotografia,
               round(100.0 * count(*) / sum(count(*)) OVER (), 1)              AS percentual
        FROM {_VALIDOS}
        GROUP BY bairro
        ORDER BY total DESC, bairro
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE gold.denuncias_por_categoria AS
        WITH agg AS (
            SELECT tipo_obstaculo, count(*) AS total,
                   count(*) FILTER (WHERE visao_classificacao = 'POSSIBLE_POTHOLE') AS possiveis_buracos
            FROM {_VALIDOS} GROUP BY tipo_obstaculo
        )
        SELECT r.chave AS categoria, r.rotulo,
               COALESCE(a.total, 0)             AS total,
               COALESCE(a.possiveis_buracos, 0) AS possiveis_buracos,
               COALESCE(round(100.0 * a.total / NULLIF(sum(a.total) OVER (), 0), 1), 0.0) AS percentual
        FROM silver.ref_tipo_obstaculo r LEFT JOIN agg a ON a.tipo_obstaculo = r.chave
        ORDER BY total DESC, r.ordem
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE gold.denuncias_por_periodo AS
        SELECT * FROM (
            SELECT 'mensal' AS granularidade, ano_mes AS periodo,
                   CAST(min(date_trunc('month', data_registro)) AS DATE) AS inicio_periodo,
                   count(*) AS total,
                   count(*) FILTER (WHERE visao_classificacao = 'POSSIBLE_POTHOLE') AS possiveis_buracos
            FROM {_VALIDOS} GROUP BY ano_mes
            UNION ALL
            SELECT 'semanal', semana_iso,
                   CAST(min(date_trunc('week', data_registro)) AS DATE),
                   count(*),
                   count(*) FILTER (WHERE visao_classificacao = 'POSSIBLE_POTHOLE')
            FROM {_VALIDOS} GROUP BY semana_iso
        )
        ORDER BY granularidade, inicio_periodo
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE gold.denuncias_por_status AS
        WITH agg AS (SELECT status, count(*) AS total FROM {_VALIDOS} GROUP BY status)
        SELECT r.chave AS status, r.rotulo, COALESCE(a.total, 0) AS total,
               COALESCE(round(100.0 * a.total / NULLIF(sum(a.total) OVER (), 0), 1), 0.0) AS percentual
        FROM silver.ref_status r LEFT JOIN agg a ON a.status = r.chave
        ORDER BY r.ordem
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE gold.resultado_visao AS
        WITH agg AS (SELECT visao_classificacao, count(*) AS total FROM {_VALIDOS} GROUP BY visao_classificacao)
        SELECT r.chave AS classificacao, r.rotulo, COALESCE(a.total, 0) AS total,
               COALESCE(round(100.0 * a.total / NULLIF(sum(a.total) OVER (), 0), 1), 0.0) AS percentual
        FROM silver.ref_visao_classificacao r
        LEFT JOIN agg a ON a.visao_classificacao IS NOT DISTINCT FROM r.chave
        ORDER BY r.ordem
    """)

    qualidade = calcular_qualidade(con)
    con.execute("CREATE OR REPLACE TABLE gold.qualidade_registros "
                "(ordem INTEGER, metrica VARCHAR, valor DOUBLE, descricao VARCHAR)")
    for i, (metrica, valor) in enumerate(qualidade.items(), start=1):
        con.execute("INSERT INTO gold.qualidade_registros VALUES (?, ?, ?, ?)",
                    [i, metrica, float(valor), DESCRICOES_QUALIDADE[metrica]])

    resultado = {f"linhas_gold_{t}": contar(con, f"gold.{t}") for t in TABELAS_GOLD}
    log.info("[gold] %s", resultado)
    return resultado


def _registros(con, sql: str) -> list[dict]:
    cur = con.execute(sql)
    nomes = [d[0] for d in cur.description]
    return [dict(zip(nomes, linha)) for linha in cur.fetchall()]


def montar_snapshot(con, execucao_id: str, gerado_em: datetime | None = None) -> dict:
    """Snapshot no formato do contrato 4.8 (sem dados pessoais)."""
    gerado_em = gerado_em or datetime.now(timezone.utc)
    qualidade = calcular_qualidade(con)
    inclui_simulados = bool(con.execute(
        "SELECT count(*) FROM silver.denuncias WHERE registro_valido AND dado_simulado").fetchone()[0])
    return {
        "disponivel": True,
        "gerado_em": gerado_em.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "execucao_id": execucao_id,
        "inclui_simulados": inclui_simulados,
        "fontes": [
            {"nome": FONTE_SIMULADA, "linhas": contar(con, TABELA_SIMULADA)},
            {"nome": FONTE_API, "linhas": contar(con, TABELA_APP)},
        ],
        "denuncias_por_bairro": _registros(
            con, "SELECT bairro, total, possiveis_buracos FROM gold.denuncias_por_bairro"),
        "denuncias_por_categoria": _registros(
            con, "SELECT categoria, rotulo, total FROM gold.denuncias_por_categoria"),
        "denuncias_por_periodo": _registros(
            con, "SELECT periodo, total FROM gold.denuncias_por_periodo WHERE granularidade = 'mensal' "
                 "ORDER BY inicio_periodo"),
        "denuncias_por_status": _registros(
            con, "SELECT status, rotulo, total FROM gold.denuncias_por_status"),
        "resultado_visao": _registros(
            con, "SELECT classificacao, rotulo, total FROM gold.resultado_visao"),
        "qualidade": qualidade,
        # extensão (não exigida pelo contrato): série semanal ISO
        "denuncias_por_semana": _registros(
            con, "SELECT periodo, total FROM gold.denuncias_por_periodo WHERE granularidade = 'semanal' "
                 "ORDER BY inicio_periodo"),
    }


def exportar_gold(con, cfg: PipelineConfig, execucao_id: str, gerado_em: datetime | None = None) -> dict:
    """Exporta cada tabela Gold em CSV (UTF-8) e grava o gold_snapshot.json."""
    cfg.gold_dir.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for tabela in TABELAS_GOLD:
        destino = Path(cfg.gold_dir) / f"{tabela}.csv"
        df = con.execute(f"SELECT * FROM gold.{tabela}").df()
        df.to_csv(destino, index=False, encoding="utf-8", lineterminator="\n")
        arquivos.append(str(destino))
    snapshot = montar_snapshot(con, execucao_id, gerado_em)
    cfg.snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    arquivos.append(str(cfg.snapshot_path))
    log.info("[gold] arquivos exportados: %s", ", ".join(Path(a).name for a in arquivos))
    return {"arquivos_gold": arquivos, "snapshot": str(cfg.snapshot_path)}
