"""Testes estruturais dos artefatos da disciplina 05 (RPA).

Verificam o que é possível verificar FORA do UiPath Studio:
- todos os .xaml e .bpmn são XML bem-formado;
- project.json é JSON válido, aponta para Main.xaml e declara as dependências esperadas;
- os seletores dos XAML usam os ids do contrato (seção 7) e o formulário em #/registrar?canal=rpa;
- os argumentos passados em Invoke Workflow File existem no workflow invocado;
- cada elemento de fluxo dos .bpmn tem BPMNShape e cada fluxo tem BPMNEdge.

Eles NÃO substituem a abertura e execução do projeto no UiPath Studio (ver PENDENCIAS_E_ACOES_MANUAIS.txt).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from lxml import etree

BASE = Path(__file__).resolve().parents[1]  # 05-Robotic-Process-Automation
PROJETO = BASE / "UiPath" / "AcessaCidade.RPA"
MAPEAMENTO = BASE / "process-mapping"

XAMLS = sorted(PROJETO.rglob("*.xaml"))
BPMNS = sorted(MAPEAMENTO.glob("*.bpmn"))

NS_X = "http://schemas.microsoft.com/winfx/2006/xaml"
NS_UI = "http://schemas.uipath.com/workflow/activities"
NS_SAP2010 = "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
NS_BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS_BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"

WORKFLOWS_ESPERADOS = {
    "Main.xaml",
    "Workflows/CarregarConfiguracao.xaml",
    "Workflows/ProcessarDenuncia.xaml",
    "Workflows/RegistrarResultado.xaml",
}

# Contrato, seção 7 — ids do formulário usados pelo robô
IDS_FORMULARIO = [
    "campo-nome", "campo-logradouro", "campo-numero", "campo-bairro", "campo-cidade",
    "campo-referencia", "campo-tipo", "campo-descricao", "campo-impacto", "campo-foto",
    "campo-consentimento", "botao-enviar", "resultado-envio", "protocolo-gerado",
    "erro-envio", "botao-nova-denuncia",
]


def _rel(p: Path) -> str:
    return p.relative_to(PROJETO).as_posix()


# --------------------------------------------------------------------------- XAML

def test_workflows_esperados_existem():
    encontrados = {_rel(p) for p in XAMLS}
    faltando = WORKFLOWS_ESPERADOS - encontrados
    assert not faltando, f"Workflows ausentes: {faltando}"


@pytest.mark.parametrize("xaml", XAMLS, ids=lambda p: p.name)
def test_xaml_bem_formado_com_namespaces(xaml: Path):
    raiz = etree.parse(str(xaml)).getroot()
    assert etree.QName(raiz).localname == "Activity"
    nsmap = {v for v in raiz.nsmap.values()}
    for ns in (NS_X, NS_UI, NS_SAP2010, "http://schemas.microsoft.com/netfx/2009/xaml/activities"):
        assert ns in nsmap, f"{xaml.name}: namespace ausente {ns}"
    assert raiz.get(f"{{{NS_X}}}Class"), f"{xaml.name}: x:Class ausente"


@pytest.mark.parametrize("xaml", XAMLS, ids=lambda p: p.name)
def test_xaml_tem_anotacoes_explicativas(xaml: Path):
    raiz = etree.parse(str(xaml)).getroot()
    anot = [el for el in raiz.iter() if el.get(f"{{{NS_SAP2010}}}Annotation.AnnotationText")]
    assert len(anot) >= 3, f"{xaml.name}: poucas anotações ({len(anot)})"


@pytest.mark.parametrize("xaml", XAMLS, ids=lambda p: p.name)
def test_xaml_idref_unicos(xaml: Path):
    raiz = etree.parse(str(xaml)).getroot()
    chave = "{http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation}WorkflowViewState.IdRef"
    ids = [el.get(chave) for el in raiz.iter() if el.get(chave)]
    repetidos = {i for i in ids if ids.count(i) > 1}
    assert not repetidos, f"{xaml.name}: IdRef repetidos {repetidos}"


def _argumentos_declarados(xaml: Path) -> set[str]:
    raiz = etree.parse(str(xaml)).getroot()
    return {el.get("Name") for el in raiz.iter(f"{{{NS_X}}}Property")}


def test_invoke_workflow_file_aponta_para_arquivos_e_argumentos_existentes():
    total = 0
    for xaml in XAMLS:
        raiz = etree.parse(str(xaml)).getroot()
        for inv in raiz.iter(f"{{{NS_UI}}}InvokeWorkflowFile"):
            total += 1
            nome = inv.get("WorkflowFileName").replace("\\", "/")
            alvo = PROJETO / nome
            assert alvo.exists(), f"{xaml.name} invoca arquivo inexistente: {nome}"
            declarados = _argumentos_declarados(alvo)
            for arg in inv.iter():
                chave = arg.get(f"{{{NS_X}}}Key")
                if chave and etree.QName(arg).localname.endswith("Argument"):
                    assert chave in declarados, f"{xaml.name}: argumento {chave} não existe em {nome}"
    assert total >= 3, "Main.xaml deveria invocar os três workflows auxiliares"


def test_main_orquestra_fluxo_completo():
    texto = (PROJETO / "Main.xaml").read_text(encoding="utf-8")
    for trecho in ("CarregarConfiguracao.xaml", "ProcessarDenuncia.xaml", "RegistrarResultado.xaml",
                   "ui:ReadRange", "ui:ForEachRow", "TryCatch", "BusinessRuleException",
                   "SUCESSO", "FALHA_NEGOCIO", "FALHA_SISTEMA"):
        assert trecho in texto, f"Main.xaml sem '{trecho}'"


def test_processar_denuncia_usa_ids_do_contrato():
    texto = (PROJETO / "Workflows" / "ProcessarDenuncia.xaml").read_text(encoding="utf-8")
    texto_sel = texto.replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'").replace("&quot;", '"')
    for id_ in IDS_FORMULARIO:
        assert re.search(rf"webctrl id='{re.escape(id_)}'", texto_sel), f"seletor ausente para #{id_}"
    assert "#/registrar?canal=rpa" in texto, "URL do formulário deve usar ?canal=rpa (origem=RPA)"
    for atividade in ("ui:TypeInto", "ui:SelectItem", "ui:Click", "ui:Check", "ui:ElementExists", "ui:GetValue"):
        assert atividade in texto, f"atividade {atividade} ausente"


def test_carregar_configuracao_le_aba_settings():
    texto = (PROJETO / "Workflows" / "CarregarConfiguracao.xaml").read_text(encoding="utf-8")
    assert "Settings" in texto and "ui:ReadRange" in texto
    assert "URL_ACESSACIDADE" in texto


def test_registrar_resultado_escreve_colunas_de_saida():
    texto = (PROJETO / "Workflows" / "RegistrarResultado.xaml").read_text(encoding="utf-8")
    for col in ("Status_Robo", "Protocolo", "Mensagem", "Data_Hora_Processamento"):
        assert col in texto
    assert "ui:WriteRange" in texto


# --------------------------------------------------------------------------- project.json

def test_project_json_valido():
    dados = json.loads((PROJETO / "project.json").read_text(encoding="utf-8"))
    assert dados["main"] == "Main.xaml"
    assert (PROJETO / dados["main"]).exists()
    assert dados["expressionLanguage"] == "VisualBasic"
    assert dados["targetFramework"] == "Windows"
    for pacote in ("UiPath.System.Activities", "UiPath.UIAutomation.Activities", "UiPath.Excel.Activities"):
        assert pacote in dados["dependencies"], f"dependência ausente: {pacote}"
        assert re.match(r"^\[?\d+\.\d+\.\d+", dados["dependencies"][pacote])
    assert any(e["filePath"] == "Main.xaml" for e in dados["entryPoints"])


def test_gitignore_exclui_pastas_locais_do_studio():
    texto = (PROJETO / ".gitignore").read_text(encoding="utf-8")
    assert ".local/" in texto and ".objects/" in texto


# --------------------------------------------------------------------------- BPMN

ELEMENTOS_FLUXO = {
    "startEvent", "endEvent", "task", "userTask", "serviceTask", "manualTask", "scriptTask",
    "sendTask", "receiveTask", "businessRuleTask", "exclusiveGateway", "parallelGateway",
    "inclusiveGateway", "eventBasedGateway", "intermediateCatchEvent", "intermediateThrowEvent",
    "boundaryEvent", "subProcess", "callActivity", "dataObjectReference", "dataStoreReference",
    "textAnnotation", "lane", "participant",
}


def test_existem_as_is_e_to_be():
    nomes = {p.name for p in BPMNS}
    assert any("AS-IS" in n for n in nomes) and any("TO-BE" in n for n in nomes), nomes


@pytest.mark.parametrize("bpmn", BPMNS, ids=lambda p: p.name)
def test_bpmn_bem_formado_e_com_diagrama(bpmn: Path):
    raiz = etree.parse(str(bpmn)).getroot()
    ns = {"bpmn": NS_BPMN, "bpmndi": NS_BPMNDI}
    assert etree.QName(raiz).localname == "definitions"
    assert raiz.xpath("//bpmndi:BPMNDiagram/bpmndi:BPMNPlane", namespaces=ns)

    shapes = {s.get("bpmnElement") for s in raiz.xpath("//bpmndi:BPMNShape", namespaces=ns)}
    edges = {e.get("bpmnElement"): e for e in raiz.xpath("//bpmndi:BPMNEdge", namespaces=ns)}

    elementos = [el for el in raiz.iter() if isinstance(el.tag, str)
                 and el.tag.startswith(f"{{{NS_BPMN}}}") and etree.QName(el).localname in ELEMENTOS_FLUXO]
    assert len(elementos) >= 8
    for el in elementos:
        assert el.get("id") in shapes, f"{bpmn.name}: elemento {el.get('id')} sem BPMNShape"

    for s in raiz.xpath("//bpmndi:BPMNShape", namespaces=ns):
        b = s.find(f"{{http://www.omg.org/spec/DD/20100524/DC}}Bounds")
        assert b is not None and float(b.get("width")) > 0 and float(b.get("height")) > 0

    ids = {el.get("id") for el in raiz.iter() if isinstance(el.tag, str) and el.get("id")}
    fluxos = raiz.xpath("//bpmn:sequenceFlow | //bpmn:association", namespaces=ns)
    assert fluxos
    for f in fluxos:
        fid = f.get("id")
        assert fid in edges, f"{bpmn.name}: fluxo {fid} sem BPMNEdge"
        waypoints = edges[fid].findall("{http://www.omg.org/spec/DD/20100524/DI}waypoint")
        assert len(waypoints) >= 2
        origem = f.get("sourceRef") or f.get("sourceRef")
        assert origem in ids and f.get("targetRef") in ids

    # incoming/outgoing coerentes com os sequenceFlow
    for f in raiz.xpath("//bpmn:sequenceFlow", namespaces=ns):
        src = raiz.xpath(f"//*[@id='{f.get('sourceRef')}']")[0]
        tgt = raiz.xpath(f"//*[@id='{f.get('targetRef')}']")[0]
        assert f.get("id") in [o.text for o in src.findall(f"{{{NS_BPMN}}}outgoing")]
        assert f.get("id") in [i.text for i in tgt.findall(f"{{{NS_BPMN}}}incoming")]


def test_bpmn_to_be_tem_raia_do_robo():
    to_be = next(p for p in BPMNS if "TO-BE" in p.name)
    raiz = etree.parse(str(to_be)).getroot()
    raias = [l.get("name") for l in raiz.iter(f"{{{NS_BPMN}}}lane")]
    assert any("Robô" in (r or "") for r in raias), raias
    assert any("AcessaCidade" in (r or "") for r in raias), raias
