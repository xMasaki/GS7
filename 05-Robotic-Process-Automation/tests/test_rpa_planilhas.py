"""Testes das planilhas da disciplina 05 (RPA): entrada SIMULADA, Config.xlsx e assessment.

Os rótulos de tipo/impacto são lidos diretamente do contrato (docs/CONTRATOS_DE_INTEGRACAO.md,
seções 3.1 e 3.2), para garantir que o texto usado pelo robô no Select Item é exatamente o texto
visível das opções do formulário.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
from openpyxl import load_workbook

BASE = Path(__file__).resolve().parents[1]  # 05-Robotic-Process-Automation
RAIZ = BASE.parent
CONTRATO = RAIZ / "docs" / "CONTRATOS_DE_INTEGRACAO.md"
ENTRADA = BASE / "spreadsheet" / "denuncias_para_cadastro_SIMULADAS.xlsx"
ASSESSMENT = BASE / "spreadsheet" / "assessment_rpa_AcessaCidade.xlsx"
CONFIG = BASE / "UiPath" / "AcessaCidade.RPA" / "Data" / "Config.xlsx"
PROJETO = BASE / "UiPath" / "AcessaCidade.RPA"
FOTOS = RAIZ / "data" / "samples" / "fotos"

COLUNAS_ENTRADA = ["Nome", "Logradouro", "Numero", "Bairro", "Cidade", "Ponto_Referencia",
                   "Tipo_Obstaculo", "Descricao", "Impacto", "Caminho_Imagem", "Data_Registro"]
COLUNAS_SAIDA = ["Status_Robo", "Protocolo", "Mensagem", "Data_Hora_Processamento"]
CHAVES_CONFIG = ["URL_ACESSACIDADE", "CAMINHO_PLANILHA_ENTRADA", "CAMINHO_PLANILHA_SAIDA",
                 "PASTA_IMAGENS", "TIMEOUT_SEGUNDOS", "NAVEGADOR"]


def _rotulos_contrato(secao: str) -> list[str]:
    """Extrai a coluna 'Rótulo' da tabela da seção indicada (ex.: '3.1')."""
    texto = CONTRATO.read_text(encoding="utf-8")
    inicio = texto.index(f"### {secao} ")
    fim = texto.index("###", inicio + 4)
    rotulos = []
    for linha in texto[inicio:fim].splitlines():
        m = re.match(r"^\|\s*`([A-Z_]+)`\s*\|\s*(.+?)\s*\|", linha)
        if m:
            rotulos.append(m.group(2))
    assert rotulos, f"tabela da seção {secao} não encontrada no contrato"
    return rotulos


TIPOS = _rotulos_contrato("3.1")
IMPACTOS = _rotulos_contrato("3.2")


def _linhas(ws):
    cab = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if any(v not in (None, "") for v in row):
            yield dict(zip(cab, row))


@pytest.fixture(scope="module")
def entrada():
    wb = load_workbook(ENTRADA)
    return wb


# --------------------------------------------------------------------------- entrada

def test_entrada_tem_colunas_esperadas(entrada):
    cab = [c.value for c in entrada["Denuncias"][1]]
    for col in COLUNAS_ENTRADA + COLUNAS_SAIDA:
        assert col in cab, f"coluna ausente: {col}"
    assert cab[: len(COLUNAS_ENTRADA)] == COLUNAS_ENTRADA


def test_entrada_tem_aba_leiame_identificando_simulacao(entrada):
    assert "LEIAME" in entrada.sheetnames
    texto = " ".join(str(c.value) for row in entrada["LEIAME"].iter_rows() for c in row if c.value)
    assert "SIMULAD" in texto.upper() or "FICT" in texto.upper()


def test_entrada_linhas_ficticias_e_rotulos_do_contrato(entrada):
    linhas = list(_linhas(entrada["Denuncias"]))
    assert 10 <= len(linhas) <= 15
    for i, l in enumerate(linhas, start=2):
        assert l["Cidade"] == "Cidade Exemplo", f"linha {i}"
        assert str(l["Nome"]).startswith("Robô Teste"), f"linha {i}: nome deve ser fictício"
        assert l["Tipo_Obstaculo"] in TIPOS, f"linha {i}: rótulo de tipo fora do contrato: {l['Tipo_Obstaculo']}"
        assert l["Impacto"] in IMPACTOS, f"linha {i}: rótulo de impacto fora do contrato: {l['Impacto']}"
        for col in COLUNAS_SAIDA:
            assert l[col] in (None, ""), f"linha {i}: coluna de saída {col} deveria estar vazia"


def test_entrada_descricoes_validas_exceto_cenarios_negativos(entrada):
    linhas = list(_linhas(entrada["Denuncias"]))
    positivas = [l for l in linhas if not str(l.get("Cenario_Teste") or "").startswith("NEGATIVO")]
    negativas = [l for l in linhas if str(l.get("Cenario_Teste") or "").startswith("NEGATIVO")]
    assert len(positivas) >= 10
    for l in positivas:
        assert 10 <= len(l["Descricao"]) <= 1000
        assert 3 <= len(l["Logradouro"]) <= 120
        assert 2 <= len(l["Bairro"]) <= 80
        assert "SIMULADO" in l["Descricao"].upper(), "descrição deve se identificar como simulada"
    # os cenários negativos existem para demonstrar o tratamento de exceção de negócio
    assert negativas, "deve haver pelo menos uma linha negativa (FALHA_NEGOCIO esperada)"


def test_entrada_tem_linhas_com_e_sem_imagem(entrada):
    linhas = list(_linhas(entrada["Denuncias"]))
    com = [l for l in linhas if l["Caminho_Imagem"]]
    sem = [l for l in linhas if not l["Caminho_Imagem"]]
    assert com and sem
    for l in com:
        assert re.match(r"^sintetica_[a-z_]+_\d{2}\.jpg$", l["Caminho_Imagem"]), l["Caminho_Imagem"]


def test_imagens_referenciadas_existem(entrada):
    if not FOTOS.is_dir():
        pytest.skip("data/samples/fotos ainda não existe (depende do gerador de imagens da disciplina 04)")
    for l in _linhas(entrada["Denuncias"]):
        if l["Caminho_Imagem"]:
            assert (FOTOS / l["Caminho_Imagem"]).is_file(), f"imagem ausente: {l['Caminho_Imagem']}"


# --------------------------------------------------------------------------- Config.xlsx

def test_config_tem_chaves_obrigatorias():
    wb = load_workbook(CONFIG)
    ws = wb["Settings"]
    assert [ws["A1"].value, ws["B1"].value] == ["Nome", "Valor"]
    cfg = {r[0]: r[1] for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}
    for chave in CHAVES_CONFIG:
        assert chave in cfg and str(cfg[chave]).strip(), f"Config sem {chave}"
    assert re.match(r"^https?://", cfg["URL_ACESSACIDADE"])
    assert int(cfg["TIMEOUT_SEGUNDOS"]) > 0


def test_config_caminhos_relativos_resolvem_a_partir_do_projeto():
    """O UiPath executa com a pasta do projeto como diretório de trabalho."""
    wb = load_workbook(CONFIG)
    cfg = {r[0]: r[1] for r in wb["Settings"].iter_rows(min_row=2, values_only=True) if r[0]}
    entrada = (PROJETO / cfg["CAMINHO_PLANILHA_ENTRADA"].replace("\\", "/")).resolve()
    assert entrada == ENTRADA.resolve()
    saida = (PROJETO / cfg["CAMINHO_PLANILHA_SAIDA"].replace("\\", "/")).resolve()
    assert saida.parent == ENTRADA.parent.resolve()
    pasta = (PROJETO / cfg["PASTA_IMAGENS"].replace("\\", "/")).resolve()
    assert pasta == FOTOS.resolve()


def test_config_sem_segredos():
    wb = load_workbook(CONFIG)
    for r in wb["Settings"].iter_rows(min_row=2, values_only=True):
        if r[0]:
            assert not re.search(r"(token|senha|password|secret|chave_api)", str(r[0]), re.I)


# --------------------------------------------------------------------------- assessment

def _carregar_gerador():
    spec = importlib.util.spec_from_file_location("gerar_planilhas_rpa", BASE / "scripts" / "gerar_planilhas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_assessment_abas_e_formulas():
    wb = load_workbook(ASSESSMENT)
    for aba in ("Assessment", "Modelo em branco", "Processos candidatos"):
        assert aba in wb.sheetnames
    ws = wb["Assessment"]
    assert "PRELIMINAR" in str(ws["B3"].value).upper()
    formulas = [c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
    assert any("SUM(" in f for f in formulas)
    assert any("Alta aptidão" in f for f in formulas)


def test_assessment_valores_conferem_com_calculo_python():
    """Recalcula a planilha em Python (Peso × Nota) e compara com o cálculo do gerador."""
    wb = load_workbook(ASSESSMENT)
    ws = wb["Assessment"]
    pesos, notas = [], []
    for r in range(7, 18):
        pesos.append(float(ws.cell(r, 4).value))
        notas.append(float(ws.cell(r, 5).value))
        assert ws.cell(r, 6).value == f'=IF(E{r}="","",D{r}*E{r})'
        assert 1 <= notas[-1] <= 5
        assert str(ws.cell(r, 8).value or "").strip(), f"linha {r} sem justificativa"
    assert sum(pesos) == 100
    pct = sum(p * n for p, n in zip(pesos, notas)) / (sum(pesos) * 5)
    calc = _carregar_gerador().calcular_assessment()
    assert abs(pct - calc["percentual"]) < 1e-9
    assert calc["classificacao"].startswith("Alta") == (pct >= 0.70)


def test_modelo_em_branco_sem_notas():
    ws = load_workbook(ASSESSMENT)["Modelo em branco"]
    assert all(ws.cell(r, 5).value in (None, "") for r in range(7, 18))
