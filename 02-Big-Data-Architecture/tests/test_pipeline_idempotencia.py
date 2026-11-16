"""Idempotência e reprodutibilidade: rodar 2x dá o mesmo resultado; a fonte é determinística."""
import hashlib
import json

from acessacidade_pipeline import simulate
from acessacidade_pipeline.config import REPO_ROOT
from acessacidade_pipeline.gold import TABELAS_GOLD
from acessacidade_pipeline.run_pipeline import executar_pipeline

VOLATEIS = {"gerado_em", "execucao_id"}


def _saidas(cfg) -> dict:
    arquivos = {t: (cfg.gold_dir / f"{t}.csv").read_bytes() for t in TABELAS_GOLD}
    snap = json.loads(cfg.snapshot_path.read_text(encoding="utf-8"))
    arquivos["snapshot"] = {k: v for k, v in snap.items() if k not in VOLATEIS}
    return arquivos


def test_rodar_duas_vezes_produz_o_mesmo_resultado(cfg_tmp):
    executar_pipeline(usar_api=False, execucao_id="manual__1", cfg=cfg_tmp)
    primeira = _saidas(cfg_tmp)
    estado = executar_pipeline(usar_api=False, execucao_id="manual__2", cfg=cfg_tmp)
    segunda = _saidas(cfg_tmp)
    assert primeira == segunda
    assert estado["linhas_raw"] == 271  # full refresh: a RAW não acumula linhas entre execuções


def test_gerador_e_deterministico(tmp_path):
    a = simulate.gerar_csv(tmp_path / "a.csv")
    b = simulate.gerar_csv(tmp_path / "b.csv")
    assert a.read_bytes() == b.read_bytes()
    assert simulate.gerar_csv(tmp_path / "c.csv", semente=1).read_bytes() != a.read_bytes()


def test_csv_versionado_no_repositorio_e_reproduzivel(tmp_path):
    versionado = REPO_ROOT / "data" / "samples" / "denuncias_simuladas.csv"
    assert versionado.exists(), "rode: python -m acessacidade_pipeline.simulate"
    gerado = simulate.gerar_csv(tmp_path / "x.csv")
    assert hashlib.sha256(versionado.read_bytes()).hexdigest() == hashlib.sha256(gerado.read_bytes()).hexdigest()
