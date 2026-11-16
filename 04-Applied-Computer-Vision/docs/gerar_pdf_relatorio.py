"""Gera o PDF de entrega da disciplina 04 a partir de docs/RELATORIO_ENTREGA_VISAO.md.

- Os links vêm de docs/links_entrega.yaml e substituem os marcadores [PREENCHER: URL_VIDEO],
  [PREENCHER: URL_MVP] e [PREENCHER: URL_REPOSITORIO] (inclusive com sufixo, ex.: .../#/analise).
- Links relativos do repositório (ex.: `[x](../results/...)`) viram links clicáveis para o GitHub
  ({url_repositorio}/blob/{ramo}/...) quando url_repositorio estiver preenchido.
- Imagens com caminho relativo são embutidas no PDF.

Uso (na raiz do repositório, PowerShell):
    .\\.venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\docs\\gerar_pdf_relatorio.py
    .\\.venv\\Scripts\\python.exe 04-Applied-Computer-Vision\\docs\\gerar_pdf_relatorio.py --estrito
      (--estrito: falha se faltar link ou se restar algum [PREENCHER])

Requer o Microsoft Edge (Playwright com channel="msedge"; não é preciso "playwright install").
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml
from pypdf import PdfReader

DOCS = Path(__file__).resolve().parent
RAIZ = DOCS.parents[1]
DOC = DOCS / "RELATORIO_ENTREGA_VISAO.md"
LINKS = DOCS / "links_entrega.yaml"
SAIDA_PADRAO = DOCS / "entrega" / "AcessaCidade_Visao_Computacional.pdf"
TITULO = "AcessaCidade — Pitch Visão Computacional (Applied Computer Vision)"
RODAPE_TEXTO = "AcessaCidade · Applied Computer Vision · FIAP GS 2026.2"

MARCADORES = {
    "url_video": "[PREENCHER: URL_VIDEO]",
    "url_mvp": "[PREENCHER: URL_MVP]",
    "url_repositorio": "[PREENCHER: URL_REPOSITORIO]",
}
RE_URL = re.compile(r"^https://[^\s<>\"'\[\]]+$")
RE_LINK_RELATIVO = re.compile(r"(?<!!)\[([^\]]+)\]\((?!https?://|mailto:|#)([^)\s]+)\)")
RE_PREENCHER = re.compile(r"\[PREENCHER[^\]]*\]")
RE_SRC_RELATIVO = re.compile(r'src="(?!https?:|data:|file:)([^"]+)"')

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; color: #1b1b1b; font-size: 10pt; line-height: 1.45; margin: 0; }
h1 { font-size: 18pt; color: #1f5fae; margin: 0 0 4mm; }
h2 { font-size: 13pt; color: #1f5fae; margin: 6mm 0 2mm; border-bottom: 0.4mm solid #c9d6ea; padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 11pt; margin: 4mm 0 1.5mm; break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: 8.6pt; }
th, td { border: 0.25mm solid #9a9a96; padding: 1.2mm 1.6mm; vertical-align: top; text-align: left; }
th { background: #e8eef7; }
tr, img, figure { break-inside: avoid; }
img { max-width: 100%; max-height: 95mm; display: block; margin: 2mm auto; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.6pt; background: #f2f2f0; padding: 0 1mm; }
pre { background: #f2f2f0; padding: 2mm; font-size: 8pt; white-space: pre-wrap; break-inside: avoid; }
blockquote { margin: 2mm 0; padding: 1mm 3mm; border-left: 1mm solid #b7791f; background: #fff8e6; }
a { color: #0b4fa0; text-decoration: underline; word-break: break-all; }
"""


def carregar_links(caminho: Path) -> tuple[dict[str, str], str, list[str]]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
    dados = dados or {}
    links, problemas = {}, []
    for chave in MARCADORES:
        valor = str(dados.get(chave) or "").strip().rstrip("/")
        if not valor:
            problemas.append(f"{chave}: vazio em {caminho.name}")
        elif not RE_URL.match(valor):
            problemas.append(f"{chave}: '{valor}' não parece uma URL https:// válida")
        else:
            links[chave] = valor
    ramo = str(dados.get("ramo") or "main").strip()
    return links, ramo, problemas


def preparar_markdown(texto: str, links: dict[str, str], ramo: str, base: Path) -> tuple[str, list[str]]:
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    for chave, marcador in MARCADORES.items():
        if chave in links:
            texto = re.sub(re.escape(marcador) + r"([^\s|)<>]*)", lambda m, u=links[chave]: f"<{u}{m.group(1)}>", texto)
    sem_link: list[str] = []

    def _relativo(m: re.Match[str]) -> str:
        rotulo, alvo = m.group(1), m.group(2)
        destino = (base / alvo.split("#")[0]).resolve()
        try:
            rel = destino.relative_to(RAIZ).as_posix()
        except ValueError:
            return f"{rotulo} (`{alvo}`)"
        repo = links.get("url_repositorio")
        if not repo:
            sem_link.append(rel)
            return f"{rotulo} (`{rel}`)"
        tipo = "tree" if destino.is_dir() else "blob"
        return f"[{rotulo}]({repo}/{tipo}/{ramo}/{quote(rel)})"

    return RE_LINK_RELATIVO.sub(_relativo, texto), sem_link


def md_para_html(texto: str, base: Path) -> str:
    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
    corpo = RE_SRC_RELATIVO.sub(lambda m: f'src="{(base / m.group(1)).resolve().as_uri()}"', corpo)
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(TITULO)}</title>'
            f"<style>{CSS}</style></head><body>{corpo}</body></html>")


def renderizar(entrada: Path, saida: Path) -> None:
    from playwright.sync_api import sync_playwright

    rodape = ('<div style="font-size:7pt;color:#666;width:100%;padding:0 15mm;display:flex;justify-content:space-between;">'
              f'<span>{html.escape(RODAPE_TEXTO)}</span>'
              '<span>página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>')
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge", headless=True)
        try:
            pagina = navegador.new_page()
            pagina.goto(entrada.resolve().as_uri())
            pagina.wait_for_load_state("load")
            pagina.pdf(path=str(saida), format="A4", print_background=True, display_header_footer=True,
                       header_template="<span></span>", footer_template=rodape,
                       margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        finally:
            navegador.close()


def links_do_pdf(caminho: Path) -> list[str]:
    encontrados = []
    for pagina in PdfReader(str(caminho)).pages:
        for anotacao in pagina.get("/Annots") or []:
            acao = anotacao.get_object().get("/A")
            if acao and acao.get("/URI"):
                encontrados.append(str(acao["/URI"]))
    return encontrados


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--links", type=Path, default=LINKS)
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    ap.add_argument("--estrito", action="store_true", help="falha se faltar link ou restar [PREENCHER]")
    args = ap.parse_args(argv)

    links, ramo, problemas = carregar_links(args.links)
    texto, sem_link = preparar_markdown(DOC.read_text(encoding="utf-8"), links, ramo, DOC.parent)
    pendentes = sorted(set(RE_PREENCHER.findall(texto)))
    for p in problemas:
        print(f"[aviso] link: {p}")
    if sem_link:
        print(f"[aviso] {len(sem_link)} caminho(s) do repositório ficaram como texto (preencha url_repositorio).")
    if pendentes:
        print(f"[aviso] {len(pendentes)} marcador(es) [PREENCHER] distintos ainda no documento.")
    if args.estrito and (problemas or pendentes):
        print("[erro] modo estrito: preencha os links e os [PREENCHER] antes de gerar o PDF final.")
        return 2

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        entrada = Path(tmp) / "relatorio.html"
        entrada.write_text(md_para_html(texto, DOC.parent), encoding="utf-8")
        renderizar(entrada, args.saida)
    n_paginas = len(PdfReader(str(args.saida)).pages)
    clicaveis = links_do_pdf(args.saida)
    print(f"PDF gerado: {args.saida} ({n_paginas} página(s), {len(clicaveis)} link(s) clicável(is))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
