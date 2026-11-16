"""Gera as planilhas da disciplina 03 (Business Intelligence & Startup Development).

Saídas:
  pitch/registro_testes_usuarios_TEMPLATE.xlsx   modelo VAZIO para registrar testes reais com usuários
                                                 (participantes, tarefas, antes x depois, SUS e resumo com fórmulas)
  business-model/MODELO_FINANCEIRO_HIPOTETICO.xlsx  premissas declaradas + ponto de equilíbrio + projeção de 36 meses
                                                 (todas as contas são fórmulas do Excel: altere as premissas e tudo recalcula)

Uso (na raiz do repositório):
    .\\.venv\\Scripts\\python.exe 03-Business-Intelligence-Startup\\scripts\\gerar_planilhas.py

O Lean Canvas (LEAN_CANVAS.xlsx) é gerado por scripts/gerar_lean_canvas.py.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

PASTA_DISCIPLINA = Path(__file__).resolve().parents[1]
AZUL = "1F5FAE"
AMARELO = "FFF4D6"
CINZA = "F2F2F0"
fino = Side(style="thin", color="9A9A96")
BORDA = Border(left=fino, right=fino, top=fino, bottom=fino)
QUEBRA = Alignment(wrap_text=True, vertical="top")
LINHAS_DADOS = 100  # linhas preparadas para preenchimento em cada aba de registro

TAREFAS = [
    ("T1", "Registrar uma denúncia de obstáculo com foto, a partir da página inicial, até ver o protocolo gerado."),
    ("T2", "Abrir a página de acompanhamento da denúncia que acabou de registrar."),
    ("T3", "Explicar, com as próprias palavras, o que a triagem automática da foto indicou e o que significa o status atual."),
    ("T4", "Consultar uma denúncia pelo número de protocolo na tela Consultar."),
    ("T5", "Perguntar ao assistente AcessaCidade Helper o que significa o status \"Aguardando revisão\"."),
    ("T6", "Abrir o painel de indicadores e dizer qual bairro tem mais denúncias registradas."),
]

SUS_ITENS = [
    "Eu acho que gostaria de usar este sistema com frequência.",
    "Eu achei o sistema desnecessariamente complexo.",
    "Eu achei o sistema fácil de usar.",
    "Eu acho que precisaria da ajuda de uma pessoa com conhecimento técnico para usar o sistema.",
    "Eu achei que as várias funções do sistema estão bem integradas.",
    "Eu achei que o sistema apresenta muita inconsistência.",
    "Eu imagino que as pessoas aprenderão a usar este sistema rapidamente.",
    "Eu achei o sistema muito complicado de usar.",
    "Eu me senti confiante ao usar o sistema.",
    "Eu precisei aprender várias coisas novas antes de conseguir usar o sistema.",
]


def _cabecalho(ws, colunas: list[tuple[str, float]], linha: int = 1) -> None:
    for i, (nome, largura) in enumerate(colunas, start=1):
        c = ws.cell(row=linha, column=i, value=nome)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDA
        ws.column_dimensions[c.column_letter].width = largura
    ws.row_dimensions[linha].height = 32
    ws.freeze_panes = ws.cell(row=linha + 1, column=1)


def _lista(ws, valores: list[str], intervalo: str, titulo: str) -> None:
    dv = DataValidation(type="list", formula1='"' + ",".join(valores) + '"', allow_blank=True,
                        showErrorMessage=True, errorTitle=titulo, error="Escolha um valor da lista.")
    ws.add_data_validation(dv)
    dv.add(intervalo)


def _numero(ws, intervalo: str, minimo: float, maximo: float, titulo: str) -> None:
    dv = DataValidation(type="decimal", operator="between", formula1=str(minimo), formula2=str(maximo),
                        allow_blank=True, showErrorMessage=True, errorTitle=titulo,
                        error=f"Informe um número entre {minimo} e {maximo}.")
    ws.add_data_validation(dv)
    dv.add(intervalo)


# ===================================================================== testes com usuários
def gerar_registro_testes(destino: Path) -> None:
    wb = Workbook()
    ultima = LINHAS_DADOS + 1

    ws = wb.active
    ws.title = "Instrucoes"
    texto = [
        ("REGISTRO DE TESTES COM USUÁRIOS — AcessaCidade (MODELO VAZIO)", True),
        ("Use esta planilha para registrar SOMENTE testes que realmente aconteceram. Não preencha valores estimados ou inventados.", False),
        ("1. Antes do teste: o participante lê e assina o termo (pitch/TERMO_CONSENTIMENTO_MODELO.md). Guarde o termo fora do repositório público.", False),
        ("2. Identifique cada pessoa apenas por um código (P01, P02...). Não escreva nomes, telefones ou e-mails nesta planilha.", False),
        ("3. Siga o roteiro pitch/ROTEIRO_TESTE_USABILIDADE.md. As tarefas estão na aba Roteiro_Tarefas.", False),
        ("4. Aba Participantes: perfil de cada participante. Aba Tarefas: uma linha por participante x tarefa (tempo em segundos, cronometrado).", False),
        ("5. Aba Antes_x_Depois: tempo para registrar um problema no canal que a pessoa usa hoje x no AcessaCidade (ver protocolo de medição no roteiro).", False),
        ("   IMPORTANTE: na medição \"antes\", NÃO envie denúncia falsa a canais oficiais. Cronometre até a etapa anterior ao envio ou registre um problema real com autorização.", False),
        ("6. Aba SUS: questionário System Usability Scale (Brooke, 1996), notas de 1 (discordo totalmente) a 5 (concordo totalmente). A pontuação é calculada sozinha.", False),
        ("7. Aba Resumo: indicadores calculados por fórmulas. Copie os números para a LISTA_DE_EVIDENCIAS e para o pitch somente depois dos testes reais.", False),
        ("8. Se algum teste for feito com membros da equipe ou colegas sem o perfil do público-alvo, marque isso no campo Observações — não apresente como teste com o público-alvo.", False),
    ]
    for i, (t, negrito) in enumerate(texto, start=1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(bold=negrito, size=13 if negrito else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 140

    wr = wb.create_sheet("Roteiro_Tarefas")
    _cabecalho(wr, [("Tarefa", 10), ("Descrição (ler para o participante)", 100), ("Critério de sucesso", 60)])
    criterios = [
        "Protocolo AC-AAAA-NNNNNN visível na tela de sucesso.",
        "Página #/denuncia/{protocolo} aberta.",
        "Explica que é uma triagem inicial que será revisada por uma pessoa.",
        "Detalhe da denúncia aberto a partir do protocolo digitado.",
        "Recebe resposta do assistente e diz se entendeu.",
        "Nomeia o bairro com maior total no painel.",
    ]
    for (cod, desc), crit in zip(TAREFAS, criterios):
        wr.append([cod, desc, crit])
    for row in wr.iter_rows(min_row=2):
        for c in row:
            c.alignment = QUEBRA
            c.border = BORDA

    wp = wb.create_sheet("Participantes")
    _cabecalho(wp, [("Código (P01...)", 14), ("Data do teste (dd/mm/aaaa)", 16), ("Perfil", 30), ("Faixa etária", 14),
                    ("Dispositivo", 20), ("Usa leitor de tela?", 12), ("Termo assinado?", 12),
                    ("Formato", 14), ("Moderador (código do integrante)", 18), ("Observações", 50)])
    _lista(wp, ["Cadeirante", "Pessoa cega ou com baixa visão", "Pessoa idosa", "Mobilidade reduzida",
                "Cuidador(a) ou acompanhante", "Outro (descrever)"], f"C2:C{ultima}", "Perfil")
    _lista(wp, ["Até 17", "18-29", "30-44", "45-59", "60-74", "75 ou mais"], f"D2:D{ultima}", "Faixa etária")
    _lista(wp, ["Celular Android", "Celular iPhone", "Computador", "Tablet"], f"E2:E{ultima}", "Dispositivo")
    _lista(wp, ["Sim", "Não"], f"F2:G{ultima}", "Sim/Não")
    _lista(wp, ["Presencial", "Remoto"], f"H2:H{ultima}", "Formato")

    wt = wb.create_sheet("Tarefas")
    _cabecalho(wt, [("Código participante", 14), ("Tarefa", 10), ("Concluiu?", 14), ("Tempo (segundos)", 14),
                    ("Nº de erros", 10), ("Pedidos de ajuda", 12), ("Comentário ou citação (com autorização)", 70)])
    _lista(wt, [t for t, _ in TAREFAS], f"B2:B{ultima}", "Tarefa")
    _lista(wt, ["Sim", "Com ajuda", "Não"], f"C2:C{ultima}", "Concluiu")
    _numero(wt, f"D2:D{ultima}", 0, 7200, "Tempo")
    _numero(wt, f"E2:F{ultima}", 0, 100, "Contagem")

    wa = wb.create_sheet("Antes_x_Depois")
    _cabecalho(wa, [("Código participante", 14), ("Canal usado hoje", 26), ("Tempo hoje (s)", 12), ("Etapas hoje", 10),
                    ("Tempo AcessaCidade (s)", 14), ("Etapas AcessaCidade", 12), ("Diferença (s)", 12),
                    ("Redução de tempo (%)", 14), ("Como o tempo \"hoje\" foi medido", 50)])
    _lista(wa, ["Central 156 / telefone", "Site ou app da prefeitura", "Rede social", "Ouvidoria", "Outro"],
           f"B2:B{ultima}", "Canal")
    _numero(wa, f"C2:F{ultima}", 0, 7200, "Valor")
    for r in range(2, ultima + 1):
        wa.cell(row=r, column=7, value=f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(E{r})),C{r}-E{r},"")')
        wa.cell(row=r, column=8, value=f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(E{r}),C{r}>0),(C{r}-E{r})/C{r},"")')
        wa.cell(row=r, column=8).number_format = "0.0%"
        for c in (7, 8):
            wa.cell(row=r, column=c).fill = PatternFill("solid", fgColor=CINZA)

    wsu = wb.create_sheet("SUS")
    _cabecalho(wsu, [("Código participante", 14)] + [(f"Q{i}", 6) for i in range(1, 11)] + [("Pontuação SUS (0-100)", 14)])
    _numero(wsu, f"B2:K{ultima}", 1, 5, "Nota SUS")
    for r in range(2, ultima + 1):
        impares = "+".join(f"({c}{r}-1)" for c in "BDFHJ")
        pares = "+".join(f"(5-{c}{r})" for c in "CEGIK")
        wsu.cell(row=r, column=12, value=f'=IF(COUNT(B{r}:K{r})=10,({impares}+{pares})*2.5,"")')
        wsu.cell(row=r, column=12).fill = PatternFill("solid", fgColor=CINZA)
    wsi = wb.create_sheet("SUS_Itens")
    _cabecalho(wsi, [("Item", 8), ("Afirmação (1 = discordo totalmente ... 5 = concordo totalmente)", 100)])
    for i, txt in enumerate(SUS_ITENS, start=1):
        wsi.append([f"Q{i}", txt])
    wsi.append([])
    wsi.append(["Fonte", "Brooke, J. (1996). SUS: a 'quick and dirty' usability scale. Tradução livre da equipe — "
                         "conferir uma tradução validada para o português antes de uso acadêmico."])

    wz = wb.create_sheet("Resumo")
    wz.column_dimensions["A"].width = 58
    wz.column_dimensions["B"].width = 18
    wz["A1"] = "Resumo calculado (fica vazio até a equipe registrar testes reais)"
    wz["A1"].font = Font(bold=True, size=12)
    linhas = [
        ("Participantes registrados", f"=COUNTA(Participantes!A2:A{ultima})", "0"),
        ("Participantes com termo assinado", f'=COUNTIF(Participantes!G2:G{ultima},"Sim")', "0"),
        ("Tarefas registradas", f"=COUNTA(Tarefas!B2:B{ultima})", "0"),
        ("Taxa de conclusão sem ajuda (todas as tarefas)",
         f'=IFERROR(COUNTIF(Tarefas!C2:C{ultima},"Sim")/COUNTA(Tarefas!C2:C{ultima}),"")', "0.0%"),
        ("Pontuação SUS média", f'=IFERROR(AVERAGE(SUS!L2:L{ultima}),"")', "0.0"),
        ("Tempo médio hoje (s)", f'=IFERROR(AVERAGE(Antes_x_Depois!C2:C{ultima}),"")', "0"),
        ("Tempo médio com AcessaCidade (s)", f'=IFERROR(AVERAGE(Antes_x_Depois!E2:E{ultima}),"")', "0"),
        ("Redução média de tempo (%)", f'=IFERROR(AVERAGE(Antes_x_Depois!H2:H{ultima}),"")', "0.0%"),
    ]
    r = 3
    for rotulo, formula, fmt in linhas:
        wz.cell(row=r, column=1, value=rotulo).border = BORDA
        c = wz.cell(row=r, column=2, value=formula)
        c.number_format = fmt
        c.border = BORDA
        r += 1
    r += 1
    wz.cell(row=r, column=1, value="Por tarefa").font = Font(bold=True)
    wz.cell(row=r, column=2, value="Conclusão sem ajuda").font = Font(bold=True)
    wz.cell(row=r, column=3, value="Tempo médio (s)").font = Font(bold=True)
    wz.column_dimensions["C"].width = 16
    for cod, desc in TAREFAS:
        r += 1
        wz.cell(row=r, column=1, value=f"{cod} — {desc[:70]}")
        c = wz.cell(row=r, column=2, value=(
            f'=IFERROR(COUNTIFS(Tarefas!B2:B{ultima},"{cod}",Tarefas!C2:C{ultima},"Sim")'
            f'/COUNTIF(Tarefas!B2:B{ultima},"{cod}"),"")'))
        c.number_format = "0.0%"
        c2 = wz.cell(row=r, column=3, value=f'=IFERROR(AVERAGEIF(Tarefas!B2:B{ultima},"{cod}",Tarefas!D2:D{ultima}),"")')
        c2.number_format = "0"
    wb.properties.title = "AcessaCidade — registro de testes com usuários (modelo vazio)"
    wb.properties.creator = "AcessaCidade (gerado por script)"
    wb.save(destino)


# ===================================================================== modelo financeiro
PREMISSAS = [
    # (chave, rótulo, valor, formato, observação)
    ("titulo_mix", "MIX DE CLIENTES MUNICIPAIS (hipótese)", None, None, None),
    ("mix_p", "Participação de municípios P (até 50 mil hab.)", 0.50, "0%", "Hipótese: municípios pequenos são a maioria no país."),
    ("mix_m", "Participação de municípios M (50 mil a 200 mil hab.)", 0.35, "0%", "Hipótese."),
    ("mix_g", "Participação de municípios G (200 mil a 1 milhão hab.)", 0.15, "0%", "Hipótese. GG (> 1 milhão) fica fora do cálculo (proposta sob medida)."),
    ("titulo_preco", "PREÇOS MENSAIS (hipótese a validar — ver ESTRATEGIA_DE_PRECO.md)", None, None, None),
    ("preco_p", "Assinatura plano Município P (R$/mês)", 1200, "#,##0", "Valor hipotético."),
    ("preco_m", "Assinatura plano Município M (R$/mês)", 2800, "#,##0", "Valor hipotético."),
    ("preco_g", "Assinatura plano Município G (R$/mês)", 6500, "#,##0", "Valor hipotético."),
    ("adesao_bi", "Clientes que contratam o módulo Painel/BI avançado", 0.30, "0%", "Hipótese."),
    ("acrescimo_bi", "Acréscimo do módulo Painel/BI sobre a assinatura", 0.25, "0%", "Hipótese."),
    ("titulo_custos", "CUSTOS (premissas — conferir preços reais antes de usar)", None, None, None),
    ("equipe", "Equipe: custo mensal total (R$)", 48000, "#,##0", "Premissa: 4 pessoas x R$ 12.000 de custo total com encargos."),
    ("infra_base", "Nuvem e monitoramento — base compartilhada (R$/mês)", 2000, "#,##0", "Premissa: conferir na calculadora de preços do provedor."),
    ("admin", "Jurídico, contabilidade, LGPD, ferramentas (R$/mês)", 3000, "#,##0", "Premissa."),
    ("comercial", "Comercial, eventos e deslocamentos (R$/mês)", 2000, "#,##0", "Premissa."),
    ("var_infra", "Custo variável de nuvem por cliente (R$/mês)", 120, "#,##0", "Premissa: armazenamento de fotos e processamento."),
    ("var_llm", "Custo variável de LLM por cliente (R$/mês)", 60, "#,##0", "Premissa: uso do assistente via OpenRouter; modo por regras reduz o custo."),
    ("var_suporte", "Suporte e atendimento por cliente (R$/mês)", 270, "#,##0", "Premissa."),
    ("titulo_rampa", "RAMPA DE VENDAS (hipótese)", None, None, None),
    ("mes_inicio", "Mês do primeiro contrato", 6, "0", "Hipótese: ciclo de venda pública longo."),
    ("novos_mes", "Novos clientes municipais por mês a partir do primeiro contrato", 2, "0", "Hipótese."),
]


def calcular_modelo(valores: dict[str, float] | None = None) -> dict[str, float]:
    """Reproduz em Python as fórmulas da planilha (usado nos testes e na documentação)."""
    v = {k: val for k, _, val, _, _ in PREMISSAS if val is not None}
    if valores:
        v.update(valores)
    base = v["mix_p"] * v["preco_p"] + v["mix_m"] * v["preco_m"] + v["mix_g"] * v["preco_g"]
    ticket = base * (1 + v["adesao_bi"] * v["acrescimo_bi"])
    fixo = v["equipe"] + v["infra_base"] + v["admin"] + v["comercial"]
    variavel = v["var_infra"] + v["var_llm"] + v["var_suporte"]
    margem = ticket - variavel
    pe = math.ceil(fixo / margem)
    acumulado, minimo, mes_pe, mes_payback = 0.0, 0.0, None, None
    for m in range(1, 37):
        clientes = max(0, m - v["mes_inicio"] + 1) * v["novos_mes"]
        resultado = clientes * ticket - (fixo + clientes * variavel)
        acumulado += resultado
        minimo = min(minimo, acumulado)
        if mes_pe is None and resultado >= 0:
            mes_pe = m
        if mes_payback is None and acumulado >= 0:
            mes_payback = m
    return {"ticket_medio": ticket, "custo_fixo": fixo, "custo_variavel": variavel, "margem_contribuicao": margem,
            "ponto_equilibrio_clientes": pe, "mes_ponto_equilibrio": mes_pe, "necessidade_caixa": -minimo,
            "mes_caixa_acumulado_positivo": mes_payback}


def gerar_modelo_financeiro(destino: Path) -> dict[str, float]:
    wb = Workbook()
    ws = wb.active
    ws.title = "Premissas"
    ws["A1"] = "AcessaCidade — premissas do modelo financeiro (TODOS OS VALORES SÃO HIPÓTESES A VALIDAR)"
    ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = "Altere apenas as células amarelas da coluna B. As demais abas recalculam sozinhas. Nada aqui é dado real de mercado."
    ws["A2"].font = Font(italic=True, color="7A2E00")
    ws.column_dimensions["A"].width = 62
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 80
    ref: dict[str, str] = {}
    r = 4
    for chave, rotulo, valor, fmt, obs in PREMISSAS:
        if valor is None:
            ws.cell(row=r, column=1, value=rotulo).font = Font(bold=True, color=AZUL)
        else:
            ws.cell(row=r, column=1, value=rotulo)
            c = ws.cell(row=r, column=2, value=valor)
            c.number_format = fmt
            c.fill = PatternFill("solid", fgColor=AMARELO)
            c.border = BORDA
            ws.cell(row=r, column=3, value=obs).font = Font(size=9, color="4A4A48")
            ref[chave] = f"Premissas!$B${r}"
        r += 1

    we = wb.create_sheet("Ponto_de_equilibrio")
    we.column_dimensions["A"].width = 62
    we.column_dimensions["B"].width = 16
    we["A1"] = "Ponto de equilíbrio (a conta fecha?) — calculado a partir das premissas"
    we["A1"].font = Font(bold=True, size=12)
    p = ref
    calc = [
        ("Ticket médio mensal sem módulo BI (R$)",
         f"={p['mix_p']}*{p['preco_p']}+{p['mix_m']}*{p['preco_m']}+{p['mix_g']}*{p['preco_g']}", "#,##0"),
        ("Ticket médio mensal com módulo BI (R$)", f"=B3*(1+{p['adesao_bi']}*{p['acrescimo_bi']})", "#,##0"),
        ("Custo fixo mensal (R$)", f"={p['equipe']}+{p['infra_base']}+{p['admin']}+{p['comercial']}", "#,##0"),
        ("Custo variável por cliente (R$/mês)", f"={p['var_infra']}+{p['var_llm']}+{p['var_suporte']}", "#,##0"),
        ("Margem de contribuição por cliente (R$/mês)", "=B4-B6", "#,##0"),
        ("Clientes municipais para o ponto de equilíbrio", "=ROUNDUP(B5/B7,0)", "0"),
        ("Mês em que o resultado mensal fica positivo (projeção)",
         '=IFERROR(INDEX(Projecao_36_meses!A2:A37,MATCH(TRUE,INDEX(Projecao_36_meses!F2:F37>=0,0),0)),"não atinge em 36 meses")', "0"),
        ("Necessidade de caixa até o equilíbrio (R$)", "=-MIN(0,MIN(Projecao_36_meses!G2:G37))", "#,##0"),
    ]
    for i, (rot, formula, fmt) in enumerate(calc, start=3):
        we.cell(row=i, column=1, value=rot).border = BORDA
        c = we.cell(row=i, column=2, value=formula)
        c.number_format = fmt
        c.border = BORDA
        c.fill = PatternFill("solid", fgColor=CINZA)
    we["A12"] = ("Leitura: receita de implantação não entra no cálculo (visão conservadora). "
                 "Clientes B2B (concessionárias, grandes áreas) e o plano GG reduziriam o número de municípios necessários.")
    we["A12"].alignment = QUEBRA
    we.merge_cells("A12:C14")

    wp = wb.create_sheet("Projecao_36_meses")
    _cabecalho(wp, [("Mês", 8), ("Clientes", 10), ("Receita recorrente (R$)", 18), ("Custo fixo (R$)", 16),
                    ("Custo variável (R$)", 16), ("Resultado do mês (R$)", 18), ("Caixa acumulado (R$)", 18)])
    for m in range(1, 37):
        r = m + 1
        wp.cell(row=r, column=1, value=m)
        wp.cell(row=r, column=2, value=f"=MAX(0,A{r}-{p['mes_inicio']}+1)*{p['novos_mes']}")
        wp.cell(row=r, column=3, value=f"=B{r}*Ponto_de_equilibrio!$B$4")
        wp.cell(row=r, column=4, value="=Ponto_de_equilibrio!$B$5")
        wp.cell(row=r, column=5, value=f"=B{r}*Ponto_de_equilibrio!$B$6")
        wp.cell(row=r, column=6, value=f"=C{r}-D{r}-E{r}")
        wp.cell(row=r, column=7, value=f"=F{r}" if m == 1 else f"=G{r-1}+F{r}")
        for c in range(3, 8):
            wp.cell(row=r, column=c).number_format = "#,##0"
    graf = LineChart()
    graf.title = "Caixa acumulado — cenário hipotético (R$)"
    graf.y_axis.title = "R$"
    graf.x_axis.title = "Mês"
    graf.height, graf.width = 8, 18
    graf.add_data(Reference(wp, min_col=7, min_row=1, max_row=37), titles_from_data=True)
    graf.set_categories(Reference(wp, min_col=1, min_row=2, max_row=37))
    graf.series[0].graphicalProperties.line.solidFill = "2A78D6"
    graf.series[0].graphicalProperties.line.width = 22000
    graf.legend = None
    wp.add_chart(graf, "I2")
    wb.properties.title = "AcessaCidade — modelo financeiro hipotético"
    wb.properties.creator = "AcessaCidade (gerado por script)"
    wb.save(destino)
    return calcular_modelo()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida-pitch", type=Path, default=PASTA_DISCIPLINA / "pitch")
    ap.add_argument("--saida-modelo", type=Path, default=PASTA_DISCIPLINA / "business-model")
    args = ap.parse_args(argv)
    args.saida_pitch.mkdir(parents=True, exist_ok=True)
    args.saida_modelo.mkdir(parents=True, exist_ok=True)
    reg = args.saida_pitch / "registro_testes_usuarios_TEMPLATE.xlsx"
    fin = args.saida_modelo / "MODELO_FINANCEIRO_HIPOTETICO.xlsx"
    gerar_registro_testes(reg)
    res = gerar_modelo_financeiro(fin)
    print(f"gerado: {reg}")
    print(f"gerado: {fin}")
    print("Resumo do cenário hipotético (mesmas fórmulas da planilha):")
    for k, v in res.items():
        print(f"  {k}: {v:,.2f}" if isinstance(v, float) else f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
