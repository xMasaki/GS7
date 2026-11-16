"""Gera os diagramas BPMN 2.0 (As-Is e To-Be) do processo automatizado pelo robô AcessaCidade.RPA.

Saídas em 05-Robotic-Process-Automation/process-mapping/:
  AS-IS_cadastro_denuncias.bpmn   -> BPMN 2.0 XML com diagrama (BPMNDiagram/BPMNShape/BPMNEdge)
  TO-BE_cadastro_denuncias.bpmn   -> idem
  AS-IS_cadastro_denuncias.svg    -> renderização SIMPLIFICADA do mesmo layout (para o relatório)
  TO-BE_cadastro_denuncias.svg

Os .bpmn abrem em https://demo.bpmn.io (File > Open) ou no Camunda Modeler. Os .svg são desenhados por
este script a partir das mesmas coordenadas; para a figura "oficial" do relatório, exporte a imagem pelo
bpmn.io/Camunda Modeler (ver process-mapping/MAPEAMENTO_PROCESSOS.md).

Uso:  .\\.venv\\Scripts\\python.exe 05-Robotic-Process-Automation\\scripts\\gerar_bpmn.py
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

BASE = Path(__file__).resolve().parents[1]
SAIDA = BASE / "process-mapping"

# Dimensões (px)
POOL_X, POOL_Y = 150, 80
POOL_LABEL_W = 30
LANE_LABEL_W = 30
COL0_X = POOL_X + POOL_LABEL_W + LANE_LABEL_W + 30  # borda esquerda da coluna 0
COL_W = 165
ROW_H = 130
LANE_BASE_H = 200
CENTER_OFFSET = 120  # centro vertical do elemento na 1ª linha da raia
SIZES = {
    "startEvent": (36, 36), "endEvent": (36, 36), "exclusiveGateway": (50, 50),
    "task": (120, 80), "userTask": (120, 80), "serviceTask": (120, 80), "manualTask": (120, 80),
    "sendTask": (120, 80), "receiveTask": (120, 80),
}
TASK_TYPES = {"task", "userTask", "serviceTask", "manualTask", "sendTask", "receiveTask"}


@dataclass
class Node:
    id: str
    tipo: str
    nome: str
    lane: str
    col: int
    row: int = 0
    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0
    incoming: list = field(default_factory=list)
    outgoing: list = field(default_factory=list)

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2


@dataclass
class Flow:
    id: str
    src: str
    tgt: str
    nome: str = ""
    via: str = ""  # "acima" = laço roteado pelo topo da raia
    pontos: list = field(default_factory=list)


@dataclass
class Anotacao:
    id: str
    texto: str
    alvo: str
    x: float = 0
    y: float = 0
    w: float = 175
    h: float = 62


@dataclass
class Processo:
    chave: str          # AsIs / ToBe
    titulo: str
    lanes: list         # [(id, nome, linhas)]
    nodes: list
    flows: list
    anotacoes: list


def _layout(p: Processo) -> dict:
    lane_geo = {}
    y = POOL_Y
    for lane_id, _nome, linhas in p.lanes:
        h = LANE_BASE_H + (linhas - 1) * ROW_H
        lane_geo[lane_id] = (y, h)
        y += h
    pool_h = y - POOL_Y
    max_col = max(n.col for n in p.nodes)
    pool_w = (COL0_X - POOL_X) + (max_col + 1) * COL_W + 40
    nodes = {n.id: n for n in p.nodes}
    for n in p.nodes:
        n.w, n.h = SIZES[n.tipo]
        lane_top, _ = lane_geo[n.lane]
        cx = COL0_X + n.col * COL_W + 60
        cy = lane_top + CENTER_OFFSET + n.row * ROW_H
        n.x, n.y = cx - n.w / 2, cy - n.h / 2
    for f in p.flows:
        s, t = nodes[f.src], nodes[f.tgt]
        s.outgoing.append(f.id)
        t.incoming.append(f.id)
        f.pontos = _rota(s, t, lane_geo, f.via)
    for a in p.anotacoes:
        alvo = nodes[a.alvo]
        lane_top, _ = lane_geo[alvo.lane]
        a.x = alvo.cx + 8
        a.y = lane_top + 6
    return {"lanes": lane_geo, "pool": (POOL_X, POOL_Y, pool_w, pool_h), "nodes": nodes}


def _rota(s: Node, t: Node, lane_geo, via: str = "") -> list:
    sy, ty = s.cy, t.cy
    if via == "acima":
        lane_top, _ = lane_geo[s.lane]
        ya = lane_top + 74
        return [(s.cx, s.y), (s.cx, ya), (t.cx, ya), (t.cx, t.y)]
    if t.cx > s.cx + 1:
        if abs(sy - ty) < 1:
            return [(s.x + s.w, sy), (t.x, ty)]
        if s.tipo == "exclusiveGateway":
            sai = s.y + s.h if ty > sy else s.y
            return [(s.cx, sai), (s.cx, ty), (t.x, ty)]
        if t.tipo == "exclusiveGateway" and t.lane == s.lane:
            entra = t.y if sy < ty else t.y + t.h
            return [(s.x + s.w, sy), (t.cx, sy), (t.cx, entra)]
        mx = (s.x + s.w + t.x) / 2
        return [(s.x + s.w, sy), (mx, sy), (mx, ty), (t.x, ty)]
    if abs(t.cx - s.cx) <= 1:
        if ty < sy:
            return [(s.cx, s.y), (t.cx, t.y + t.h)]
        return [(s.cx, s.y + s.h), (t.cx, t.y)]
    # alvo à esquerda (retorno/laço)
    if abs(sy - ty) < 1:
        lane_top, lane_h = lane_geo[s.lane]
        yb = lane_top + lane_h - 14
        return [(s.cx, s.y + s.h), (s.cx, yb), (t.cx, yb), (t.cx, t.y + t.h)]
    entra = t.y if sy < ty else t.y + t.h
    return [(s.x, sy), (t.cx, sy), (t.cx, entra)]


def _wrap(texto: str, largura: int) -> list[str]:
    return textwrap.wrap(texto, width=largura) or [""]


# ---------------------------------------------------------------------------
# BPMN XML
# ---------------------------------------------------------------------------
def gerar_bpmn_xml(p: Processo) -> str:
    geo = _layout(p)
    nodes = geo["nodes"]
    k = p.chave
    out = []
    w = out.append
    w('<?xml version="1.0" encoding="UTF-8"?>')
    w('<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"'
      ' xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"'
      ' xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"'
      ' xmlns:di="http://www.omg.org/spec/DD/20100524/DI"'
      ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
      f' id="Definitions_{k}" targetNamespace="http://bpmn.io/schema/bpmn"'
      ' exporter="AcessaCidade gerar_bpmn.py" exporterVersion="1.0">')
    w(f'  <bpmn:collaboration id="Collaboration_{k}">')
    w(f'    <bpmn:participant id="Participant_{k}" name="{escape(p.titulo)}" processRef="Process_{k}" />')
    w('  </bpmn:collaboration>')
    w(f'  <bpmn:process id="Process_{k}" name="{escape(p.titulo)}" isExecutable="false">')
    w(f'    <bpmn:laneSet id="LaneSet_{k}">')
    for lane_id, nome, _ in p.lanes:
        w(f'      <bpmn:lane id="{lane_id}" name="{escape(nome)}">')
        for n in p.nodes:
            if n.lane == lane_id:
                w(f'        <bpmn:flowNodeRef>{n.id}</bpmn:flowNodeRef>')
        w('      </bpmn:lane>')
    w('    </bpmn:laneSet>')
    for n in p.nodes:
        extra = ""
        w(f'    <bpmn:{n.tipo} id="{n.id}" name="{escape(n.nome)}"{extra}>')
        for fid in n.incoming:
            w(f'      <bpmn:incoming>{fid}</bpmn:incoming>')
        for fid in n.outgoing:
            w(f'      <bpmn:outgoing>{fid}</bpmn:outgoing>')
        w(f'    </bpmn:{n.tipo}>')
    for f in p.flows:
        nome = f' name="{escape(f.nome)}"' if f.nome else ""
        w(f'    <bpmn:sequenceFlow id="{f.id}"{nome} sourceRef="{f.src}" targetRef="{f.tgt}" />')
    for a in p.anotacoes:
        w(f'    <bpmn:textAnnotation id="{a.id}">')
        w(f'      <bpmn:text>{escape(a.texto)}</bpmn:text>')
        w('    </bpmn:textAnnotation>')
        w(f'    <bpmn:association id="Association_{a.id}" associationDirection="None" sourceRef="{a.id}" targetRef="{a.alvo}" />')
    w('  </bpmn:process>')
    w(f'  <bpmndi:BPMNDiagram id="BPMNDiagram_{k}">')
    w(f'    <bpmndi:BPMNPlane id="BPMNPlane_{k}" bpmnElement="Collaboration_{k}">')
    px, py, pw, ph = geo["pool"]
    w(f'      <bpmndi:BPMNShape id="Participant_{k}_di" bpmnElement="Participant_{k}" isHorizontal="true">')
    w(f'        <dc:Bounds x="{px}" y="{py}" width="{pw:.0f}" height="{ph:.0f}" />')
    w('      </bpmndi:BPMNShape>')
    for lane_id, _nome, _ in p.lanes:
        ly, lh = geo["lanes"][lane_id]
        w(f'      <bpmndi:BPMNShape id="{lane_id}_di" bpmnElement="{lane_id}" isHorizontal="true">')
        w(f'        <dc:Bounds x="{px + POOL_LABEL_W}" y="{ly:.0f}" width="{pw - POOL_LABEL_W:.0f}" height="{lh:.0f}" />')
        w('      </bpmndi:BPMNShape>')
    for n in p.nodes:
        marker = ' isMarkerVisible="true"' if n.tipo == "exclusiveGateway" else ""
        w(f'      <bpmndi:BPMNShape id="{n.id}_di" bpmnElement="{n.id}"{marker}>')
        w(f'        <dc:Bounds x="{n.x:.0f}" y="{n.y:.0f}" width="{n.w:.0f}" height="{n.h:.0f}" />')
        if n.tipo not in TASK_TYPES:
            linhas = _wrap(n.nome, 22)
            lw, lh = 140, 14 * len(linhas)
            ly = n.y + n.h + 6 if n.tipo != "exclusiveGateway" else n.y - lh - 6
            w('        <bpmndi:BPMNLabel>')
            w(f'          <dc:Bounds x="{n.cx - lw / 2:.0f}" y="{ly:.0f}" width="{lw}" height="{lh}" />')
            w('        </bpmndi:BPMNLabel>')
        w('      </bpmndi:BPMNShape>')
    for a in p.anotacoes:
        w(f'      <bpmndi:BPMNShape id="{a.id}_di" bpmnElement="{a.id}">')
        w(f'        <dc:Bounds x="{a.x:.0f}" y="{a.y:.0f}" width="{a.w:.0f}" height="{a.h:.0f}" />')
        w('      </bpmndi:BPMNShape>')
    for f in p.flows:
        w(f'      <bpmndi:BPMNEdge id="{f.id}_di" bpmnElement="{f.id}">')
        for x, y in f.pontos:
            w(f'        <di:waypoint x="{x:.0f}" y="{y:.0f}" />')
        if f.nome:
            (x0, y0), (x1, y1) = f.pontos[0], f.pontos[1]
            w('        <bpmndi:BPMNLabel>')
            w(f'          <dc:Bounds x="{(x0 + x1) / 2 + 4:.0f}" y="{(y0 + y1) / 2 - 18:.0f}" width="{max(30, 7 * len(f.nome)):.0f}" height="14" />')
            w('        </bpmndi:BPMNLabel>')
        w('      </bpmndi:BPMNEdge>')
    for a in p.anotacoes:
        alvo = nodes[a.alvo]
        w(f'      <bpmndi:BPMNEdge id="Association_{a.id}_di" bpmnElement="Association_{a.id}">')
        w(f'        <di:waypoint x="{a.x + 10:.0f}" y="{a.y + a.h:.0f}" />')
        w(f'        <di:waypoint x="{alvo.cx + 20:.0f}" y="{alvo.y:.0f}" />')
        w('      </bpmndi:BPMNEdge>')
    w('    </bpmndi:BPMNPlane>')
    w('  </bpmndi:BPMNDiagram>')
    w('</bpmn:definitions>')
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# SVG simplificado (mesmo layout)
# ---------------------------------------------------------------------------
CORES = {"userTask": "#DDEBF7", "serviceTask": "#E2EFDA", "manualTask": "#FFF2CC", "task": "#FFFFFF",
         "sendTask": "#FFFFFF", "receiveTask": "#FFFFFF"}
ROTULO_TIPO = {"userTask": "Usuário", "serviceTask": "Automática", "manualTask": "Manual"}


def gerar_svg(p: Processo) -> str:
    geo = _layout(p)
    nodes = geo["nodes"]
    px, py, pw, ph = geo["pool"]
    W, H = px + pw + 40, py + ph + 60
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
      'font-family="Segoe UI, Arial, sans-serif" font-size="11">')
    a('<defs><marker id="seta" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">'
      '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>')
    a(f'<rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#FFFFFF"/>')
    a(f'<text x="{px}" y="{py - 30}" font-size="16" font-weight="bold" fill="#1F4E79">{escape(p.titulo)}</text>')
    a(f'<text x="{px}" y="{py - 12}" font-size="11" fill="#555">Renderização simplificada gerada por '
      'scripts/gerar_bpmn.py a partir do mesmo layout do arquivo .bpmn (abra o .bpmn no bpmn.io para a versão oficial).</text>')
    a(f'<rect x="{px}" y="{py}" width="{pw:.0f}" height="{ph:.0f}" fill="none" stroke="#333" stroke-width="1.5"/>')
    a(f'<text transform="translate({px + 19},{py + ph / 2:.0f}) rotate(-90)" text-anchor="middle" font-weight="bold">'
      f'{escape(p.titulo[:80])}</text>')
    for lane_id, nome, _ in p.lanes:
        ly, lh = geo["lanes"][lane_id]
        a(f'<rect x="{px + POOL_LABEL_W}" y="{ly:.0f}" width="{pw - POOL_LABEL_W:.0f}" height="{lh:.0f}" fill="none" stroke="#333"/>')
        a(f'<line x1="{px + POOL_LABEL_W + LANE_LABEL_W}" y1="{ly:.0f}" x2="{px + POOL_LABEL_W + LANE_LABEL_W}" y2="{ly + lh:.0f}" stroke="#333"/>')
        a(f'<text transform="translate({px + POOL_LABEL_W + 19},{ly + lh / 2:.0f}) rotate(-90)" text-anchor="middle">{escape(nome)}</text>')
    for an in p.anotacoes:
        alvo = nodes[an.alvo]
        a(f'<path d="M{an.x + 12:.0f},{an.y:.0f} L{an.x:.0f},{an.y:.0f} L{an.x:.0f},{an.y + an.h:.0f} L{an.x + 12:.0f},{an.y + an.h:.0f}" fill="none" stroke="#C00000"/>')
        a(f'<line x1="{an.x + 10:.0f}" y1="{an.y + an.h:.0f}" x2="{alvo.cx + 20:.0f}" y2="{alvo.y:.0f}" stroke="#C00000" stroke-dasharray="4,3"/>')
        for i, linha in enumerate(_wrap(an.texto, 32)[:4]):
            a(f'<text x="{an.x + 5:.0f}" y="{an.y + 13 + i * 13:.0f}" fill="#C00000" font-size="10">{escape(linha)}</text>')
    for f in p.flows:
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in f.pontos)
        a(f'<polyline points="{pts}" fill="none" stroke="#333" stroke-width="1.3" marker-end="url(#seta)"/>')
        if f.nome:
            (x0, y0), (x1, y1) = f.pontos[0], f.pontos[1]
            a(f'<text x="{(x0 + x1) / 2 + 4:.0f}" y="{(y0 + y1) / 2 - 5:.0f}" font-size="10" fill="#1F4E79">{escape(f.nome)}</text>')
    for n in p.nodes:
        if n.tipo in TASK_TYPES:
            a(f'<rect x="{n.x:.0f}" y="{n.y:.0f}" width="{n.w:.0f}" height="{n.h:.0f}" rx="10" fill="{CORES[n.tipo]}" stroke="#333" stroke-width="1.3"/>')
            if n.tipo in ROTULO_TIPO:
                a(f'<text x="{n.x + 5:.0f}" y="{n.y + 11:.0f}" font-size="8" fill="#666">{ROTULO_TIPO[n.tipo]}</text>')
            linhas = _wrap(n.nome, 20)[:5]
            y0 = n.cy - (len(linhas) - 1) * 6.5 + 4
            for i, linha in enumerate(linhas):
                a(f'<text x="{n.cx:.0f}" y="{y0 + i * 13:.0f}" text-anchor="middle">{escape(linha)}</text>')
        elif n.tipo == "exclusiveGateway":
            a(f'<polygon points="{n.cx:.0f},{n.y:.0f} {n.x + n.w:.0f},{n.cy:.0f} {n.cx:.0f},{n.y + n.h:.0f} {n.x:.0f},{n.cy:.0f}" fill="#FFF" stroke="#333" stroke-width="1.3"/>')
            a(f'<text x="{n.cx:.0f}" y="{n.cy + 6:.0f}" text-anchor="middle" font-size="18" font-weight="bold">×</text>')
            linhas = _wrap(n.nome, 22)
            for i, linha in enumerate(linhas):
                a(f'<text x="{n.cx:.0f}" y="{n.y - 8 - (len(linhas) - 1 - i) * 13:.0f}" text-anchor="middle">{escape(linha)}</text>')
        else:
            sw = 3.5 if n.tipo == "endEvent" else 1.5
            a(f'<circle cx="{n.cx:.0f}" cy="{n.cy:.0f}" r="18" fill="#FFF" stroke="#333" stroke-width="{sw}"/>')
            for i, linha in enumerate(_wrap(n.nome, 22)):
                a(f'<text x="{n.cx:.0f}" y="{n.y + n.h + 16 + i * 13:.0f}" text-anchor="middle">{escape(linha)}</text>')
    a('</svg>')
    return "\n".join(s) + "\n"


# ---------------------------------------------------------------------------
# Definição dos processos
# ---------------------------------------------------------------------------
def processo_as_is() -> Processo:
    lanes = [("Lane_AsIs_Associacao", "Cidadão / Associação", 1),
             ("Lane_AsIs_Operador", "Operador AcessaCidade", 1),
             ("Lane_AsIs_Sistema", "AcessaCidade (web)", 1)]
    A, O, S = (l[0] for l in lanes)
    nodes = [
        Node("Start_AsIs", "startEvent", "Problema de acessibilidade identificado", A, 0),
        Node("Task_AsIs_Registrar", "manualTask", "Registrar denúncia em papel, planilha ou e-mail", A, 1),
        Node("Task_AsIs_Enviar", "sendTask", "Enviar planilha ou e-mail ao operador", A, 2),
        Node("Task_AsIs_Abrir", "userTask", "Abrir planilha ou e-mail recebido", O, 3),
        Node("Task_AsIs_Padronizar", "userTask", "Interpretar e padronizar endereço, tipo e impacto", O, 4),
        Node("Gateway_AsIs_Completo", "exclusiveGateway", "Dados completos?", O, 5),
        Node("Task_AsIs_Complementar", "manualTask", "Complementar informações solicitadas", A, 5),
        Node("Task_AsIs_Digitar", "userTask", "Digitar a denúncia campo a campo no formulário web", O, 6),
        Node("Task_AsIs_Gerar", "serviceTask", "Validar, registrar e gerar protocolo", S, 7),
        Node("Task_AsIs_Conferir", "userTask", "Conferir cadastro e copiar protocolo manualmente", O, 8),
        Node("Task_AsIs_Informar", "sendTask", "Informar protocolo à associação por e-mail", O, 9),
        Node("Task_AsIs_Receber", "receiveTask", "Receber protocolo para acompanhamento", A, 10),
        Node("End_AsIs", "endEvent", "Denúncia registrada e protocolo entregue", A, 11),
    ]
    flows = [
        Flow("Flow_AsIs_01", "Start_AsIs", "Task_AsIs_Registrar"),
        Flow("Flow_AsIs_02", "Task_AsIs_Registrar", "Task_AsIs_Enviar"),
        Flow("Flow_AsIs_03", "Task_AsIs_Enviar", "Task_AsIs_Abrir"),
        Flow("Flow_AsIs_04", "Task_AsIs_Abrir", "Task_AsIs_Padronizar"),
        Flow("Flow_AsIs_05", "Task_AsIs_Padronizar", "Gateway_AsIs_Completo"),
        Flow("Flow_AsIs_06", "Gateway_AsIs_Completo", "Task_AsIs_Complementar", "Não"),
        Flow("Flow_AsIs_07", "Task_AsIs_Complementar", "Task_AsIs_Abrir"),
        Flow("Flow_AsIs_08", "Gateway_AsIs_Completo", "Task_AsIs_Digitar", "Sim"),
        Flow("Flow_AsIs_09", "Task_AsIs_Digitar", "Task_AsIs_Gerar"),
        Flow("Flow_AsIs_10", "Task_AsIs_Gerar", "Task_AsIs_Conferir"),
        Flow("Flow_AsIs_11", "Task_AsIs_Conferir", "Task_AsIs_Informar"),
        Flow("Flow_AsIs_12", "Task_AsIs_Informar", "Task_AsIs_Receber"),
        Flow("Flow_AsIs_13", "Task_AsIs_Receber", "End_AsIs"),
    ]
    anot = [
        Anotacao("Annotation_AsIs_Fila", "GARGALO: planilhas acumulam na caixa de e-mail; depende da agenda do operador.",
                 "Task_AsIs_Abrir"),
        Anotacao("Annotation_AsIs_Digitar", "GARGALO: ~10 campos digitados por denúncia; erros de digitação e de categoria.",
                 "Task_AsIs_Digitar"),
        Anotacao("Annotation_AsIs_Conferir", "GARGALO: cópia manual do protocolo; risco de enviar o protocolo errado.",
                 "Task_AsIs_Conferir"),
    ]
    return Processo("AsIs", "AS-IS — Cadastro manual de denúncias recebidas de parceiros", lanes, nodes, flows, anot)


def processo_to_be() -> Processo:
    lanes = [("Lane_ToBe_Associacao", "Cidadão / Associação", 1),
             ("Lane_ToBe_Operador", "Operador AcessaCidade", 1),
             ("Lane_ToBe_Robo", "Robô UiPath (AcessaCidade.RPA)", 2),
             ("Lane_ToBe_Sistema", "AcessaCidade (web)", 1)]
    A, O, R, S = (l[0] for l in lanes)
    nodes = [
        Node("Start_ToBe", "startEvent", "Denúncias coletadas pela associação", A, 0),
        Node("Task_ToBe_Preencher", "manualTask", "Preencher a planilha-modelo padronizada", A, 1),
        Node("Task_ToBe_Enviar", "sendTask", "Enviar a planilha ao AcessaCidade", A, 2),
        Node("Task_ToBe_Iniciar", "userTask", "Salvar planilha na pasta de entrada e iniciar o robô", O, 3),
        Node("Task_ToBe_Config", "serviceTask", "Carregar configuração (Config.xlsx)", R, 4),
        Node("Task_ToBe_Ler", "serviceTask", "Ler planilha de entrada (Read Range)", R, 5),
        Node("Task_ToBe_Validar", "serviceTask", "Validar a linha (regras e rótulos do contrato)", R, 6),
        Node("Gateway_ToBe_Valida", "exclusiveGateway", "Linha válida?", R, 7),
        Node("Task_ToBe_Formulario", "serviceTask", "Preencher e enviar #/registrar?canal=rpa", R, 8),
        Node("Task_ToBe_Registrar", "serviceTask", "Validar, registrar (origem=RPA) e gerar protocolo", S, 9),
        Node("Gateway_ToBe_Protocolo", "exclusiveGateway", "Protocolo capturado?", R, 10),
        Node("Task_ToBe_Sucesso", "serviceTask", "Gravar SUCESSO e protocolo na planilha de saída", R, 11),
        Node("Task_ToBe_Falha", "serviceTask", "Gravar FALHA_NEGOCIO ou FALHA_SISTEMA e mensagem", R, 11, row=1),
        Node("Gateway_ToBe_Mais", "exclusiveGateway", "Há mais linhas?", R, 12),
        Node("Task_ToBe_Resumo", "serviceTask", "Gerar resumo com totais (log)", R, 13),
        Node("Task_ToBe_Excecoes", "userTask", "Tratar somente as exceções (FALHA_*)", O, 14),
        Node("Task_ToBe_Informar", "sendTask", "Enviar planilha de saída com protocolos à associação", O, 15),
        Node("Task_ToBe_Receber", "receiveTask", "Receber protocolos para acompanhamento", A, 16),
        Node("End_ToBe", "endEvent", "Denúncias registradas e protocolos entregues", A, 17),
    ]
    flows = [
        Flow("Flow_ToBe_01", "Start_ToBe", "Task_ToBe_Preencher"),
        Flow("Flow_ToBe_02", "Task_ToBe_Preencher", "Task_ToBe_Enviar"),
        Flow("Flow_ToBe_03", "Task_ToBe_Enviar", "Task_ToBe_Iniciar"),
        Flow("Flow_ToBe_04", "Task_ToBe_Iniciar", "Task_ToBe_Config"),
        Flow("Flow_ToBe_05", "Task_ToBe_Config", "Task_ToBe_Ler"),
        Flow("Flow_ToBe_06", "Task_ToBe_Ler", "Task_ToBe_Validar"),
        Flow("Flow_ToBe_07", "Task_ToBe_Validar", "Gateway_ToBe_Valida"),
        Flow("Flow_ToBe_08", "Gateway_ToBe_Valida", "Task_ToBe_Formulario", "Sim"),
        Flow("Flow_ToBe_09", "Gateway_ToBe_Valida", "Task_ToBe_Falha", "Não"),
        Flow("Flow_ToBe_10", "Task_ToBe_Formulario", "Task_ToBe_Registrar"),
        Flow("Flow_ToBe_11", "Task_ToBe_Registrar", "Gateway_ToBe_Protocolo"),
        Flow("Flow_ToBe_12", "Gateway_ToBe_Protocolo", "Task_ToBe_Sucesso", "Sim"),
        Flow("Flow_ToBe_13", "Gateway_ToBe_Protocolo", "Task_ToBe_Falha", "Não (erro/tempo)"),
        Flow("Flow_ToBe_14", "Task_ToBe_Sucesso", "Gateway_ToBe_Mais"),
        Flow("Flow_ToBe_15", "Task_ToBe_Falha", "Gateway_ToBe_Mais"),
        Flow("Flow_ToBe_16", "Gateway_ToBe_Mais", "Task_ToBe_Validar", "Sim", via="acima"),
        Flow("Flow_ToBe_17", "Gateway_ToBe_Mais", "Task_ToBe_Resumo", "Não"),
        Flow("Flow_ToBe_18", "Task_ToBe_Resumo", "Task_ToBe_Excecoes"),
        Flow("Flow_ToBe_19", "Task_ToBe_Excecoes", "Task_ToBe_Informar"),
        Flow("Flow_ToBe_20", "Task_ToBe_Informar", "Task_ToBe_Receber"),
        Flow("Flow_ToBe_21", "Task_ToBe_Receber", "End_ToBe"),
    ]
    anot = [
        Anotacao("Annotation_ToBe_Inicio", "Futuro: disparo agendado (Orchestrator ou Agendador do Windows).",
                 "Task_ToBe_Iniciar"),
        Anotacao("Annotation_ToBe_Seletores", "Seletores pelos ids estáveis do contrato (seção 7).",
                 "Task_ToBe_Formulario"),
        Anotacao("Annotation_ToBe_Excecoes", "Operador só atua nas linhas com FALHA_* (corrige e reprocessa).",
                 "Task_ToBe_Excecoes"),
    ]
    return Processo("ToBe", "TO-BE — Cadastro automatizado pelo robô UiPath (operador trata exceções)",
                    lanes, nodes, flows, anot)


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for proc, nome in ((processo_as_is(), "AS-IS_cadastro_denuncias"), (processo_to_be(), "TO-BE_cadastro_denuncias")):
        (SAIDA / f"{nome}.bpmn").write_text(gerar_bpmn_xml(proc), encoding="utf-8")
        # o layout é recalculado do zero para o SVG (listas incoming/outgoing reiniciadas)
        proc2 = processo_as_is() if proc.chave == "AsIs" else processo_to_be()
        (SAIDA / f"{nome}.svg").write_text(gerar_svg(proc2), encoding="utf-8")
        print(f"[ok] process-mapping/{nome}.bpmn  ({len(proc.nodes)} elementos, {len(proc.flows)} fluxos, "
              f"{len(proc.lanes)} raias)  + .svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
