"""Testes da análise (acessacidade_vision.analyze_image) com imagens SINTÉTICAS geradas em memória."""

from __future__ import annotations

import importlib.util
import json
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pytest

from acessacidade_vision import (
    ALGORITHM_VERSION,
    CLASS_LABELS,
    STAGE_ORDER,
    AnalysisResult,
    VisionError,
    analyze_image,
    correct_perspective,
    sanitize_image,
)
from acessacidade_vision.constants import AVISO

COMPONENT = Path(__file__).resolve().parents[1]
EXPECTED_KEYS = {"classificacao", "rotulo", "pontuacao", "explicacao", "metricas", "deteccoes", "versao_algoritmo", "aviso"}


@lru_cache(maxsize=1)
def _gerador():
    path = COMPONENT / "scripts" / "gerar_imagens_sinteticas.py"
    spec = importlib.util.spec_from_file_location("acessacidade_gerador_sinteticas", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _jpeg(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    assert ok
    return buf.tobytes()


@lru_cache(maxsize=None)
def _cena(nome: str) -> bytes:
    g = _gerador()
    rng = np.random.default_rng(12345)
    if nome == "buraco":
        img = g.cena_buraco(rng, (1024, 768), "concreto", 0.17)
    elif nome == "buraco_asfalto":
        img = g.cena_buraco(rng, (1024, 768), "asfalto", 0.2)
    elif nome == "lisa":
        img = g.to_bgr(*g.pavement(rng, 768, 1024, "concreto"))
    elif nome == "escura":
        img = g._degrade(g.cena_buraco(rng, (1024, 768), "concreto", 0.16), "escura", rng)
    elif nome == "borrada":
        img = g._degrade(g.cena_buraco(rng, (1024, 768), "concreto", 0.16), "borrada", rng)
    elif nome == "rachadura":
        g2, tint = g.pavement(rng, 768, 1024, "concreto")
        img = g.to_bgr(g.add_crack(rng, g2, 1), tint)
    else:  # pragma: no cover
        raise KeyError(nome)
    return _jpeg(img)


@pytest.fixture(scope="module")
def resultado_buraco() -> AnalysisResult:
    return analyze_image(_cena("buraco"))


def test_constantes_publicas():
    assert ALGORITHM_VERSION == "1.0.0"
    assert STAGE_ORDER == ("original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos")
    assert CLASS_LABELS == {
        "POSSIBLE_POTHOLE": "Possível buraco identificado",
        "NOT_IDENTIFIED": "Nenhum indício suficiente de buraco",
        "INCONCLUSIVE": "Análise inconclusiva",
    }


def test_retorna_todas_as_etapas(resultado_buraco):
    assert tuple(resultado_buraco.stages.keys()) == STAGE_ORDER
    h, w = resultado_buraco.stages["original"].shape[:2]
    for nome in STAGE_ORDER:
        img = resultado_buraco.stages[nome]
        assert isinstance(img, np.ndarray) and img.dtype == np.uint8
        assert img.shape[:2] == (h, w)
    assert max(h, w) == 800  # cópia de trabalho


def test_to_dict_tem_chaves_do_contrato_e_e_serializavel(resultado_buraco):
    d = resultado_buraco.to_dict()
    assert set(d.keys()) == EXPECTED_KEYS
    assert d["versao_algoritmo"] == ALGORITHM_VERSION
    assert d["aviso"] == AVISO
    assert d["rotulo"] == CLASS_LABELS[d["classificacao"]]
    assert isinstance(d["explicacao"], list) and all(isinstance(t, str) for t in d["explicacao"])
    assert 0.0 <= d["pontuacao"] <= 1.0
    for k in ("brilho_medio", "contraste_rms", "nitidez_laplaciano", "limiar_otsu", "candidatas"):
        assert k in d["metricas"]
    json.dumps(d)  # não levanta
    assert "stages" not in d


def test_deteccoes_tem_campos_do_contrato(resultado_buraco):
    assert resultado_buraco.detections, "o buraco sintético deveria gerar ao menos uma detecção"
    w = resultado_buraco.metrics["largura_analise"]
    h = resultado_buraco.metrics["altura_analise"]
    for det in resultado_buraco.detections:
        for k in ("x", "y", "largura", "altura", "area_px"):
            assert isinstance(det[k], int)
        assert 0 <= det["x"] < w and 0 <= det["y"] < h
        assert det["x"] + det["largura"] <= w and det["y"] + det["altura"] <= h
        assert det["area_px"] > 0


def test_buraco_sintetico_e_possible_pothole(resultado_buraco):
    assert resultado_buraco.classification == "POSSIBLE_POTHOLE"
    assert resultado_buraco.label == "Possível buraco identificado"
    assert resultado_buraco.score >= 0.60
    texto = " ".join(resultado_buraco.reasons)
    assert "não é probabilidade" in texto
    assert "sombras" in texto  # limitação sempre citada


def test_buraco_em_asfalto_e_possible_pothole():
    assert analyze_image(_cena("buraco_asfalto")).classification == "POSSIBLE_POTHOLE"


def test_calcada_lisa_e_not_identified():
    r = analyze_image(_cena("lisa"))
    assert r.classification == "NOT_IDENTIFIED"
    assert r.detections == []
    assert r.score < 0.42


def test_rachadura_fina_nao_e_buraco():
    assert analyze_image(_cena("rachadura")).classification == "NOT_IDENTIFIED"


def test_imagem_escura_e_inconclusive():
    r = analyze_image(_cena("escura"))
    assert r.classification == "INCONCLUSIVE"
    assert r.metrics["qualidade_adequada"] is False
    assert any("escura" in t for t in r.reasons)
    assert r.detections == []


def test_imagem_borrada_e_inconclusive():
    r = analyze_image(_cena("borrada"))
    assert r.classification == "INCONCLUSIVE"
    assert any("borrada" in t for t in r.reasons)


def test_imagem_uniforme_e_inconclusive():
    plain = np.full((480, 640, 3), 128, dtype=np.uint8)
    r = analyze_image(_jpeg(plain))
    assert r.classification == "INCONCLUSIVE"


def test_classes_sempre_validas():
    for nome in ("buraco", "lisa", "escura", "borrada", "rachadura"):
        r = analyze_image(_cena(nome))
        assert r.classification in CLASS_LABELS
        assert r.label == CLASS_LABELS[r.classification]
        assert 0.0 <= r.score <= 1.0


def test_determinismo():
    data = _cena("buraco")
    a, b = analyze_image(data), analyze_image(data)
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)
    for nome in STAGE_ORDER:
        assert np.array_equal(a.stages[nome], b.stages[nome])


def test_encode_stages_gera_jpeg_de_cada_etapa(resultado_buraco):
    enc = resultado_buraco.encode_stages()
    assert tuple(enc.keys()) == STAGE_ORDER
    for nome, data in enc.items():
        assert data[:3] == b"\xff\xd8\xff", nome
        assert cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED) is not None
    png = resultado_buraco.encode_stages(".png")
    assert png["mascara"][:8] == b"\x89PNG\r\n\x1a\n"


def test_fluxo_do_backend_valida_sanitiza_analisa():
    limpa = sanitize_image(_cena("buraco"), max_side=1600)
    r = analyze_image(limpa)
    assert r.classification == "POSSIBLE_POTHOLE"


def test_analyze_rejeita_entrada_invalida():
    with pytest.raises(VisionError):
        analyze_image(b"\x00\x01\x02")


def test_imagem_pequena_valida_e_analisada():
    rng = np.random.default_rng(5)
    img = rng.integers(100, 160, (80, 100, 3), dtype=np.uint8)
    r = analyze_image(_jpeg(img))
    assert r.classification in CLASS_LABELS
    assert r.stages["original"].shape[:2] == (80, 100)  # não amplia


def test_correcao_de_perspectiva():
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    pts = np.array([[100, 50], [500, 80], [550, 380], [60, 350]], dtype=np.int32)
    cv2.fillPoly(img, [pts], (255, 255, 255))
    out = correct_perspective(img, pts.astype(np.float32).tolist())
    assert out.shape[0] > 100 and out.shape[1] > 100
    # depois da retificação o quadrilátero branco ocupa (quase) toda a imagem
    assert (out > 200).mean() > 0.95
    fixed = correct_perspective(img, pts.tolist(), output_size=(300, 200))
    assert fixed.shape[:2] == (200, 300)
    with pytest.raises(VisionError):
        correct_perspective(img, [[0, 0], [1, 1]])


def test_analyze_com_pontos_de_perspectiva():
    data = _cena("buraco")
    pts = [[50, 40], [980, 40], [980, 730], [50, 730]]
    r = analyze_image(data, perspective_points=pts)
    assert r.classification in CLASS_LABELS
    assert r.metrics["largura_original"] == 1024
