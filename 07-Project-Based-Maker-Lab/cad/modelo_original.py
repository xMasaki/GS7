"""OBJETO ORIGINAL (simplificado) — placa genérica de ponto de ônibus SEM recursos de acessibilidade.

O que o modelo representa (simplificado ao que importa para o problema):
  * placa metálica retangular presa ALTO no poste (borda inferior ~2,2 m — ESTIMADO);
  * texto pintado com BAIXO contraste (no modelo: rebaixo raso só para visualização);
  * SEM relevo, SEM Braille, SEM QR Code / canal para reportar problemas;
  * fixação por 2 abraçadeiras metálicas no poste.

ATENÇÃO: TODAS as dimensões são ESTIMADAS ("a substituir após medição em campo") e ficam no bloco
"OBJETO ORIGINAL" de parametros.py. Escala 1:1 (tamanho real estimado). Origem: piso, no eixo do
poste; Y vertical; a placa fica à frente do poste (+Z).
"""

from __future__ import annotations

import cadquery as cq

import geometria_2d as G
import parametros as P
from cq_util import cortar, extrudar_formas


def _centro_placa_y() -> float:
    return P.ORIGINAL_ALTURA_BORDA_INFERIOR + P.ORIGINAL_PLACA_ALTURA / 2


def _z_traseira_placa() -> float:
    return P.ORIGINAL_POSTE_DIAMETRO / 2 + P.ORIGINAL_AFASTAMENTO_PLACA_POSTE


def _furos_original() -> list[tuple[float, float]]:
    dy = P.ORIGINAL_PLACA_ALTURA / 3
    return [(0.0, dy), (0.0, -dy)]


def placa_original(com_texto: bool = True) -> cq.Workplane:
    """Placa original em coordenadas locais (centro na origem, face traseira Z=0)."""
    t = P.ORIGINAL_PLACA_ESPESSURA
    contorno = G.RetanguloArredondado(0, 0, P.ORIGINAL_PLACA_LARGURA, P.ORIGINAL_PLACA_ALTURA,
                                      P.ORIGINAL_PLACA_RAIO_CANTO)
    placa = (cq.Workplane("XY").rect(contorno.largura, contorno.altura).extrude(t)
             .edges("|Z").fillet(contorno.raio))
    furos = [cq.Solid.makeCylinder(P.ORIGINAL_FURO_DIAMETRO / 2, t + 2, cq.Vector(x, y, -1))
             for x, y in _furos_original()]
    placa = cortar(placa, furos)
    if com_texto:
        placa = cortar(placa, extrudar_formas(texto_original_formas(), t - 0.2, 0.5))
    return placa


def texto_original_formas():
    # texto deslocado para a metade de cima, sem interferir nos furos (layout ESTIMADO)
    return G.texto_formas(P.ORIGINAL_TEXTO, P.ORIGINAL_TEXTO_ALTURA, 0, -P.ORIGINAL_TEXTO_ALTURA / 2)


def poste_original() -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        P.ORIGINAL_POSTE_DIAMETRO / 2, P.ORIGINAL_POSTE_ALTURA_MODELADA, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0)))


def abracadeiras_original() -> cq.Workplane:
    """Duas abraçadeiras metálicas simplificadas: anel em volta do poste + aba até a placa."""
    r_int = P.ORIGINAL_POSTE_DIAMETRO / 2
    r_ext = r_int + P.ORIGINAL_ABRACADEIRA_ESPESSURA
    w = P.ORIGINAL_ABRACADEIRA_LARGURA
    yc = _centro_placa_y()
    solidos = []
    for _, dy in _furos_original():
        y0 = yc + dy - w / 2
        anel = cq.Solid.makeCylinder(r_ext, w, cq.Vector(0, y0, 0), cq.Vector(0, 1, 0)).cut(
            cq.Solid.makeCylinder(r_int, w, cq.Vector(0, y0, 0), cq.Vector(0, 1, 0)))
        aba = cq.Solid.makeBox(w, w, _z_traseira_placa() - r_int + 1, cq.Vector(-w / 2, y0, r_int - 1))
        solidos.append(anel.fuse(aba))
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solidos))


def montagem_original(placa=None) -> cq.Assembly:
    placa = placa if placa is not None else placa_original()
    assy = cq.Assembly(name="original_placa_ponto_onibus_ESTIMADO")
    assy.add(poste_original(), name="poste_ESTIMADO", color=cq.Color(0.45, 0.47, 0.5))
    assy.add(abracadeiras_original(), name="abracadeiras_ESTIMADO", color=cq.Color(0.6, 0.6, 0.62))
    assy.add(placa, name="placa_original_ESTIMADO",
             loc=cq.Location(cq.Vector(0, _centro_placa_y(), _z_traseira_placa())),
             color=cq.Color(0.20, 0.33, 0.55))
    return assy


if __name__ == "__main__":
    p = placa_original()
    bb = p.val().BoundingBox()
    print(f"placa original (ESTIMADA): {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.1f} mm, válida={p.val().isValid()}")
    print(f"borda inferior a {P.ORIGINAL_ALTURA_BORDA_INFERIOR:.0f} mm do piso (ESTIMADO)")
