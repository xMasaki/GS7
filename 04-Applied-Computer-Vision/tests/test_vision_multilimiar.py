"""Testes do multi-limiar, do Canny adaptativo e da regressão em fotos reais de buraco."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from acessacidade_vision import analyze_image, sanitize_image
from acessacidade_vision import classifier, segmentation

COMPONENT = Path(__file__).resolve().parents[1]
PASTA_REAIS = COMPONENT / "buraco"

# Caixa aproximada do buraco (x0, y0, x1, y1) e tamanho original (w, h), marcada à mão.
BURACOS_REAIS = {
    "Buraco1.jpg": (70, 95, 360, 310, 480, 360),
    "Buraco2.jpg": (262, 255, 750, 590, 900, 675),
    "RUA.jpeg": (470, 275, 600, 352, 900, 506),
    "b4.jpg": (240, 225, 495, 405, 700, 466),
}


def test_multi_otsu_isola_populacao_mais_escura():
    rng = np.random.default_rng(0)
    img = np.concatenate([
        rng.normal(30, 4, 2000), rng.normal(130, 6, 6000), rng.normal(220, 5, 2000)
    ]).clip(0, 255).astype(np.uint8).reshape(100, 100)
    t1 = segmentation.multi_otsu_dark_threshold(img)
    assert 40 <= t1 <= 130  # entre a população escura e a média


def test_niveis_de_limiar_ordenados_unicos_e_com_chaves_historicas():
    rng = np.random.default_rng(1)
    gray = rng.normal(140, 25, (120, 160)).clip(0, 255).astype(np.uint8)
    stats, levels = segmentation.threshold_levels(gray)
    assert levels and all(0 <= lv["valor"] <= 254 for lv in levels)
    valores = [lv["valor"] for lv in levels]
    assert all(abs(a - b) > 4.0 for i, a in enumerate(valores) for b in valores[i + 1:])
    for k in ("limiar_otsu", "limiar_robusto", "limiar_aplicado", "mediana_cinza", "efetividade_otsu"):
        assert k in stats


def test_limiar_robusto_tem_teto_em_cena_heterogenea():
    # metade escura, metade clara: sigma robusto enorme derrubaria o limiar para ~0
    gray = np.hstack([np.full((100, 100), 20, np.uint8), np.full((100, 100), 230, np.uint8)])
    gray[:, 95:105] = 125
    stats, levels = segmentation.threshold_levels(gray)
    med = stats["mediana_cinza"]
    assert any(lv["valor"] >= (1 - 0.55) * med - 1 for lv in levels)


def test_canny_adaptativo_reduz_bordas_em_cena_carregada_e_preserva_em_cena_limpa():
    rng = np.random.default_rng(2)
    limpa = np.full((200, 200), 120, np.uint8)
    cv2.rectangle(limpa, (60, 60), (140, 140), 40, -1)
    carregada = rng.integers(0, 255, (200, 200), dtype=np.uint8)
    carregada = cv2.GaussianBlur(carregada, (0, 0), 0.6)
    lo_l, hi_l = segmentation.canny_thresholds(cv2.GaussianBlur(limpa, (0, 0), 1.5))
    lo_c, hi_c = segmentation.canny_thresholds(carregada)
    assert (lo_l, hi_l) == (40.0, 110.0)  # imagem limpa: limiares originais
    assert hi_c > 110.0 and lo_c > 40.0   # cena carregada: sobem
    assert segmentation.detect_edges(limpa)[60:140, 58:62].any()  # borda do quadrado preservada


def test_fator_topo_penaliza_regiao_no_topo_sem_alterar_regiao_central():
    base = {
        "area_relativa": 0.05, "solidez": 0.9, "alongamento": 1.3, "circularidade": 0.6,
        "contraste_int_ext": 0.6, "textura_relativa": 2.0, "razao_bordas": 2.5, "nitidez_borda": 0.1,
        "gradiente_profundidade": 0.1, "fracao_toca_borda_imagem": 0.0,
    }
    s_centro, subs_c = classifier.score_candidate({**base, "centro_y_relativo": 0.55})
    s_topo, subs_t = classifier.score_candidate({**base, "centro_y_relativo": 0.10})
    assert subs_c["fator_topo_imagem"] == 1.0
    assert subs_t["fator_topo_imagem"] < 0.7
    assert s_topo < s_centro


def test_merge_funde_mesma_regiao_de_niveis_diferentes():
    def cand(nivel, x, score, fails=()):
        return {"x": x, "y": 10, "largura": 50, "altura": 50, "area_px": 2000, "pontuacao": score,
                "criterios_nao_atendidos": list(fails), "_nivel_idx": nivel}
    merged = classifier.merge_candidates([cand(0, 10, 0.5), cand(1, 12, 0.7), cand(2, 300, 0.4)])
    assert len(merged) == 2
    mesma = next(c for c in merged if c["x"] < 100)
    assert mesma["pontuacao"] == 0.7 and mesma["niveis_confirmam"] == 2


@pytest.mark.skipif(not PASTA_REAIS.is_dir(), reason="pasta de fotos reais (buraco/) ausente")
@pytest.mark.parametrize("nome", sorted(BURACOS_REAIS))
def test_fotos_reais_de_buraco_localizam_o_buraco(nome):
    arq = PASTA_REAIS / nome
    if not arq.exists():
        pytest.skip(f"{nome} ausente")
    r = analyze_image(sanitize_image(arq.read_bytes()))
    assert r.classification == "POSSIBLE_POTHOLE"
    x0, y0, x1, y1, gw, _gh = BURACOS_REAIS[nome]
    s = r.metrics["largura_analise"] / gw
    gt = (x0 * s, y0 * s, x1 * s, y1 * s)

    def iou(a, b):
        iw, ih = max(0, min(a[2], b[2]) - max(a[0], b[0])), max(0, min(a[3], b[3]) - max(a[1], b[1]))
        i = iw * ih
        return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)

    melhor = max(iou((d["x"], d["y"], d["x"] + d["largura"], d["y"] + d["altura"]), gt) for d in r.detections)
    assert melhor >= 0.5, f"{nome}: a detecção não coincide com o buraco (IoU {melhor:.2f})"
