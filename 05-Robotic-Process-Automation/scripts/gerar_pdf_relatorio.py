"""Converte docs/RELATORIO_RPA.md em PDF (HTML intermediário + Microsoft Edge/Chrome headless).

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe 05-Robotic-Process-Automation\\scripts\\gerar_pdf_relatorio.py
    [--saida caminho.pdf] [--navegador "C:\\...\\msedge.exe"]

Gere o PDF DEPOIS de preencher os campos [PREENCHER: ...] e de colocar os prints em
05-Robotic-Process-Automation/evidencias/. Imagens referenciadas no Markdown com caminho relativo
(ex.: ![E1](../evidencias/E1_assessment.png)) são resolvidas a partir da pasta docs/.
O script avisa se ainda houver [PREENCHER] no texto.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parents[1]
ORIGEM = BASE / "docs" / "RELATORIO_RPA.md"
SAIDA_PADRAO = BASE / "entrega" / "RELATORIO_RPA_AcessaCidade.pdf"

CANDIDATOS_NAVEGADOR = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

CSS = """
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #1a1a1a; margin: 0 8mm; }
h1 { color: #1F4E79; font-size: 20pt; border-bottom: 2px solid #1F4E79; padding-bottom: 4px; }
h2 { color: #1F4E79; font-size: 15pt; margin-top: 18pt; page-break-after: avoid; }
h3 { font-size: 12.5pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #bfbfbf; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #DDEBF7; }
blockquote { border-left: 4px solid #FFC000; background: #FFF8E1; margin: 6pt 0; padding: 4pt 8pt; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f3f3f3; padding: 0 2px; }
img { max-width: 100%; border: 1px solid #ccc; }
"""


def encontrar_navegador(informado: str | None) -> str | None:
    if informado:
        return informado if Path(informado).exists() else None
    for c in CANDIDATOS_NAVEGADOR:
        if Path(c).exists():
            return c
    return shutil.which("msedge") or shutil.which("chrome")


def gerar_html(md_texto: str) -> str:
    corpo = markdown.markdown(md_texto, extensions=["tables", "fenced_code", "sane_lists"])
    base_href = (BASE / "docs").as_uri() + "/"
    return (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><base href='{base_href}'>"
            f"<title>AcessaCidade - Relatório RPA</title><style>{CSS}</style></head><body>{corpo}</body></html>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    ap.add_argument("--navegador")
    args = ap.parse_args()

    texto = ORIGEM.read_text(encoding="utf-8")
    pendentes = texto.count("[PREENCHER")
    if pendentes:
        print(f"AVISO: o relatório ainda tem {pendentes} marcador(es) [PREENCHER]. Complete antes da entrega.")

    navegador = encontrar_navegador(args.navegador)
    if not navegador:
        print("ERRO: Edge/Chrome não encontrado. Informe --navegador ou abra o HTML e use 'Imprimir > Salvar como PDF'.")
        return 2

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        html = Path(tmp) / "relatorio.html"
        html.write_text(gerar_html(texto), encoding="utf-8")
        cmd = [navegador, "--headless", "--disable-gpu", "--no-pdf-header-footer",
               f"--user-data-dir={Path(tmp) / 'perfil'}",
               f"--print-to-pdf={args.saida.resolve()}", html.as_uri()]
        # Ferramenta LOCAL de documentação: lista de argumentos (sem shell=True) e executável escolhido
        # pelo próprio usuário (--navegador/variável de ambiente) para converter o HTML em PDF.
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args
    if not args.saida.exists() or args.saida.stat().st_size == 0:
        print("ERRO: o navegador não gerou o PDF.", res.stderr[-500:] if res.stderr else "")
        return 1
    print(f"PDF gerado: {args.saida} ({args.saida.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
