"""Gera a base de imagens SINTÉTICAS de teste do AcessaCidade (semente fixa).

As imagens são desenhadas por procedimento (numpy + OpenCV): textura de pavimento
(concreto, asfalto ou bloquete), buracos com borda irregular e gradiente de
profundidade, sombras, manchas, rachaduras, poça e fotos de baixa qualidade.
Nenhuma imagem é fotografia real; todas são identificadas como SINTÉTICAS no nome
do arquivo (prefixo ``sintetica_``), no LEIAME.txt e no CSV de rótulos.

O "rótulo manual" de cada imagem é o rótulo ESPERADO POR CONSTRUÇÃO (quem escreveu
o gerador sabe o que desenhou em cada cena). Ele NÃO é uma anotação de foto real.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\gerar_imagens_sinteticas.py
Opções: --saida <pasta das fotos>  --rotulos <csv>  --semente 2026
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "data" / "samples" / "fotos"
DEFAULT_LABELS = ROOT / "04-Applied-Computer-Vision" / "samples" / "rotulos_manuais_sinteticas.csv"
SEED = 2026

POSSIBLE = "POSSIBLE_POTHOLE"
NOT_ID = "NOT_IDENTIFIED"
INCONC = "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Texturas
# ---------------------------------------------------------------------------
def noise_layer(rng: np.random.Generator, h: int, w: int, cell: int) -> np.ndarray:
    """Ruído suave (valor ~N(0,1)) com estrutura na escala ``cell`` px."""
    sh, sw = max(2, h // cell + 2), max(2, w // cell + 2)
    small = rng.normal(0.0, 1.0, (sh, sw)).astype(np.float32)
    big = cv2.resize(small, (w + 2 * cell, h + 2 * cell), interpolation=cv2.INTER_CUBIC)
    return big[cell:cell + h, cell:cell + w]


def speckles(rng, img, n, rmin, rmax, amp):
    h, w = img.shape
    for _ in range(n):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        r = int(rng.integers(rmin, rmax + 1))
        cv2.circle(img, (x, y), r, float(rng.uniform(-amp, amp)), -1)


def pavement(rng, h, w, kind):
    if kind == "concreto":
        base = rng.uniform(150, 175)
        g = base + 9 * noise_layer(rng, h, w, 96) + 6 * noise_layer(rng, h, w, 18) + 5 * noise_layer(rng, h, w, 4)
        agg = np.zeros((h, w), np.float32)
        speckles(rng, agg, int(h * w / 250), 1, 2, 22)
        g = g + cv2.GaussianBlur(agg, (3, 3), 0) + rng.normal(0, 4.5, (h, w))
        if rng.random() < 0.8:  # juntas de dilatação entre placas
            step = int(rng.uniform(0.35, 0.5) * w)
            for x in range(step, w, step):
                cv2.line(g, (x, 0), (x + int(rng.integers(-15, 15)), h), float(base - 35), 3)
        tint = (0.97, 1.0, 1.03)
    elif kind == "asfalto":
        base = rng.uniform(105, 125)
        g = base + 7 * noise_layer(rng, h, w, 80) + 6 * noise_layer(rng, h, w, 10) + 8 * noise_layer(rng, h, w, 3)
        agg = np.zeros((h, w), np.float32)
        speckles(rng, agg, int(h * w / 120), 1, 2, 35)
        g = g + cv2.GaussianBlur(agg, (3, 3), 0) + rng.normal(0, 6, (h, w))
        tint = (1.02, 1.0, 0.98)
    else:  # bloquete (pavers retangulares)
        base = rng.uniform(140, 160)
        g = np.zeros((h, w), np.float32)
        bw, bh = int(rng.integers(110, 140)), int(rng.integers(55, 70))
        for r, y in enumerate(range(-bh, h + bh, bh)):
            off = (bw // 2) * (r % 2)
            for x in range(-bw - off, w + bw, bw):
                g[max(0, y):max(0, y + bh), max(0, x):max(0, x + bw)] = base + rng.uniform(-10, 10)
                cv2.rectangle(g, (x, y), (x + bw, y + bh), float(base - 45), 3)
        g = cv2.GaussianBlur(g, (3, 3), 0)
        g = g + 5 * noise_layer(rng, h, w, 12) + 4 * noise_layer(rng, h, w, 3) + rng.normal(0, 4, (h, w))
        tint = (0.95, 1.0, 1.06)
    # gradiente de iluminação suave
    ang = rng.uniform(0, 2 * math.pi)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ramp = (np.cos(ang) * xx / w + np.sin(ang) * yy / h)
    g = g * (0.95 + 0.08 * (ramp - ramp.min()) / max(1e-6, np.ptp(ramp)))
    return g.astype(np.float32), tint


def to_bgr(gray, tint):
    b = np.clip(gray * tint[0], 0, 255)
    g = np.clip(gray * tint[1], 0, 255)
    r = np.clip(gray * tint[2], 0, 255)
    return np.dstack([b, g, r]).astype(np.uint8)


# ---------------------------------------------------------------------------
# Formas
# ---------------------------------------------------------------------------
def irregular_mask(rng, h, w, cx, cy, radius, irregular=0.35, stretch=1.0, angle=0.0, n=220):
    theta = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = np.ones_like(theta)
    for k in range(2, 9):
        r += rng.uniform(0, irregular / k) * np.cos(k * theta + rng.uniform(0, 2 * math.pi))
    r += rng.normal(0, 0.02, n)  # recortes finos na borda
    r = radius * np.clip(r, 0.35, 2.0)
    x = r * np.cos(theta) * stretch
    y = r * np.sin(theta)
    ca, sa = math.cos(angle), math.sin(angle)
    px = cx + x * ca - y * sa
    py = cy + x * sa + y * ca
    pts = np.stack([px, py], axis=1).round().astype(np.int32)
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [pts], 255)
    return m


def add_pothole(rng, g, cx, cy, radius, stretch=1.0, angle=0.0, raso=False, agua=False):
    h, w = g.shape
    m = irregular_mask(rng, h, w, cx, cy, radius, 0.45, stretch, angle)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    dn = dist / max(1.0, dist.max())
    pave = float(np.median(g[m == 0]))
    # fundo: mais escuro no centro (profundidade)
    depth = pave * ((0.84 - 0.08 * np.sqrt(dn)) if raso else (0.66 - 0.30 * np.sqrt(dn)))
    rough = (14 * noise_layer(rng, h, w, 3) + 12 * noise_layer(rng, h, w, 9) + 8 * noise_layer(rng, h, w, 25))
    if raso:  # buraco raso: fundo pouco mais escuro e pouco rugoso
        rough *= 0.35
    stones = np.zeros((h, w), np.float32)
    ys, xs = np.nonzero(m)
    for _ in range(int(len(xs) / 180)):
        i = int(rng.integers(0, len(xs)))
        r = int(rng.integers(2, 6))
        cv2.circle(stones, (int(xs[i]), int(ys[i])), r, float(rng.uniform(35, 75)), -1)
        cv2.circle(stones, (int(xs[i]) + r, int(ys[i]) + r), r, float(rng.uniform(-30, -15)), -1)
    interior = depth + rough + cv2.GaussianBlur(stones, (3, 3), 0)
    # parede interna sombreada (luz vinda de um lado)
    dx, dy = int(rng.integers(-1, 2)) * max(3, radius // 8), max(3, radius // 8)
    shifted = np.roll(np.roll(m, dy, axis=0), dx, axis=1)
    wall = (m > 0) & (shifted == 0)
    interior[wall] *= 0.85 if raso else 0.6
    if agua:  # buraco cheio de água: superfície lisa e escura com reflexos, mantendo a borda quebrada
        inner = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        water = 62 + 5 * noise_layer(rng, h, w, 50) + cv2.GaussianBlur(
            (noise_layer(rng, h, w, 25) > 1.3).astype(np.float32) * 60, (0, 0), 3)
        interior[inner] = water[inner]
    # borda quebrada: anel externo irregular mais claro (lascas)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    ring = (cv2.dilate(m, k) > 0) & (m == 0)
    chips = (noise_layer(rng, h, w, 4) > 0.3) & ring
    g = g.copy()
    g[chips] += 28
    alpha = cv2.GaussianBlur((m > 0).astype(np.float32), (5, 5), 1.0)
    return g * (1 - alpha) + interior * alpha


def add_multiplicative(g, mask, strength, blur_sigma, extra=None):
    alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), blur_sigma)
    factor = 1.0 - strength * alpha
    if extra is not None:
        factor = factor * extra
    return g * factor


def add_building_shadow(rng, g, sigma):
    h, w = g.shape
    m = np.zeros((h, w), np.uint8)
    x1 = int(rng.uniform(0.35, 0.55) * w)
    x2 = int(rng.uniform(0.5, 0.75) * w)
    cv2.fillPoly(m, [np.array([[0, 0], [x1, 0], [x2, h], [0, h]], np.int32)], 255)
    return add_multiplicative(g, m, rng.uniform(0.42, 0.55), sigma)


def add_pole_shadow(rng, g):
    h, w = g.shape
    m = np.zeros((h, w), np.uint8)
    x0 = int(rng.uniform(0.2, 0.4) * w)
    cv2.line(m, (x0, h), (int(x0 + 0.45 * w), 0), 255, int(rng.integers(28, 40)))
    return add_multiplicative(g, m, rng.uniform(0.45, 0.55), 4.0)


def add_tree_shade(rng, g, center=None):
    h, w = g.shape
    cx, cy = center if center is not None else (rng.uniform(0.4, 0.6), rng.uniform(0.4, 0.6))
    m = irregular_mask(rng, h, w, w * cx, h * cy,
                       min(h, w) * 0.16, 0.6, 1.3, rng.uniform(0, 3.14))
    return add_multiplicative(g, m, rng.uniform(0.45, 0.55), 6.0)


def add_stain(rng, g, strength, radius_frac, sigma, radial=True):
    h, w = g.shape
    m = irregular_mask(rng, h, w, w * rng.uniform(0.35, 0.65), h * rng.uniform(0.35, 0.65),
                       min(h, w) * radius_frac, 0.4, rng.uniform(1.0, 1.4), rng.uniform(0, 3.14))
    extra = None
    if radial:
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
        dn = dist / max(1.0, dist.max())
        extra = 1.0 - 0.12 * dn  # óleo concentrado no centro
    mottle = 1.0 + 0.04 * noise_layer(rng, h, w, 20) * (m > 0)
    extra = mottle if extra is None else extra * mottle
    return add_multiplicative(g, m, strength, sigma, extra)


def add_crack(rng, g, branches=1):
    h, w = g.shape
    m = np.zeros((h, w), np.uint8)
    for b in range(branches):
        x, y = float(rng.uniform(0.05, 0.3) * w), float(rng.uniform(0.2, 0.8) * h)
        ang = rng.uniform(-0.5, 0.5)
        width = int(rng.integers(3, 6))
        for _ in range(140):
            ang += rng.normal(0, 0.25)
            ang = float(np.clip(ang, -1.0, 1.0))
            step = rng.uniform(4, 9)
            nx, ny = x + step * math.cos(ang), y + step * math.sin(ang)
            cv2.line(m, (int(x), int(y)), (int(nx), int(ny)), 255, max(1, width + int(rng.integers(-1, 2))))
            x, y = nx, ny
            if not (0 <= x < w and 0 <= y < h):
                break
    alpha = cv2.GaussianBlur(m.astype(np.float32) / 255.0, (3, 3), 0)
    return g * (1 - 0.6 * alpha)


def add_manhole(rng, g):
    """Tampa de bueiro/caixa de inspeção: disco escuro com relevo em grade e aro metálico."""
    h, w = g.shape
    cx, cy, r = int(w * 0.52), int(h * 0.5), int(min(h, w) * 0.15)
    disk = np.zeros((h, w), np.uint8)
    cv2.circle(disk, (cx, cy), r, 255, -1)
    cover = np.full((h, w), 72.0, np.float32) + 6 * noise_layer(rng, h, w, 6)
    for k in range(-r, r, 14):
        cv2.line(cover, (cx + k, cy - r), (cx + k, cy + r), 105.0, 3)
        cv2.line(cover, (cx - r, cy + k), (cx + r, cy + k), 105.0, 3)
    out = g.copy()
    out[disk > 0] = cover[disk > 0]
    cv2.circle(out, (cx, cy), r, 125.0, 5)  # aro
    soft = cv2.GaussianBlur(out, (3, 3), 0.8)  # suaviza só a tampa (antisserrilhado)
    region = cv2.dilate(disk, np.ones((9, 9), np.uint8)) > 0
    out[region] = soft[region]
    return out


def add_puddle(rng, g):
    h, w = g.shape
    m = irregular_mask(rng, h, w, w * 0.5, h * 0.55, min(h, w) * 0.2, 0.35, 1.6, rng.uniform(-0.3, 0.3))
    water = 55 + 6 * noise_layer(rng, h, w, 60)  # superfície lisa, reflexo escuro
    hl = (noise_layer(rng, h, w, 30) > 1.4).astype(np.float32) * 70  # reflexos do céu
    water = water + cv2.GaussianBlur(hl, (0, 0), 3)
    alpha = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 1.5)
    return g * (1 - alpha) + water * alpha


# ---------------------------------------------------------------------------
# Cenas
# ---------------------------------------------------------------------------
def _scene(rng, size, kind):
    w, h = size
    g, tint = pavement(rng, h, w, kind)
    return g, tint, h, w


def cena_buraco(rng, size, kind, rfrac, pos=(0.5, 0.5), stretch=1.0, extras=(), **kw):
    g, tint, h, w = _scene(rng, size, kind)
    for e in extras:
        if e == "sombra_suave":
            g = add_tree_shade(rng, g, center=(0.74, 0.32))
        elif e == "mancha":
            g = add_stain(rng, g, 0.3, 0.07, 6.0)
    r = int(min(h, w) * rfrac)
    g = add_pothole(rng, g, w * pos[0], h * pos[1], r, stretch, rng.uniform(-0.6, 0.6), **kw)
    return to_bgr(g, tint)


def build_scenes(seed: int = SEED) -> list[dict]:
    """Lista de cenas: nome do arquivo, imagem BGR, rótulo esperado, cenário e descrição."""
    specs = [
        ("sintetica_buraco_01.jpg", POSSIBLE, "buraco", "Buraco médio no centro, calçada de concreto.",
         lambda r: cena_buraco(r, (1024, 768), "concreto", 0.17)),
        ("sintetica_buraco_02.jpg", POSSIBLE, "buraco", "Buraco grande em asfalto de travessia.",
         lambda r: cena_buraco(r, (1024, 768), "asfalto", 0.22, (0.45, 0.55))),
        ("sintetica_buraco_03.jpg", POSSIBLE, "buraco", "Buraco em calçada de bloquetes.",
         lambda r: cena_buraco(r, (960, 720), "bloquete", 0.16, (0.55, 0.5))),
        ("sintetica_buraco_04.jpg", POSSIBLE, "buraco", "Buraco pequeno fora do centro, concreto com juntas.",
         lambda r: cena_buraco(r, (1200, 900), "concreto", 0.10, (0.68, 0.38))),
        ("sintetica_buraco_05.jpg", POSSIBLE, "buraco_com_sombra", "Buraco com sombra suave de árvore em outra parte da foto.",
         lambda r: cena_buraco(r, (1024, 768), "concreto", 0.14, (0.27, 0.66), extras=("sombra_suave",))),
        ("sintetica_buraco_06.jpg", POSSIBLE, "buraco", "Buraco alongado pela perspectiva (foto oblíqua), asfalto, foto em pé.",
         lambda r: cena_buraco(r, (768, 1024), "asfalto", 0.16, (0.5, 0.62), stretch=1.6)),
        ("sintetica_buraco_07.jpg", POSSIBLE, "buraco_com_mancha", "Buraco com uma mancha escura próxima.",
         lambda r: cena_buraco(r, (1024, 768), "concreto", 0.15, (0.62, 0.55), extras=("mancha",))),
        ("sintetica_buraco_raso_01.jpg", POSSIBLE, "buraco_dificil", "Buraco raso, pouco mais escuro que o piso (caso difícil).",
         lambda r: cena_buraco(r, (1024, 768), "concreto", 0.17, raso=True)),
        ("sintetica_buraco_com_agua_01.jpg", POSSIBLE, "buraco_dificil", "Buraco cheio de água: fundo liso e escuro (caso difícil).",
         lambda r: cena_buraco(r, (1024, 768), "asfalto", 0.18, (0.5, 0.55), agua=True)),
        ("sintetica_calcada_lisa_01.jpg", NOT_ID, "calcada_lisa", "Calçada de concreto sem defeitos, com juntas.",
         lambda r: to_bgr(*pavement(r, 768, 1024, "concreto"))),
        ("sintetica_calcada_lisa_02.jpg", NOT_ID, "calcada_lisa", "Asfalto sem defeitos.",
         lambda r: to_bgr(*pavement(r, 768, 1024, "asfalto"))),
        ("sintetica_calcada_lisa_03.jpg", NOT_ID, "calcada_lisa", "Calçada de bloquetes sem defeitos.",
         lambda r: to_bgr(*pavement(r, 720, 960, "bloquete"))),
        ("sintetica_sombra_01.jpg", NOT_ID, "sombra", "Sombra de edifício com borda nítida, encostada na lateral.",
         lambda r: _apply(r, (1024, 768), "concreto", lambda rr, g: add_building_shadow(rr, g, 2.5))),
        ("sintetica_sombra_02.jpg", NOT_ID, "sombra", "Sombra de poste atravessando o asfalto.",
         lambda r: _apply(r, (1024, 768), "asfalto", add_pole_shadow)),
        ("sintetica_sombra_03.jpg", NOT_ID, "sombra", "Sombra arredondada de copa de árvore no meio da calçada.",
         lambda r: _apply(r, (1024, 768), "concreto", add_tree_shade)),
        ("sintetica_mancha_01.jpg", NOT_ID, "mancha", "Mancha de óleo escura (mais concentrada no centro).",
         lambda r: _apply(r, (1024, 768), "concreto", lambda rr, g: add_stain(rr, g, 0.45, 0.13, 5.0))),
        ("sintetica_mancha_02.jpg", NOT_ID, "mancha", "Mancha de umidade grande e suave em bloquetes.",
         lambda r: _apply(r, (960, 720), "bloquete", lambda rr, g: add_stain(rr, g, 0.35, 0.2, 12.0, radial=False))),
        ("sintetica_rachadura_01.jpg", NOT_ID, "rachadura", "Rachadura fina atravessando o concreto.",
         lambda r: _apply(r, (1024, 768), "concreto", lambda rr, g: add_crack(rr, g, 1))),
        ("sintetica_rachadura_02.jpg", NOT_ID, "rachadura", "Rede de rachaduras no asfalto.",
         lambda r: _apply(r, (1024, 768), "asfalto", lambda rr, g: add_crack(rr, g, 3))),
        ("sintetica_tampa_bueiro_01.jpg", NOT_ID, "tampa_bueiro", "Tampa de bueiro escura com relevo em grade (não é buraco).",
         lambda r: _apply(r, (1024, 768), "concreto", add_manhole)),
        ("sintetica_poca_01.jpg", NOT_ID, "poca", "Poça d'água rasa sobre asfalto (sem buraco desenhado).",
         lambda r: _apply(r, (1024, 768), "asfalto", add_puddle)),
        ("sintetica_escura_01.jpg", INCONC, "foto_escura", "Cena com buraco fotografada quase sem luz.",
         lambda r: _degrade(cena_buraco(r, (1024, 768), "concreto", 0.16), "escura", r)),
        ("sintetica_clara_01.jpg", INCONC, "foto_estourada", "Cena com buraco superexposta (estourada).",
         lambda r: _degrade(cena_buraco(r, (1024, 768), "concreto", 0.16), "clara", r)),
        ("sintetica_borrada_01.jpg", INCONC, "foto_borrada", "Cena com buraco fora de foco (borrada).",
         lambda r: _degrade(cena_buraco(r, (1024, 768), "asfalto", 0.18), "borrada", r)),
        ("sintetica_baixo_contraste_01.jpg", INCONC, "foto_baixo_contraste", "Cena com buraco e contraste muito baixo (neblina/lente suja).",
         lambda r: _degrade(cena_buraco(r, (1024, 768), "concreto", 0.16), "baixo_contraste", r)),
    ]
    scenes = []
    for idx, (name, label, cenario, desc, fn) in enumerate(specs):
        rng = np.random.default_rng(seed * 1000 + idx)
        scenes.append({"arquivo": name, "rotulo": label, "cenario": cenario, "descricao": desc, "imagem": fn(rng)})
    return scenes


def _apply(rng, size, kind, fn):
    g, tint, h, w = _scene(rng, size, kind)
    return to_bgr(fn(rng, g), tint)


def _degrade(img, mode, rng):
    f = img.astype(np.float32)
    if mode == "escura":
        f = f * 0.16 + rng.normal(0, 2.5, f.shape)
    elif mode == "clara":
        f = f * 1.5 + 95
    elif mode == "borrada":
        f = cv2.GaussianBlur(f, (0, 0), 7.0)
    elif mode == "baixo_contraste":
        f = (f - f.mean()) * 0.15 + 150
    return np.clip(f, 0, 255).astype(np.uint8)


LEIAME = """BASE DE IMAGENS SINTÉTICAS — AcessaCidade (disciplina Applied Computer Vision)
==============================================================================

TODAS as imagens desta pasta são SINTÉTICAS: foram desenhadas por computador pelo
script 04-Applied-Computer-Vision/scripts/gerar_imagens_sinteticas.py (semente fixa {seed}).
Nenhuma delas é fotografia real, nenhuma mostra pessoas, placas de veículos ou locais reais.

Para que servem
- Testar o fluxo de visão computacional de ponta a ponta (validação, filtragem,
  limiarização, morfologia, contornos, medidas e regra de classificação).
- Demonstrar casos que costumam confundir a triagem (sombras, manchas, rachaduras, poça)
  e casos de foto inadequada (escura, estourada, borrada, baixo contraste).

O que NÃO são
- Não medem o desempenho do sistema no mundo real. Resultados obtidos com elas não
  podem ser apresentados como acurácia em fotos reais de calçadas.

Rótulos
- O rótulo "manual" de cada imagem está em
  04-Applied-Computer-Vision/samples/rotulos_manuais_sinteticas.csv e é o rótulo
  ESPERADO POR CONSTRUÇÃO (quem gerou a cena sabe o que desenhou nela).

Como regenerar (na raiz do repositório)
  .venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\scripts\\gerar_imagens_sinteticas.py

Arquivos ({n} imagens)
{lista}
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gera imagens sintéticas de teste (semente fixa).")
    ap.add_argument("--saida", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--rotulos", type=Path, default=DEFAULT_LABELS)
    ap.add_argument("--semente", type=int, default=SEED)
    args = ap.parse_args(argv)

    args.saida.mkdir(parents=True, exist_ok=True)
    args.rotulos.parent.mkdir(parents=True, exist_ok=True)
    scenes = build_scenes(args.semente)
    for s in scenes:
        ok, buf = cv2.imencode(".jpg", s["imagem"], [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        assert ok
        (args.saida / s["arquivo"]).write_bytes(buf.tobytes())

    with open(args.rotulos, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["arquivo", "rotulo_manual", "cenario", "descricao", "origem", "metodo_rotulagem"])
        for s in scenes:
            wr.writerow([s["arquivo"], s["rotulo"], s["cenario"], s["descricao"], "SINTETICA",
                         "esperado_por_construcao"])

    lista = "\n".join(f"- {s['arquivo']}: {s['descricao']} (rótulo esperado: {s['rotulo']})" for s in scenes)
    (args.saida / "LEIAME.txt").write_text(
        LEIAME.format(seed=args.semente, n=len(scenes), lista=lista), encoding="utf-8"
    )
    print(f"{len(scenes)} imagens sintéticas geradas em {args.saida}")
    print(f"Rótulos esperados por construção: {args.rotulos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
