"""Utilitários CadQuery compartilhados pelos modelos original e redesign."""

from __future__ import annotations

import cadquery as cq

from geometria_2d import Forma, Poligono, RetanguloArredondado


def _wire(poly: Poligono, z: float) -> cq.Wire:
    pts = [cq.Vector(x, y, z) for x, y in poly]
    return cq.Wire.makePolygon(pts, close=True)


def extrudar_formas(formas: list[Forma], z0: float, altura: float) -> list[cq.Solid]:
    """Extruda cada forma (externo com furos) de z0 até z0 + altura."""
    solidos = []
    for f in formas:
        face = cq.Face.makeFromWires(_wire(f.externo, z0), [_wire(h, z0) for h in f.furos])
        solidos.append(cq.Solid.extrudeLinear(face, cq.Vector(0, 0, altura)))
    return solidos


def compor(solidos: list[cq.Shape]) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solidos))


def retangulo_arredondado_solido(r: RetanguloArredondado, z0: float, espessura: float) -> cq.Workplane:
    return (cq.Workplane("XY").workplane(offset=z0).center(r.cx, r.cy)
            .rect(r.largura, r.altura).extrude(espessura).edges("|Z").fillet(r.raio))


def cortar(base: cq.Workplane, solidos: list[cq.Shape]) -> cq.Workplane:
    """Subtrai os sólidos um a um (bem mais rápido que um único corte com um composto grande)."""
    if not solidos:
        return base
    forma = base.val()
    for s in solidos:
        forma = forma.cut(s)
    return cq.Workplane("XY").add(forma.clean())


def unir(base: cq.Workplane, solidos: list[cq.Shape]) -> cq.Workplane:
    if not solidos:
        return base
    return base.union(compor(solidos))
