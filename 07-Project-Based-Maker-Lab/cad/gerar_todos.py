"""Gera TODOS os arquivos de CAD/fabricação/documentação da disciplina 07 (Maker Lab).

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 07-Project-Based-Maker-Lab\\cad\\gerar_todos.py
    .venv\\Scripts\\python.exe 07-Project-Based-Maker-Lab\\cad\\gerar_todos.py --sem-imagens   (mais rápido)

Saídas (todas em milímetros):
    cad/original_placa_ESTIMADO.step          placa original (dimensões ESTIMADAS)
    cad/original_montagem_ESTIMADO.step       placa + abraçadeiras + trecho de poste (ESTIMADO)
    cad/redesign_placa_principal_laser.step   placa principal (peça a laser)
    cad/redesign_modulo_tatil_3d.step         módulo tátil (peça impressa)
    cad/redesign_suporte_tubo_3d.step         suporte/abraçadeira para tubo (peça impressa)
    cad/redesign_montagem.step                montagem completa do redesign
    3d-print/modulo_tatil.stl  + .3mf         já orientado para impressão (base na mesa)
    3d-print/suporte_tubo.stl  + .3mf         já orientado para impressão (face da flange na mesa)
    laser-cut/placa_principal_laser.dxf + .svg  contorno, furos, gravações e ÁREA reservada do QR
    docs/imagens/*.png e *.svg                comparação lado a lado, vistas, croquis
    cad/relatorio_geracao.txt                 dimensões medidas nos arquivos gerados
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ_07 = AQUI.parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

import parametros as P  # noqa: E402
import geometria_2d as G  # noqa: E402

DIR_CAD = RAIZ_07 / "cad"
DIR_3D = RAIZ_07 / "3d-print"
DIR_LASER = RAIZ_07 / "laser-cut"
DIR_IMG = RAIZ_07 / "docs" / "imagens"

ARQ = {
    "original_placa_step": DIR_CAD / "original_placa_ESTIMADO.step",
    "original_montagem_step": DIR_CAD / "original_montagem_ESTIMADO.step",
    "placa_step": DIR_CAD / "redesign_placa_principal_laser.step",
    "modulo_step": DIR_CAD / "redesign_modulo_tatil_3d.step",
    "suporte_step": DIR_CAD / "redesign_suporte_tubo_3d.step",
    "montagem_step": DIR_CAD / "redesign_montagem.step",
    "modulo_stl": DIR_3D / "modulo_tatil.stl",
    "modulo_3mf": DIR_3D / "modulo_tatil.3mf",
    "suporte_stl": DIR_3D / "suporte_tubo.stl",
    "suporte_3mf": DIR_3D / "suporte_tubo.3mf",
    "placa_dxf": DIR_LASER / "placa_principal_laser.dxf",
    "placa_svg": DIR_LASER / "placa_principal_laser.svg",
    "relatorio": DIR_CAD / "relatorio_geracao.txt",
}


def _log(msg: str) -> None:
    print(msg, flush=True)


def _na_mesa(wp):
    """Translada a peça para que a base fique em Z = 0 e o centro em X/Y = 0 (mesa da impressora)."""
    import cadquery as cq
    bb = wp.val().BoundingBox()
    return wp.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def exportar_step(obj, caminho: Path) -> Path:
    import cadquery as cq
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, cq.Assembly):
        if hasattr(obj, "export"):          # CadQuery >= 2.5 (save() está obsoleto)
            obj.export(str(caminho), exportType="STEP")
        else:
            obj.save(str(caminho), exportType="STEP")
    else:
        cq.exporters.export(obj, str(caminho), exportType="STEP")
    return caminho


def exportar_stl_3mf(wp, stl: Path, tmf: Path) -> tuple[Path, Path, str]:
    """STL pelo CadQuery; 3MF pelo CadQuery e, se falhar, pelo trimesh a partir do STL."""
    import cadquery as cq
    stl.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(wp, str(stl), exportType="STL", tolerance=0.02, angularTolerance=0.1)
    metodo = "cadquery"
    try:
        cq.exporters.export(wp, str(tmf), exportType="3MF", tolerance=0.02, angularTolerance=0.1)
        if not tmf.exists() or tmf.stat().st_size == 0:
            raise RuntimeError("3MF vazio")
    except Exception as exc:  # noqa: BLE001 — qualquer falha do exporter cai no plano B
        import trimesh
        trimesh.load(str(stl), force="mesh").export(str(tmf), file_type="3mf")
        metodo = f"trimesh (exporter 3MF do CadQuery falhou: {exc.__class__.__name__})"
    return stl, tmf, metodo


def gerar_laser(layout=None) -> tuple[Path, Path]:
    layout = layout or G.layout_placa()
    dxf = G.escrever_dxf_placa(layout, ARQ["placa_dxf"])
    svg = G.escrever_svg_placa(layout, ARQ["placa_svg"])
    return dxf, svg


def _poste_curto_original():
    """Trecho de poste só para a imagem de comparação (o STEP do original leva o poste inteiro)."""
    import cadquery as cq
    import modelo_original as MO
    yc = MO._centro_placa_y()
    meio = P.ORIGINAL_PLACA_ALTURA * 0.9
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        P.ORIGINAL_POSTE_DIAMETRO / 2, 2 * meio, cq.Vector(0, yc - meio, 0), cq.Vector(0, 1, 0)))


def gerar_cad(com_imagens: bool = True) -> list[str]:
    import cadquery as cq
    import trimesh
    import modelo_original as MO
    import modelo_redesign as MR

    linhas: list[str] = []

    # ---------------- ORIGINAL (ESTIMADO) ----------------
    t0 = time.time()
    placa_o = MO.placa_original()
    exportar_step(placa_o, ARQ["original_placa_step"])
    exportar_step(MO.montagem_original(placa_o), ARQ["original_montagem_step"])
    bb = placa_o.val().BoundingBox()
    linhas.append(f"Original (ESTIMADO): placa {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm; "
                  f"borda inferior a {P.ORIGINAL_ALTURA_BORDA_INFERIOR:g} mm do piso; "
                  f"medido em campo = {P.ORIGINAL_MEDIDO_EM_CAMPO}")
    _log(f"[ok] STEP do original ({time.time() - t0:.1f} s)")

    # ---------------- REDESIGN ----------------
    t0 = time.time()
    placa = MR.placa_principal()
    modulo = MR.modulo_tatil()
    suporte = MR.suporte_tubo()
    _log(f"[ok] sólidos do redesign ({time.time() - t0:.1f} s)")
    for nome, peca in (("placa", placa), ("modulo", modulo), ("suporte", suporte)):
        if not peca.val().isValid():
            raise RuntimeError(f"Sólido inválido: {nome}")
    exportar_step(placa, ARQ["placa_step"])
    exportar_step(modulo, ARQ["modulo_step"])
    exportar_step(suporte, ARQ["suporte_step"])
    exportar_step(MR.montagem(placa, modulo, suporte), ARQ["montagem_step"])
    _log("[ok] STEP do redesign (peças + montagem)")

    for nome, peca, chave in (("Placa principal (laser)", placa, "placa_step"),
                              ("Módulo tátil (3D)", modulo, "modulo_step"),
                              ("Suporte para tubo (3D)", suporte, "suporte_step")):
        b = peca.val().BoundingBox()
        linhas.append(f"{nome}: {b.xlen:.2f} x {b.ylen:.2f} x {b.zlen:.2f} mm -> {ARQ[chave].name}")

    # ---------------- IMPRESSÃO 3D ----------------
    modulo_mesa = _na_mesa(modulo)                       # relevo para cima, verso liso na mesa
    suporte_mesa = _na_mesa(MR.suporte_para_impressao(suporte))   # face da flange na mesa
    for nome, wp, k_stl, k_3mf in (("modulo_tatil", modulo_mesa, "modulo_stl", "modulo_3mf"),
                                   ("suporte_tubo", suporte_mesa, "suporte_stl", "suporte_3mf")):
        stl, tmf, metodo = exportar_stl_3mf(wp, ARQ[k_stl], ARQ[k_3mf])
        m = trimesh.load(str(stl), force="mesh")
        ext = m.bounds[1] - m.bounds[0]
        linhas.append(f"{stl.name}: {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} mm, {len(m.faces)} triângulos, "
                      f"estanque={m.is_watertight}, volume={m.volume / 1000:.2f} cm3; 3MF via {metodo}")
        if not m.is_watertight:
            _log(f"[ATENÇÃO] {stl.name} NÃO é estanque — revise a geometria antes de fatiar")
        _log(f"[ok] {stl.name} / {tmf.name} (3MF via {metodo})")

    # ---------------- IMAGENS ----------------
    if com_imagens:
        import imagens as I
        DIR_IMG.mkdir(parents=True, exist_ok=True)
        yc, zt = MO._centro_placa_y(), MO._z_traseira_placa()
        placa_o_pos = placa_o.translate(cq.Vector(0, yc, zt))
        orig_partes = [(_poste_curto_original().val(), "#8A8D91"),
                       (MO.abracadeiras_original().val(), "#A7A9AC"),
                       (placa_o_pos.val(), I.COR_ORIG_PLACA)]
        mx, my = P.MODULO_CENTRO_NA_PLACA
        modulo_pos = modulo.translate(cq.Vector(mx, my, P.PLACA_ESPESSURA))
        tubo_curto = cq.Workplane("XY").add(cq.Solid.makeCylinder(
            P.TUBO_DIAMETRO / 2, P.PLACA_ALTURA * 1.4, cq.Vector(0, -P.PLACA_ALTURA * 0.7,
                                                                 -P.suporte_profundidade_total()),
            cq.Vector(0, 1, 0)))
        red_partes = [(tubo_curto.val(), "#D9D9D9"), (suporte.val(), "#8E9196"),
                      (placa.val(), I.COR_PLACA_NOVA), (MR.gravacao_representacao().val(), I.COR_TEXTO_NOVO),
                      (modulo_pos.val(), I.COR_MODULO)]
        saidas = [
            I.imagem_comparacao_3d(orig_partes, red_partes, DIR_IMG / "comparacao_lado_a_lado_3d.png"),
            I.imagem_vistas_frontais(DIR_IMG / "comparacao_vistas_frontais.png"),
            I.imagem_elevacao(DIR_IMG / "comparacao_instalacao_escala_real.png"),
            I.imagem_previa_laser(DIR_IMG / "previa_arquivo_laser.png"),
            I.imagem_braille(DIR_IMG / "detalhe_braille_seta.png"),
            I.imagem_peca([(modulo.val(), I.COR_MODULO)], "Módulo tátil (impressão 3D, 1:1)",
                          DIR_IMG / "peca_modulo_tatil.png", elev=40, azim=-70),
            I.imagem_peca([(suporte.val(), "#8E9196")], "Suporte para tubo Ø25 (impressão 3D)",
                          DIR_IMG / "peca_suporte_tubo.png", elev=20, azim=-130, tol=0.1),
            I.imagem_peca([(placa.val(), I.COR_PLACA_NOVA),
                           (MR.gravacao_representacao().val(), I.COR_TEXTO_NOVO)],
                          "Placa principal (corte a laser, 1:3)", DIR_IMG / "peca_placa_laser.png",
                          elev=30, azim=-75, tol=0.2),
            I.croqui_redesign(DIR_IMG / "croqui_redesign.svg"),
            I.croqui_original_modelo(DIR_IMG / "croqui_original_A_PREENCHER.svg"),
        ]
        for s in saidas:
            linhas.append(f"Imagem: docs/imagens/{Path(s).name}")
        _log(f"[ok] {len(saidas)} imagens em docs/imagens")
    return linhas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gera STEP, STL, 3MF, DXF, SVG e imagens do Maker Lab.")
    ap.add_argument("--sem-imagens", action="store_true", help="não gera as imagens de documentação")
    ap.add_argument("--so-laser", action="store_true", help="gera apenas o DXF/SVG da placa (não exige CadQuery)")
    args = ap.parse_args(argv)

    problemas = P.verificar_coerencia() + G.verificar_layout()
    if problemas:
        _log("ERRO — parâmetros incoerentes:\n  - " + "\n  - ".join(problemas))
        return 2
    _log("[ok] parâmetros coerentes (parametros.verificar_coerencia + geometria_2d.verificar_layout)")

    inicio = time.time()
    dxf, svg = gerar_laser()
    _log(f"[ok] laser: {dxf.name}, {svg.name}")
    linhas = [f"Laser: {dxf.name} e {svg.name} — placa {P.PLACA_LARGURA:g} x {P.PLACA_ALTURA:g} mm, "
              f"área do QR {P.AREA_QR_LADO:g} mm SEM QR (rodar laser-cut/gerar_qrcode.py --url <URL_PUBLICA>)"]
    if not args.so_laser:
        linhas += gerar_cad(com_imagens=not args.sem_imagens)

    cabecalho = [
        "Relatório gerado automaticamente por cad/gerar_todos.py (valores lidos dos arquivos gerados).",
        f"Data/hora local: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Escala do protótipo: {P.ESCALA_TEXTO}",
        "ATENÇÃO: o objeto ORIGINAL usa dimensões ESTIMADAS até a medição em campo "
        f"(ORIGINAL_MEDIDO_EM_CAMPO = {P.ORIGINAL_MEDIDO_EM_CAMPO}).",
        "",
    ]
    ARQ["relatorio"].write_text("\n".join(cabecalho + linhas) + "\n", encoding="utf-8")
    for linha in linhas:
        _log("   " + linha)
    _log(f"Concluído em {time.time() - inicio:.0f} s. Relatório: {ARQ['relatorio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
