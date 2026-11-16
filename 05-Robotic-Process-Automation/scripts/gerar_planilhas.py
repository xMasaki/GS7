"""Gera as planilhas da disciplina 05 (Robotic Process Automation) do AcessaCidade.

Arquivos gerados (todos com dados FICTÍCIOS / SIMULADOS, cidade fictícia "Cidade Exemplo"):

  spreadsheet/denuncias_para_cadastro_SIMULADAS.xlsx    -> entrada do robô UiPath
  spreadsheet/assessment_rpa_AcessaCidade.xlsx          -> assessment de automatizabilidade (com fórmulas)
  UiPath/AcessaCidade.RPA/Data/Config.xlsx              -> configuração do robô (aba Settings: Nome/Valor)

Uso (na raiz do repositório):
  .\\.venv\\Scripts\\python.exe 05-Robotic-Process-Automation\\scripts\\gerar_planilhas.py

O openpyxl grava as FÓRMULAS, mas não calcula os valores: o Excel (ou LibreOffice) recalcula ao abrir
(a pasta é marcada com fullCalcOnLoad). Os mesmos valores são calculados aqui em Python e impressos
no final, para conferência e para o relatório.
"""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BASE = Path(__file__).resolve().parents[1]  # 05-Robotic-Process-Automation
SPREADSHEET_DIR = BASE / "spreadsheet"
CONFIG_PATH = BASE / "UiPath" / "AcessaCidade.RPA" / "Data" / "Config.xlsx"
ENTRADA_PATH = SPREADSHEET_DIR / "denuncias_para_cadastro_SIMULADAS.xlsx"
ASSESSMENT_PATH = SPREADSHEET_DIR / "assessment_rpa_AcessaCidade.xlsx"

# ---------------------------------------------------------------------------
# Contrato (docs/CONTRATOS_DE_INTEGRACAO.md, seções 3.1 e 3.2) — RÓTULOS exatos
# ---------------------------------------------------------------------------
TIPOS_OBSTACULO = {
    "BURACO_CALCADA": "Buraco na calçada",
    "BURACO_VIA": "Buraco na via ou travessia",
    "CALCADA_DANIFICADA": "Calçada quebrada ou desnivelada",
    "RAMPA_IRREGULAR": "Rampa ausente ou irregular",
    "PISO_TATIL": "Piso tátil ausente ou danificado",
    "OBSTACULO_FIXO": "Obstáculo fixo (poste, lixeira, placa)",
    "OBSTACULO_TEMPORARIO": "Obstáculo temporário (entulho, veículo, obra)",
    "OUTRO": "Outro",
}
IMPACTOS = {
    "IMPEDE_PASSAGEM": "Impede a passagem",
    "DIFICULTA_PASSAGEM": "Dificulta a passagem",
    "RISCO_QUEDA": "Risco de queda ou acidente",
    "BAIXO_IMPACTO": "Baixo impacto",
}

COLUNAS_ENTRADA = [
    "Nome", "Logradouro", "Numero", "Bairro", "Cidade", "Ponto_Referencia",
    "Tipo_Obstaculo", "Descricao", "Impacto", "Caminho_Imagem", "Data_Registro",
]
COLUNAS_SAIDA = ["Status_Robo", "Protocolo", "Mensagem", "Data_Hora_Processamento"]
COLUNA_CENARIO = "Cenario_Teste"  # informativa: o robô ignora esta coluna

PREFIXO = "[TESTE SIMULADO RPA] "

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
AZUL = "1F4E79"
CINZA = "F2F2F2"
AMARELO = "FFF2CC"
VERDE = "E2EFDA"
FONTE_TITULO = Font(bold=True, size=14, color=AZUL)
FONTE_CAB = Font(bold=True, color="FFFFFF")
PREENCH_CAB = PatternFill("solid", fgColor=AZUL)
PREENCH_SAIDA = PatternFill("solid", fgColor="7F7F7F")
PREENCH_AVISO = PatternFill("solid", fgColor=AMARELO)
PREENCH_TOTAL = PatternFill("solid", fgColor=VERDE)
PREENCH_INPUT = PatternFill("solid", fgColor="DDEBF7")
BORDA = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
QUEBRA = Alignment(wrap_text=True, vertical="top")


def _cabecalho(ws, linha: int, titulos: list[str], preench=PREENCH_CAB) -> None:
    for col, titulo in enumerate(titulos, start=1):
        c = ws.cell(row=linha, column=col, value=titulo)
        c.font = FONTE_CAB
        c.fill = preench
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BORDA


def _larguras(ws, larguras: dict[str, float]) -> None:
    for letra, largura in larguras.items():
        ws.column_dimensions[letra].width = largura


# ---------------------------------------------------------------------------
# 1) Planilha de entrada do robô
# ---------------------------------------------------------------------------
# Imagens sintéticas: geradas por outro componente em data/samples/fotos com nomes
# sintetica_<tipo>_<nn>.jpg. Algumas linhas ficam propositalmente SEM imagem.
LINHAS_ENTRADA = [
    dict(Nome="Robô Teste 01", Logradouro="Rua das Acácias", Numero="120", Bairro="Centro",
         Ponto_Referencia="Em frente ao ponto de ônibus", Tipo_Obstaculo="Buraco na calçada",
         Descricao="Buraco de aproximadamente 40 cm no meio da calçada; cadeirantes precisam desviar pela rua.",
         Impacto="Impede a passagem", Caminho_Imagem="sintetica_buraco_01.jpg", Data_Registro="03/11/2026",
         Cenario_Teste="POSITIVO - com imagem"),
    dict(Nome="Robô Teste 02", Logradouro="Avenida Central", Numero="455", Bairro="Vila Nova",
         Ponto_Referencia="Ao lado da praça", Tipo_Obstaculo="Calçada quebrada ou desnivelada",
         Descricao="Placas de concreto soltas e desnível de cerca de 5 cm ao longo de 10 metros de calçada.",
         Impacto="Risco de queda ou acidente", Caminho_Imagem="", Data_Registro="03/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 03", Logradouro="Rua Projetada A", Numero="S/N", Bairro="Jardim Esperança",
         Ponto_Referencia="Esquina com a Rua Projetada B", Tipo_Obstaculo="Rampa ausente ou irregular",
         Descricao="Esquina sem rampa de acesso; a guia tem cerca de 20 cm de altura e impede a travessia.",
         Impacto="Impede a passagem", Caminho_Imagem="", Data_Registro="04/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 04", Logradouro="Rua dos Ipês", Numero="78", Bairro="Parque das Flores",
         Ponto_Referencia="Próximo à unidade de saúde", Tipo_Obstaculo="Buraco na via ou travessia",
         Descricao="Buraco na faixa de pedestres, bem no trajeto de quem atravessa com andador ou cadeira de rodas.",
         Impacto="Risco de queda ou acidente", Caminho_Imagem="sintetica_buraco_02.jpg", Data_Registro="04/11/2026",
         Cenario_Teste="POSITIVO - com imagem"),
    dict(Nome="Robô Teste 05", Logradouro="Travessa do Sol", Numero="12", Bairro="Bela Vista",
         Ponto_Referencia="", Tipo_Obstaculo="Piso tátil ausente ou danificado",
         Descricao="Piso tátil interrompido e com peças faltando no trecho entre a escola e o ponto de ônibus.",
         Impacto="Dificulta a passagem", Caminho_Imagem="", Data_Registro="05/11/2026",
         Cenario_Teste="POSITIVO - sem imagem e sem referência"),
    dict(Nome="Robô Teste 06", Logradouro="Rua das Acácias", Numero="300", Bairro="Centro",
         Ponto_Referencia="Em frente à farmácia", Tipo_Obstaculo="Obstáculo fixo (poste, lixeira, placa)",
         Descricao="Poste instalado no centro da calçada deixa menos de 60 cm livres para passagem.",
         Impacto="Impede a passagem", Caminho_Imagem="", Data_Registro="05/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 07", Logradouro="Avenida das Palmeiras", Numero="1001", Bairro="Vila Nova",
         Ponto_Referencia="Perto do mercado", Tipo_Obstaculo="Obstáculo temporário (entulho, veículo, obra)",
         Descricao="Entulho de obra ocupando toda a largura da calçada há mais de uma semana.",
         Impacto="Impede a passagem", Caminho_Imagem="", Data_Registro="06/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 08", Logradouro="Rua Projetada C", Numero="45", Bairro="Jardim Esperança",
         Ponto_Referencia="Ao lado da quadra", Tipo_Obstaculo="Buraco na calçada",
         Descricao="Dois buracos próximos na calçada, com bordas quebradas, difíceis de ver à noite.",
         Impacto="Risco de queda ou acidente", Caminho_Imagem="sintetica_buraco_03.jpg", Data_Registro="06/11/2026",
         Cenario_Teste="POSITIVO - com imagem"),
    dict(Nome="Robô Teste 09", Logradouro="Rua do Comércio", Numero="210", Bairro="Centro",
         Ponto_Referencia="Saída do terminal", Tipo_Obstaculo="Outro",
         Descricao="Grade de escoamento solta na calçada, com vãos largos onde rodas pequenas podem prender.",
         Impacto="Dificulta a passagem", Caminho_Imagem="", Data_Registro="07/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 10", Logradouro="Rua das Orquídeas", Numero="33", Bairro="Parque das Flores",
         Ponto_Referencia="", Tipo_Obstaculo="Calçada quebrada ou desnivelada",
         Descricao="Raízes de árvore levantaram a calçada; há rachaduras e um degrau irregular.",
         Impacto="Baixo impacto", Caminho_Imagem="", Data_Registro="07/11/2026",
         Cenario_Teste="POSITIVO - sem imagem"),
    dict(Nome="Robô Teste 11", Logradouro="Avenida Central", Numero="900", Bairro="Bela Vista",
         Ponto_Referencia="Em frente ao banco", Tipo_Obstaculo="Buraco na calçada",
         Descricao="Buraco",
         Impacto="Dificulta a passagem", Caminho_Imagem="", Data_Registro="08/11/2026",
         Cenario_Teste="NEGATIVO - descrição curta (< 10 caracteres): esperado FALHA_NEGOCIO"),
    dict(Nome="Robô Teste 12", Logradouro="R.", Numero="5", Bairro="Centro",
         Ponto_Referencia="", Tipo_Obstaculo="Rampa ausente ou irregular",
         Descricao="Rampa com inclinação muito acentuada e sem corrimão, perigosa para cadeirantes.",
         Impacto="Risco de queda ou acidente", Caminho_Imagem="", Data_Registro="08/11/2026",
         Cenario_Teste="NEGATIVO - logradouro com menos de 3 caracteres: esperado FALHA_NEGOCIO"),
]


def gerar_entrada() -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Denuncias"
    colunas = COLUNAS_ENTRADA + COLUNAS_SAIDA + [COLUNA_CENARIO]
    _cabecalho(ws, 1, colunas)
    for idx in range(len(COLUNAS_ENTRADA), len(COLUNAS_ENTRADA) + len(COLUNAS_SAIDA)):
        ws.cell(row=1, column=idx + 1).fill = PREENCH_SAIDA
    ws.cell(row=1, column=len(colunas)).fill = PatternFill("solid", fgColor="BF8F00")

    for r, linha in enumerate(LINHAS_ENTRADA, start=2):
        valores = dict(linha)
        valores["Cidade"] = "Cidade Exemplo"
        valores["Descricao"] = PREFIXO + valores["Descricao"] if valores["Descricao"] != "Buraco" else valores["Descricao"]
        for c, nome in enumerate(colunas, start=1):
            valor = valores.get(nome, "")
            cel = ws.cell(row=r, column=c, value=valor if valor != "" else None)
            cel.number_format = "@"  # texto: evita que "120" vire número e "S/N" quebre a coluna
            cel.alignment = QUEBRA
            cel.border = BORDA
    ws.freeze_panes = "B2"
    _larguras(ws, {"A": 16, "B": 24, "C": 9, "D": 18, "E": 16, "F": 28, "G": 34, "H": 60, "I": 26,
                   "J": 26, "K": 14, "L": 16, "M": 18, "N": 40, "O": 22, "P": 46})
    ws.auto_filter.ref = f"A1:{get_column_letter(len(colunas))}{len(LINHAS_ENTRADA) + 1}"

    leia = wb.create_sheet("LEIAME")
    textos = [
        ("DADOS FICTÍCIOS / SIMULADOS — NÃO SÃO DENÚNCIAS REAIS", FONTE_TITULO),
        ("Planilha de entrada do robô UiPath do AcessaCidade (disciplina 05 — Robotic Process Automation).", None),
        ("Todas as linhas foram criadas pela equipe para teste. Cidade fictícia: \"Cidade Exemplo\". Os nomes", None),
        ("(\"Robô Teste NN\") e endereços são inventados; nenhuma afirmação é feita sobre ruas reais.", None),
        ("As descrições começam com \"[TESTE SIMULADO RPA]\" para que os registros criados no AcessaCidade", None),
        ("sejam reconhecidos como teste (o sistema grava origem=RPA).", None),
        ("", None),
        ("Colunas de ENTRADA (lidas pelo robô):", Font(bold=True)),
        ("  Nome, Logradouro, Numero, Bairro, Cidade, Ponto_Referencia, Tipo_Obstaculo, Descricao, Impacto,", None),
        ("  Caminho_Imagem (nome do arquivo dentro de data/samples/fotos; vazio = sem foto), Data_Registro.", None),
        ("  Tipo_Obstaculo e Impacto usam o RÓTULO exato exibido no formulário (contrato, seções 3.1 e 3.2).", None),
        ("Colunas de SAÍDA (preenchidas pelo robô na planilha de saída): Status_Robo, Protocolo, Mensagem,", Font(bold=True)),
        ("  Data_Hora_Processamento. Status possíveis: SUCESSO, FALHA_NEGOCIO, FALHA_SISTEMA.", None),
        ("Coluna Cenario_Teste: apenas documenta o resultado esperado; o robô a ignora.", None),
        ("  As linhas 11 e 12 são NEGATIVAS de propósito (validação de regra de negócio do robô).", None),
        ("", None),
        ("Imagens: arquivos sintetica_<tipo>_<nn>.jpg gerados por script em data/samples/fotos (imagens SINTÉTICAS).", None),
        ("Se a pasta ainda não existir, rode o gerador de imagens do projeto ou apague a coluna Caminho_Imagem.", None),
        ("", None),
        ("Gerado por: 05-Robotic-Process-Automation/scripts/gerar_planilhas.py", None),
    ]
    for i, (texto, fonte) in enumerate(textos, start=1):
        c = leia.cell(row=i, column=1, value=texto)
        if fonte:
            c.font = fonte
    leia["A1"].fill = PREENCH_AVISO
    leia.column_dimensions["A"].width = 110

    ENTRADA_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ENTRADA_PATH)
    return ENTRADA_PATH


# ---------------------------------------------------------------------------
# 2) Configuração do robô (Data/Config.xlsx)
# ---------------------------------------------------------------------------
CONFIG = [
    ("URL_ACESSACIDADE", "http://localhost:8000",
     "URL base do AcessaCidade, sem barra no final. Teste: http://localhost:8000. Produção: URL pública da Azure "
     "([PREENCHER: URL pública do MVP]). O robô abre <URL>/#/registrar?canal=rpa (origem=RPA)."),
    ("CAMINHO_PLANILHA_ENTRADA", r"..\..\spreadsheet\denuncias_para_cadastro_SIMULADAS.xlsx",
     "Planilha com as denúncias a cadastrar. Caminho relativo à pasta do projeto UiPath ou absoluto."),
    ("CAMINHO_PLANILHA_SAIDA", r"..\..\spreadsheet\denuncias_resultado_RPA.xlsx",
     "Planilha de saída (criada/atualizada pelo robô a cada linha). Feche-a no Excel antes de executar."),
    ("PASTA_IMAGENS", r"..\..\..\data\samples\fotos",
     "Pasta das imagens SINTÉTICAS referenciadas em Caminho_Imagem."),
    ("TIMEOUT_SEGUNDOS", "30", "Tempo máximo (s) para o formulário carregar e para o resultado do envio aparecer."),
    ("NAVEGADOR", "Edge", "Edge ou Chrome (a extensão UiPath correspondente precisa estar instalada)."),
    ("ABA_ENTRADA", "Denuncias", "Nome da aba lida na planilha de entrada."),
    ("ABA_SAIDA", "Resultado", "Nome da aba escrita na planilha de saída."),
    ("MODO_UPLOAD_FOTO", "DIALOGO",
     "DIALOGO = clica em #campo-foto e digita o caminho no diálogo 'Abrir' do Windows (funciona em Edge/Chrome). "
     "TYPEINTO = digita o caminho direto no <input type=file> (só use se funcionar no seu navegador). "
     "IGNORAR = não envia fotos."),
]


def gerar_config() -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Settings"
    _cabecalho(ws, 1, ["Nome", "Valor", "Descricao"])
    for r, (nome, valor, desc) in enumerate(CONFIG, start=2):
        for c, v in enumerate((nome, valor, desc), start=1):
            cel = ws.cell(row=r, column=c, value=v)
            cel.number_format = "@"
            cel.alignment = QUEBRA
            cel.border = BORDA
        ws.cell(row=r, column=2).fill = PREENCH_INPUT
    _larguras(ws, {"A": 28, "B": 58, "C": 90})
    leia = wb.create_sheet("LEIAME")
    leia["A1"] = "Configuração do robô AcessaCidade.RPA — lida por Workflows/CarregarConfiguracao.xaml (aba Settings)."
    leia["A2"] = "Altere apenas a coluna Valor. Não coloque senhas, tokens ou chaves nesta planilha."
    leia["A3"] = "Caminhos relativos são resolvidos a partir da pasta do projeto (onde está o project.json)."
    leia["A4"] = "Gerado por: 05-Robotic-Process-Automation/scripts/gerar_planilhas.py"
    leia.column_dimensions["A"].width = 110
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CONFIG_PATH)
    return CONFIG_PATH


# ---------------------------------------------------------------------------
# 3) Assessment de automatizabilidade
# ---------------------------------------------------------------------------
PROCESSO = ("Cadastro, no AcessaCidade, de denúncias de acessibilidade recebidas por canais não digitais "
            "e por planilhas de parceiros (associações, ONGs e agentes comunitários)")

# (critério, pergunta orientadora, peso, nota, justificativa preliminar, escala 1..5)
CRITERIOS = [
    ("Baseado em regras", "As decisões do processo seguem regras claras, sem julgamento subjetivo?", 15, 5,
     "Cada linha da planilha vira um registro com campos fixos; tipo e impacto vêm de listas fechadas (contrato 3.1/3.2).",
     "1 = depende de julgamento humano · 5 = 100% regras explícitas"),
    ("Entrada estruturada e digital", "Os dados de entrada chegam em formato digital e estruturado?", 12, 4,
     "A planilha-modelo é estruturada; parte das denúncias ainda chega em papel/e-mail livre e precisa ser "
     "transcrita para o modelo antes do robô (fora do escopo).",
     "1 = papel/texto livre · 5 = planilha/arquivo padronizado"),
    ("Volume", "Quantos itens por mês? (HIPÓTESE a validar)", 10, 3,
     "Premissa: 300 denúncias/mês vindas de parceiros na fase piloto. [PREENCHER: volume real após conversa com parceiros].",
     "1 = < 20/mês · 3 = 100–500/mês · 5 = > 2.000/mês"),
    ("Frequência", "Com que frequência o processo é executado?", 8, 4,
     "Planilhas chegam semanalmente (premissa); o robô pode rodar diariamente.",
     "1 = anual/eventual · 3 = mensal · 5 = diária"),
    ("Estabilidade da aplicação", "A interface alvo muda pouco e tem identificadores estáveis?", 10, 4,
     "O formulário tem ids, name e data-rpa estáveis definidos em contrato; risco residual de mudança de layout.",
     "1 = muda toda semana · 5 = estável e versionada"),
    ("Número de sistemas", "Quantos sistemas o robô precisa operar? (menos = melhor)", 5, 4,
     "Dois: Excel (planilha) e o navegador com o AcessaCidade.",
     "1 = 5 ou mais sistemas · 5 = 1 sistema"),
    ("Exceções", "As exceções são poucas e previsíveis?", 10, 4,
     "Exceções conhecidas: campo obrigatório vazio, rótulo inválido, imagem ausente, sistema fora do ar. "
     "Todas são registradas na planilha de saída para o operador.",
     "1 = exceções frequentes e imprevisíveis · 5 = raras e catalogadas"),
    ("Tempo manual por item", "Quanto tempo uma pessoa leva por item? (HIPÓTESE a validar)", 8, 3,
     "Premissa: 4 min por denúncia (abrir planilha, digitar ~10 campos, anexar foto, copiar protocolo). "
     "[PREENCHER: tempo cronometrado pela equipe].",
     "1 = < 30 s · 3 = 2–5 min · 5 = > 10 min"),
    ("Propensão a erro humano", "A digitação manual gera erros relevantes?", 7, 4,
     "Transcrição de endereço e escolha de categoria são suscetíveis a erro e a cópia de protocolo também.",
     "1 = erro raro e sem impacto · 5 = erro frequente e caro"),
    ("Impacto ao cidadão", "Automatizar melhora a vida do cidadão?", 10, 5,
     "Denúncias de pessoas com deficiência e idosos entram mais rápido no sistema e recebem protocolo de acompanhamento.",
     "1 = nenhum impacto · 5 = impacto direto e alto"),
    ("Ausência de API / integração nativa", "Os sistemas de origem NÃO oferecem integração por API? (5 = sem API)", 5, 2,
     "O AcessaCidade TEM API (POST /api/denuncias), o que reduz a necessidade de RPA; porém os parceiros não têm "
     "capacidade técnica para integrar. Ver docs/ANALISE_RPA_VS_API.md.",
     "1 = API disponível e usada pelas duas pontas · 5 = nenhuma integração possível"),
]

LIMIAR_ALTA = 0.70
LIMIAR_MEDIA = 0.50


def classificar(percentual: float) -> str:
    if percentual >= LIMIAR_ALTA:
        return "Alta aptidão para RPA"
    if percentual >= LIMIAR_MEDIA:
        return "Média aptidão (otimizar o processo antes de automatizar)"
    return "Baixa aptidão (não automatizar com RPA)"


def calcular_assessment(criterios=CRITERIOS) -> dict:
    soma_pesos = sum(c[2] for c in criterios)
    ponderada = sum(c[2] * c[3] for c in criterios)
    maxima = soma_pesos * 5
    percentual = ponderada / maxima
    return {
        "soma_pesos": soma_pesos,
        "pontuacao_ponderada": ponderada,
        "pontuacao_maxima": maxima,
        "percentual": percentual,
        "classificacao": classificar(percentual),
        "linhas": [
            {"criterio": c[0], "peso": c[2], "nota": c[3], "ponderada": c[2] * c[3]} for c in criterios
        ],
    }


def _formula_classificacao(celula: str) -> str:
    return (f'=IF({celula}="","",IF({celula}>={LIMIAR_ALTA},"Alta aptidão para RPA",'
            f'IF({celula}>={LIMIAR_MEDIA},"Média aptidão (otimizar o processo antes de automatizar)",'
            f'"Baixa aptidão (não automatizar com RPA)")))')


def _aba_assessment(ws, preenchida: bool) -> None:
    ws["A1"] = "AcessaCidade — Assessment de automatizabilidade (RPA)"
    ws["A1"].font = FONTE_TITULO
    ws["A2"] = "Processo avaliado:"
    ws["A2"].font = Font(bold=True)
    ws["B2"] = PROCESSO if preenchida else "[PREENCHER: nome do processo]"
    ws["A3"] = "Situação:"
    ws["A3"].font = Font(bold=True)
    ws["B3"] = ("AVALIAÇÃO PRELIMINAR DA EQUIPE — REVISAR COM A EQUIPE. Volume e tempo são HIPÓTESES a validar."
                if preenchida else "[PREENCHER: preliminar / revisada]")
    ws["B3"].fill = PREENCH_AVISO
    ws["A4"] = "Avaliadores / data:"
    ws["A4"].font = Font(bold=True)
    ws["B4"] = "[PREENCHER: integrantes da equipe e data da revisão]"
    ws.merge_cells("B2:I2")
    ws.merge_cells("B3:I3")
    ws.merge_cells("B4:I4")

    cab = ["Nº", "Critério", "Pergunta orientadora", "Peso (%)", "Nota (1–5)",
           "Pontuação ponderada", "Pontuação máxima", "Justificativa", "Escala de referência"]
    _cabecalho(ws, 6, cab)
    primeira = 7
    for i, (crit, perg, peso, nota, just, escala) in enumerate(CRITERIOS):
        r = primeira + i
        valores = [i + 1, crit, perg, peso, nota if preenchida else None,
                   f'=IF(E{r}="","",D{r}*E{r})', f"=D{r}*5",
                   just if preenchida else "[PREENCHER]", escala]
        for c, v in enumerate(valores, start=1):
            cel = ws.cell(row=r, column=c, value=v)
            cel.alignment = QUEBRA
            cel.border = BORDA
        ws.cell(row=r, column=5).fill = PREENCH_INPUT
        ws.cell(row=r, column=4).fill = PREENCH_INPUT
    ultima = primeira + len(CRITERIOS) - 1
    rt = ultima + 1
    ws.cell(row=rt, column=2, value="TOTAL").font = Font(bold=True)
    ws.cell(row=rt, column=4, value=f"=SUM(D{primeira}:D{ultima})")
    ws.cell(row=rt, column=6, value=f"=SUM(F{primeira}:F{ultima})")
    ws.cell(row=rt, column=7, value=f"=SUM(G{primeira}:G{ultima})")
    ws.cell(row=rt, column=8, value=f'=IF(D{rt}=100,"Pesos OK (somam 100)","ATENÇÃO: os pesos devem somar 100")')
    for c in range(1, 10):
        ws.cell(row=rt, column=c).fill = PREENCH_TOTAL
        ws.cell(row=rt, column=c).border = BORDA
        ws.cell(row=rt, column=c).font = Font(bold=True)

    r_pct = rt + 2
    ws.cell(row=r_pct, column=2, value="Aderência ao RPA (% da pontuação máxima)").font = Font(bold=True)
    cel_pct = ws.cell(row=r_pct, column=4,
                      value=f'=IF(COUNT(E{primeira}:E{ultima})<{len(CRITERIOS)},"",F{rt}/G{rt})')
    cel_pct.number_format = "0.0%"
    cel_pct.font = Font(bold=True, size=13)
    ws.cell(row=r_pct + 1, column=2, value="Classificação final").font = Font(bold=True)
    ws.cell(row=r_pct + 1, column=4, value=_formula_classificacao(f"D{r_pct}")).font = Font(bold=True, size=13)
    ws.merge_cells(start_row=r_pct + 1, start_column=4, end_row=r_pct + 1, end_column=8)
    ws.cell(row=r_pct + 2, column=2, value="Notas preenchidas").font = Font(bold=True)
    ws.cell(row=r_pct + 2, column=4, value=f'=COUNT(E{primeira}:E{ultima})&" de {len(CRITERIOS)}"')

    r_leg = r_pct + 4
    legenda = [
        "Como ler: nota 5 = critério MUITO favorável ao RPA; nota 1 = desfavorável.",
        f"Faixas: ≥ {LIMIAR_ALTA:.0%} = Alta aptidão · {LIMIAR_MEDIA:.0%} a {LIMIAR_ALTA:.0%} = Média aptidão "
        f"(otimizar antes) · < {LIMIAR_MEDIA:.0%} = Baixa aptidão (não automatizar com RPA).",
        "Pontuação ponderada = Peso × Nota. Aderência = soma ponderada ÷ (soma dos pesos × 5).",
        "As fórmulas são recalculadas automaticamente pelo Excel ao abrir o arquivo.",
    ]
    for i, t in enumerate(legenda):
        ws.cell(row=r_leg + i, column=2, value=t)

    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True,
                        showErrorMessage=True, errorTitle="Nota inválida", error="Use um número inteiro de 1 a 5.")
    ws.add_data_validation(dv)
    dv.add(f"E{primeira}:E{ultima}")
    _larguras(ws, {"A": 6, "B": 30, "C": 42, "D": 10, "E": 10, "F": 13, "G": 13, "H": 70, "I": 40})
    ws.freeze_panes = "C7"


def _aba_candidatos(ws) -> None:
    ws["A1"] = "Processos candidatos à automação — comparação preliminar (revisar com a equipe)"
    ws["A1"].font = FONTE_TITULO
    ws["A2"] = "Notas de 1 a 5 (5 = mais favorável ao RPA). Critérios simplificados para triagem inicial."
    cab = ["Processo candidato", "Descrição", "Baseado em regras", "Entrada estruturada",
           "Estabilidade da interface", "Volume / repetição", "Pouco julgamento humano",
           "Sem integração nativa viável", "Total (máx. 30)", "Aderência (%)", "Decisão", "Por quê"]
    _cabecalho(ws, 4, cab)
    candidatos = [
        ("A) Cadastro de denúncias recebidas por planilhas de parceiros / canais não digitais",
         "Operador digita no formulário do AcessaCidade cada denúncia que chega por planilha ou e-mail de associações.",
         5, 4, 4, 3, 5, 3, "ESCOLHIDO",
         "Tarefa repetitiva, baseada em regras, com formulário de ids estáveis e ganho direto ao cidadão. "
         "Os parceiros não conseguem consumir a API; o robô faz a ponte."),
        ("B) Envio semanal de relatório de indicadores para as associações",
         "Exportar indicadores do painel, montar planilha e enviar por e-mail.",
         4, 5, 4, 1, 4, 1, "NÃO ESCOLHIDO",
         "Os dados já estão disponíveis via API (/api/indicadores) e pipeline (camada Gold): integração nativa/BI "
         "resolve melhor que RPA. Volume baixo (1 vez por semana)."),
        ("C) Revisão da triagem das fotos e mudança de status",
         "Equipe confere a análise de visão computacional e muda o status da denúncia.",
         1, 3, 4, 3, 1, 3, "NÃO AUTOMATIZAR",
         "Exige julgamento humano por princípio (IA responsável: pessoa no circuito). Automatizar contrariaria a "
         "regra do produto de revisão humana."),
    ]
    for i, (proc, desc, n1, n2, n3, n4, n5, n6, dec, pq) in enumerate(candidatos):
        r = 5 + i
        vals = [proc, desc, n1, n2, n3, n4, n5, n6, f"=SUM(C{r}:H{r})", f"=I{r}/30", dec, pq]
        for c, v in enumerate(vals, start=1):
            cel = ws.cell(row=r, column=c, value=v)
            cel.alignment = QUEBRA
            cel.border = BORDA
        ws.cell(row=r, column=10).number_format = "0%"
        if dec == "ESCOLHIDO":
            for c in range(1, 13):
                ws.cell(row=r, column=c).fill = PREENCH_TOTAL
    _larguras(ws, {"A": 40, "B": 48, "C": 11, "D": 11, "E": 11, "F": 11, "G": 11, "H": 11, "I": 11,
                   "J": 11, "K": 18, "L": 70})
    ws["A9"] = ("Critério eliminatório: 'Pouco julgamento humano' = 1 significa que a decisão deve continuar "
                "humana (IA responsável), independentemente da pontuação total.")
    ws["A10"] = "'Sem integração nativa viável': 5 = não existe alternativa por API; 1 = a API/pipeline já resolve."
    return candidatos


def gerar_assessment() -> tuple[Path, dict, list]:
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessment"
    _aba_assessment(ws, preenchida=True)
    _aba_assessment(wb.create_sheet("Modelo em branco"), preenchida=False)
    candidatos = _aba_candidatos(wb.create_sheet("Processos candidatos"))
    leia = wb.create_sheet("LEIAME")
    for i, t in enumerate([
        "Assessment de automatizabilidade do AcessaCidade (disciplina 05 — RPA).",
        "Aba Assessment: avaliação PRELIMINAR preenchida pela equipe — REVISAR COM A EQUIPE antes da entrega.",
        "Volume, frequência e tempo manual são PREMISSAS (hipóteses), não medições. Substitua pelos dados reais.",
        "Aba Modelo em branco: mesmo modelo, com fórmulas, para uma nova avaliação.",
        "Aba Processos candidatos: comparação de 3 processos e justificativa da escolha.",
        "Gerado por: 05-Robotic-Process-Automation/scripts/gerar_planilhas.py (fórmulas recalculadas ao abrir).",
    ], start=1):
        leia.cell(row=i, column=1, value=t)
    leia.column_dimensions["A"].width = 110
    wb.calculation.fullCalcOnLoad = True
    ASSESSMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ASSESSMENT_PATH)
    return ASSESSMENT_PATH, calcular_assessment(), candidatos


def main() -> int:
    entrada = gerar_entrada()
    config = gerar_config()
    assessment, resultado, candidatos = gerar_assessment()
    print(f"[ok] {entrada.relative_to(BASE)}  ({len(LINHAS_ENTRADA)} linhas simuladas)")
    print(f"[ok] {config.relative_to(BASE)}  ({len(CONFIG)} parâmetros)")
    print(f"[ok] {assessment.relative_to(BASE)}")
    print("\nAssessment (valores calculados em Python — o Excel mostra os mesmos ao abrir):")
    print(f"  {'Critério':38s} {'Peso':>5s} {'Nota':>5s} {'Pond.':>6s}")
    for l in resultado["linhas"]:
        print(f"  {l['criterio']:38s} {l['peso']:5d} {l['nota']:5d} {l['ponderada']:6d}")
    print(f"  Soma dos pesos: {resultado['soma_pesos']}")
    print(f"  Pontuação ponderada: {resultado['pontuacao_ponderada']} de {resultado['pontuacao_maxima']}")
    print(f"  Aderência: {resultado['percentual']:.1%}  ->  {resultado['classificacao']}")
    print("\nProcessos candidatos:")
    for c in candidatos:
        total = sum(c[2:8])
        print(f"  {c[0][:70]:70s} total={total}/30 ({total / 30:.0%})  {c[8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
