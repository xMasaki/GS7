"""
DAG: acessacidade_elt_pipeline
================================

Orquestra o pipeline ELT do AcessaCidade (Raw -> Bronze -> Silver -> Gold) no Apache
Airflow 2.10.5 (Python 3.11), com a API TaskFlow (@dag / @task) — a mesma usada no
notebook da Aula 06, agora aplicada às denúncias de acessibilidade.

    extract_and_load_raw -> transform_bronze -> curate_silver -> build_gold
        -> quality_report -> publish_gold

Diferente do DAG da aula (autossuficiente, com as funções copiadas dentro do arquivo), este
DAG apenas IMPORTA o pacote `acessacidade_pipeline` (02-Big-Data-Architecture/src): a lógica
é uma só para o Airflow, para o runner local (`python -m acessacidade_pipeline`) e para o
notebook. Cada task abre sua própria conexão com o DuckDB (as tasks rodam em processos
separados) e devolve um dicionário pequeno (XCom) com as contagens da etapa.

Parâmetro de execução (Trigger DAG w/ config): {"usar_api": true|false}
Variáveis de ambiente lidas pelo pacote: PIPELINE_DATA_DIR, ACESSACIDADE_API_URL, PIPELINE_TOKEN.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Torna o pacote importável quando o DAG está dentro do repositório
# (02-Big-Data-Architecture/dags -> ../src). No container também vale o PYTHONPATH.
_SRC = Path(__file__).resolve().parent.parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from airflow.decorators import dag, task  # noqa: E402

from acessacidade_pipeline import run_pipeline as rp  # noqa: E402

DAG_ID = "acessacidade_elt_pipeline"

DEFAULT_ARGS = {
    "owner": "acessacidade-dados",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def _usar_api(params: dict | None) -> bool:
    valor = (params or {}).get("usar_api", True)
    if isinstance(valor, str):
        return valor.strip().lower() not in {"false", "0", "nao", "não", "no"}
    return bool(valor)


@dag(
    dag_id=DAG_ID,
    description="AcessaCidade: denúncias de acessibilidade — ELT raw -> bronze -> silver -> gold (DuckDB)",
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,          # DuckDB: um único escritor por vez no arquivo do warehouse
    default_args=DEFAULT_ARGS,
    params={"usar_api": True},
    tags=["acessacidade", "citizentech", "ods11", "elt", "duckdb", "gs2026"],
    doc_md=__doc__,
)
def acessacidade_elt_pipeline():

    @task
    def extract_and_load_raw(run_id: str | None = None, params: dict | None = None) -> dict:
        """Extract (CSV simulado + exportação da API, se disponível) e Load na RAW, sem transformar."""
        return rp.tarefa_extract_and_load_raw(execucao_id=run_id, usar_api=_usar_api(params))

    @task
    def transform_bronze(estado: dict) -> dict:
        """Tipagem, dedup técnico, flags e minimização (nome não passa da RAW)."""
        return rp.tarefa_transform_bronze(estado)

    @task
    def curate_silver(estado: dict) -> dict:
        """Regras de negócio RN-01..RN-12: padronização, mapeamento ao contrato e dedup de negócio."""
        return rp.tarefa_curate_silver(estado)

    @task
    def build_gold(estado: dict) -> dict:
        """Agregados Gold + CSVs + gold_snapshot.json (contrato 4.8)."""
        return rp.tarefa_build_gold(estado)

    @task
    def quality_report(estado: dict) -> dict:
        """Relatório de qualidade e verificações automáticas (falha = não publica)."""
        return rp.tarefa_quality_report(estado)

    @task
    def publish_gold(estado: dict) -> dict:
        """POST /api/pipeline/gold com X-Pipeline-Token (pula com aviso se não configurado)."""
        return rp.tarefa_publish_gold(estado)

    raw = extract_and_load_raw()
    bronze = transform_bronze(raw)
    silver = curate_silver(bronze)
    gold = build_gold(silver)
    qualidade = quality_report(gold)
    publish_gold(qualidade)


acessacidade_elt_pipeline()
