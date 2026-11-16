"""Imagens de documentação geradas a partir do CAD e da geometria 2D.

* Renderizações 3D simples (matplotlib, sombreamento por face) das malhas do CadQuery.
* Vistas frontais antes × depois, elevação de instalação (escala real) e prévia do arquivo de laser.
* Croquis cotados em SVG (redesign — gerado dos parâmetros; original — MODELO A PREENCHER).

Nenhuma imagem aqui é foto: são desenhos gerados do modelo. As fotos reais do local e do
protótipo são responsabilidade da equipe (ver docs/FOTOS_A_REALIZAR.md).
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

import geometria_2d as G  # noqa: E402
import parametros as P  # noqa: E402

COR_PLACA_NOVA = "#151515"
COR_TEXTO_NOVO = "#F7F7F7"
COR_MODULO = "#F5C400"
COR_ORIG_PLACA = "#5B7290"
COR_ORIG_TEXTO = "#8FA3B8"
AVISO_ESTIMADO = "Dimensões ESTIMADAS — a substituir após medição em campo"


# =====================================================================================
# Renderização 3D
# =====================================================================================
def malha(shape, tol: float = 0.2, ang: float = 0.3) -> tuple[np.ndarray, np.ndarray]:
    verts, tris = shape.tessellate(tol, ang)
    v = np.array([(p.x, p.y, p.z) for p in verts], dtype=float)
    t = np.array(tris, dtype=int)
    return v, t


def renderizar(ax, partes: list[tuple[object, str]], titulo: str, elev: float = 18, azim: float = -58,
               tol: float = 0.2):
    """partes: lista de (shape CadQuery, cor). Eixo Y do modelo vira o eixo vertical do gráfico."""
    luz = np.array([-0.4, -0.8, 0.6])
    luz /= np.linalg.norm(luz)
    tris_all, cores = [], []
    mins, maxs = [], []
    for shape, cor in partes:
        v, t = malha(shape, tol)
        if len(t) == 0:
            continue
        # Subdivide triângulos longos: o matplotlib ordena polígonos pela profundidade média
        # (algoritmo do pintor); triângulos enormes geravam sobreposições erradas na imagem.
        import trimesh
        diag = float(np.linalg.norm(v.max(axis=0) - v.min(axis=0)))
        v, t = trimesh.remesh.subdivide_to_size(v, t, max_edge=max(diag / 25, 1.0), max_iter=12)
        vp = np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])     # (x, -z, y)
        tri = vp[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nn = np.linalg.norm(n, axis=1)
        nn[nn == 0] = 1
        n = n / nn[:, None]
        k = 0.35 + 0.65 * np.clip(np.abs(n @ luz), 0, 1)
        base = np.array(matplotlib.colors.to_rgb(cor))
        cores.append(np.clip(base[None, :] * k[:, None], 0, 1))
        tris_all.append(tri)
        mins.append(vp.min(axis=0))
        maxs.append(vp.max(axis=0))
    tris = np.concatenate(tris_all)
    col = Poly3DCollection(tris, facecolors=np.concatenate(cores), edgecolors="none", linewidths=0)
    ax.add_collection3d(col)
    lo, hi = np.min(mins, axis=0), np.max(maxs, axis=0)
    centro = (lo + hi) / 2
    meio = (hi - lo).max() / 2 * 1.05
    ax.set_xlim(centro[0] - meio, centro[0] + meio)
    ax.set_ylim(centro[1] - meio, centro[1] + meio)
    ax.set_zlim(centro[2] - meio, centro[2] + meio)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(titulo, fontsize=11)


def imagem_comparacao_3d(original_partes, redesign_partes, destino: Path) -> Path:
    fig = plt.figure(figsize=(13, 6.4), dpi=130)
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    renderizar(ax1, original_partes, "ANTES — placa genérica (modelo do original)", tol=1.0)
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    renderizar(ax2, redesign_partes, "DEPOIS — placa acessível AcessaCidade (redesign)", tol=0.15)
    fig.text(0.25, 0.04, f"Escala 1:1 estimada · {AVISO_ESTIMADO}\nSem relevo, sem Braille, sem QR; fixação alta; "
             "baixo contraste (hipótese a verificar no local)", ha="center", fontsize=8.5, color="#333")
    fig.text(0.75, 0.04, "Protótipo: placa 1:3 (laser) + módulo tátil 1:1 (3D) + suporte para tubo Ø25 (3D)\n"
             "Alto contraste, seta e letras em relevo, Braille \"PONTO\", área do QR para reportar no AcessaCidade",
             ha="center", fontsize=8.5, color="#333")
    fig.suptitle("Modelos CAD lado a lado — original × redesign (renderização do modelo, não é foto)", fontsize=12)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


def imagem_peca(partes, titulo: str, destino: Path, elev=28, azim=-60, tol=0.08) -> Path:
    fig = plt.figure(figsize=(6.5, 5.5), dpi=130)
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    renderizar(ax, partes, titulo, elev=elev, azim=azim, tol=tol)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


# =====================================================================================
# 2D: vistas frontais e prévia do laser
# =====================================================================================
def _patch_formas(formas, dx=0.0, dy=0.0, escala=1.0, **kw) -> PathPatch:
    verts, codes = [], []
    for f in formas:
        for poly in f.todos():
            pts = [((x + dx) * escala, (y + dy) * escala) for x, y in poly]
            verts += pts + [pts[0]]
            codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1) + [MplPath.CLOSEPOLY]
    return PathPatch(MplPath(verts, codes), **kw)


def _poly_patch(poly, **kw) -> PathPatch:
    verts = list(poly) + [poly[0]]
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(poly) - 1) + [MplPath.CLOSEPOLY]
    return PathPatch(MplPath(verts, codes), **kw)


def desenhar_placa_redesign(ax, escala: float = 1.0, com_modulo: bool = True, cores_laser: bool = False):
    L = G.layout_placa()
    s = escala
    contorno = [(x * s, y * s) for x, y in L.contorno.poligono()]
    if cores_laser:
        ax.add_patch(_poly_patch(contorno, facecolor="white", edgecolor="#FF0000", lw=1.2))
        for c in L.furos:
            ax.add_patch(Circle((c.cx * s, c.cy * s), c.diametro / 2 * s, fc="white", ec="#FF0000", lw=1))
        for r in L.vetorial:
            ax.add_patch(_poly_patch([(x * s, y * s) for x, y in r.poligono()], fill=False, ec="#0000FF", lw=0.8))
        ax.add_patch(_patch_formas(L.raster, escala=s, facecolor="black", edgecolor="black", lw=0.2))
        qx, qy, lado = L.area_qr
        ax.add_patch(Rectangle(((qx - lado / 2) * s, (qy - lado / 2) * s), lado * s, lado * s, fill=False,
                               ec="#808080", ls="--", lw=1))
        ax.text(qx * s, qy * s, "ÁREA DO QR\n(gerar com URL real)", ha="center", va="center", fontsize=7,
                color="#666")
        return
    ax.add_patch(_poly_patch(contorno, facecolor=COR_PLACA_NOVA, edgecolor="black", lw=1))
    for c in L.furos:
        ax.add_patch(Circle((c.cx * s, c.cy * s), c.diametro / 2 * s, fc="white", ec="#444", lw=0.5))
    ax.add_patch(_poly_patch([(x * s, y * s) for x, y in L.vetorial[0].poligono()], fill=False,
                             ec=COR_TEXTO_NOVO, lw=0.8))
    ax.add_patch(_patch_formas(L.raster, escala=s, facecolor=COR_TEXTO_NOVO, edgecolor="none"))
    qx, qy, lado = L.area_qr
    ax.add_patch(Rectangle(((qx - lado / 2) * s, (qy - lado / 2) * s), lado * s, lado * s, fc=COR_TEXTO_NOVO,
                           ec="#999", hatch="////", lw=0.8))
    ax.text(qx * s, qy * s, "QR CODE\n(URL real\na gerar)", ha="center", va="center", fontsize=7, color="#222",
            bbox=dict(fc="white", ec="none", alpha=0.85))
    if com_modulo:
        mx, my = P.MODULO_CENTRO_NA_PLACA
        mod = G.RetanguloArredondado(mx, my, P.MODULO_LARGURA, P.MODULO_ALTURA, P.MODULO_RAIO_CANTO)
        ax.add_patch(_poly_patch([(x * s, y * s) for x, y in mod.poligono()], fc=COR_MODULO, ec="#8a6d00", lw=0.8))
        seta = G.seta_poligono(mx, my + P.SETA_CENTRO_Y, P.SETA_COMPRIMENTO, P.SETA_LARGURA_HASTE,
                               P.SETA_LARGURA_PONTA, P.SETA_COMPRIMENTO_PONTA, P.SETA_SENTIDO)
        ax.add_patch(_poly_patch([(x * s, y * s) for x, y in seta], fc="#D9A900", ec="#5c4700", lw=0.8))
        letras = G.texto_formas(P.MODULO_TEXTO_RELEVO, P.MODULO_TEXTO_ALTURA_MAIUSCULA, mx, my + P.MODULO_TEXTO_BASE_Y)
        ax.add_patch(_patch_formas(letras, escala=s, fc="#D9A900", ec="#5c4700", lw=0.5))
        for x, y in P.braille_pontos():
            ax.add_patch(Circle(((x + mx) * s, (y + my) * s), P.BRAILLE_DIAMETRO_PONTO / 2 * s, fc="#B38B00",
                                ec="#5c4700", lw=0.4))


def desenhar_placa_original(ax, escala: float = 1.0):
    s = escala
    c = G.RetanguloArredondado(0, 0, P.ORIGINAL_PLACA_LARGURA, P.ORIGINAL_PLACA_ALTURA, P.ORIGINAL_PLACA_RAIO_CANTO)
    ax.add_patch(_poly_patch([(x * s, y * s) for x, y in c.poligono()], fc=COR_ORIG_PLACA, ec="#333", lw=1))
    texto = G.texto_formas(P.ORIGINAL_TEXTO, P.ORIGINAL_TEXTO_ALTURA, 0, -P.ORIGINAL_TEXTO_ALTURA / 2)
    ax.add_patch(_patch_formas(texto, escala=s, fc=COR_ORIG_TEXTO, ec="none"))
    dy = P.ORIGINAL_PLACA_ALTURA / 3
    for y in (dy, -dy):
        ax.add_patch(Circle((0, y * s), P.ORIGINAL_FURO_DIAMETRO / 2 * s, fc="#ccc", ec="#333", lw=0.5))


def _ajustar(ax, w, h, margem=10):
    ax.set_xlim(-w / 2 - margem, w / 2 + margem)
    ax.set_ylim(-h / 2 - margem, h / 2 + margem)
    ax.set_aspect("equal")
    ax.axis("off")


def imagem_vistas_frontais(destino: Path) -> Path:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2), dpi=130)
    desenhar_placa_original(a1)
    _ajustar(a1, P.ORIGINAL_PLACA_LARGURA, P.ORIGINAL_PLACA_ALTURA, 25)
    a1.set_title(f"ANTES — placa genérica {P.ORIGINAL_PLACA_LARGURA:g} × {P.ORIGINAL_PLACA_ALTURA:g} mm (ESTIMADO)\n"
                 "texto de baixo contraste, sem relevo/Braille/QR", fontsize=10)
    desenhar_placa_redesign(a2, escala=1 / P.ESCALA_PROTOTIPO)
    _ajustar(a2, P.REAL_PLACA_LARGURA, P.REAL_PLACA_ALTURA, 25)
    a2.set_title(f"DEPOIS — placa acessível {P.REAL_PLACA_LARGURA:g} × {P.REAL_PLACA_ALTURA:g} mm (escala real sugerida;\n"
                 "protótipo 1:3). Obs.: no tamanho real o módulo tátil continua 1:1", fontsize=10)
    fig.suptitle("Vista frontal na MESMA escala (desenho do modelo; cores ilustrativas)", fontsize=12)
    fig.text(0.5, 0.02, AVISO_ESTIMADO + " (original). Contraste real depende do material — verificar no protótipo.",
             ha="center", fontsize=8.5)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


def imagem_previa_laser(destino: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6.4), dpi=150)
    desenhar_placa_redesign(ax, cores_laser=True)
    _ajustar(ax, P.PLACA_LARGURA, P.PLACA_ALTURA, 8)
    ax.set_title("Prévia do arquivo de laser (placa_principal.dxf / .svg) — 200 × 150 mm\n"
                 "vermelho = CORTE · azul = GRAVAÇÃO VETORIAL · preto = GRAVAÇÃO RASTER · cinza tracejado = área do QR",
                 fontsize=9)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


def imagem_elevacao(destino: Path) -> Path:
    """Elevação em escala real: alturas do original (ESTIMADAS) × proposta (a verificar na NBR 9050)."""
    fig, axs = plt.subplots(1, 2, figsize=(11, 7.2), dpi=130, sharey=True)
    r = P.ORIGINAL_POSTE_DIAMETRO / 2
    for ax in axs:
        ax.add_patch(Rectangle((-900, -80), 1800, 80, fc="#bbb", ec="none"))
        ax.add_patch(Rectangle((-r, 0), 2 * r, 3000, fc="#8d949c", ec="#555"))
        ax.set_xlim(-900, 900)
        ax.set_ylim(-100, 3100)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_ylabel("altura a partir do piso (mm)")
        ax.grid(axis="y", ls=":", lw=0.6)
    # Original
    a = axs[0]
    w, h, y0 = P.ORIGINAL_PLACA_LARGURA, P.ORIGINAL_PLACA_ALTURA, P.ORIGINAL_ALTURA_BORDA_INFERIOR
    a.add_patch(Rectangle((-w / 2, y0), w, h, fc=COR_ORIG_PLACA, ec="#222"))
    a.text(0, y0 + h / 2, P.ORIGINAL_TEXTO, ha="center", va="center", color=COR_ORIG_TEXTO, fontsize=12, weight="bold")
    a.annotate("", (520, y0), (520, 0), arrowprops=dict(arrowstyle="<->"))
    a.text(540, y0 / 2, f"{y0:.0f} mm\n(ESTIMADO)", va="center", fontsize=9)
    a.set_title("ANTES (estimado)\nplaca alta, só visual", fontsize=11)
    # Redesign
    b = axs[1]
    W, H, yb = P.REAL_PLACA_LARGURA, P.REAL_PLACA_ALTURA, P.REAL_ALTURA_BORDA_INFERIOR_PLACA
    b.add_patch(Rectangle((-W / 2, yb), W, H, fc=COR_PLACA_NOVA, ec="#000"))
    b.text(0, yb + H * 0.82, "PONTO DE ÔNIBUS", ha="center", va="center", color="white", fontsize=9, weight="bold")
    qx, _ = P.AREA_QR_CENTRO
    lq = P.AREA_QR_LADO / P.ESCALA_PROTOTIPO
    b.add_patch(Rectangle((qx / P.ESCALA_PROTOTIPO - lq / 2, yb + H / 2 - lq / 2), lq, lq, fc="white", ec="#999",
                          hatch="///"))
    ym = P.REAL_ALTURA_CENTRO_MODULO_TATIL
    b.add_patch(Rectangle((r + 5, ym - P.MODULO_ALTURA / 2), P.MODULO_LARGURA, P.MODULO_ALTURA, fc=COR_MODULO, ec="#5c4700"))
    b.annotate("", (-520, yb), (-520, 0), arrowprops=dict(arrowstyle="<->"))
    b.text(-860, yb / 2 + 150, f"{yb:.0f} mm\n(proposta,\nVERIFICAR\nNBR 9050)", va="center", fontsize=8.5)
    b.annotate("", (420, ym), (420, 0), arrowprops=dict(arrowstyle="<->"))
    b.text(440, ym / 2, f"{ym:.0f} mm\nmódulo tátil\n(proposta,\nVERIFICAR\nNBR 9050)", va="center", fontsize=8.5)
    b.set_title("DEPOIS (proposta em escala real)\nplaca visual + QR · módulo tátil no alcance da mão", fontsize=11)
    fig.text(0.5, 0.015, "Alturas são HIPÓTESES de projeto: conferir a ABNT NBR 9050 vigente (alcance, sinalização "
             "tátil/Braille, objetos suspensos) e a NBR 16537 (piso tátil até o ponto). Original: " + AVISO_ESTIMADO + ".",
             ha="center", fontsize=8, wrap=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


def imagem_braille(destino: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=150)
    pts = P.braille_pontos(centro=(0, 0))
    for x, y in pts:
        ax.add_patch(Circle((x, y), P.BRAILLE_DIAMETRO_PONTO / 2, fc="#222"))
    # posições vazias (referência)
    for i, (letra, _) in enumerate(P.braille_celas()):
        largura = (len(P.BRAILLE_TEXTO) - 1) * P.BRAILLE_DIST_CELAS + P.BRAILLE_DIST_PONTOS
        xc = -largura / 2 + i * P.BRAILLE_DIST_CELAS
        for col in range(2):
            for lin in range(3):
                ax.add_patch(Circle((xc + col * P.BRAILLE_DIST_PONTOS, P.BRAILLE_DIST_PONTOS - lin * P.BRAILLE_DIST_PONTOS),
                                    P.BRAILLE_DIAMETRO_PONTO / 2, fc="none", ec="#bbb", lw=0.6, ls=":"))
        nums = "".join(str(n) for n in P.BRAILLE_ALFABETO[letra])
        ax.text(xc + P.BRAILLE_DIST_PONTOS / 2, -5.2, f"{letra}\n({nums})", ha="center", va="top", fontsize=9)
    x0 = pts[0][0]
    ax.annotate("", (x0, 5.2), (x0 + P.BRAILLE_DIST_CELAS, 5.2), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x0 + P.BRAILLE_DIST_CELAS / 2, 5.6, f"{P.BRAILLE_DIST_CELAS:g} mm (entre celas)", ha="center", fontsize=8)
    ax.annotate("", (x0 - 2, 2.5), (x0 - 2, 0), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x0 - 2.3, 1.25, f"{P.BRAILLE_DIST_PONTOS:g} mm", ha="right", va="center", fontsize=8)
    ax.set_xlim(-20, 20)
    ax.set_ylim(-10, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Braille \"{P.BRAILLE_TEXTO}\" — ponto Ø{P.BRAILLE_DIAMETRO_PONTO:g} mm, altura "
                 f"{P.BRAILLE_ALTURA_PONTO:g} mm (valores usuais; VERIFICAR NBR 9050)", fontsize=9.5)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, bbox_inches="tight")
    plt.close(fig)
    return destino


# =====================================================================================
# Croquis SVG cotados
# =====================================================================================
class SvgDesenho:
    """Mini-gerador de desenho técnico em SVG (unidades em mm no papel)."""

    def __init__(self, largura: float, altura: float, titulo: str):
        self.w, self.h = largura, altura
        self.el: list[str] = []
        self.titulo = titulo

    @staticmethod
    def _esc(t: str) -> str:
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def linha(self, x1, y1, x2, y2, cor="#000", lw=0.25, tracejado=None):
        d = f' stroke-dasharray="{tracejado}"' if tracejado else ""
        self.el.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{cor}" '
                       f'stroke-width="{lw}"{d}/>')

    def caminho(self, d, cor="#000", lw=0.35, fill="none", tracejado=None):
        t = f' stroke-dasharray="{tracejado}"' if tracejado else ""
        self.el.append(f'<path d="{d}" stroke="{cor}" stroke-width="{lw}" fill="{fill}"{t} fill-rule="evenodd"/>')

    def circulo(self, cx, cy, r, cor="#000", lw=0.3, fill="none"):
        self.el.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" stroke="{cor}" stroke-width="{lw}" fill="{fill}"/>')

    def texto(self, x, y, t, tam=3.0, anchor="start", cor="#000", peso="normal", rot=0):
        r = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot else ""
        self.el.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{tam}" text-anchor="{anchor}" fill="{cor}" '
                       f'font-weight="{peso}" font-family="DejaVu Sans, Arial, sans-serif"{r}>{self._esc(t)}</text>')

    def cota_h(self, x1, x2, y, y_ref, texto, tam=2.6):
        """Cota horizontal entre x1 e x2, linha de cota em y, linhas de chamada a partir de y_ref."""
        for x in (x1, x2):
            self.linha(x, y_ref, x, y + (1.5 if y > y_ref else -1.5), "#0055AA", 0.18)
        self.linha(x1, y, x2, y, "#0055AA", 0.2)
        for x, s in ((x1, 1), (x2, -1)):
            self.caminho(f"M{x:.3f},{y:.3f} l{1.6 * s:.3f},-0.6 l0,1.2 Z", "#0055AA", 0.1, "#0055AA")
        self.texto((x1 + x2) / 2, y - 0.8, texto, tam, "middle", "#0055AA")

    def cota_v(self, y1, y2, x, x_ref, texto, tam=2.6):
        for y in (y1, y2):
            self.linha(x_ref, y, x + (1.5 if x > x_ref else -1.5), y, "#0055AA", 0.18)
        self.linha(x, y1, x, y2, "#0055AA", 0.2)
        for y, s in ((y1, 1), (y2, -1)):
            self.caminho(f"M{x:.3f},{y:.3f} l-0.6,{1.6 * s:.3f} l1.2,0 Z", "#0055AA", 0.1, "#0055AA")
        self.texto(x - 0.8, (y1 + y2) / 2, texto, tam, "middle", "#0055AA", rot=-90)

    def salvar(self, caminho: Path) -> Path:
        s = [
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:g}mm" height="{self.h:g}mm" '
            f'viewBox="0 0 {self.w:g} {self.h:g}" version="1.1">',
            f"<title>{self._esc(self.titulo)}</title>",
            f'<rect x="0" y="0" width="{self.w:g}" height="{self.h:g}" fill="white"/>',
            *self.el,
            "</svg>",
        ]
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text("\n".join(s), encoding="utf-8")
        return caminho


def croqui_redesign(destino: Path) -> Path:
    """Folha A3 (420 × 297 mm): placa 1:1 (do protótipo), módulo tátil 1:1, detalhe Braille 5:1 e suporte 1:1."""
    d = SvgDesenho(420, 297, "Croqui cotado do redesign - AcessaCidade (gerado de parametros.py)")
    d.caminho("M5,5 H415 V292 H5 Z", lw=0.5)
    d.texto(10, 13, "CROQUI COTADO — REDESIGN: PLACA ACESSÍVEL PARA PONTO DE ÔNIBUS (AcessaCidade)", 5, peso="bold")
    d.texto(10, 19, f"Unidades: mm · Protótipo: placa e suporte em {P.ESCALA_TEXTO} · Desenho gerado automaticamente "
                    "de cad/parametros.py (não é medição de campo)", 2.8)

    # --- Vista A: placa (desenho 1:1 do protótipo) ---------------------------------
    L = G.layout_placa()
    ox, oy = 20 + P.PLACA_LARGURA / 2, 40 + P.PLACA_ALTURA / 2    # centro da placa no papel

    def t(p):
        return ox + p[0], oy - p[1]

    d.texto(20, 32, "VISTA A — PLACA PRINCIPAL (laser, 3 mm) — escala do desenho 1:1 do protótipo", 3.2, peso="bold")
    d.caminho(L.contorno.caminho_svg(t), "#C00000", 0.4)
    d.caminho(L.vetorial[0].caminho_svg(t), "#0000C0", 0.2, tracejado="1,0.6")
    d.caminho(L.vetorial[1].caminho_svg(t), "#B08000", 0.3, tracejado="2,1")
    d.caminho(G._svg_path_formas(L.raster, t), "#000", 0.05, "#000")
    for c in L.furos:
        X, Y = t((c.cx, c.cy))
        d.circulo(X, Y, c.diametro / 2, "#C00000", 0.3)
    qx, qy, lado = L.area_qr
    X, Y = t((qx - lado / 2, qy + lado / 2))
    d.caminho(f"M{X:.3f},{Y:.3f} h{lado} v{lado} h{-lado} Z", "#666", 0.3, tracejado="1.5,1")
    Xc, Yc = t((qx, qy))
    d.texto(Xc, Yc, "ÁREA QR", 3, "middle", "#666")
    d.texto(Xc, Yc + 4, f"{lado:g} × {lado:g}", 2.6, "middle", "#666")
    mx, my = P.MODULO_CENTRO_NA_PLACA
    Xm, Ym = t((mx, my))
    d.texto(Xm, Ym, "MÓDULO TÁTIL (3D)", 2.8, "middle", "#8a6d00")
    d.texto(Xm, Ym + 4, f"{P.MODULO_LARGURA:g} × {P.MODULO_ALTURA:g}", 2.6, "middle", "#8a6d00")
    W, H = P.PLACA_LARGURA, P.PLACA_ALTURA
    x_esq, x_dir = ox - W / 2, ox + W / 2
    y_top, y_base = oy - H / 2, oy + H / 2
    d.cota_h(x_esq, x_dir, y_base + 14, y_base, f"{W:g}")
    d.cota_v(y_top, y_base, x_esq - 8, x_esq, f"{H:g}")
    fx, fy = P.furos_canto()[0]
    Xf, Yf = t((fx, fy))
    d.cota_h(x_esq, Xf, y_base + 7, y_base, f"{P.FURO_CANTO_DIST_BORDA:g}")
    d.cota_v(Yf, y_base, x_dir + 7, x_dir, f"{P.FURO_CANTO_DIST_BORDA:g}")
    Xq0, _ = t((qx - lado / 2, 0))
    d.cota_h(x_esq, Xq0, y_top - 6, y_top, f"{qx - lado / 2 + W / 2:g}")
    _, Ys1 = t((0, P.FURO_SUPORTE_DIST_Y))
    _, Ys2 = t((0, -P.FURO_SUPORTE_DIST_Y))
    d.cota_v(Ys1, Ys2, x_dir + 16, ox, f"{2 * P.FURO_SUPORTE_DIST_Y:g} (furos suporte)")
    d.texto(x_esq, y_base + 22, f"Cantos R{P.PLACA_RAIO_CANTO:g} · 4 furos de canto Ø{P.FURO_CANTO_DIAMETRO:g} · "
                                f"2 furos suporte Ø{P.FURO_SUPORTE_DIAMETRO:g} (M4) em X=0 · 2 furos módulo "
                                f"Ø{P.FURO_MODULO_DIAMETRO:g} (M3)", 2.6)
    d.texto(x_esq, y_base + 26, f"Título \"{P.TEXTO_TITULO}\" altura de maiúscula {P.TEXTO_TITULO_ALTURA_MAIUSCULA:g} · "
                                f"rodapé {P.TEXTO_RODAPE_ALTURA_MAIUSCULA:g} · moldura gravada a "
                                f"{P.PLACA_BORDA_GRAVADA_MARGEM:g} da borda", 2.6)
    d.texto(x_esq, y_base + 30, f"Escala real sugerida: {P.REAL_PLACA_LARGURA:g} × {P.REAL_PLACA_ALTURA:g} mm (×3)", 2.6)

    # --- Vista B: módulo tátil 1:1 ---------------------------------------------------
    bx, by = 290, 85
    d.texto(250, 32, "VISTA B — MÓDULO TÁTIL (impressão 3D) — 1:1", 3.2, peso="bold")

    def tb(p):
        return bx + p[0], by - p[1]

    mod = G.RetanguloArredondado(0, 0, P.MODULO_LARGURA, P.MODULO_ALTURA, P.MODULO_RAIO_CANTO)
    d.caminho(mod.caminho_svg(tb), "#000", 0.4)
    seta = G.seta_poligono(0, P.SETA_CENTRO_Y, P.SETA_COMPRIMENTO, P.SETA_LARGURA_HASTE, P.SETA_LARGURA_PONTA,
                           P.SETA_COMPRIMENTO_PONTA, P.SETA_SENTIDO)
    d.caminho("M" + " L".join(f"{tb(p)[0]:.3f},{tb(p)[1]:.3f}" for p in seta) + " Z", "#000", 0.3, "#E8C000")
    letras = G.texto_formas(P.MODULO_TEXTO_RELEVO, P.MODULO_TEXTO_ALTURA_MAIUSCULA, 0, P.MODULO_TEXTO_BASE_Y)
    d.caminho(G._svg_path_formas(letras, tb), "#000", 0.15, "#E8C000")
    for x, y in P.braille_pontos():
        X, Y = tb((x, y))
        d.circulo(X, Y, P.BRAILLE_DIAMETRO_PONTO / 2, "#000", 0.15, "#000")
    for x, y in P.MODULO_FURO_GUIA_POSICOES:
        X, Y = tb((x, y))
        d.circulo(X, Y, P.MODULO_FURO_GUIA_DIAMETRO / 2, "#666", 0.2)
    mw, mh = P.MODULO_LARGURA / 2, P.MODULO_ALTURA / 2
    d.cota_h(bx - mw, bx + mw, by + mh + 8, by + mh, f"{P.MODULO_LARGURA:g}")
    d.cota_v(by - mh, by + mh, bx - mw - 7, bx - mw, f"{P.MODULO_ALTURA:g}")
    sx0, sx1 = tb((-P.SETA_COMPRIMENTO / 2, 0))[0], tb((P.SETA_COMPRIMENTO / 2, 0))[0]
    d.cota_h(sx0, sx1, by - mh - 5, by - mh, f"seta {P.SETA_COMPRIMENTO:g} (relevo {P.SETA_RELEVO_ALTURA:g})")
    d.texto(bx - mw, by + mh + 15, f"Base {P.MODULO_ESPESSURA_BASE:g} mm · letras \"{P.MODULO_TEXTO_RELEVO}\" "
                                   f"h{P.MODULO_TEXTO_ALTURA_MAIUSCULA:g} relevo {P.MODULO_TEXTO_RELEVO_ALTURA:g}", 2.6)
    d.texto(bx - mw, by + mh + 19, f"Furos-guia cegos no verso Ø{P.MODULO_FURO_GUIA_DIAMETRO:g} × "
                                   f"{P.MODULO_FURO_GUIA_PROFUNDIDADE:g} (tracejado = não visível pela frente)", 2.6)

    # --- Detalhe C: Braille 5:1 -----------------------------------------------------
    k = 5.0
    cx0, cy0 = 262, 165
    d.texto(250, 145, "DETALHE C — BRAILLE \"PONTO\" — escala 5:1 (VERIFICAR NBR 9050)", 3.2, peso="bold")
    pts = P.braille_pontos(texto="PO", centro=(0, 0))
    for x, y in pts:
        d.circulo(cx0 + x * k + 20, cy0 - y * k, P.BRAILLE_DIAMETRO_PONTO / 2 * k, "#000", 0.2, "#333")
    xa = cx0 + pts[0][0] * k + 20
    ya = cy0 - pts[0][1] * k
    d.cota_h(xa, xa + P.BRAILLE_DIST_PONTOS * k, ya - 8, ya, f"{P.BRAILLE_DIST_PONTOS:g}")
    d.cota_h(xa, xa + P.BRAILLE_DIST_CELAS * k, ya - 15, ya, f"{P.BRAILLE_DIST_CELAS:g} (entre celas)")
    d.cota_v(ya, ya + P.BRAILLE_DIST_PONTOS * k, xa - 8, xa, f"{P.BRAILLE_DIST_PONTOS:g}")
    d.texto(cx0 + 85, cy0 - 6, f"Ø ponto: {P.BRAILLE_DIAMETRO_PONTO:g} mm", 2.8)
    d.texto(cx0 + 85, cy0 - 2, f"Altura: {P.BRAILLE_ALTURA_PONTO:g} mm (faixa usual 0,6–0,8)", 2.8)
    d.texto(cx0 + 85, cy0 + 2, "P=1234 O=135 N=1345 T=2345 O=135", 2.8)
    d.texto(cx0 + 85, cy0 + 6, "Mostradas: celas P e O", 2.8)

    # --- Vista D: suporte (vista lateral, 1:1) -------------------------------------
    dx0, dy0 = 290, 235
    d.texto(250, 197, "VISTA D — SUPORTE PARA TUBO (3D) — corte lateral 1:1", 3.2, peso="bold")
    tf = P.SUPORTE_FLANGE_ESPESSURA
    prof = P.suporte_profundidade_total()
    rb = P.raio_berco()
    hf = P.SUPORTE_FLANGE_ALTURA
    # perfil lateral (Z para a direita, Y para cima): flange + bloco
    d.caminho(f"M{dx0:.3f},{dy0 - hf / 2:.3f} h{tf} v{hf} h{-tf} Z", "#000", 0.35, "#ddd")
    hb = P.SUPORTE_BERCO_COMPRIMENTO
    d.caminho(f"M{dx0 + tf:.3f},{dy0 - hb / 2:.3f} h{prof - tf} v{hb} h{-(prof - tf)} Z", "#000", 0.35, "#ddd")
    d.linha(dx0 + prof, dy0 - hb / 2 - 6, dx0 + prof, dy0 + hb / 2 + 6, "#666", 0.2, "3,1,1,1")
    d.texto(dx0 + prof + 1, dy0 - hb / 2 - 7, "eixo do tubo", 2.4, cor="#666")
    d.linha(dx0 + tf + P.SUPORTE_AFASTAMENTO, dy0 - hb / 2, dx0 + tf + P.SUPORTE_AFASTAMENTO, dy0 + hb / 2, "#666", 0.2, "1,1")
    d.linha(dx0 - 3, dy0 - hf / 2 - 2, dx0 - 3, dy0 + hf / 2 + 2, "#C00000", 0.6)
    d.texto(dx0 - 4, dy0 + hf / 2 + 5, "placa", 2.4, "end", "#C00000")
    d.cota_h(dx0, dx0 + tf, dy0 - hf / 2 - 4, dy0 - hf / 2, f"{tf:g}")
    d.cota_h(dx0, dx0 + prof, dy0 + hf / 2 + 6, dy0 + hb / 2, f"{prof:.1f} até o eixo")
    d.cota_v(dy0 - hf / 2, dy0 + hf / 2, dx0 - 9, dx0, f"{hf:g}")
    d.texto(dx0 + prof + 8, dy0 - 10, f"Berço R{rb:.1f} (tubo Ø{P.TUBO_DIAMETRO:g} + folga {P.TUBO_FOLGA:g})", 2.6)
    d.texto(dx0 + prof + 8, dy0 - 6, f"Flange {P.SUPORTE_FLANGE_LARGURA:g} × {hf:g} × {tf:g}", 2.6)
    d.texto(dx0 + prof + 8, dy0 - 2, f"2 túneis {P.SUPORTE_TUNEL_LARGURA:g} × {P.SUPORTE_TUNEL_ALTURA:g} para abraçadeira", 2.6)
    d.texto(dx0 + prof + 8, dy0 + 2, f"Porcas M4 embutidas (sextavado {P.SUPORTE_PORCA_M4_ENTRE_FACES + P.SUPORTE_PORCA_FOLGA:g})", 2.6)
    d.texto(dx0 + prof + 8, dy0 + 6, f"Furos Ø{P.FURO_SUPORTE_DIAMETRO:g} a ±{P.FURO_SUPORTE_DIST_Y:g} do centro", 2.6)

    d.texto(10, 288, "Normas de referência a VERIFICAR (sem declaração de conformidade): ABNT NBR 9050 "
                     "(contraste, alturas, Braille, relevo) · ABNT NBR 16537 (piso tátil).", 2.8)
    return d.salvar(destino)


def croqui_original_modelo(destino: Path) -> Path:
    """Modelo de croqui do OBJETO ORIGINAL para preencher em campo (cotas A–L sem valores)."""
    d = SvgDesenho(297, 210, "Modelo de croqui do objeto original (preencher em campo)")
    d.caminho("M5,5 H292 V205 H5 Z", lw=0.5)
    d.texto(10, 13, "MODELO DE CROQUI — OBJETO ORIGINAL (placa do ponto de ônibus) — PREENCHER EM CAMPO", 4.2, peso="bold")
    d.texto(10, 19, "Imprima esta folha, leve ao local e anote as medidas (mm). Não há valores: tudo deve vir da "
                    "medição real.", 2.8)
    # vista frontal (esquemática, sem escala)
    gx, gy = 70, 190      # piso
    d.linha(15, gy, 150, gy, "#000", 0.6)
    d.texto(16, gy + 5, "PISO / CALÇADA", 2.6)
    d.caminho(f"M{gx - 4},{gy} V40 h8 V{gy}", "#000", 0.4, "#ccc")
    d.caminho(f"M{gx - 40},45 h80 v45 h-80 Z", "#000", 0.5, "#e8eef5")
    d.texto(gx, 70, "TEXTO DA PLACA", 3, "middle")
    d.cota_h(gx - 40, gx + 40, 37, 45, "A = largura")
    d.cota_v(45, 90, gx - 50, gx - 40, "B = altura")
    d.cota_v(90, gy, gx + 52, gx + 40, "C = piso → borda inferior")
    d.cota_v(45, gy, gx + 70, gx + 40, "D = piso → borda superior")
    d.cota_h(gx - 4, gx + 4, gy - 30, gy - 40, "E = Ø poste")
    d.texto(gx - 38, 52, "F = altura da letra", 2.4)
    # tabela
    tx, ty = 165, 32
    d.texto(tx, ty, "TABELA DE MEDIDAS (mm)", 3.4, peso="bold")
    itens = [
        "A  Largura da placa", "B  Altura da placa", "C  Piso → borda inferior", "D  Piso → borda superior",
        "E  Diâmetro do poste (perímetro ÷ π)", "F  Altura das letras maiúsculas", "G  Espessura da chapa",
        "H  Afastamento placa ↔ poste", "I  Largura livre da calçada no ponto", "J  Distância poste ↔ meio-fio",
        "K  Altura do assento/abrigo (se houver)", "L  Distância até o piso tátil (se houver)",
    ]
    for i, item in enumerate(itens):
        y = ty + 8 + i * 9
        d.texto(tx, y, item, 2.8)
        d.linha(tx + 78, y + 0.8, tx + 118, y + 0.8, "#000", 0.25)
    y = ty + 8 + len(itens) * 9 + 4
    d.texto(tx, y, "Local (sem endereço residencial): ______________________", 2.8)
    d.texto(tx, y + 6, "Data/hora: ____/____/______  ____:____   Clima: __________", 2.8)
    d.texto(tx, y + 12, "Instrumento: trena ( )  paquímetro ( )  Medido por: __________", 2.8)
    d.texto(10, 200, "Observações (contraste, sujeira, desgaste, Braille/relevo, QR, piso tátil): "
                     "______________________________________________", 2.8)
    return d.salvar(destino)
