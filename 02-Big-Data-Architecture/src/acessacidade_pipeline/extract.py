"""Extract: localiza/obtém os arquivos das duas fontes do pipeline.

Fonte 1 — `data/samples/denuncias_simuladas.csv` (sistema legado FICTÍCIO, dados SIMULADOS).
Fonte 2 — exportação anonimizada da aplicação AcessaCidade:
          GET {ACESSACIDADE_API_URL}/api/export/denuncias?formato=csv  (header X-Pipeline-Token)
          A resposta é salva, sem alteração, em data/exports/denuncias_api_<timestamp>.csv.

Se a API ou o token não estiverem disponíveis, a extração registra um AVISO e o pipeline
segue apenas com a fonte simulada (degradação elegante).
"""
from __future__ import annotations

import csv
import io
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .config import PipelineConfig
from .dominio import COLUNAS_EXPORTACAO_API
from . import simulate

log = logging.getLogger("acessacidade_pipeline")

ROTA_EXPORTACAO = "/api/export/denuncias"


@dataclass
class ResultadoExtracaoApi:
    status: str                 # "OK" | "PULADA" | "FALHOU"
    mensagem: str
    arquivo: str | None = None
    linhas: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def garantir_fonte_simulada(cfg: PipelineConfig) -> Path:
    """Garante que o CSV simulado existe (gera com a semente fixa se estiver ausente)."""
    if not cfg.samples_csv.exists():
        log.warning("Fonte simulada não encontrada em %s — gerando com a semente fixa %s.",
                    cfg.samples_csv, simulate.SEMENTE)
        simulate.gerar_csv(cfg.samples_csv)
    return cfg.samples_csv


def _validar_csv_exportado(conteudo: str) -> int:
    """Confere o cabeçalho contra o contrato 4.7 e devolve o número de linhas de dados."""
    leitor = csv.reader(io.StringIO(conteudo.lstrip("﻿")))
    try:
        cabecalho = [c.strip() for c in next(leitor)]
    except StopIteration as exc:
        raise ValueError("a exportação veio vazia (sem cabeçalho)") from exc
    faltando = [c for c in COLUNAS_EXPORTACAO_API if c not in cabecalho]
    if faltando:
        raise ValueError(f"colunas do contrato 4.7 ausentes na exportação: {', '.join(faltando)}")
    proibidas = [c for c in cabecalho if "nome" in c.lower()]
    if proibidas:
        raise ValueError(f"a exportação contém colunas com dados pessoais não previstas: {proibidas}")
    return sum(1 for linha in leitor if any(campo.strip() for campo in linha))


def exportar_denuncias_api(
    cfg: PipelineConfig,
    *,
    client: httpx.Client | None = None,
    agora: datetime | None = None,
) -> ResultadoExtracaoApi:
    """Baixa a exportação CSV da API. Nunca levanta exceção por indisponibilidade: devolve
    status PULADA (não configurada) ou FALHOU (erro de rede/HTTP/formato) com mensagem clara."""
    if not cfg.api_url:
        return ResultadoExtracaoApi("PULADA", "ACESSACIDADE_API_URL não configurada; usando só a fonte simulada.")
    if not cfg.pipeline_token:
        return ResultadoExtracaoApi("PULADA", "PIPELINE_TOKEN não configurado; usando só a fonte simulada.")

    url = f"{cfg.api_url}{ROTA_EXPORTACAO}"
    proprio_cliente = client is None
    client = client or httpx.Client(timeout=cfg.http_timeout)
    try:
        resposta = client.get(url, params={"formato": "csv"}, headers={"X-Pipeline-Token": cfg.pipeline_token})
    except httpx.HTTPError as exc:
        return ResultadoExtracaoApi("FALHOU", f"API indisponível em {url} ({type(exc).__name__}); "
                                               "usando só a fonte simulada.")
    finally:
        if proprio_cliente:
            client.close()

    if resposta.status_code == 403:
        return ResultadoExtracaoApi("FALHOU", "API respondeu 403: exportação desativada no servidor "
                                               "(PIPELINE_TOKEN vazio no backend).")
    if resposta.status_code == 401:
        return ResultadoExtracaoApi("FALHOU", "API respondeu 401: PIPELINE_TOKEN diferente do configurado no backend.")
    if resposta.status_code != 200:
        return ResultadoExtracaoApi("FALHOU", f"API respondeu HTTP {resposta.status_code} na exportação.")

    conteudo = resposta.content.decode("utf-8-sig")
    try:
        linhas = _validar_csv_exportado(conteudo)
    except ValueError as exc:
        return ResultadoExtracaoApi("FALHOU", f"Exportação recebida fora do contrato: {exc}")

    agora = agora or datetime.now(timezone.utc)
    cfg.exports_dir.mkdir(parents=True, exist_ok=True)
    destino = cfg.exports_dir / f"denuncias_api_{agora.strftime('%Y%m%dT%H%M%SZ')}.csv"
    # Cópia fiel do que a API devolveu (só o BOM, se houver, é removido).
    destino.write_text(conteudo, encoding="utf-8", newline="")
    return ResultadoExtracaoApi("OK", f"Exportação da API salva com {linhas} linhas.", str(destino), linhas)
