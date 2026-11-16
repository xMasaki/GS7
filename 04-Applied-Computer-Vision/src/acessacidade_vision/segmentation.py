"""Segmentação: limiarização das regiões escuras, detecção de bordas (Canny),
morfologia matemática e extração de contornos.
"""

from __future__ import annotations

import cv2
import numpy as np

from .constants import SEGMENTATION


def robust_sigma(values: np.ndarray) -> tuple[float, float]:
    """Mediana e desvio robusto (1,4826 · MAD) — pouco sensíveis à própria região escura."""
    v = values.astype(np.float64).ravel()
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med)))
    return med, 1.4826 * mad


def otsu_threshold(gray: np.ndarray) -> tuple[float, float]:
    """Limiar de Otsu e a efetividade η = σ²_entre / σ²_total (0..1).

    Otsu escolhe o limiar t que maximiza a variância entre as classes
    "escura" e "clara". η próximo de 1 indica histograma bimodal (duas populações
    bem separadas); η baixo indica uma única população (piso uniforme).
    """
    t, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    g = gray.astype(np.float64).ravel()
    total_var = float(g.var())
    if total_var <= 1e-9:
        return float(t), 0.0
    low, high = g[g <= t], g[g > t]
    if low.size == 0 or high.size == 0:
        return float(t), 0.0
    w0, w1 = low.size / g.size, high.size / g.size
    between = w0 * w1 * (low.mean() - high.mean()) ** 2
    return float(t), float(between / total_var)


def dark_region_threshold(gray: np.ndarray) -> dict:
    """Combina Otsu com um limiar estatístico robusto.

    limiar_aplicado = min(limiar_otsu, mediana − max(delta_minimo, k · σ_robusto))

    O termo robusto garante que só sejam marcados pixels *claramente* mais escuros
    que o piso predominante; o Otsu garante a separação entre as duas populações
    quando o histograma é bimodal.
    """
    med, sig = robust_sigma(gray)
    t_otsu, eta = otsu_threshold(gray)
    t_rob = med - max(SEGMENTATION["delta_minimo"], SEGMENTATION["k_robusto"] * sig)
    dark_frac = float(np.count_nonzero(gray <= t_otsu)) / float(gray.size)
    # Histograma claramente bimodal com população escura grande (ex.: sombra extensa):
    # a mediana deixa de representar o piso, então usa-se o Otsu para que a região
    # escura apareça como candidata e seja avaliada (e explicada) pela regra.
    bimodal = eta >= SEGMENTATION["eta_bimodal"] and dark_frac >= SEGMENTATION["fracao_escura_bimodal"]
    t = max(0.0, t_otsu if bimodal else min(t_otsu, t_rob))
    return {
        "histograma_bimodal_extenso": bool(bimodal),
        "fracao_escura_otsu": round(dark_frac, 4),
        "mediana_cinza": round(med, 2),
        "sigma_robusto": round(sig, 2),
        "limiar_otsu": round(t_otsu, 2),
        "efetividade_otsu": round(eta, 4),
        "limiar_robusto": round(t_rob, 2),
        "limiar_aplicado": round(t, 2),
    }


def threshold_dark(gray: np.ndarray, threshold: float) -> np.ndarray:
    """Máscara binária: 255 onde o pixel é mais escuro que o limiar (limiarização inversa)."""
    return np.where(gray <= threshold, 255, 0).astype(np.uint8)


def detect_edges(gray: np.ndarray) -> np.ndarray:
    """Detector de bordas de Canny sobre a imagem realçada.

    Antes do Canny aplica-se uma suavização gaussiana extra (σ = 1,5) porque o CLAHE
    também realça a granulação do piso; sem ela o asfalto vira um "tapete" de bordas.
    O Canny calcula o gradiente (Sobel 3x3, norma L2), afina as bordas por supressão
    de não-máximos e liga os trechos por histerese com limiares 40 (fraco) e 110 (forte).
    """
    smooth = cv2.GaussianBlur(gray, (0, 0), SEGMENTATION["canny_sigma_pre"])
    return cv2.Canny(smooth, SEGMENTATION["canny_baixo"], SEGMENTATION["canny_alto"], L2gradient=True)


def morphology(mask: np.ndarray) -> np.ndarray:
    """Abertura (erosão→dilatação) remove pontos isolados e rachaduras finas;
    fechamento (dilatação→erosão) une fragmentos da mesma região; por fim os
    furos internos são preenchidos."""
    k_open = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (SEGMENTATION["abertura_kernel"], SEGMENTATION["abertura_kernel"])
    )
    k_close = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (SEGMENTATION["fechamento_kernel"], SEGMENTATION["fechamento_kernel"])
    )
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_open, iterations=SEGMENTATION["abertura_iteracoes"])
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, k_close, iterations=1)
    return fill_holes(closed)


def fill_holes(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    return filled


def find_candidate_contours(mask: np.ndarray) -> list[np.ndarray]:
    """Contornos externos com área ≥ ``area_minima_rel`` da imagem, do maior para o menor."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    min_area = SEGMENTATION["area_minima_rel"] * mask.shape[0] * mask.shape[1]
    kept = [c for c in contours if cv2.contourArea(c) >= min_area]
    # ordem determinística: área decrescente, depois posição
    kept.sort(key=lambda c: (-cv2.contourArea(c), tuple(int(v) for v in cv2.boundingRect(c))))
    return kept[: SEGMENTATION["max_candidatas"]]
