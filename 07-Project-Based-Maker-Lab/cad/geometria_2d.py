"""Geometria 2D da placa a laser (layout) e escritores DXF/SVG.

Fonte única de verdade para:
  * o arquivo de corte/gravação a laser (DXF e SVG);
  * a gravação representada no modelo 3D (CadQuery);
  * as letras em relevo do módulo tátil;
  * os desenhos 2D usados nas imagens de comparação.

Textos são convertidos em CONTORNOS (polígonos fechados) com a fonte DejaVu Sans Bold que vem
embutida no matplotlib — assim o arquivo não depende de fontes instaladas na máquina do laser.
Uma cópia em TEXT editável vai para a camada TEXTO_REFERENCIA (não deve ser enviada ao laser).

Convenção de camadas (DXF) / grupos (SVG):
  CORTE               vermelho (ACI 1 / #FF0000)  — corte passante: contorno e furos
  GRAVACAO_VETORIAL   azul     (ACI 5 / #0000FF)  — gravação de linha (moldura, posição do módulo)
  GRAVACAO_RASTER     preto    (ACI 7 / #000000)  — gravação de preenchimento (textos, pictograma, QR)
  AREA_QR             cinza    (ACI 8 / #808080)  — GUIA da área reservada ao QR (NÃO enviar ao laser)
  TEXTO_REFERENCIA    verde    (ACI 3 / #00A000)  — textos editáveis e notas (NÃO enviar ao laser)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import parametros as P

FONTE_PADRAO = "DejaVuSans-Bold.ttf"

CAMADAS = {
    # nome: (cor ACI, cor RGB hexadecimal, enviar ao laser?, descrição)
    "CORTE": (1, "#FF0000", True, "Corte passante (contorno e furos). Executar POR ÚLTIMO."),
    "GRAVACAO_VETORIAL": (5, "#0000FF", True, "Gravação de linha (baixa potência): moldura e marca de posição do módulo tátil."),
    "GRAVACAO_RASTER": (7, "#000000", True, "Gravação de preenchimento (raster/fill): textos, pictograma e QR Code."),
    "AREA_QR": (8, "#808080", False, "Guia da área reservada ao QR Code. NÃO enviar ao laser (desligar a saída)."),
    "TEXTO_REFERENCIA": (3, "#00A000", False, "Textos editáveis e notas. NÃO enviar ao laser."),
}

Ponto = tuple[float, float]
Poligono = list[Ponto]


# =====================================================================================
# Primitivas
# =====================================================================================
@dataclass
class RetanguloArredondado:
    cx: float
    cy: float
    largura: float
    altura: float
    raio: float

    def poligono(self, segmentos_por_canto: int = 12) -> Poligono:
        hx, hy, r = self.largura / 2, self.altura / 2, self.raio
        pts: Poligono = []
        cantos = ((hx - r, -hy + r, -90), (hx - r, hy - r, 0), (-hx + r, hy - r, 90), (-hx + r, -hy + r, 180))
        for ccx, ccy, a0 in cantos:  # anti-horário
            for i in range(segmentos_por_canto + 1):
                a = math.radians(a0 + 90 * i / segmentos_por_canto)
                pts.append((self.cx + ccx + r * math.cos(a), self.cy + ccy + r * math.sin(a)))
        return pts

    def pontos_com_bulge(self) -> list[tuple[float, float, float]]:
        """Vértices (x, y, bulge) para LWPOLYLINE fechada com arcos de 90° (anti-horário)."""
        hx, hy, r = self.largura / 2, self.altura / 2, self.raio
        b = math.tan(math.radians(90) / 4)
        cx, cy = self.cx, self.cy
        return [
            (cx - hx + r, cy - hy, 0.0), (cx + hx - r, cy - hy, b),
            (cx + hx, cy - hy + r, 0.0), (cx + hx, cy + hy - r, b),
            (cx + hx - r, cy + hy, 0.0), (cx - hx + r, cy + hy, b),
            (cx - hx, cy + hy - r, 0.0), (cx - hx, cy - hy + r, b),
        ]

    def caminho_svg(self, tx) -> str:
        """Caminho SVG com arcos verdadeiros. `tx` converte (x, y) do modelo para o SVG."""
        hx, hy, r = self.largura / 2, self.altura / 2, self.raio
        cx, cy = self.cx, self.cy

        def p(x, y):
            X, Y = tx((x, y))
            return f"{X:.4f},{Y:.4f}"

        # No SVG o eixo Y é invertido: arcos anti-horários no modelo viram horários (sweep=0)
        return (f"M{p(cx - hx + r, cy - hy)} L{p(cx + hx - r, cy - hy)} "
                f"A{r:.4f},{r:.4f} 0 0 0 {p(cx + hx, cy - hy + r)} L{p(cx + hx, cy + hy - r)} "
                f"A{r:.4f},{r:.4f} 0 0 0 {p(cx + hx - r, cy + hy)} L{p(cx - hx + r, cy + hy)} "
                f"A{r:.4f},{r:.4f} 0 0 0 {p(cx - hx, cy + hy - r)} L{p(cx - hx, cy - hy + r)} "
                f"A{r:.4f},{r:.4f} 0 0 0 {p(cx - hx + r, cy - hy)} Z")


@dataclass
class Circulo:
    cx: float
    cy: float
    diametro: float
    funcao: str = ""


@dataclass
class Forma:
    """Polígono externo (anti-horário) com furos internos (horários)."""
    externo: Poligono
    furos: list[Poligono] = field(default_factory=list)

    def todos(self) -> list[Poligono]:
        return [self.externo, *self.furos]


@dataclass
class TextoRef:
    texto: str
    x: float
    y: float
    altura: float


@dataclass
class LayoutPlaca:
    contorno: RetanguloArredondado
    furos: list[Circulo]
    vetorial: list[RetanguloArredondado]
    raster: list[Forma]
    area_qr: tuple[float, float, float]           # (cx, cy, lado)
    textos_ref: list[TextoRef]
    largura: float
    altura: float


# =====================================================================================
# Polígonos: área, orientação, aninhamento
# =====================================================================================
def area_assinada(poly: Poligono) -> float:
    s = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2


def ponto_no_poligono(pt: Ponto, poly: Poligono) -> bool:
    x, y = pt
    dentro = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xint = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xint:
                dentro = not dentro
        j = i
    return dentro


def limpar_poligono(poly, tol: float = 1e-3) -> Poligono:
    out: Poligono = []
    for x, y in poly:
        p = (float(x), float(y))
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    while len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out.pop()
    # remove pontos colineares
    limpo: Poligono = []
    n = len(out)
    for i in range(n):
        a, b, c = out[i - 1], out[i], out[(i + 1) % n]
        cruz = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cruz) > 1e-7:
            limpo.append(b)
    return limpo


def organizar_formas(polys: list[Poligono]) -> list[Forma]:
    """Agrupa polígonos em formas (externo + furos) pela regra par/ímpar de aninhamento."""
    polys = [p for p in (limpar_poligono(p) for p in polys) if len(p) >= 3 and abs(area_assinada(p)) > 1e-4]
    profundidade = []
    for i, p in enumerate(polys):
        d = sum(1 for j, q in enumerate(polys) if j != i and ponto_no_poligono(p[0], q)
                and abs(area_assinada(q)) > abs(area_assinada(p)))
        profundidade.append(d)
    formas: dict[int, Forma] = {}
    for i, p in enumerate(polys):
        if profundidade[i] % 2 == 0:
            ext = p if area_assinada(p) > 0 else p[::-1]
            formas[i] = Forma(ext)
    for i, p in enumerate(polys):
        if profundidade[i] % 2 == 1:
            pais = [j for j in formas if ponto_no_poligono(p[0], polys[j])
                    and profundidade[j] == profundidade[i] - 1]
            if not pais:
                continue
            pai = min(pais, key=lambda j: abs(area_assinada(polys[j])))
            formas[pai].furos.append(p if area_assinada(p) < 0 else p[::-1])
    return list(formas.values())


def caixa(formas: list[Forma]) -> tuple[float, float, float, float]:
    xs = [x for f in formas for x, _ in f.externo]
    ys = [y for f in formas for _, y in f.externo]
    return min(xs), min(ys), max(xs), max(ys)


# =====================================================================================
# Texto → contornos
# =====================================================================================
def caminho_fonte(nome: str = FONTE_PADRAO) -> Path:
    import matplotlib
    return Path(matplotlib.get_data_path()) / "fonts" / "ttf" / nome


def texto_formas(texto: str, altura_maiuscula: float, x: float, base_y: float,
                 alinhamento: str = "centro", fonte: str = FONTE_PADRAO) -> list[Forma]:
    """Converte `texto` em formas. `altura_maiuscula` = altura da letra H em mm."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath

    fp = FontProperties(fname=str(caminho_fonte(fonte)))
    ref = TextPath((0, 0), "H", size=100, prop=fp).get_extents()
    tamanho = altura_maiuscula / (ref.height / 100.0)
    tp = TextPath((0, 0), texto, size=tamanho, prop=fp)
    ext = tp.get_extents()
    if alinhamento == "centro":
        dx = x - (ext.x0 + ext.x1) / 2
    elif alinhamento == "esquerda":
        dx = x - ext.x0
    else:
        dx = x - ext.x1
    polys = [[(px + dx, py + base_y) for px, py in poly] for poly in tp.to_polygons(closed_only=True)]
    return organizar_formas(polys)


def largura_texto(texto: str, altura_maiuscula: float) -> float:
    f = texto_formas(texto, altura_maiuscula, 0, 0)
    x0, _, x1, _ = caixa(f)
    return x1 - x0


# =====================================================================================
# Pictograma simplificado de ônibus (vista frontal) — desenho próprio da equipe
# =====================================================================================
def pictograma_onibus(cx: float, base_y: float, largura: float, altura: float) -> list[Forma]:
    roda_h = altura * 0.16
    corpo = RetanguloArredondado(cx, base_y + roda_h + (altura - roda_h) / 2, largura, altura - roda_h, largura * 0.18)
    corpo_poly = corpo.poligono(8)
    topo = corpo.cy + corpo.altura / 2
    # para-brisa (furo)
    pb_w, pb_h = largura * 0.72, (altura - roda_h) * 0.38
    pb_cy = topo - largura * 0.14 - pb_h / 2
    para_brisa = RetanguloArredondado(cx, pb_cy, pb_w, pb_h, largura * 0.06).poligono(4)[::-1]
    # faróis (furos circulares)
    farois = []
    fy = corpo.cy - corpo.altura / 2 + (altura - roda_h) * 0.2
    for sx in (-1, 1):
        fx = cx + sx * largura * 0.27
        rr = largura * 0.08
        farois.append([(fx + rr * math.cos(a), fy - rr * math.sin(a))
                       for a in [2 * math.pi * k / 16 for k in range(16)]])
    formas = [Forma(corpo_poly, [para_brisa, *farois])]
    # rodas (retângulos abaixo do corpo)
    for sx in (-1, 1):
        rx = cx + sx * largura * 0.3
        roda = RetanguloArredondado(rx, base_y + roda_h / 2 + 0.2, largura * 0.2, roda_h + 0.4, 0.6).poligono(3)
        formas.append(Forma(roda))
    return formas


# =====================================================================================
# Seta direcional (usada no módulo tátil e nas imagens)
# =====================================================================================
def seta_poligono(cx: float, cy: float, comprimento: float, largura_haste: float,
                  largura_ponta: float, comprimento_ponta: float, sentido: str = "direita") -> Poligono:
    x0 = cx - comprimento / 2
    x1 = cx + comprimento / 2
    xp = x1 - comprimento_ponta
    hh, hp = largura_haste / 2, largura_ponta / 2
    pts = [(x0, cy - hh), (xp, cy - hh), (xp, cy - hp), (x1, cy), (xp, cy + hp), (xp, cy + hh), (x0, cy + hh)]
    if sentido == "esquerda":
        pts = [(2 * cx - x, y) for x, y in pts][::-1]
    return pts


# =====================================================================================
# Layout da placa principal (coordenadas relativas ao centro da placa)
# =====================================================================================
def layout_placa() -> LayoutPlaca:
    contorno = RetanguloArredondado(0, 0, P.PLACA_LARGURA, P.PLACA_ALTURA, P.PLACA_RAIO_CANTO)
    furos = [Circulo(x, y, d, f) for x, y, d, f in P.todos_furos_placa()]
    m = P.PLACA_BORDA_GRAVADA_MARGEM
    moldura = RetanguloArredondado(0, 0, P.PLACA_LARGURA - 2 * m, P.PLACA_ALTURA - 2 * m, P.PLACA_BORDA_GRAVADA_RAIO)
    mx, my = P.MODULO_CENTRO_NA_PLACA
    marca_modulo = RetanguloArredondado(mx, my, P.MODULO_LARGURA, P.MODULO_ALTURA, P.MODULO_RAIO_CANTO)

    raster: list[Forma] = []
    textos: list[TextoRef] = []
    # Título + pictograma (conjunto centralizado)
    w_tit = largura_texto(P.TEXTO_TITULO, P.TEXTO_TITULO_ALTURA_MAIUSCULA)
    w_total = P.PICTOGRAMA_ONIBUS_LARGURA + P.PICTOGRAMA_ESPACO_TEXTO + w_tit
    x_ini = -w_total / 2
    base_pict = P.TEXTO_TITULO_BASE_Y - (P.PICTOGRAMA_ONIBUS_ALTURA - P.TEXTO_TITULO_ALTURA_MAIUSCULA) / 2
    raster += pictograma_onibus(x_ini + P.PICTOGRAMA_ONIBUS_LARGURA / 2, base_pict,
                                P.PICTOGRAMA_ONIBUS_LARGURA, P.PICTOGRAMA_ONIBUS_ALTURA)
    x_tit = x_ini + P.PICTOGRAMA_ONIBUS_LARGURA + P.PICTOGRAMA_ESPACO_TEXTO
    raster += texto_formas(P.TEXTO_TITULO, P.TEXTO_TITULO_ALTURA_MAIUSCULA, x_tit, P.TEXTO_TITULO_BASE_Y, "esquerda")
    textos.append(TextoRef(P.TEXTO_TITULO, x_tit + w_tit / 2, P.TEXTO_TITULO_BASE_Y, P.TEXTO_TITULO_ALTURA_MAIUSCULA))
    # Rodapé
    for linha, base in zip(P.TEXTO_RODAPE_LINHAS, P.TEXTO_RODAPE_BASES_Y):
        raster += texto_formas(linha, P.TEXTO_RODAPE_ALTURA_MAIUSCULA, 0, base)
        textos.append(TextoRef(linha, 0, base, P.TEXTO_RODAPE_ALTURA_MAIUSCULA))
    # Legenda sob a área do QR
    qx, qy = P.AREA_QR_CENTRO
    base_leg = qy - P.AREA_QR_LADO / 2 - 2.0 - P.TEXTO_QR_LEGENDA_ALTURA
    raster += texto_formas(P.TEXTO_QR_LEGENDA, P.TEXTO_QR_LEGENDA_ALTURA, qx, base_leg)
    textos.append(TextoRef(P.TEXTO_QR_LEGENDA, qx, base_leg, P.TEXTO_QR_LEGENDA_ALTURA))
    textos.append(TextoRef("AREA RESERVADA AO QR CODE - gerar com laser-cut/gerar_qrcode.py --url <URL_PUBLICA>",
                           qx, qy, 1.6))

    return LayoutPlaca(contorno, furos, [moldura, marca_modulo], raster,
                       (qx, qy, P.AREA_QR_LADO), textos, P.PLACA_LARGURA, P.PLACA_ALTURA)


def verificar_layout(layout: LayoutPlaca | None = None) -> list[str]:
    """Checa se textos/pictograma ficam dentro da moldura e longe dos furos (com cabeça de parafuso)."""
    layout = layout or layout_placa()
    problemas = []
    m = P.PLACA_BORDA_GRAVADA_MARGEM + 1.0
    hx, hy = P.PLACA_LARGURA / 2 - m, P.PLACA_ALTURA / 2 - m
    for f in layout.raster:
        x0, y0, x1, y1 = caixa([f])
        if x0 < -hx or x1 > hx or y0 < -hy or y1 > hy:
            problemas.append(f"Gravação fora da moldura: caixa ({x0:.1f},{y0:.1f})-({x1:.1f},{y1:.1f})")
        for c in layout.furos:
            folga = (P.CABECA_PARAFUSO_M4_DIAMETRO if c.funcao in ("suporte", "canto") else c.diametro) / 2 + 1.0
            if x0 - folga < c.cx < x1 + folga and y0 - folga < c.cy < y1 + folga:
                problemas.append(f"Gravação muito perto do furo de {c.funcao} em ({c.cx:g},{c.cy:g})")
        qx, qy, lado = layout.area_qr
        if x1 > qx - lado / 2 and x0 < qx + lado / 2 and y1 > qy - lado / 2 and y0 < qy + lado / 2:
            problemas.append("Gravação invade a área do QR")
        mx, my = P.MODULO_CENTRO_NA_PLACA
        if x1 > mx - P.MODULO_LARGURA / 2 and x0 < mx + P.MODULO_LARGURA / 2 and \
                y1 > my - P.MODULO_ALTURA / 2 and y0 < my + P.MODULO_ALTURA / 2:
            problemas.append("Gravação ficaria escondida sob o módulo tátil")
    return problemas


# =====================================================================================
# Escritores DXF / SVG
# =====================================================================================
def _novo_dxf():
    import ezdxf
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for nome, (aci, rgb, _, desc) in CAMADAS.items():
        camada = doc.layers.add(nome, color=aci)
        camada.rgb = tuple(int(rgb[i:i + 2], 16) for i in (1, 3, 5))
        camada.description = desc
        if nome == "AREA_QR":
            camada.dxf.linetype = "DASHED"
        if not CAMADAS[nome][2]:
            camada.dxf.plot = 0    # camadas de referência não são "plotadas"
    return doc


def _add_formas_dxf(msp, formas: list[Forma], camada: str, dx: float, dy: float):
    for forma in formas:
        for poly in forma.todos():
            msp.add_lwpolyline([(x + dx, y + dy) for x, y in poly], close=True, dxfattribs={"layer": camada})


def escrever_dxf_placa(layout: LayoutPlaca, caminho: Path, qr_formas: list[Forma] | None = None,
                       qr_info: str | None = None) -> Path:
    """Gera o DXF da placa. Origem no canto inferior esquerdo (todas as coordenadas positivas)."""
    doc = _novo_dxf()
    msp = doc.modelspace()
    dx, dy = layout.largura / 2, layout.altura / 2
    # Corte
    pts = [(x + dx, y + dy, b) for x, y, b in layout.contorno.pontos_com_bulge()]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "CORTE"})
    for c in layout.furos:
        msp.add_circle((c.cx + dx, c.cy + dy), c.diametro / 2, dxfattribs={"layer": "CORTE"})
    # Gravação vetorial
    for r in layout.vetorial:
        pts = [(x + dx, y + dy, b) for x, y, b in r.pontos_com_bulge()]
        msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "GRAVACAO_VETORIAL"})
    # Gravação raster
    _add_formas_dxf(msp, layout.raster, "GRAVACAO_RASTER", dx, dy)
    if qr_formas:
        _add_formas_dxf(msp, qr_formas, "GRAVACAO_RASTER", dx, dy)
    # Área do QR (guia)
    qx, qy, lado = layout.area_qr
    h = lado / 2
    msp.add_lwpolyline([(qx - h + dx, qy - h + dy), (qx + h + dx, qy - h + dy), (qx + h + dx, qy + h + dy),
                        (qx - h + dx, qy + h + dy)], close=True, dxfattribs={"layer": "AREA_QR"})
    # Textos de referência
    for t in layout.textos_ref:
        if qr_formas and t.texto.startswith("AREA RESERVADA"):
            continue
        msp.add_text(t.texto, height=t.altura, dxfattribs={"layer": "TEXTO_REFERENCIA"}).set_placement(
            (t.x + dx, t.y + dy), align=_alinhamento_centro())
    nota = ("AcessaCidade - placa acessivel ponto de onibus - prototipo escala 1:3 - unidades mm - "
            "CORTE=vermelho GRAVACAO_VETORIAL=azul GRAVACAO_RASTER=preto; AREA_QR e TEXTO_REFERENCIA nao enviar ao laser")
    if qr_info:
        nota += " - " + qr_info
    msp.add_text(nota, height=1.5, dxfattribs={"layer": "TEXTO_REFERENCIA"}).set_placement((0, -6))
    caminho.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(caminho)
    return caminho


def _alinhamento_centro():
    from ezdxf.enums import TextEntityAlignment
    return TextEntityAlignment.BOTTOM_CENTER


def _svg_path_formas(formas: list[Forma], tx) -> str:
    partes = []
    for forma in formas:
        for poly in forma.todos():
            pts = [tx(p) for p in poly]
            partes.append("M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in pts) + " Z")
    return " ".join(partes)


def escrever_svg_placa(layout: LayoutPlaca, caminho: Path, qr_formas: list[Forma] | None = None,
                       incluir_referencias: bool = True) -> Path:
    """SVG em milímetros (width/height em mm, viewBox 1 unidade = 1 mm), cores = camadas do laser."""
    W, H = layout.largura, layout.altura

    def tx(p):
        return p[0] + W / 2, H / 2 - p[1]

    s = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}" version="1.1">',
        "<title>AcessaCidade - placa acessível para ponto de ônibus (protótipo 1:3, mm)</title>",
        "<desc>Vermelho #FF0000 = CORTE; azul #0000FF = GRAVACAO_VETORIAL; preto #000000 = GRAVACAO_RASTER "
        "(preenchimento); cinza #808080 = AREA_QR (guia, não enviar ao laser); verde = TEXTO_REFERENCIA "
        "(não enviar). Ordem: gravação raster, gravação vetorial e por último o corte.</desc>",
    ]
    # Raster primeiro (ordem de execução sugerida)
    raster = list(layout.raster) + (qr_formas or [])
    s.append('<g id="GRAVACAO_RASTER" inkscape:groupmode="layer" inkscape:label="GRAVACAO_RASTER">')
    s.append(f'<path d="{_svg_path_formas(raster, tx)}" fill="#000000" fill-rule="evenodd" '
             f'stroke="#000000" stroke-width="0.05"/>')
    s.append("</g>")
    s.append('<g id="GRAVACAO_VETORIAL" inkscape:groupmode="layer" inkscape:label="GRAVACAO_VETORIAL">')
    for r in layout.vetorial:
        s.append(f'<path d="{r.caminho_svg(tx)}" fill="none" stroke="#0000FF" stroke-width="0.1"/>')
    s.append("</g>")
    s.append('<g id="CORTE" inkscape:groupmode="layer" inkscape:label="CORTE">')
    s.append(f'<path d="{layout.contorno.caminho_svg(tx)}" fill="none" stroke="#FF0000" stroke-width="0.1"/>')
    for c in layout.furos:
        X, Y = tx((c.cx, c.cy))
        s.append(f'<circle cx="{X:.4f}" cy="{Y:.4f}" r="{c.diametro / 2:.4f}" fill="none" stroke="#FF0000" '
                 f'stroke-width="0.1"/>')
    s.append("</g>")
    if incluir_referencias:
        qx, qy, lado = layout.area_qr
        X, Y = tx((qx - lado / 2, qy + lado / 2))
        s.append('<g id="AREA_QR" inkscape:groupmode="layer" inkscape:label="AREA_QR (nao enviar ao laser)">')
        s.append(f'<rect x="{X:.4f}" y="{Y:.4f}" width="{lado:.4f}" height="{lado:.4f}" fill="none" '
                 f'stroke="#808080" stroke-width="0.1" stroke-dasharray="1,1"/>')
        if not qr_formas:
            X2, Y2 = tx((qx, qy))
            s.append(f'<text x="{X2:.3f}" y="{Y2:.3f}" font-size="2.6" text-anchor="middle" fill="#808080" '
                     f'font-family="DejaVu Sans, Arial, sans-serif">ÁREA DO QR CODE</text>')
            s.append(f'<text x="{X2:.3f}" y="{Y2 + 3.5:.3f}" font-size="1.8" text-anchor="middle" fill="#808080" '
                     f'font-family="DejaVu Sans, Arial, sans-serif">gerar com gerar_qrcode.py --url</text>')
        s.append("</g>")
    s.append("</svg>")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(s), encoding="utf-8")
    return caminho
