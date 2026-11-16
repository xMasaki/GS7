"""Testes dos arquivos de fabricação gerados (STEP, STL, 3MF) e dos sólidos CadQuery.

Os testes de arquivo usam apenas trimesh (os arquivos ficam versionados no repositório).
Os testes que reconstroem os sólidos exigem CadQuery (pytest.importorskip), que pode não
estar instalado no CI.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

RAIZ_07 = Path(__file__).resolve().parents[1]
CAD = RAIZ_07 / "cad"
if str(CAD) not in sys.path:
    sys.path.insert(0, str(CAD))

import parametros as P  # noqa: E402

STEPS = [
    "original_placa_ESTIMADO.step", "original_montagem_ESTIMADO.step",
    "redesign_placa_principal_laser.step", "redesign_modulo_tatil_3d.step",
    "redesign_suporte_tubo_3d.step", "redesign_montagem.step",
]
IMPRESSOS = {   # arquivo: dimensões esperadas (x, y, z) já orientadas na mesa
    "modulo_tatil": (P.MODULO_LARGURA, P.MODULO_ALTURA, P.MODULO_ESPESSURA_BASE + P.SETA_RELEVO_ALTURA),
    "suporte_tubo": (P.SUPORTE_FLANGE_LARGURA, P.SUPORTE_FLANGE_ALTURA, None),
}
IMAGENS = [
    "comparacao_lado_a_lado_3d.png", "comparacao_vistas_frontais.png", "comparacao_instalacao_escala_real.png",
    "previa_arquivo_laser.png", "detalhe_braille_seta.png", "croqui_redesign.svg",
    "croqui_original_A_PREENCHER.svg",
]


@pytest.mark.parametrize("nome", STEPS)
def test_maker_step_existe_e_valido(nome):
    caminho = CAD / nome
    assert caminho.exists(), f"{nome} ausente — rode cad/gerar_todos.py"
    inicio = caminho.read_bytes()[:200].decode("ascii", "ignore")
    assert inicio.startswith("ISO-10303-21")
    assert "END-ISO-10303-21" in caminho.read_bytes()[-200:].decode("ascii", "ignore")


@pytest.mark.parametrize("nome", sorted(IMPRESSOS))
def test_maker_stl_estanque_e_cabe_na_mesa(nome):
    trimesh = pytest.importorskip("trimesh")
    stl = RAIZ_07 / "3d-print" / f"{nome}.stl"
    assert stl.exists(), "rode cad/gerar_todos.py"
    m = trimesh.load(stl, force="mesh")
    assert m.is_watertight, f"{nome}.stl não é estanque"
    assert m.volume > 0
    ext = m.bounds[1] - m.bounds[0]
    assert ext[0] <= P.MESA_IMPRESSORA_X and ext[1] <= P.MESA_IMPRESSORA_Y and ext[2] <= P.MESA_IMPRESSORA_Z
    assert max(ext) <= 200.0
    assert m.bounds[0][2] == pytest.approx(0.0, abs=1e-3), "peça deve estar apoiada na mesa (Z mínimo = 0)"
    esperado = IMPRESSOS[nome]
    for eixo, valor in enumerate(esperado):
        if valor is not None:
            assert ext[eixo] == pytest.approx(valor, abs=0.05)


def test_maker_suporte_profundidade():
    trimesh = pytest.importorskip("trimesh")
    m = trimesh.load(RAIZ_07 / "3d-print" / "suporte_tubo.stl", force="mesh")
    ext = m.bounds[1] - m.bounds[0]
    # da face da flange até o topo do berço: profundidade até o eixo + metade do berço aberto
    assert P.suporte_profundidade_total() - 1 < ext[2] < P.suporte_profundidade_total() + P.raio_berco()


@pytest.mark.parametrize("nome", sorted(IMPRESSOS))
def test_maker_3mf_valido(nome):
    tmf = RAIZ_07 / "3d-print" / f"{nome}.3mf"
    assert tmf.exists()
    with zipfile.ZipFile(tmf) as z:
        nomes = z.namelist()
        assert "[Content_Types].xml" in nomes
        modelo = [n for n in nomes if n.lower().endswith(".model")]
        assert modelo, "3MF sem 3D/*.model"
        xml = z.read(modelo[0]).decode("utf-8", "ignore")
        assert "<vertices" in xml and "<triangles" in xml
        assert 'unit="millimeter"' in xml or "unit=" not in xml


@pytest.mark.parametrize("nome", IMAGENS)
def test_maker_imagens_geradas(nome):
    caminho = RAIZ_07 / "docs" / "imagens" / nome
    assert caminho.exists() and caminho.stat().st_size > 1000


def test_maker_relatorio_geracao():
    rel = CAD / "relatorio_geracao.txt"
    assert rel.exists()
    texto = rel.read_text(encoding="utf-8")
    assert "ESTIMADAS" in texto
    assert "estanque=False" not in texto


# ----------------------------------------------------------------------------- com CadQuery
@pytest.fixture(scope="module")
def pecas():
    pytest.importorskip("cadquery")
    import modelo_redesign as MR
    return {"placa": MR.placa_principal(com_gravacao=False), "modulo": MR.modulo_tatil(),
            "suporte": MR.suporte_tubo()}


def test_maker_solidos_validos_e_dimensoes(pecas):
    placa = pecas["placa"].val()
    assert placa.isValid()
    bb = placa.BoundingBox()
    assert (bb.xlen, bb.ylen, bb.zlen) == pytest.approx((P.PLACA_LARGURA, P.PLACA_ALTURA, P.PLACA_ESPESSURA), abs=0.01)
    for nome in ("modulo", "suporte"):
        v = pecas[nome].val()
        assert v.isValid()
        assert len(v.Solids()) == 1, f"{nome} deve ser um único sólido (peças soltas não imprimem)"


def test_maker_placa_tem_todos_os_furos(pecas):
    import math
    placa = pecas["placa"].val()
    area = P.PLACA_LARGURA * P.PLACA_ALTURA - (4 - math.pi) * P.PLACA_RAIO_CANTO ** 2
    area -= sum(math.pi * (d / 2) ** 2 for *_, d, _f in P.todos_furos_placa())
    assert placa.Volume() == pytest.approx(area * P.PLACA_ESPESSURA, rel=1e-3)


def test_maker_modelo_original_estimado():
    pytest.importorskip("cadquery")
    import modelo_original as MO
    p = MO.placa_original(com_texto=False).val()
    bb = p.BoundingBox()
    assert bb.xlen == pytest.approx(P.ORIGINAL_PLACA_LARGURA, abs=0.01)
    assert bb.ylen == pytest.approx(P.ORIGINAL_PLACA_ALTURA, abs=0.01)
    assert not (P.ORIGINAL_TEM_BRAILLE or P.ORIGINAL_TEM_RELEVO or P.ORIGINAL_TEM_QR)
