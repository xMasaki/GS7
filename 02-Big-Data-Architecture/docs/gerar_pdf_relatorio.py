"""Gera o PDF único da entrega (relatório + dicionário de dados) a partir dos Markdown.

Junta docs/RELATORIO_ENTREGA_BIGDATA.md + docs/DICIONARIO_DE_DADOS.md, converte para HTML (biblioteca
`markdown`), desenha os diagramas Mermaid e imprime em PDF com o Microsoft Edge via Playwright.

Uso (na raiz do repositório, com o .venv):
    .\.venv\Scripts\python.exe 02-Big-Data-Architecture/docs/gerar_pdf_relatorio.py [--saida arquivo.pdf]

Requisitos: pacotes `markdown` e `playwright` (já no requirements-dev.txt), Microsoft Edge instalado e acesso à
internet para baixar o Mermaid do CDN jsDelivr na hora da geração. Antes de gerar a versão final, substitua todos
os marcadores [PREENCHER: ...] do relatório — o script avisa quantos restam.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

DOCS = Path(__file__).resolve().parent
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

CSS = """
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; color: #1b1b1b; line-height: 1.4; }
h1 { font-size: 20pt; border-bottom: 3px solid #0b5cad; padding-bottom: 4px; }
h2 { font-size: 14pt; color: #0b5cad; margin-top: 18px; page-break-after: avoid; }
h3 { font-size: 12pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #b8c2cc; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #e8f0f8; }
tr { page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 8.5pt; background: #f2f4f6; padding: 0 2px; }
pre.mermaid { text-align: center; background: none; page-break-inside: avoid; }
.quebra { page-break-before: always; }
"""


def _md_para_html(texto: str) -> str:
    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code"])
    # ```mermaid -> <pre class="mermaid"> (o Mermaid desenha no navegador)
    return re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                  lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', corpo, flags=re.S)


def montar_html() -> tuple[str, int]:
    relatorio = (DOCS / "RELATORIO_ENTREGA_BIGDATA.md").read_text(encoding="utf-8")
    dicionario = (DOCS / "DICIONARIO_DE_DADOS.md").read_text(encoding="utf-8")
    pendentes = len(re.findall(r"\[PREENCHER", relatorio))
    corpo = _md_para_html(relatorio) + '<div class="quebra"></div>' + _md_para_html(dicionario)
    pagina = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{html.escape('AcessaCidade — Pipeline de Dados')}</title><style>{CSS}</style>
<script src="{MERMAID_CDN}"></script></head><body>{corpo}
<script>mermaid.initialize({{startOnLoad: false, theme: 'neutral', flowchart: {{htmlLabels: true}}}});
mermaid.run().then(() => {{ document.body.dataset.pronto = '1'; }})
  .catch(e => {{ document.body.dataset.pronto = 'erro:' + e; }});</script></body></html>"""
    return pagina, pendentes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", default=str(DOCS / "RELATORIO_ENTREGA_BIGDATA.pdf"))
    args = parser.parse_args(argv)
    pagina, pendentes = montar_html()
    html_tmp = Path(args.saida).with_suffix(".html")
    html_tmp.write_text(pagina, encoding="utf-8")
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge", headless=True)
        aba = navegador.new_page()
        aba.goto(html_tmp.resolve().as_uri())
        aba.wait_for_function("document.body.dataset.pronto !== undefined", timeout=60000)
        estado = aba.evaluate("document.body.dataset.pronto")
        if estado != "1":
            print(f"ERRO ao desenhar os diagramas Mermaid: {estado}")
            navegador.close()
            return 1
        diagramas = aba.evaluate("document.querySelectorAll('pre.mermaid svg').length")
        aba.pdf(path=args.saida, format="A4", print_background=True,
                margin={"top": "15mm", "bottom": "15mm", "left": "14mm", "right": "14mm"})
        navegador.close()
    html_tmp.unlink(missing_ok=True)
    print(f"PDF gerado: {args.saida} | diagramas desenhados: {diagramas}")
    if pendentes:
        print(f"ATENÇÃO: ainda há {pendentes} marcador(es) [PREENCHER] no relatório — substitua antes da entrega.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
