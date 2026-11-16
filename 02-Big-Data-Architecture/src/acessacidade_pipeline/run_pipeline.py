"""Tarefas do pipeline (as MESMAS chamadas pela DAG do Airflow) e runner local.

Ordem: extract_and_load_raw -> transform_bronze -> curate_silver -> build_gold
       -> quality_report -> publish_gold

Cada tarefa:
- recebe o "estado" (dict serializável em JSON, trafega como XCom no Airflow);
- abre e fecha sua própria conexão com o warehouse DuckDB;
- devolve o estado acrescido das suas contagens.

Runner local (Windows/Linux, sem Airflow):
    python -m acessacidade_pipeline [--sem-api] [--execucao-id ID] [--log-arquivo caminho.log]
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import __version__
from .bronze import construir_bronze
from .config import REPO_ROOT, PipelineConfig
from .extract import ResultadoExtracaoApi, exportar_denuncias_api, garantir_fonte_simulada
from .gold import construir_gold, exportar_gold
from .publish import publicar_snapshot
from .quality import gerar_relatorio
from .raw import carregar_raw
from .silver import construir_silver
from .warehouse import conectar

log = logging.getLogger("acessacidade_pipeline")

ORDEM_TAREFAS = ("extract_and_load_raw", "transform_bronze", "curate_silver", "build_gold",
                 "quality_report", "publish_gold")


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def novo_execucao_id(agora: datetime | None = None) -> str:
    return "manual__" + (agora or _agora()).strftime("%Y-%m-%dT%H:%M:%S")


def _rel(caminho: str | Path | None) -> str | None:
    """Caminho relativo à raiz do repositório (logs/relatórios sem caminhos pessoais da máquina)."""
    if not caminho:
        return None
    try:
        return Path(caminho).resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(caminho).name


def _cfg(cfg: PipelineConfig | None) -> PipelineConfig:
    cfg = cfg or PipelineConfig.from_env()
    cfg.garantir_pastas()
    return cfg


def tarefa_extract_and_load_raw(execucao_id: str | None = None, usar_api: bool = True,
                                cfg: PipelineConfig | None = None,
                                client: httpx.Client | None = None) -> dict:
    cfg = _cfg(cfg)
    execucao_id = execucao_id or novo_execucao_id()
    log.info("[extract] execução %s | configuração: %s", execucao_id,
             {k: (_rel(v) if k.endswith(("_dir", "_csv", "_path")) else v) for k, v in cfg.descrever().items()})
    garantir_fonte_simulada(cfg)
    if usar_api:
        extracao = exportar_denuncias_api(cfg, client=client)
    else:
        extracao = ResultadoExtracaoApi("PULADA", "Execução com --sem-api: somente a fonte simulada.")
    if extracao.status == "OK":
        log.info("[extract] API: %s Arquivo: %s", extracao.mensagem, _rel(extracao.arquivo))
    else:
        log.warning("[extract] API %s: %s", extracao.status, extracao.mensagem)

    with conectar(cfg) as con:
        contagens = carregar_raw(con, cfg, execucao_id, _agora().replace(tzinfo=None), extracao.arquivo,
                                 extracao.status, extracao.mensagem)
    extracao_dict = extracao.to_dict() | {"arquivo": _rel(extracao.arquivo)}
    return {"execucao_id": execucao_id, "usar_api": usar_api, "extracao_api": extracao_dict, **contagens}


def tarefa_transform_bronze(estado: dict, cfg: PipelineConfig | None = None) -> dict:
    cfg = _cfg(cfg)
    with conectar(cfg) as con:
        return {**estado, **construir_bronze(con)}


def tarefa_curate_silver(estado: dict, cfg: PipelineConfig | None = None) -> dict:
    cfg = _cfg(cfg)
    with conectar(cfg) as con:
        return {**estado, **construir_silver(con, referencia=_agora().replace(tzinfo=None))}


def tarefa_build_gold(estado: dict, cfg: PipelineConfig | None = None) -> dict:
    cfg = _cfg(cfg)
    with conectar(cfg) as con:
        resultado = construir_gold(con)
        arquivos = exportar_gold(con, cfg, estado["execucao_id"])
    return {**estado, **resultado, "arquivos_gold": [_rel(a) for a in arquivos["arquivos_gold"]],
            "snapshot": _rel(arquivos["snapshot"])}


def tarefa_quality_report(estado: dict, cfg: PipelineConfig | None = None) -> dict:
    cfg = _cfg(cfg)
    with conectar(cfg) as con:
        rel = gerar_relatorio(con, cfg, estado["execucao_id"], contexto=estado)
    log.info("[qualidade] situação: %s | relatório: %s e %s", rel["situacao"], _rel(cfg.relatorio_json_path),
             _rel(cfg.relatorio_md_path))
    return {**estado, "qualidade": rel["qualidade_contrato"], "situacao_qualidade": rel["situacao"]}


def tarefa_publish_gold(estado: dict, cfg: PipelineConfig | None = None,
                        client: httpx.Client | None = None) -> dict:
    cfg = _cfg(cfg)
    if not estado.get("usar_api", True):
        resultado = {"status": "PULADA", "mensagem": "Execução com --sem-api: publicação na API não realizada."}
    else:
        resultado = publicar_snapshot(cfg, client=client)
    (log.info if resultado["status"] == "OK" else log.warning)("[publish] %s", resultado["mensagem"])
    return {**estado, "publicacao": resultado}


def executar_pipeline(usar_api: bool = True, execucao_id: str | None = None,
                      cfg: PipelineConfig | None = None, client: httpx.Client | None = None) -> dict:
    """Executa as 6 tarefas em sequência, como a DAG faria."""
    cfg = _cfg(cfg)
    inicio_total = time.perf_counter()
    estado: dict = {}
    for nome in ORDEM_TAREFAS:
        inicio = time.perf_counter()
        log.info("=== tarefa %s: início ===", nome)
        if nome == "extract_and_load_raw":
            estado = tarefa_extract_and_load_raw(execucao_id, usar_api, cfg, client)
        elif nome == "transform_bronze":
            estado = tarefa_transform_bronze(estado, cfg)
        elif nome == "curate_silver":
            estado = tarefa_curate_silver(estado, cfg)
        elif nome == "build_gold":
            estado = tarefa_build_gold(estado, cfg)
        elif nome == "quality_report":
            estado = tarefa_quality_report(estado, cfg)
        else:
            estado = tarefa_publish_gold(estado, cfg, client)
        log.info("=== tarefa %s: concluída em %.2f s ===", nome, time.perf_counter() - inicio)
    log.info("Pipeline concluído em %.2f s. Execução %s.", time.perf_counter() - inicio_total, estado["execucao_id"])
    return estado


def configurar_logs(nivel: str = "INFO", arquivo: str | None = None) -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if arquivo:
        Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(arquivo, mode="w", encoding="utf-8"))
    logging.basicConfig(level=nivel, format="%(asctime)s %(levelname)-7s %(name)s - %(message)s",
                        handlers=handlers, force=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m acessacidade_pipeline",
        description="Pipeline ELT do AcessaCidade (raw -> bronze -> silver -> gold) sem Airflow.")
    parser.add_argument("--sem-api", action="store_true",
                        help="Não exporta da API nem publica o snapshot (usa só a fonte simulada).")
    parser.add_argument("--execucao-id", help="Identificador da execução (padrão: manual__<data-hora UTC>).")
    parser.add_argument("--log-arquivo", help="Também grava o log neste arquivo (UTF-8).")
    parser.add_argument("--nivel-log", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args(argv)

    configurar_logs(args.nivel_log, args.log_arquivo)
    log.info("AcessaCidade pipeline v%s | Python %s | modo: %s", __version__, sys.version.split()[0],
             "sem API (--sem-api)" if args.sem_api else "com API (se configurada)")
    try:
        estado = executar_pipeline(usar_api=not args.sem_api, execucao_id=args.execucao_id)
    except Exception:  # noqa: BLE001 — o runner registra e devolve código de erro
        log.exception("Pipeline interrompido por erro.")
        return 1
    log.info("Resumo: %s", {k: estado[k] for k in ("linhas_raw", "linhas_bronze", "linhas_silver",
                                                   "registros_validos", "situacao_qualidade")})
    log.info("Qualidade (contrato 4.8): %s", estado["qualidade"])
    log.info("Publicação: %s", estado["publicacao"]["status"])
    return 0
