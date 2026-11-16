"""Testes do Maker Lab que NÃO exigem CadQuery: parâmetros, layout 2D, DXF/SVG e QR Code."""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

RAIZ_07 = Path(__file__).resolve().parents[1]
for sub in ("cad", "laser-cut"):
    p = str(RAIZ_07 / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import parametros as P  # noqa: E402

ezdxf = pytest.importorskip("ezdxf")
G = pytest.importorskip("geometria_2d")   # usa matplotlib (fonte DejaVu) para os contornos de texto

DXF = RAIZ_07 / "laser-cut" / "placa_principal_laser.dxf"
SVG = RAIZ_07 / "laser-cut" / "placa_principal_laser.svg"
NS = "{http://www.w3.org/2000/svg}"
URL_TESTE = "https://teste.invalid"    # domínio reservado (RFC 2606) — nunca vai a um arquivo do repositório


# ----------------------------------------------------------------------------- parâmetros
def test_maker_parametros_coerentes():
    assert P.verificar_coerencia() == []


def test_maker_layout_sem_conflitos():
    assert G.verificar_layout() == []


def test_maker_furos_dentro_da_placa():
    for x, y, d, funcao in P.todos_furos_placa():
        assert P._dentro_retangulo_arredondado(x, y, d / 2 + 2 * P.PLACA_ESPESSURA), (funcao, x, y)


def test_maker_braille_palavra_ponto():
    assert P.BRAILLE_TEXTO == "PONTO"
    esperado = [("P", (1, 2, 3, 4)), ("O", (1, 3, 5)), ("N", (1, 3, 4, 5)), ("T", (2, 3, 4, 5)), ("O", (1, 3, 5))]
    assert P.braille_celas() == esperado
    assert len(P.braille_pontos()) == sum(len(c) for _, c in esperado) == 18


def test_maker_braille_dimensoes_usuais():
    assert P.BRAILLE_DIAMETRO_PONTO == pytest.approx(1.5, abs=0.3)
    assert 0.6 <= P.BRAILLE_ALTURA_PONTO <= 0.8
    assert P.BRAILLE_DIST_PONTOS == pytest.approx(2.5, abs=0.2)
    assert P.BRAILLE_DIST_CELAS == pytest.approx(6.0, abs=0.5)
    # pontos não se tocam (base Ø1,5 com 2,5 entre centros deixa 1,0 mm livre)
    pts = P.braille_pontos()
    dmin = min(math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:])
    assert dmin >= P.BRAILLE_DIAMETRO_PONTO + 0.8


def test_maker_relevos_e_fdm():
    assert P.SETA_RELEVO_ALTURA >= 1.0
    assert P.MODULO_TEXTO_RELEVO_ALTURA >= 1.0
    assert P.SETA_LARGURA_HASTE >= 3 * P.BICO_FDM
    assert P.SUPORTE_PAREDE_BERCO >= P.ESPESSURA_MINIMA_PAREDE_FDM
    # cada ponto Braille tem pelo menos ~4 camadas
    assert P.BRAILLE_ALTURA_PONTO / P.ALTURA_CAMADA_FDM >= 4


def test_maker_original_marcado_como_estimado():
    assert P.ORIGINAL_MEDIDO_EM_CAMPO is False or P.ORIGINAL_MEDIDO_EM_CAMPO is True
    fonte = (RAIZ_07 / "cad" / "parametros.py").read_text(encoding="utf-8")
    if not P.ORIGINAL_MEDIDO_EM_CAMPO:
        assert fonte.count("a substituir após medição") >= 5


def test_maker_escala_real():
    assert P.REAL_PLACA_LARGURA == pytest.approx(P.PLACA_LARGURA / P.ESCALA_PROTOTIPO)
    assert P.PLACA_LARGURA <= P.MESA_LASER_X and P.PLACA_ALTURA <= P.MESA_LASER_Y


# ----------------------------------------------------------------------------- DXF
def test_maker_dxf_existe_e_tem_camadas():
    assert DXF.exists(), "rode cad/gerar_todos.py"
    doc = ezdxf.readfile(DXF)
    nomes = {c.dxf.name for c in doc.layers}
    for camada in ("CORTE", "GRAVACAO_VETORIAL", "GRAVACAO_RASTER", "AREA_QR", "TEXTO_REFERENCIA"):
        assert camada in nomes
    assert doc.layers.get("CORTE").color == 1          # vermelho
    assert doc.layers.get("GRAVACAO_VETORIAL").color == 5   # azul
    assert doc.layers.get("GRAVACAO_RASTER").color == 7     # preto/branco
    assert doc.units == ezdxf.units.MM


def test_maker_dxf_contorno_e_furos():
    doc = ezdxf.readfile(DXF)
    msp = doc.modelspace()
    contornos = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "CORTE"]
    assert len(contornos) == 1
    from ezdxf import bbox
    caixa = bbox.extents(contornos)
    assert caixa.size.x == pytest.approx(P.PLACA_LARGURA, abs=0.01)
    assert caixa.size.y == pytest.approx(P.PLACA_ALTURA, abs=0.01)
    assert caixa.extmin.x == pytest.approx(0, abs=0.01) and caixa.extmin.y == pytest.approx(0, abs=0.01)
    assert contornos[0].closed
    circulos = [e for e in msp.query("CIRCLE") if e.dxf.layer == "CORTE"]
    assert len(circulos) == len(P.todos_furos_placa())
    for c in circulos:
        x, y = c.dxf.center.x, c.dxf.center.y
        assert 0 < x - c.dxf.radius and x + c.dxf.radius < P.PLACA_LARGURA
        assert 0 < y - c.dxf.radius and y + c.dxf.radius < P.PLACA_ALTURA


def test_maker_dxf_sem_qr_ate_url_real():
    """A placa versionada só tem a ÁREA do QR (guia); nenhum QR com URL inventada."""
    doc = ezdxf.readfile(DXF)
    msp = doc.modelspace()
    area = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "AREA_QR"]
    assert len(area) == 1
    qx, qy = P.AREA_QR_CENTRO
    cx, cy = qx + P.PLACA_LARGURA / 2, qy + P.PLACA_ALTURA / 2
    h = P.AREA_QR_LADO / 2
    # nenhuma gravação raster dentro da área do QR
    for e in msp.query("LWPOLYLINE"):
        if e.dxf.layer != "GRAVACAO_RASTER":
            continue
        for x, y in e.get_points("xy"):
            assert not (cx - h + 0.01 < x < cx + h - 0.01 and cy - h + 0.01 < y < cy + h - 0.01)
    assert not any("QR:" in t.dxf.text for t in msp.query("TEXT"))


def test_maker_dxf_textos_convertidos_em_contornos():
    doc = ezdxf.readfile(DXF)
    msp = doc.modelspace()
    raster = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "GRAVACAO_RASTER"]
    assert len(raster) > 50 and all(e.closed for e in raster)
    textos = [e for e in msp.query("TEXT")]
    assert all(t.dxf.layer == "TEXTO_REFERENCIA" for t in textos)
    assert any(P.TEXTO_TITULO in t.dxf.text for t in textos)


# ----------------------------------------------------------------------------- SVG
def test_maker_svg_valido_em_mm():
    assert SVG.exists(), "rode cad/gerar_todos.py"
    raiz = ET.parse(SVG).getroot()
    assert raiz.tag == NS + "svg"
    assert raiz.get("width") == f"{P.PLACA_LARGURA:g}mm" and raiz.get("height") == f"{P.PLACA_ALTURA:g}mm"
    assert raiz.get("viewBox") == f"0 0 {P.PLACA_LARGURA:g} {P.PLACA_ALTURA:g}"
    grupos = {g.get("id") for g in raiz.iter(NS + "g")}
    assert {"CORTE", "GRAVACAO_VETORIAL", "GRAVACAO_RASTER", "AREA_QR"} <= grupos
    corte = next(g for g in raiz.iter(NS + "g") if g.get("id") == "CORTE")
    assert len(list(corte.iter(NS + "circle"))) == len(P.todos_furos_placa())
    assert all(el.get("stroke") == "#FF0000" for el in corte)


def test_maker_croqui_svg_valido():
    croqui = RAIZ_07 / "docs" / "imagens" / "croqui_redesign.svg"
    if not croqui.exists():
        pytest.skip("croqui é gerado por gerar_todos.py (com imagens)")
    raiz = ET.parse(croqui).getroot()
    assert raiz.tag == NS + "svg"
    texto = croqui.read_text(encoding="utf-8")
    assert f"{P.PLACA_LARGURA:g}" in texto


# ----------------------------------------------------------------------------- QR Code
def _decodificar_svg(caminho: Path) -> str:
    cv2 = pytest.importorskip("cv2")
    import numpy as np
    raiz = ET.parse(caminho).getroot()
    _, _, w, h = (float(v) for v in raiz.get("viewBox").split())
    k = 12  # px por mm
    img = np.full((int(h * k) + 1, int(w * k) + 1), 255, np.uint8)
    for g in raiz.iter(NS + "g"):
        if g.get("id") != "GRAVACAO_RASTER":
            continue
        for p in g.iter(NS + "path"):
            for sub in re.findall(r"M([^Z]+)Z", p.get("d")):
                pts = [[float(a) * k for a in xy.split(",")] for xy in re.split(r"\s*L\s*", sub.strip())]
                cv2.fillPoly(img, [np.array(pts, np.int32)], 0)
    img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)
    return cv2.QRCodeDetector().detectAndDecode(img)[0]


def test_maker_qrcode_gera_e_decodifica(tmp_path):
    pytest.importorskip("qrcode")
    import gerar_qrcode as Q
    r = Q.gerar(URL_TESTE, tmp_path)
    assert r["conteudo"] == URL_TESTE + "/" + P.ROTA_REGISTRAR_APP
    assert r["modulo_mm"] >= P.QR_MODULO_MINIMO
    for chave in ("qr_svg", "qr_dxf", "placa_svg", "placa_dxf", "info"):
        assert r["arquivos"][chave].exists()
    assert _decodificar_svg(r["arquivos"]["qr_svg"]) == r["conteudo"]
    assert _decodificar_svg(r["arquivos"]["placa_svg"]) == r["conteudo"]
    doc = ezdxf.readfile(r["arquivos"]["placa_dxf"])
    n_raster_com_qr = sum(1 for e in doc.modelspace().query("LWPOLYLINE") if e.dxf.layer == "GRAVACAO_RASTER")
    n_raster_sem_qr = sum(1 for e in ezdxf.readfile(DXF).modelspace().query("LWPOLYLINE")
                          if e.dxf.layer == "GRAVACAO_RASTER")
    assert n_raster_com_qr > n_raster_sem_qr


@pytest.mark.parametrize("url", ["", "[PREENCHER: URL]", "ftp://x.invalid", "https://localhost:8000",
                                 "http://192.168.0.10", "acessacidade"])
def test_maker_qrcode_recusa_url_invalida(url, tmp_path):
    pytest.importorskip("qrcode")
    import gerar_qrcode as Q
    with pytest.raises(Q.ErroQR):
        Q.gerar(url, tmp_path)


def test_maker_qrcode_url_longa_demais(tmp_path):
    pytest.importorskip("qrcode")
    import gerar_qrcode as Q
    with pytest.raises(Q.ErroQR):
        Q.gerar(URL_TESTE + "/" + "a" * 400, tmp_path, correcao="H")


def test_maker_repositorio_sem_qr_pronto():
    """Nenhum QR é versionado antes de existir a URL pública real."""
    assert not (RAIZ_07 / "laser-cut" / "qrcode_acessacidade.svg").exists() or \
        (RAIZ_07 / "laser-cut" / "qrcode_acessacidade_info.txt").exists()
