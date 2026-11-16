"""Converte um documento Markdown do repositório em PDF (Markdown + Mermaid -> HTML -> Microsoft Edge headless).

Gerador GENÉRICO, usado pelas disciplinas que não têm gerador próprio (06 e 07) e por tools/gerar_todos_pdfs.ps1.

- Tabelas, blocos de código e listas: extensão `markdown` (tables, fenced_code, sane_lists, toc).
- Blocos ```mermaid são desenhados no navegador pelo Mermaid (CDN jsDelivr, versão fixa) antes de imprimir.
  Exige internet no momento da geração; sem internet, use --sem-mermaid (o código do diagrama sai como texto).
- Links https:// continuam clicáveis no PDF.
- Links RELATIVOS do repositório (ex.: `[x](../terraform/main.tf)`) viram links clicáveis para o GitHub
  ({repo}/blob/{ramo}/caminho) quando --repo-url for informado; sem --repo-url, viram texto com o caminho
  (um PDF entregue ao professor não consegue abrir arquivos locais).
- Imagens com caminho relativo são embutidas no PDF.
- Marcadores [PREENCHER...] restantes são contados e avisados; --estrito faz o script falhar se houver algum.

Uso (na raiz do repositório, PowerShell):
    .\\.venv\\Scripts\\python.exe tools\\gerar_pdf_markdown.py 06-Secure-DevOps-Cloud\\docs\\RELATORIO_ENTREGA_DEVOPS.md `
        --saida entregas\\pdf\\AcessaCidade_06_DevOps.pdf --titulo "AcessaCidade — Secure DevOps"
    (opcional) --repo-url https://github.com/<conta>/<repositorio> --ramo main --estrito

Requer o Microsoft Edge instalado (Playwright com channel="msedge"; não é preciso "playwright install").
Sem Playwright, tenta o Edge/Chrome diretamente com --headless --print-to-pdf.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

import markdown

RAIZ = Path(__file__).resolve().parents[1]
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
RE_URL_REPO = re.compile(r"^https://[^\s<>\"'\[\]]+$")
RE_LINK_RELATIVO = re.compile(r"(?<!!)\[([^\]]+)\]\((?!https?://|mailto:|#)([^)\s]+)\)")
RE_PREENCHER = re.compile(r"\[PREENCHER[^\]]*\]")
RE_SRC_RELATIVO = re.compile(r'src="(?!https?:|data:|file:)([^"]+)"')
RE_MERMAID = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)

CANDIDATOS_NAVEGADOR = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

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
tr, img, figure, pre.mermaid { break-inside: avoid; }
img { max-width: 100%; max-height: 120mm; display: block; margin: 2mm auto; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.6pt; background: #f2f2f0; padding: 0 1mm; }
pre { background: #f2f2f0; padding: 2mm; font-size: 8pt; white-space: pre-wrap; break-inside: avoid; }
pre.mermaid { background: none; text-align: center; }
blockquote { margin: 2mm 0; padding: 1mm 3mm; border-left: 1mm solid #b7791f; background: #fff8e6; }
a { color: #0b4fa0; text-decoration: underline; word-break: break-all; }
"""


def preparar_markdown(texto: str, base: Path, repo: str | None, ramo: str) -> tuple[str, list[str]]:
    """Remove comentários HTML e converte links relativos (GitHub se houver --repo-url; senão, texto)."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    sem_link: list[str] = []

    def _relativo(m: re.Match[str]) -> str:
        rotulo, alvo = m.group(1), m.group(2)
        caminho, _, ancora = alvo.partition("#")
        destino = (base / caminho).resolve()
        try:
            rel = destino.relative_to(RAIZ).as_posix()
        except ValueError:
            return f"{rotulo} (`{alvo}`)"
        if not repo:
            sem_link.append(rel)
            return f"{rotulo} (`{rel}`)"
        tipo = "tree" if destino.is_dir() else "blob"
        sufixo = f"#{ancora}" if ancora else ""
        return f"[{rotulo}]({repo}/{tipo}/{ramo}/{quote(rel)}{sufixo})"

    return RE_LINK_RELATIVO.sub(_relativo, texto), sem_link


def md_para_html(texto: str, base: Path, titulo: str, mermaid: bool) -> str:
    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
    corpo = RE_SRC_RELATIVO.sub(lambda m: f'src="{(base / m.group(1)).resolve().as_uri()}"', corpo)
    tem_mermaid = bool(RE_MERMAID.search(corpo))
    script = ""
    if mermaid and tem_mermaid:
        corpo = RE_MERMAID.sub(lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', corpo)
        script = (f'<script src="{MERMAID_CDN}"></script>'
                  "<script>mermaid.initialize({startOnLoad:false,theme:'neutral',flowchart:{htmlLabels:true}});"
                  "mermaid.run().then(()=>{document.body.dataset.pronto='1';})"
                  ".catch(e=>{document.body.dataset.pronto='erro';document.body.dataset.erro=String(e);});</script>")
    else:
        script = "<script>document.body.dataset.pronto='1';</script>"
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
            f"<style>{CSS}</style></head><body>{corpo}{script}</body></html>")


def _rodape(texto: str) -> str:
    return ('<div style="font-size:7pt;color:#666;width:100%;padding:0 15mm;display:flex;justify-content:space-between;">'
            f'<span>{html.escape(texto)}</span>'
            '<span>página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>')


def renderizar_playwright(entrada: Path, saida: Path, rodape: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge", headless=True)
        try:
            pagina = navegador.new_page()
            pagina.goto(entrada.resolve().as_uri())
            pagina.wait_for_function("document.body && document.body.dataset.pronto", timeout=60000)
            estado = pagina.evaluate("document.body.dataset.pronto")
            if estado == "erro":
                raise RuntimeError("Mermaid falhou: " + str(pagina.evaluate("document.body.dataset.erro")))
            pagina.pdf(path=str(saida), format="A4", print_background=True, display_header_footer=True,
                       header_template="<span></span>", footer_template=_rodape(rodape),
                       margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        finally:
            navegador.close()


def renderizar_cli(entrada: Path, saida: Path, navegador: str | None) -> None:
    exe = navegador or next((c for c in CANDIDATOS_NAVEGADOR if Path(c).exists()), None) \
        or shutil.which("msedge") or shutil.which("chrome")
    if not exe:
        raise RuntimeError("Edge/Chrome não encontrado. Informe --navegador ou abra o HTML e use Imprimir > Salvar como PDF.")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as perfil:
        cmd = [exe, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
               f"--user-data-dir={perfil}", f"--print-to-pdf={saida.resolve()}", entrada.resolve().as_uri()]
        # Ferramenta LOCAL de documentação: lista de argumentos (sem shell=True); o executável é o navegador
        # instalado ou o informado pelo próprio usuário em --navegador.
        subprocess.run(cmd, capture_output=True, text=True, timeout=180)  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", type=Path, help="arquivo .md de origem")
    ap.add_argument("--saida", type=Path, required=True, help="arquivo .pdf de destino")
    ap.add_argument("--titulo", default=None, help="título do documento (padrão: nome do arquivo)")
    ap.add_argument("--rodape", default="AcessaCidade · FIAP Global Solution 2026.2 · CitizenTech (ODS 11)")
    ap.add_argument("--repo-url", default=None, help="URL https:// do repositório público (para links relativos)")
    ap.add_argument("--ramo", default="main")
    ap.add_argument("--sem-mermaid", action="store_true", help="não desenhar diagramas (sem internet)")
    ap.add_argument("--navegador", default=None, help="caminho do Edge/Chrome (só no modo sem Playwright)")
    ap.add_argument("--estrito", action="store_true", help="falha se restar [PREENCHER] ou link relativo sem --repo-url")
    args = ap.parse_args(argv)

    entrada = args.entrada.resolve()
    if not entrada.is_file():
        print(f"ERRO: arquivo não encontrado: {args.entrada}")
        return 2
    repo = (args.repo_url or "").strip().rstrip("/") or None
    if repo and not RE_URL_REPO.match(repo):
        print(f"ERRO: --repo-url '{repo}' não parece uma URL https:// válida.")
        return 2

    texto = entrada.read_text(encoding="utf-8")
    texto, sem_link = preparar_markdown(texto, entrada.parent, repo, args.ramo)
    pendentes = RE_PREENCHER.findall(texto)
    if pendentes:
        print(f"AVISO: {len(pendentes)} marcador(es) [PREENCHER] em {entrada.name} — complete antes da entrega final.")
    if sem_link:
        print(f"AVISO: {len(sem_link)} link(s) relativo(s) viraram texto (informe --repo-url para torná-los clicáveis).")
    if args.estrito and (pendentes or sem_link):
        print("ERRO (--estrito): ainda há [PREENCHER] ou links relativos sem --repo-url. PDF não gerado.")
        return 1

    titulo = args.titulo or entrada.stem
    saida = args.saida.resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        html_tmp = Path(tmp) / "documento.html"
        html_tmp.write_text(md_para_html(texto, entrada.parent, titulo, not args.sem_mermaid), encoding="utf-8")
        try:
            renderizar_playwright(html_tmp, saida, args.rodape)
        except ImportError:
            print("AVISO: Playwright não instalado; usando o navegador em linha de comando (--print-to-pdf).")
            renderizar_cli(html_tmp, saida, args.navegador)

    if not saida.exists() or saida.stat().st_size == 0:
        print("ERRO: o PDF não foi gerado.")
        return 1
    try:
        from pypdf import PdfReader

        leitor = PdfReader(str(saida))
        paginas = len(leitor.pages)
        caracteres = sum(len(p.extract_text() or "") for p in leitor.pages)
        if paginas == 0 or caracteres == 0:
            print(f"ERRO: PDF sem conteúdo ({paginas} página(s), {caracteres} caracteres).")
            return 1
        print(f"PDF gerado: {saida} ({paginas} página(s), {saida.stat().st_size} bytes)")
    except ImportError:
        print(f"PDF gerado: {saida} ({saida.stat().st_size} bytes; pypdf ausente, conteúdo não conferido)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
