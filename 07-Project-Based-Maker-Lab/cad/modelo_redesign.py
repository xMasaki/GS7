"""REDESIGN — Placa de sinalização acessível para ponto de ônibus (AcessaCidade).

Três peças fabricáveis + montagem:
  1. Placa principal (CORTE A LASER, 3 mm, escala 1:3): cantos arredondados, título e pictograma
     de alto contraste, rodapé convidando a reportar problemas, ÁREA RESERVADA ao QR Code,
     furos de fixação.
  2. Módulo tátil (IMPRESSÃO 3D, escala 1:1): letras "PONTO" em relevo, seta direcional em
     relevo (1,5 mm) e "PONTO" em Braille (5 celas).
  3. Suporte/abraçadeira para tubo (IMPRESSÃO 3D, escala 1:3): flange parafusada no verso da
     placa, berço para tubo Ø25 mm (stand-in do poste em 1:3) e túneis para abraçadeiras de nylon.

Todas as medidas vêm de parametros.py (mm). Uso direto:  python modelo_redesign.py
"""

from __future__ import annotations

import math

import cadquery as cq

import geometria_2d as G
import parametros as P
from cq_util import cortar, extrudar_formas, retangulo_arredondado_solido, unir


# -------------------------------------------------------------------------------------
# 1. Placa principal (laser)
# -------------------------------------------------------------------------------------
def placa_principal(com_gravacao: bool = True) -> cq.Workplane:
    """Placa com face traseira em Z=0 e face frontal em Z=PLACA_ESPESSURA.

    com_gravacao=True rebaixa os textos/pictograma (PROFUNDIDADE_GRAVACAO_MODELO) e a área do QR
    (0,1 mm) — leva ~30 s. com_gravacao=False gera só o recorte (contorno + furos)."""
    layout = G.layout_placa()
    t = P.PLACA_ESPESSURA
    placa = retangulo_arredondado_solido(layout.contorno, 0, t)
    furos = [cq.Solid.makeCylinder(c.diametro / 2, t + 2, cq.Vector(c.cx, c.cy, -1)) for c in layout.furos]
    placa = cortar(placa, furos)
    if com_gravacao:
        prof = P.PROFUNDIDADE_GRAVACAO_MODELO
        gravacao = extrudar_formas(layout.raster, t - prof, prof + 0.5)
        # área do QR representada como rebaixo de 0,1 mm (só visual; o QR real é gerado depois)
        qx, qy, lado = layout.area_qr
        gravacao.append(cq.Solid.makeBox(lado, lado, 0.6, cq.Vector(qx - lado / 2, qy - lado / 2, t - 0.1)))
        placa = cortar(placa, gravacao)
    return placa


# -------------------------------------------------------------------------------------
# 2. Módulo tátil (impressão 3D, 1:1) — base em Z=0..MODULO_ESPESSURA_BASE, centro na origem
# -------------------------------------------------------------------------------------
def _seta_solido(z0: float) -> cq.Workplane:
    pts = G.seta_poligono(0, P.SETA_CENTRO_Y, P.SETA_COMPRIMENTO, P.SETA_LARGURA_HASTE,
                          P.SETA_LARGURA_PONTA, P.SETA_COMPRIMENTO_PONTA, P.SETA_SENTIDO)
    seta = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(
        P.SETA_RELEVO_ALTURA + (P.MODULO_ESPESSURA_BASE - z0))
    try:
        seta = seta.faces(">Z").edges().chamfer(P.SETA_CHANFRO)
    except Exception:  # pragma: no cover - chanfro é só acabamento
        pass
    return seta


def braille_solidos(z_base: float) -> list[cq.Solid]:
    """Pontos Braille como calotas esféricas (base Ø BRAILLE_DIAMETRO_PONTO, altura BRAILLE_ALTURA_PONTO)."""
    R = P.braille_raio_esfera()
    zc = z_base + P.BRAILLE_ALTURA_PONTO - R
    corte_inferior = z_base - 0.3          # a parte de baixo da esfera fica embutida na base
    # O topo é aparado em BRAILLE_APARO_TOPO (0,02 mm, imperceptível e menor que 1 camada FDM):
    # elimina o "polo" da esfera, que gera triângulos degenerados e deixava o STL não estanque.
    altura_caixa = (z_base + P.BRAILLE_ALTURA_PONTO - P.BRAILLE_APARO_TOPO) - corte_inferior
    solidos = []
    for x, y in P.braille_pontos():
        esfera = cq.Solid.makeSphere(R, cq.Vector(x, y, zc), angleDegrees1=-90, angleDegrees2=90)
        caixa = cq.Solid.makeBox(2 * R + 1, 2 * R + 1, altura_caixa, cq.Vector(x - R - 0.5, y - R - 0.5, corte_inferior))
        solidos.append(esfera.intersect(caixa))
    return solidos


def modulo_tatil() -> cq.Workplane:
    h = P.MODULO_ESPESSURA_BASE
    base = (cq.Workplane("XY").rect(P.MODULO_LARGURA, P.MODULO_ALTURA).extrude(h)
            .edges("|Z").fillet(P.MODULO_RAIO_CANTO)
            .faces(">Z").edges().chamfer(P.MODULO_CHANFRO_SUPERIOR))
    # furos-guia cegos pelo verso
    furos = [cq.Solid.makeCylinder(P.MODULO_FURO_GUIA_DIAMETRO / 2, P.MODULO_FURO_GUIA_PROFUNDIDADE + 0.01,
                                   cq.Vector(x, y, -0.01)) for x, y in P.MODULO_FURO_GUIA_POSICOES]
    base = cortar(base, furos)
    # relevo: seta, letras e Braille (sobrepostos 0,2 mm na base para garantir a fusão)
    modulo = base.union(_seta_solido(h - 0.2))
    letras = G.texto_formas(P.MODULO_TEXTO_RELEVO, P.MODULO_TEXTO_ALTURA_MAIUSCULA, 0, P.MODULO_TEXTO_BASE_Y)
    modulo = unir(modulo, extrudar_formas(letras, h - 0.2, P.MODULO_TEXTO_RELEVO_ALTURA + 0.2))
    modulo = unir(modulo, braille_solidos(h))
    return modulo


# -------------------------------------------------------------------------------------
# 3. Suporte / abraçadeira para tubo (impressão 3D) — face de contato com a placa em Z=0,
#    corpo para Z negativo; tubo vertical (eixo Y)
# -------------------------------------------------------------------------------------
def suporte_tubo() -> cq.Workplane:
    tf = P.SUPORTE_FLANGE_ESPESSURA
    flange = (cq.Workplane("XY").workplane(offset=-tf).rect(P.SUPORTE_FLANGE_LARGURA, P.SUPORTE_FLANGE_ALTURA)
              .extrude(tf).edges("|Z").fillet(P.SUPORTE_FLANGE_RAIO))
    rb = P.raio_berco()
    zc = -P.suporte_profundidade_total()           # eixo do tubo
    larg = P.suporte_largura_berco()
    bloco = cq.Workplane("XY").box(larg, P.SUPORTE_BERCO_COMPRIMENTO, -zc - tf, centered=(True, True, False)) \
        .translate((0, 0, zc))
    corpo = flange.union(bloco)
    # berço cilíndrico
    berco = cq.Solid.makeCylinder(rb, P.SUPORTE_BERCO_COMPRIMENTO + 4,
                                  cq.Vector(0, -P.SUPORTE_BERCO_COMPRIMENTO / 2 - 2, zc), cq.Vector(0, 1, 0))
    # túneis para as abraçadeiras de nylon (atravessam o bloco no eixo X)
    z_tunel = -(tf + P.SUPORTE_AFASTAMENTO / 2)
    tuneis = [cq.Solid.makeBox(larg + 4, P.SUPORTE_TUNEL_LARGURA, P.SUPORTE_TUNEL_ALTURA,
                               cq.Vector(-larg / 2 - 2, ty - P.SUPORTE_TUNEL_LARGURA / 2,
                                         z_tunel - P.SUPORTE_TUNEL_ALTURA / 2)) for ty in P.SUPORTE_TUNEIS_Y]
    # furos M4 e alojamentos sextavados das porcas (no lado de trás da flange)
    furos = [cq.Solid.makeCylinder(P.FURO_SUPORTE_DIAMETRO / 2, tf + 2, cq.Vector(x, y, -tf - 1))
             for x, y in P.furos_suporte()]
    d_circ = 2 * (P.SUPORTE_PORCA_M4_ENTRE_FACES + P.SUPORTE_PORCA_FOLGA) / math.sqrt(3)
    porcas = []
    for x, y in P.furos_suporte():
        porca = (cq.Workplane("XY").workplane(offset=-tf - 0.01).center(x, y)
                 .polygon(6, d_circ).extrude(P.SUPORTE_PORCA_PROFUNDIDADE + 0.01))
        porcas.append(porca.val())
    return cortar(corpo, [berco, *tuneis, *furos, *porcas])


def suporte_para_impressao(suporte: cq.Workplane | None = None) -> cq.Workplane:
    """Suporte girado 180° em X: face de contato com a placa apoiada na mesa (Z=0), berço para cima."""
    s = suporte if suporte is not None else suporte_tubo()
    return s.rotate((0, 0, 0), (1, 0, 0), 180)


def tubo_demonstracao() -> cq.Workplane:
    zc = -P.suporte_profundidade_total()
    L = P.TUBO_COMPRIMENTO_MODELO
    return cq.Workplane("XY").add(
        cq.Solid.makeCylinder(P.TUBO_DIAMETRO / 2, L, cq.Vector(0, -L / 2, zc), cq.Vector(0, 1, 0)))


# -------------------------------------------------------------------------------------
# Montagem
# -------------------------------------------------------------------------------------
def gravacao_representacao() -> cq.Workplane:
    """Textos/pictograma como 'adesivo' fino (0,1 mm) sobre a face frontal — só para visualização
    em cor contrastante (o processo real é gravação a laser na própria placa)."""
    layout = G.layout_placa()
    from cq_util import compor
    return compor(extrudar_formas(layout.raster, P.PLACA_ESPESSURA - 0.05, 0.1))


def montagem(placa=None, modulo=None, suporte=None) -> cq.Assembly:
    placa = placa if placa is not None else placa_principal()
    modulo = modulo if modulo is not None else modulo_tatil()
    suporte = suporte if suporte is not None else suporte_tubo()
    mx, my = P.MODULO_CENTRO_NA_PLACA
    assy = cq.Assembly(name="redesign_placa_acessivel")
    assy.add(placa, name="placa_principal_laser", color=cq.Color(0.08, 0.08, 0.08))
    assy.add(gravacao_representacao(), name="gravacao_alto_contraste_representacao", color=cq.Color(0.97, 0.97, 0.97))
    assy.add(modulo, name="modulo_tatil_3d", loc=cq.Location(cq.Vector(mx, my, P.PLACA_ESPESSURA)),
             color=cq.Color(0.98, 0.80, 0.05))
    assy.add(suporte, name="suporte_tubo_3d", color=cq.Color(0.55, 0.57, 0.6))
    assy.add(tubo_demonstracao(), name="tubo_pvc_25mm_referencia", color=cq.Color(0.85, 0.85, 0.85))
    return assy


if __name__ == "__main__":
    for nome, peca in (("placa", placa_principal()), ("modulo", modulo_tatil()), ("suporte", suporte_tubo())):
        bb = peca.val().BoundingBox()
        print(f"{nome}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, válido={peca.val().isValid()}")
