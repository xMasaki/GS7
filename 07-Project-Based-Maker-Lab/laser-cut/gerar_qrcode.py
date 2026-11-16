"""Gera o QR Code do AcessaCidade para GRAVAÇÃO A LASER na área reservada da placa.

IMPORTANTE: rode SOMENTE com a URL PÚBLICA REAL do AcessaCidade (depois do deploy). Este repositório
não contém nenhum QR pronto de propósito — um QR apontando para um endereço inventado ou fora do ar
seria um "botão falso" na rua.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 07-Project-Based-Maker-Lab\\laser-cut\\gerar_qrcode.py --url https://<URL_PUBLICA>

Por padrão a rota da tela de registro (#/registrar, contrato seção 7) é acrescentada quando a URL não
tem fragmento '#'. Use --sem-rota para gravar a URL exatamente como informada.

Saídas (em --saida, padrão: esta pasta laser-cut/):
    qrcode_acessacidade.svg / .dxf              só o QR (inclui a zona de silêncio), em mm
    placa_principal_laser_com_qr.svg / .dxf     placa completa com o QR dentro da área reservada
    qrcode_acessacidade_info.txt                URL codificada, versão, tamanho do módulo, data
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
DIR_CAD = AQUI.parent / "cad"
if str(DIR_CAD) not in sys.path:
    sys.path.insert(0, str(DIR_CAD))

import parametros as P  # noqa: E402
import geometria_2d as G  # noqa: E402

NIVEIS_CORRECAO = {"L": 1, "M": 0, "Q": 3, "H": 2}   # constantes do pacote qrcode
HOSTS_LOCAIS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


class ErroQR(ValueError):
    pass


def validar_url(url: str, permitir_local: bool = False) -> str:
    url = (url or "").strip()
    if not url or "PREENCHER" in url.upper() or "<" in url or ">" in url or " " in url:
        raise ErroQR("Informe a URL pública REAL do AcessaCidade (sem placeholders e sem espaços).")
    u = urlparse(url)
    if u.scheme not in ("https", "http") or not u.netloc:
        raise ErroQR("A URL deve começar com https:// (ou http://) e ter um domínio.")
    host = (u.hostname or "").lower()
    if not permitir_local and (host in HOSTS_LOCAIS or host.startswith("192.168.") or host.startswith("10.")):
        raise ErroQR("URL local/privada não funciona no celular de quem está no ponto de ônibus. "
                     "Use a URL pública (ou --permitir-local apenas para teste de bancada).")
    return url


def montar_url(url: str, sem_rota: bool = False) -> str:
    if sem_rota or "#" in url:
        return url
    return url.rstrip("/") + "/" + P.ROTA_REGISTRAR_APP


def matriz_qr(conteudo: str, correcao: str = "M") -> list[list[bool]]:
    """Matriz de módulos do QR SEM a zona de silêncio (True = módulo escuro)."""
    import qrcode
    qr = qrcode.QRCode(error_correction=NIVEIS_CORRECAO[correcao], border=0, box_size=1)
    qr.add_data(conteudo)
    qr.make(fit=True)
    return [list(map(bool, linha)) for linha in qr.get_matrix()]


def tamanho_modulo(n_modulos: int, lado: float = P.AREA_QR_LADO, zona: int = P.QR_ZONA_SILENCIO_MODULOS) -> float:
    return lado / (n_modulos + 2 * zona)


def formas_qr(matriz: list[list[bool]], cx: float, cy: float, lado: float = P.AREA_QR_LADO,
              zona: int = P.QR_ZONA_SILENCIO_MODULOS) -> list[G.Forma]:
    """Retângulos (sequências horizontais de módulos escuros) centrados em (cx, cy), em mm."""
    n = len(matriz)
    m = tamanho_modulo(n, lado, zona)
    x_esq, y_topo = cx - lado / 2 + zona * m, cy + lado / 2 - zona * m
    formas: list[G.Forma] = []
    for r, linha in enumerate(matriz):
        c = 0
        while c < n:
            if not linha[c]:
                c += 1
                continue
            c0 = c
            while c < n and linha[c]:
                c += 1
            x0, x1 = x_esq + c0 * m, x_esq + c * m
            y1 = y_topo - r * m
            y0 = y1 - m
            formas.append(G.Forma([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
    return formas


def escrever_qr_svg(formas: list[G.Forma], lado: float, caminho: Path, conteudo: str) -> Path:
    def tx(p):
        return p[0] + lado / 2, lado / 2 - p[1]
    d = G._svg_path_formas(formas, tx)
    svg = "\n".join([
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lado:g}mm" height="{lado:g}mm" '
        f'viewBox="0 0 {lado:g} {lado:g}" version="1.1">',
        "<title>QR Code AcessaCidade (gravação raster, mm, inclui zona de silêncio)</title>",
        f"<desc>Conteúdo: {conteudo.replace('&', '&amp;').replace('<', '&lt;')}</desc>",
        '<g id="GRAVACAO_RASTER">',
        f'<path d="{d}" fill="#000000" fill-rule="nonzero" stroke="none"/>',
        "</g>",
        "</svg>",
    ])
    caminho.write_text(svg, encoding="utf-8")
    return caminho


def escrever_qr_dxf(formas: list[G.Forma], lado: float, caminho: Path, conteudo: str) -> Path:
    doc = G._novo_dxf()
    msp = doc.modelspace()
    G._add_formas_dxf(msp, formas, "GRAVACAO_RASTER", lado / 2, lado / 2)
    msp.add_lwpolyline([(0, 0), (lado, 0), (lado, lado), (0, lado)], close=True, dxfattribs={"layer": "AREA_QR"})
    msp.add_text(f"QR AcessaCidade - {conteudo}", height=1.2,
                 dxfattribs={"layer": "TEXTO_REFERENCIA"}).set_placement((0, -3))
    doc.saveas(caminho)
    return caminho


def gerar(url: str, saida: Path = AQUI, correcao: str = "M", sem_rota: bool = False,
          permitir_local: bool = False) -> dict:
    conteudo = montar_url(validar_url(url, permitir_local), sem_rota)
    matriz = matriz_qr(conteudo, correcao)
    n = len(matriz)
    modulo = tamanho_modulo(n)
    if modulo < P.QR_MODULO_MINIMO:
        raise ErroQR(f"URL longa demais: módulo de {modulo:.2f} mm < mínimo {P.QR_MODULO_MINIMO} mm. "
                     "Use uma URL mais curta, correção 'L' ou aumente AREA_QR_LADO em parametros.py.")
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    lado = P.AREA_QR_LADO
    qx, qy = P.AREA_QR_CENTRO
    arquivos = {
        "qr_svg": escrever_qr_svg(formas_qr(matriz, 0, 0), lado, saida / "qrcode_acessacidade.svg", conteudo),
        "qr_dxf": escrever_qr_dxf(formas_qr(matriz, 0, 0), lado, saida / "qrcode_acessacidade.dxf", conteudo),
    }
    layout = G.layout_placa()
    formas_placa = formas_qr(matriz, qx, qy)
    arquivos["placa_dxf"] = G.escrever_dxf_placa(layout, saida / "placa_principal_laser_com_qr.dxf",
                                                 qr_formas=formas_placa, qr_info=f"QR: {conteudo}")
    arquivos["placa_svg"] = G.escrever_svg_placa(layout, saida / "placa_principal_laser_com_qr.svg",
                                                 qr_formas=formas_placa)
    versao = (n - 17) // 4
    info = [
        "QR Code AcessaCidade — gerado por laser-cut/gerar_qrcode.py",
        f"Data/hora local: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Conteúdo codificado: {conteudo}",
        f"Versão QR: {versao} ({n} x {n} módulos), correção de erro: {correcao}",
        f"Área total: {lado:g} x {lado:g} mm com zona de silêncio de {P.QR_ZONA_SILENCIO_MODULOS} módulos",
        f"Tamanho do módulo: {modulo:.3f} mm (mínimo configurado: {P.QR_MODULO_MINIMO} mm)",
        f"Em escala real (placa 1:1 = protótipo x {1 / P.ESCALA_PROTOTIPO:g}): módulo ≈ {modulo / P.ESCALA_PROTOTIPO:.2f} mm",
        "ANTES DE GRAVAR: abra o SVG na tela, leia com 2 celulares diferentes e confirme que abre a tela de registro.",
        "DEPOIS DE GRAVAR: leia o QR gravado na peça (luz ambiente e de lado) e registre a evidência (print/foto).",
    ]
    arquivos["info"] = saida / "qrcode_acessacidade_info.txt"
    arquivos["info"].write_text("\n".join(info) + "\n", encoding="utf-8")
    return {"conteudo": conteudo, "modulos": n, "versao": versao, "modulo_mm": modulo,
            "matriz": matriz, "arquivos": arquivos}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gera SVG/DXF do QR Code do AcessaCidade para gravação a laser.")
    ap.add_argument("--url", required=True, help="URL pública REAL do AcessaCidade (ex.: https://<seu-dominio>)")
    ap.add_argument("--saida", type=Path, default=AQUI, help="pasta de saída (padrão: laser-cut/)")
    ap.add_argument("--correcao", choices=sorted(NIVEIS_CORRECAO), default="M",
                    help="nível de correção de erro (padrão M; H tolera mais sujeira/riscos, mas exige URL curta)")
    ap.add_argument("--sem-rota", action="store_true", help=f"não acrescenta {P.ROTA_REGISTRAR_APP} à URL")
    ap.add_argument("--permitir-local", action="store_true", help="aceita localhost/IP privado (só teste de bancada)")
    args = ap.parse_args(argv)
    try:
        r = gerar(args.url, args.saida, args.correcao, args.sem_rota, args.permitir_local)
    except ErroQR as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    print(f"QR gerado para: {r['conteudo']}")
    print(f"Versão {r['versao']} ({r['modulos']}x{r['modulos']}), módulo {r['modulo_mm']:.3f} mm")
    for nome, caminho in r["arquivos"].items():
        print(f"  {nome}: {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
