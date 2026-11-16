"""Configuração do pipeline: caminhos e integrações lidos de variáveis de ambiente.

Variáveis reconhecidas (nenhuma é obrigatória para a execução local com --sem-api):

| Variável                  | Padrão                                              |
|---------------------------|-----------------------------------------------------|
| PIPELINE_DATA_DIR         | <raiz do repositório>/data                          |
| PIPELINE_WAREHOUSE_PATH   | <PIPELINE_DATA_DIR>/processed/warehouse/acessacidade.duckdb |
| ACESSACIDADE_API_URL      | (vazio = sem integração com a API)                  |
| PIPELINE_TOKEN            | (vazio = sem integração com a API)                  |
| PIPELINE_HTTP_TIMEOUT     | 20 (segundos)                                       |

O token nunca é registrado em log nem gravado em arquivo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path

# src/acessacidade_pipeline/config.py -> parents[0]=acessacidade_pipeline, [1]=src,
# [2]=02-Big-Data-Architecture, [3]=raiz do repositório
REPO_ROOT = Path(__file__).resolve().parents[3]

NOME_CSV_SIMULADO = "denuncias_simuladas.csv"
NOME_WAREHOUSE = "acessacidade.duckdb"


def _env(nome: str) -> str | None:
    valor = os.environ.get(nome)
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


@dataclass(frozen=True)
class PipelineConfig:
    data_dir: Path
    samples_csv: Path
    exports_dir: Path
    processed_dir: Path
    gold_dir: Path
    warehouse_path: Path
    api_url: str | None = None
    pipeline_token: str | None = field(default=None, repr=False)
    http_timeout: float = 20.0

    @classmethod
    def from_env(cls, **overrides) -> "PipelineConfig":
        """Monta a configuração a partir do ambiente. `overrides` substitui qualquer campo."""
        data_dir = Path(overrides.pop("data_dir", None) or _env("PIPELINE_DATA_DIR") or REPO_ROOT / "data")
        processed_dir = Path(overrides.pop("processed_dir", None) or data_dir / "processed")
        warehouse = (
            overrides.pop("warehouse_path", None)
            or _env("PIPELINE_WAREHOUSE_PATH")
            or processed_dir / "warehouse" / NOME_WAREHOUSE
        )
        api_url = overrides.pop("api_url", None) if "api_url" in overrides else _env("ACESSACIDADE_API_URL")
        token = (
            overrides.pop("pipeline_token", None) if "pipeline_token" in overrides else _env("PIPELINE_TOKEN")
        )
        timeout_txt = _env("PIPELINE_HTTP_TIMEOUT")
        cfg = cls(
            data_dir=data_dir,
            samples_csv=Path(overrides.pop("samples_csv", None) or data_dir / "samples" / NOME_CSV_SIMULADO),
            exports_dir=Path(overrides.pop("exports_dir", None) or data_dir / "exports"),
            processed_dir=processed_dir,
            gold_dir=Path(overrides.pop("gold_dir", None) or processed_dir / "gold"),
            warehouse_path=Path(warehouse),
            api_url=api_url.rstrip("/") if api_url else None,
            pipeline_token=token or None,
            http_timeout=float(overrides.pop("http_timeout", None) or timeout_txt or 20.0),
        )
        if overrides:
            raise TypeError(f"Parâmetros de configuração desconhecidos: {sorted(overrides)}")
        return cfg

    def com(self, **mudancas) -> "PipelineConfig":
        """Cópia da configuração com campos alterados."""
        return replace(self, **mudancas)

    @property
    def api_configurada(self) -> bool:
        return bool(self.api_url and self.pipeline_token)

    @property
    def snapshot_path(self) -> Path:
        return self.gold_dir / "gold_snapshot.json"

    @property
    def relatorio_json_path(self) -> Path:
        return self.processed_dir / "relatorio_qualidade.json"

    @property
    def relatorio_md_path(self) -> Path:
        return self.processed_dir / "relatorio_qualidade.md"

    def garantir_pastas(self) -> None:
        for pasta in (self.exports_dir, self.processed_dir, self.gold_dir, self.warehouse_path.parent):
            pasta.mkdir(parents=True, exist_ok=True)

    def descrever(self) -> dict:
        """Resumo seguro para log (sem o token)."""
        return {
            "data_dir": str(self.data_dir),
            "samples_csv": str(self.samples_csv),
            "exports_dir": str(self.exports_dir),
            "gold_dir": str(self.gold_dir),
            "warehouse_path": str(self.warehouse_path),
            "api_url": self.api_url or "(não configurada)",
            "pipeline_token": "(configurado)" if self.pipeline_token else "(não configurado)",
        }
