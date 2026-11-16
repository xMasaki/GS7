"""Gera o PDF ÚNICO da entrega da disciplina 03 com links clicáveis.

Composição (nesta ordem):
  1. docs/DOCUMENTO_DE_ENTREGA_BI.md      (A4 retrato) — capa, links, resumo, evidências, checklist
  2. business-model/LEAN_CANVAS.html      (A4 paisagem) — Anexo A: Lean Canvas visual
  3. business-model/LEAN_CANVAS.md        (A4 retrato) — Anexo B: validação por bloco e o que mudou
  4. business-model/MODELO_DE_NEGOCIO.md  (A4 retrato) — Anexo C: modelo de negócio

Os links vêm de docs/links_entrega.yaml e substituem os marcadores
[PREENCHER: URL_VIDEO], [PREENCHER: URL_MVP] e [PREENCHER: URL_REPOSITORIO].

Uso (na raiz do repositório, Windows PowerShell):
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\scripts\\gerar_pdf_entrega.py
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\scripts\\gerar_pdf_entrega.py --estrito
      (--estrito: falha se faltar link ou se restar algum [PREENCHER])

Requer o Microsoft Edge instalado (Playwright com channel="msedge"; não é preciso "playwright install").
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import tempfile
from pathlib import Path

import markdown
import yaml
from pypdf import PdfReader, PdfWriter

PASTA = Path(__file__).resolve().parents[1]
DOC = PASTA / "docs" / "DOCUMENTO_DE_ENTREGA_BI.md"
CANVAS_HTML = PASTA / "business-model" / "LEAN_CANVAS.html"
CANVAS_MD = PASTA / "business-model" / "LEAN_CANVAS.md"
MODELO_MD = PASTA / "business-model" / "MODELO_DE_NEGOCIO.md"
LINKS = PASTA / "docs" / "links_entrega.yaml"
SAIDA_PADRAO = PASTA / "entrega" / "AcessaCidade_BI_Pitch_MVP.pdf"

MARCADORES = {
    "url_video": "[PREENCHER: URL_VIDEO]",
    "url_mvp": "[PREENCHER: URL_MVP]",
    "url_repositorio": "[PREENCHER: URL_REPOSITORIO]",
}
RE_URL = re.compile(r"^https://[^\s<>\"'\[\]]+$")
RE_LINK_RELATIVO = re.compile(r"\[([^\]]+)\]\((?!https?://|mailto:|#)([^)]+)\)")
RE_PREENCHER = re.compile(r"\[PREENCHER[^\]]*\]")

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: #1b1b1b; font-size: 10pt; line-height: 1.45; margin: 0; }
h1 { font-size: 18pt; color: #1f5fae; margin: 0 0 4mm; }
h2 { font-size: 13pt; color: #1f5fae; margin: 6mm 0 2mm; border-bottom: 0.4mm solid #c9d6ea; padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 11pt; margin: 4mm 0 1.5mm; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: 8.8pt; break-inside: auto; }
th, td { border: 0.25mm solid #9a9a96; padding: 1.2mm 1.6mm; vertical-align: top; text-align: left; }
th { background: #e8eef7; }
tr { break-inside: avoid; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.8pt; background: #f2f2f0; padding: 0 1mm; border-radius: 0.6mm; }
pre { background: #f2f2f0; padding: 2mm; font-size: 8pt; white-space: pre-wrap; }
blockquote { margin: 2mm 0; padding: 1mm 3mm; border-left: 1mm solid #b7791f; background: #fff8e6; }
a { color: #0b4fa0; text-decoration: underline; word-break: break-all; }
hr { border: 0; border-top: 0.3mm solid #c9c9c4; margin: 4mm 0; }
.anexo { break-before: page; }
.rotulo-anexo { font-size: 9pt; color: #4a4a48; text-transform: uppercase; letter-spacing: 0.4pt; margin: 0 0 1mm; }
"""


def carregar_links(caminho: Path) -> tuple[dict[str, str], list[str]]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    links, problemas = {}, []
    for chave in MARCADORES:
        valor = str(dados.get(chave) or "").strip()
        if not valor:
            problemas.append(f"{chave}: vazio em {caminho.name}")
        elif not RE_URL.match(valor):
            problemas.append(f"{chave}: '{valor}' não parece uma URL https:// válida")
        else:
            links[chave] = valor
    return links, problemas


def aplicar_links(texto: str, links: dict[str, str]) -> str:
    for chave, marcador in MARCADORES.items():
        if chave in links:
            url = links[chave]
            texto = texto.replace(marcador, f"[{url}]({url})")
    return texto


def preparar_markdown(texto: str, links: dict[str, str]) -> str:
    texto = aplicar_links(texto, links)
    # links relativos do repositório não funcionam no PDF: viram texto com o caminho
    texto = RE_LINK_RELATIVO.sub(lambda m: f"{m.group(1)} (`{m.group(2)}`)", texto)
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return texto


def md_para_html(partes: list[tuple[str | None, str]], titulo: str) -> str:
    corpo = []
    for rotulo, texto in partes:
        conteudo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
        if rotulo:
            corpo.append(f'<section class="anexo"><p class="rotulo-anexo">{html.escape(rotulo)}</p>{conteudo}</section>')
        else:
            corpo.append(f"<section>{conteudo}</section>")
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
            f"<style>{CSS}</style></head><body>{''.join(corpo)}</body></html>")


RODAPE = ('<div style="font-size:7pt;color:#666;width:100%;padding:0 15mm;display:flex;justify-content:space-between;">'
          '<span>AcessaCidade — Pitch de Negócio + MVP · FIAP GS 2026.2</span>'
          '<span>página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>')


def renderizar(html_docs: list[tuple[Path, Path, bool]]) -> None:
    """html_docs: (html de entrada, pdf de saída, usa_tamanho_da_pagina_css)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge", headless=True)
        try:
            pagina = navegador.new_page()
            for entrada, saida, css_page in html_docs:
                pagina.goto(entrada.resolve().as_uri())
                pagina.emulate_media(media="print")
                if css_page:
                    pagina.pdf(path=str(saida), prefer_css_page_size=True, print_background=True)
                else:
                    pagina.pdf(path=str(saida), format="A4", print_background=True, display_header_footer=True,
                               header_template="<span></span>", footer_template=RODAPE,
                               margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        finally:
            navegador.close()


def links_do_pdf(caminho: Path) -> list[str]:
    encontrados = []
    for pagina in PdfReader(str(caminho)).pages:
        for anotacao in pagina.get("/Annots") or []:
            obj = anotacao.get_object()
            acao = obj.get("/A")
            if acao and acao.get("/URI"):
                encontrados.append(str(acao["/URI"]))
    return encontrados


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--links", type=Path, default=LINKS)
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    ap.add_argument("--estrito", action="store_true", help="falha se faltar link ou restar [PREENCHER]")
    args = ap.parse_args(argv)

    for arquivo in (DOC, CANVAS_HTML, CANVAS_MD, MODELO_MD, args.links):
        if not arquivo.is_file():
            print(f"ERRO: arquivo não encontrado: {arquivo}", file=sys.stderr)
            return 2
    links, problemas_links = carregar_links(args.links)

    doc = preparar_markdown(DOC.read_text(encoding="utf-8"), links)
    anexo_b = preparar_markdown(CANVAS_MD.read_text(encoding="utf-8"), links)
    anexo_c = preparar_markdown(MODELO_MD.read_text(encoding="utf-8"), links)
    pendencias = {nome: len(RE_PREENCHER.findall(txt)) for nome, txt in
                  (("DOCUMENTO_DE_ENTREGA_BI.md", doc), ("LEAN_CANVAS (HTML/MD)", anexo_b), ("MODELO_DE_NEGOCIO.md", anexo_c))}

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="acessacidade_pdf_") as tmp:
        t = Path(tmp)
        (t / "1_doc.html").write_text(md_para_html([(None, doc)], "Documento de entrega"), encoding="utf-8")
        (t / "3_anexos.html").write_text(md_para_html([
            ("Anexo B — Lean Canvas consolidado (validação por bloco)", anexo_b),
            ("Anexo C — Modelo de negócio", anexo_c),
        ], "Anexos"), encoding="utf-8")
        renderizar([
            (t / "1_doc.html", t / "1_doc.pdf", False),
            (CANVAS_HTML, t / "2_canvas.pdf", True),
            (t / "3_anexos.html", t / "3_anexos.pdf", False),
        ])
        escritor = PdfWriter()
        for nome in ("1_doc.pdf", "2_canvas.pdf", "3_anexos.pdf"):
            escritor.append(str(t / nome))
        escritor.add_metadata({"/Title": "AcessaCidade — Pitch de Negócio + MVP CitizenTech",
                               "/Subject": "FIAP Global Solution 2026.2 — Business Intelligence & Startup Development"})
        with args.saida.open("wb") as f:
            escritor.write(f)

    total_paginas = len(PdfReader(str(args.saida)).pages)
    urls = links_do_pdf(args.saida)
    print(f"PDF gerado: {args.saida} ({total_paginas} páginas)")
    print(f"Links clicáveis no PDF: {len(urls)}")
    for chave in MARCADORES:
        if chave in links:
            print(f"  {chave}: {links[chave]} -> {'OK (clicável)' if links[chave] in urls else 'NÃO encontrado como link'}")
    for p in problemas_links:
        print(f"  PENDENTE: {p}")
    for nome, qtd in pendencias.items():
        if qtd:
            print(f"  PENDENTE: {qtd} marcador(es) [PREENCHER] em {nome}")
    if args.estrito and (problemas_links or any(pendencias.values())):
        print("Modo estrito: há pendências — NÃO envie este PDF ainda.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
