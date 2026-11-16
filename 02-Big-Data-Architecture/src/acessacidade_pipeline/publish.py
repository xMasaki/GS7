"""Publicação do snapshot Gold na aplicação AcessaCidade.

POST {ACESSACIDADE_API_URL}/api/pipeline/gold  (header X-Pipeline-Token, corpo = gold_snapshot.json)
O backend salva o snapshot e o expõe em GET /api/indicadores/analiticos (painel "#/painel").

- API/token não configurados  -> a etapa é PULADA com mensagem clara (não é erro).
- Configurados, mas a API recusa/está fora do ar -> PublicacaoError (a task da DAG falha e
  o Airflow faz 1 nova tentativa, conforme retries=1).
"""
from __future__ import annotations

import json
import logging

import httpx

from .config import PipelineConfig

log = logging.getLogger("acessacidade_pipeline")

ROTA_PUBLICACAO = "/api/pipeline/gold"


class PublicacaoError(RuntimeError):
    """A API estava configurada, mas a publicação do snapshot falhou."""


def publicar_snapshot(cfg: PipelineConfig, *, client: httpx.Client | None = None) -> dict:
    if not cfg.api_url or not cfg.pipeline_token:
        faltando = [n for n, v in (("ACESSACIDADE_API_URL", cfg.api_url), ("PIPELINE_TOKEN", cfg.pipeline_token))
                    if not v]
        msg = (f"Publicação PULADA: {' e '.join(faltando)} não configurado(s). O snapshot continua disponível em "
               f"data/processed/gold/gold_snapshot.json.")
        return {"status": "PULADA", "mensagem": msg}

    if not cfg.snapshot_path.exists():
        raise PublicacaoError(f"Snapshot Gold não encontrado ({cfg.snapshot_path.name}); rode build_gold antes.")
    corpo = json.loads(cfg.snapshot_path.read_text(encoding="utf-8"))
    url = f"{cfg.api_url}{ROTA_PUBLICACAO}"

    proprio_cliente = client is None
    client = client or httpx.Client(timeout=cfg.http_timeout)
    try:
        resposta = client.post(url, json=corpo, headers={"X-Pipeline-Token": cfg.pipeline_token})
    except httpx.HTTPError as exc:
        raise PublicacaoError(f"Não foi possível contatar a API em {url} ({type(exc).__name__}).") from exc
    finally:
        if proprio_cliente:
            client.close()

    if resposta.status_code in (200, 201, 202, 204):
        return {"status": "OK", "mensagem": f"Snapshot {corpo.get('execucao_id')} publicado (HTTP {resposta.status_code}).",
                "http_status": resposta.status_code}
    if resposta.status_code == 403:
        motivo = "publicação desativada no servidor (PIPELINE_TOKEN vazio no backend)"
    elif resposta.status_code == 401:
        motivo = "PIPELINE_TOKEN diferente do configurado no backend"
    else:
        motivo = f"resposta inesperada: {resposta.text[:200]}"
    raise PublicacaoError(f"API recusou a publicação (HTTP {resposta.status_code}): {motivo}.")
