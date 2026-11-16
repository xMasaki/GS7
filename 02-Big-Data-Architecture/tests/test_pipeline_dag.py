"""DAG do Airflow testada SEM o Airflow instalado (ele não roda no Windows nativo).

Um stub mínimo de `airflow.decorators` (dag/task) é injetado em sys.modules. O stub registra
as tasks criadas e as dependências formadas pela passagem de XComArgs (o retorno de uma task
usado como argumento de outra), exatamente como o TaskFlow faz.
"""
import importlib.util
import sys
import types

import pytest

from acessacidade_pipeline.config import REPO_ROOT

DAG_PATH = REPO_ROOT / "02-Big-Data-Architecture" / "dags" / "acessacidade_elt_pipeline.py"
ORDEM = ["extract_and_load_raw", "transform_bronze", "curate_silver", "build_gold", "quality_report",
         "publish_gold"]


class _TaskStub:
    def __init__(self, task_id, funcao, upstream):
        self.task_id, self.funcao, self.upstream = task_id, funcao, upstream


class _DagStub:
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.tasks: list[_TaskStub] = []


def _criar_stub():
    estado = {"atual": None, "dags": []}

    def task(funcao=None, **_):
        def decorar(f):
            def chamar(*args, **kwargs):
                ups = [a.task_id for a in (*args, *kwargs.values()) if isinstance(a, _TaskStub)]
                no = _TaskStub(f.__name__, f, ups)
                estado["atual"].tasks.append(no)
                return no
            return chamar
        return decorar(funcao) if funcao else decorar

    def dag(**kwargs_dag):
        def decorar(f):
            def construir(*a, **k):
                d = _DagStub(kwargs_dag)
                estado["atual"] = d
                f(*a, **k)
                estado["atual"] = None
                estado["dags"].append(d)
                return d
            return construir
        return decorar

    airflow = types.ModuleType("airflow")
    decorators = types.ModuleType("airflow.decorators")
    decorators.dag, decorators.task = dag, task
    airflow.decorators = decorators
    return airflow, decorators, estado


@pytest.fixture
def dag_carregada(monkeypatch):
    airflow, decorators, estado = _criar_stub()
    monkeypatch.setitem(sys.modules, "airflow", airflow)
    monkeypatch.setitem(sys.modules, "airflow.decorators", decorators)
    spec = importlib.util.spec_from_file_location("acessacidade_elt_pipeline_dag_teste", DAG_PATH)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    assert len(estado["dags"]) == 1
    return estado["dags"][0]


def test_dag_configuracao(dag_carregada):
    k = dag_carregada.kwargs
    assert k["dag_id"] == "acessacidade_elt_pipeline"
    assert k["schedule"] == "@daily" and k["catchup"] is False
    assert k["default_args"]["retries"] == 1
    assert {"acessacidade", "elt"} <= set(k["tags"])
    assert k["max_active_runs"] == 1


def test_dag_tasks_e_dependencias(dag_carregada):
    ids = [t.task_id for t in dag_carregada.tasks]
    assert ids == ORDEM
    dependencias = {t.task_id: t.upstream for t in dag_carregada.tasks}
    assert dependencias["extract_and_load_raw"] == []
    for anterior, seguinte in zip(ORDEM, ORDEM[1:]):
        assert dependencias[seguinte] == [anterior]


def test_tasks_da_dag_executam_o_pipeline(dag_carregada, cfg_tmp, monkeypatch):
    """Executa as funções das tasks na ordem da DAG (como o worker faria), sem API."""
    monkeypatch.setenv("PIPELINE_DATA_DIR", str(cfg_tmp.data_dir))
    tarefas = {t.task_id: t.funcao for t in dag_carregada.tasks}
    estado = tarefas["extract_and_load_raw"](run_id="manual__2026-11-14T13:39:00+00:00",
                                             params={"usar_api": False})
    for nome in ORDEM[1:]:
        estado = tarefas[nome](estado)
    assert estado["execucao_id"] == "manual__2026-11-14T13:39:00+00:00"
    assert estado["situacao_qualidade"] == "APROVADO"
    assert estado["publicacao"]["status"] == "PULADA"
    assert cfg_tmp.snapshot_path.exists()
