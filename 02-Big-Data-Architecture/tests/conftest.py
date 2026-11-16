"""Fixtures dos testes do pipeline (disciplina 02).

Cada teste roda em uma pasta de dados TEMPORÁRIA (PIPELINE_DATA_DIR isolado): os testes
nunca alteram data/processed do repositório.
"""
from __future__ import annotations

import pytest

from acessacidade_pipeline import simulate
from acessacidade_pipeline.config import PipelineConfig
from acessacidade_pipeline.run_pipeline import executar_pipeline


def criar_config(base) -> PipelineConfig:
    cfg = PipelineConfig.from_env(data_dir=base / "data", api_url=None, pipeline_token=None)
    simulate.gerar_csv(cfg.samples_csv)
    return cfg


@pytest.fixture
def cfg_tmp(tmp_path, monkeypatch) -> PipelineConfig:
    for var in ("PIPELINE_DATA_DIR", "PIPELINE_WAREHOUSE_PATH", "ACESSACIDADE_API_URL", "PIPELINE_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    return criar_config(tmp_path)


@pytest.fixture(scope="module")
def pipeline_sem_api(tmp_path_factory):
    """Executa o pipeline completo (sem API) uma vez por módulo de teste."""
    cfg = criar_config(tmp_path_factory.mktemp("pipeline"))
    estado = executar_pipeline(usar_api=False, execucao_id="manual__teste", cfg=cfg)
    return cfg, estado
