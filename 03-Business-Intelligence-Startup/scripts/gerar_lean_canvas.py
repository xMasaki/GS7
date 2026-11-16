"""Gera o Lean Canvas do AcessaCidade em três formatos a partir de uma única fonte.

Fonte única:  03-Business-Intelligence-Startup/business-model/lean_canvas.json
Saídas:       business-model/LEAN_CANVAS.md    (documento consolidado com status de validação)
              business-model/LEAN_CANVAS.html  (visual imprimível em A4 paisagem, sem dependências externas)
              business-model/LEAN_CANVAS.xlsx  (planilha com o canvas e a tabela de validação)

Uso (na raiz do repositório):
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\scripts\\gerar_lean_canvas.py

Para atualizar o canvas, edite SOMENTE o JSON e rode o script de novo.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PASTA_DISCIPLINA = Path(__file__).resolve().parents[1]
PASTA_MODELO = PASTA_DISCIPLINA / "business-model"
ORDEM = [
    "problema", "segmentos", "proposta_valor", "solucao", "canais",
    "receitas", "custos", "metricas", "vantagem_injusta",
]

# Posição de cada bloco no layout clássico do Lean Canvas (grade de 10 colunas x 3 linhas)
LAYOUT = {
    "problema": "1 / 1 / 3 / 3",
    "solucao": "1 / 3 / 2 / 5",
    "metricas": "2 / 3 / 3 / 5",
    "proposta_valor": "1 / 5 / 3 / 7",
    "vantagem_injusta": "1 / 7 / 2 / 9",
    "canais": "2 / 7 / 3 / 9",
    "segmentos": "1 / 9 / 3 / 11",
    "custos": "3 / 1 / 4 / 6",
    "receitas": "3 / 6 / 4 / 11",
}

COERENCIA = [
    ("Problema → Segmentos", "Cada dor do bloco Problema tem um dono: a dor de deslocamento é do usuário (cidadão), a dor de triagem e priorização é do pagante (quem precisa resolver)."),
    ("Segmentos → Proposta de valor", "A proposta tem duas metades: rapidez e transparência para o cidadão; denúncias padronizadas e priorizáveis para o pagante."),
    ("Proposta de valor → Solução", "Cada promessa corresponde a uma funcionalidade que existe no MVP: formulário + protocolo, triagem explicável com revisão humana, consulta, assistente e painel."),
    ("Solução → Métricas-chave", "As métricas medem o que a solução promete: tempo para registrar, % de fotos analisadas, % revisadas por humano, tempo até encaminhamento."),
    ("Segmentos → Canais", "Usuários chegam por associações e divulgação local; pagantes por chamamentos públicos, inovação aberta e venda consultiva."),
    ("Segmentos → Receitas", "Somente organizações pagam; o cidadão nunca paga. Preço por faixa de população (municípios) ou por área/volume (B2B)."),
    ("Solução → Custos", "Os custos seguem a arquitetura real do MVP: container em nuvem, armazenamento de fotos, LLM por uso (com modo por regras) e equipe."),
    ("Receitas × Custos", "O ponto de equilíbrio com premissas declaradas está em MODELO_DE_NEGOCIO.md (seção \"A conta fecha\")."),
    ("Vantagem injusta", "Declarada como inexistente hoje; o que pode virar vantagem (base de dados e comunidade) depende de uso real."),
]


def carregar(caminho: Path) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    ids = {b["id"] for b in dados["blocos"]}
    faltando = set(ORDEM) - ids
    if faltando:
        raise SystemExit(f"lean_canvas.json incompleto: faltam os blocos {sorted(faltando)}")
    for bloco in dados["blocos"]:
        if not bloco.get("itens"):
            raise SystemExit(f"O bloco '{bloco['id']}' está sem itens.")
        if not bloco.get("status"):
            raise SystemExit(f"O bloco '{bloco['id']}' está sem status de validação.")
    return dados


def blocos_ordenados(dados: dict) -> list[dict]:
    por_id = {b["id"]: b for b in dados["blocos"]}
    return [por_id[i] for i in ORDEM]


# ----------------------------------------------------------------- Markdown
def gerar_md(dados: dict) -> str:
    linhas: list[str] = []
    a = linhas.append
    a(f"# Lean Canvas consolidado — {dados['produto']}")
    a("")
    a(f"> {dados['subtitulo']}.  ")
    a(f"> Versão: {dados['versao']} · Referência: {dados['data_referencia']} · Equipe: {dados['equipe']}")
    a("")
    a("<!-- ARQUIVO GERADO por scripts/gerar_lean_canvas.py a partir de lean_canvas.json. Edite o JSON, não este arquivo. -->")
    a("")
    a("**Como ler:** cada bloco traz o conteúdo atual e o **status de validação**. Nada aqui foi declarado como validado "
      "sem evidência: enquanto a equipe não preencher o campo de validação com o que foi confirmado no CP1, nas entrevistas "
      "e nos testes com usuários, o bloco permanece como **HIPÓTESE (não validada)**.")
    a("")
    a("Versão visual para impressão (A4 paisagem): [LEAN_CANVAS.html](LEAN_CANVAS.html) · Planilha: [LEAN_CANVAS.xlsx](LEAN_CANVAS.xlsx)")
    a("")
    a("## Quadro-resumo de validação")
    a("")
    a("| Bloco | Status | Validação no CP1 / entrevistas / testes — e o que mudou |")
    a("|---|---|---|")
    for b in blocos_ordenados(dados):
        a(f"| {b['titulo']} | {b['status']} | {b['validacao']} |")
    a("")
    for b in blocos_ordenados(dados):
        a(f"## {b['titulo']}")
        a("")
        a(f"**Status:** {b['status']}  ")
        a(f"**Validação:** {b['validacao']}")
        a("")
        for item in b["itens"]:
            a(f"- {item}")
        if b.get("secundario_titulo"):
            a("")
            a(f"**{b['secundario_titulo']}:**")
            a("")
            for item in b["secundario_itens"]:
                a(f"- {item}")
        a("")
    a("## Coerência entre os blocos")
    a("")
    a("| Ligação | Como os blocos se sustentam |")
    a("|---|---|")
    for ligacao, texto in COERENCIA:
        a(f"| {ligacao} | {texto} |")
    a("")
    a("## O que mudou desde o CP1 (preencher com fatos)")
    a("")
    a("| Momento | Hipótese anterior | Evidência obtida | Decisão / o que mudou |")
    a("|---|---|---|---|")
    a("| CP1 | [PREENCHER: hipótese do primeiro canvas] | [PREENCHER: evidência real] | [PREENCHER: decisão] |")
    a("| Entrevistas | [PREENCHER] | [PREENCHER: nº de entrevistas, perfis — sem nomes] | [PREENCHER] |")
    a("| Protótipo / MVP 0 | [PREENCHER] | [PREENCHER] | [PREENCHER] |")
    a("| MVP 1 / GS | [PREENCHER] | [PREENCHER: teste de usabilidade registrado em pitch/registro_testes_usuarios_TEMPLATE.xlsx] | [PREENCHER] |")
    a("")
    a("> Regra da equipe: quando um bloco for confirmado por evidência, troque o `status` no JSON por "
      "\"VALIDADA PARCIALMENTE\" ou \"VALIDADA\" e descreva a evidência em `validacao` (quantas pessoas, como, quando). "
      "Nunca marcar como validado sem a evidência guardada em `03-Business-Intelligence-Startup/pitch/evidencias/`.")
    a("")
    a(f"_{dados['nota_rodape']}_")
    a("")
    return "\n".join(linhas)


# --------------------------------------------------------------------- HTML
CSS = """
@page { size: A4 landscape; margin: 7mm; }
* { box-sizing: border-box; }
:root { --tinta: #1b1b1b; --tinta-2: #4a4a48; --linha: #2b2b2b; --fundo: #ffffff;
        --destaque: #1f5fae; --hipotese-fundo: #fff4d6; --hipotese-borda: #b7791f; --hipotese-texto: #6b4500; }
html, body { margin: 0; background: var(--fundo); color: var(--tinta);
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }
.pagina { width: 283mm; height: 196mm; margin: 0 auto; display: flex; flex-direction: column; gap: 2mm; }
header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 0.6mm solid var(--linha); padding-bottom: 1.2mm; }
header h1 { margin: 0; font-size: 15pt; letter-spacing: 0.2pt; }
header h1 span { color: var(--destaque); }
header p { margin: 0.6mm 0 0; font-size: 7.6pt; color: var(--tinta-2); }
.meta { text-align: right; font-size: 7pt; color: var(--tinta-2); line-height: 1.35; }
.legenda { display: inline-block; font-size: 6.6pt; font-weight: 700; color: var(--hipotese-texto);
  background: var(--hipotese-fundo); border: 0.25mm solid var(--hipotese-borda); border-radius: 1mm; padding: 0.2mm 1.2mm; }
.canvas { flex: 1; display: grid; grid-template-columns: repeat(10, 1fr); grid-template-rows: 1fr 1fr 0.58fr;
  border: 0.6mm solid var(--linha); min-height: 0; }
.bloco { border: 0.3mm solid var(--linha); padding: 1.6mm 1.8mm; overflow: hidden; display: flex; flex-direction: column; min-height: 0; }
.bloco h2 { margin: 0 0 1mm; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.3pt; color: var(--destaque); }
.bloco ul { margin: 0; padding-left: 3.2mm; }
.bloco li { font-size: 7.05pt; line-height: 1.27; margin-bottom: 0.7mm; }
.bloco h3 { margin: 1.2mm 0 0.6mm; font-size: 6.9pt; color: var(--tinta-2); text-transform: uppercase; letter-spacing: 0.2pt; }
.bloco .secundario li { font-size: 6.8pt; color: var(--tinta-2); }
.status { margin-top: auto; padding-top: 1mm; }
.status .legenda { font-size: 6.2pt; }
.status p { margin: 0.6mm 0 0; font-size: 6.3pt; color: var(--tinta-2); line-height: 1.25; }
footer { font-size: 6.4pt; color: var(--tinta-2); line-height: 1.3; }
@media screen {
  body { padding: 12px 16px; background: #eceae4; }
  .pagina { background: var(--fundo); padding: 7mm; height: auto; min-height: 196mm; width: auto; max-width: 297mm;
    box-shadow: 0 1px 4px rgba(0,0,0,.18); }
}
@media screen and (max-width: 900px) {
  .canvas { display: flex; flex-direction: column; }
  .bloco li { font-size: 10.5pt; }
  .bloco h2 { font-size: 12pt; }
  .status p { font-size: 9pt; }
  header { flex-direction: column; align-items: flex-start; gap: 4px; }
  .meta { text-align: left; }
}
@media print { body { background: none; padding: 0; } }
"""


def gerar_html(dados: dict) -> str:
    e = html.escape
    partes = []
    for b in blocos_ordenados(dados):
        itens = "".join(f"<li>{e(i)}</li>" for i in b["itens"])
        sec = ""
        if b.get("secundario_titulo"):
            sec_itens = "".join(f"<li>{e(i)}</li>" for i in b["secundario_itens"])
            sec = f'<h3>{e(b["secundario_titulo"])}</h3><ul class="secundario">{sec_itens}</ul>'
        partes.append(
            f'<section class="bloco" id="bloco-{b["id"]}" style="grid-area: {LAYOUT[b["id"]]}" aria-labelledby="t-{b["id"]}">'
            f'<h2 id="t-{b["id"]}">{e(b["titulo"])}</h2><ul>{itens}</ul>{sec}'
            f'<div class="status"><span class="legenda">{e(b["status"])}</span><p>Validação: {e(b["validacao"])}</p></div>'
            f"</section>"
        )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lean Canvas — {e(dados['produto'])}</title>
<!-- ARQUIVO GERADO por scripts/gerar_lean_canvas.py a partir de lean_canvas.json. Edite o JSON, não este arquivo. -->
<style>{CSS}</style>
</head>
<body>
<main class="pagina">
<header>
  <div>
    <h1>Lean Canvas · <span>{e(dados['produto'])}</span></h1>
    <p>{e(dados['subtitulo'])}</p>
  </div>
  <div class="meta">Versão {e(dados['versao'])}<br>Referência: {e(dados['data_referencia'])} · Equipe: {e(dados['equipe'])}<br>
  Legenda de status: <span class="legenda">{e(dados['status_padrao'])}</span></div>
</header>
<div class="canvas">
{''.join(partes)}
</div>
<footer>{e(dados['nota_rodape'])} FIAP Global Solution 2026.2 · CitizenTech · ODS 11.</footer>
</main>
</body>
</html>
"""


# --------------------------------------------------------------------- XLSX
def gerar_xlsx(dados: dict, destino: Path) -> None:
    wb = Workbook()
    fino = Side(style="thin", color="2B2B2B")
    borda = Border(left=fino, right=fino, top=fino, bottom=fino)
    quebra = Alignment(wrap_text=True, vertical="top")
    hipotese = PatternFill("solid", fgColor="FFF4D6")

    # Aba 1: canvas no layout clássico (10 colunas)
    ws = wb.active
    ws.title = "Lean Canvas"
    ws["A1"] = f"Lean Canvas — {dados['produto']}"
    ws["A1"].font = Font(bold=True, size=16)
    ws["A2"] = f"{dados['subtitulo']} · Versão {dados['versao']} · Equipe: {dados['equipe']}"
    ws["A2"].font = Font(italic=True, size=9, color="4A4A48")
    for col in range(1, 11):
        ws.column_dimensions[get_column_letter(col)].width = 19
    # linhas do canvas: 4-5 (linha superior), 6-7 (linha inferior), 8 (custos/receitas)
    mapa_linhas = {1: (4, 5), 2: (6, 7), 3: (8, 8)}
    ws.row_dimensions[4].height = 20
    ws.row_dimensions[5].height = 190
    ws.row_dimensions[6].height = 20
    ws.row_dimensions[7].height = 190
    ws.row_dimensions[8].height = 150
    por_id = {b["id"]: b for b in dados["blocos"]}
    for bid, area in LAYOUT.items():
        r0, c0, r1, c1 = (int(x) for x in area.split("/"))
        linha_ini = mapa_linhas[r0][0]
        linha_fim = mapa_linhas[r1 - 1][1]
        b = por_id[bid]
        texto = [b["titulo"].upper(), ""] + [f"• {i}" for i in b["itens"]]
        if b.get("secundario_titulo"):
            texto += ["", b["secundario_titulo"].upper() + ":"] + [f"• {i}" for i in b["secundario_itens"]]
        texto += ["", f"STATUS: {b['status']}", f"Validação: {b['validacao']}"]
        ws.merge_cells(start_row=linha_ini, start_column=c0, end_row=linha_fim, end_column=c1 - 1)
        cel = ws.cell(row=linha_ini, column=c0, value="\n".join(texto))
        cel.alignment = quebra
        cel.font = Font(size=9)
        for r in range(linha_ini, linha_fim + 1):
            for c in range(c0, c1):
                ws.cell(row=r, column=c).border = borda
    ws["A10"] = dados["nota_rodape"]
    ws["A10"].font = Font(italic=True, size=8, color="4A4A48")
    ws.merge_cells("A10:J11")
    ws["A10"].alignment = quebra
    ws.row_dimensions[10].height = 30
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # Aba 2: validação por bloco (para a equipe atualizar)
    wv = wb.create_sheet("Validacao")
    cab = ["Bloco", "Conteúdo atual", "Status", "Validação (CP1/entrevistas/testes) e o que mudou", "Evidência (arquivo/link)"]
    wv.append(cab)
    for c in range(1, len(cab) + 1):
        wv.cell(row=1, column=c).font = Font(bold=True, color="FFFFFF")
        wv.cell(row=1, column=c).fill = PatternFill("solid", fgColor="1F5FAE")
    for b in blocos_ordenados(dados):
        wv.append([b["titulo"], "\n".join(f"• {i}" for i in b["itens"]), b["status"], b["validacao"],
                   "[PREENCHER: caminho em pitch/evidencias/ ou link]"])
    for col, larg in zip("ABCDE", (24, 70, 22, 50, 32)):
        wv.column_dimensions[col].width = larg
    for row in wv.iter_rows(min_row=2):
        for cel in row:
            cel.alignment = quebra
            cel.border = borda
        row[2].fill = hipotese
    wv.freeze_panes = "A2"

    # Aba 3: coerência
    wc = wb.create_sheet("Coerencia")
    wc.append(["Ligação", "Como os blocos se sustentam"])
    for c in (1, 2):
        wc.cell(row=1, column=c).font = Font(bold=True)
    for lig, txt in COERENCIA:
        wc.append([lig, txt])
    wc.column_dimensions["A"].width = 32
    wc.column_dimensions["B"].width = 110
    for row in wc.iter_rows(min_row=2):
        for cel in row:
            cel.alignment = quebra
    wb.properties.title = f"Lean Canvas — {dados['produto']}"
    wb.properties.creator = "AcessaCidade (gerado por script)"
    wb.save(destino)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=PASTA_MODELO / "lean_canvas.json")
    p.add_argument("--saida", type=Path, default=PASTA_MODELO, help="pasta de saída (padrão: business-model/)")
    args = p.parse_args(argv)
    dados = carregar(args.fonte)
    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / "LEAN_CANVAS.md").write_text(gerar_md(dados), encoding="utf-8")
    (args.saida / "LEAN_CANVAS.html").write_text(gerar_html(dados), encoding="utf-8")
    gerar_xlsx(dados, args.saida / "LEAN_CANVAS.xlsx")
    for nome in ("LEAN_CANVAS.md", "LEAN_CANVAS.html", "LEAN_CANVAS.xlsx"):
        print(f"gerado: {args.saida / nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
