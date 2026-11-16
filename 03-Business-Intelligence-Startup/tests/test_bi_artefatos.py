"""Testes dos artefatos e geradores da disciplina 03 (Business Intelligence & Startup Development).

Conferem coisas verificáveis por máquina — não a qualidade do modelo de negócio (que é hipótese até a
validação pela equipe):
- o Lean Canvas tem os 9 blocos, todos com itens e marcados como HIPÓTESE (nada apresentado como validado);
- os arquivos versionados LEAN_CANVAS.md/.html são exatamente o que o gerador produz a partir do JSON;
- os geradores de planilhas e o exportador da Gold para Excel funcionam em pasta temporária;
- os links de entrega estão vazios ou são https:// (nenhum link inventado).
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import openpyxl
import pytest
import yaml

PASTA = Path(__file__).resolve().parents[1]
RAIZ = PASTA.parent
MODELO = PASTA / "business-model"


def _carregar_modulo(caminho: Path):
    spec = importlib.util.spec_from_file_location(caminho.stem + "_mod03", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def lean():
    return _carregar_modulo(PASTA / "scripts" / "gerar_lean_canvas.py")


def test_lean_canvas_tem_9_blocos_com_itens(lean):
    dados = lean.carregar(MODELO / "lean_canvas.json")
    ids = [b["id"] for b in dados["blocos"]]
    assert sorted(ids) == sorted(lean.ORDEM)
    assert len(ids) == 9
    assert all(b["itens"] for b in dados["blocos"])


def test_lean_canvas_nao_apresenta_hipotese_como_validada(lean):
    dados = lean.carregar(MODELO / "lean_canvas.json")
    for bloco in dados["blocos"]:
        assert "HIPÓTESE" in bloco["status"].upper(), bloco["id"]


def test_lean_canvas_rejeita_json_incompleto(lean, tmp_path):
    dados = json.loads((MODELO / "lean_canvas.json").read_text(encoding="utf-8"))
    dados["blocos"] = [b for b in dados["blocos"] if b["id"] != "receitas"]
    fonte = tmp_path / "incompleto.json"
    fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="receitas"):
        lean.carregar(fonte)


def test_arquivos_versionados_do_canvas_batem_com_o_gerador(lean, tmp_path):
    assert lean.main(["--saida", str(tmp_path)]) == 0
    for nome in ("LEAN_CANVAS.md", "LEAN_CANVAS.html"):
        gerado = (tmp_path / nome).read_text(encoding="utf-8")
        versionado = (MODELO / nome).read_text(encoding="utf-8")
        assert gerado == versionado, f"{nome} desatualizado: rode scripts/gerar_lean_canvas.py"
    wb = openpyxl.load_workbook(tmp_path / "LEAN_CANVAS.xlsx")
    assert wb.sheetnames


def test_gerador_de_planilhas_cria_modelo_financeiro_e_registro_de_testes(tmp_path):
    mod = _carregar_modulo(PASTA / "scripts" / "gerar_planilhas.py")
    rc = mod.main(["--saida-pitch", str(tmp_path / "pitch"), "--saida-modelo", str(tmp_path / "modelo")])
    assert rc in (0, None)
    registro = tmp_path / "pitch" / "registro_testes_usuarios_TEMPLATE.xlsx"
    financeiro = tmp_path / "modelo" / "MODELO_FINANCEIRO_HIPOTETICO.xlsx"
    assert registro.is_file() and financeiro.is_file()
    # O modelo de registro de testes nasce sem dados de participantes (nada inventado).
    wb = openpyxl.load_workbook(registro)
    assert wb.sheetnames


def test_exportador_gold_para_excel_gera_abas(tmp_path):
    gold = RAIZ / "data" / "processed" / "gold"
    if not (gold / "denuncias_por_bairro.csv").is_file():
        pytest.skip("Gold ainda não gerada (rode o pipeline da disciplina 02)")
    mod = _carregar_modulo(PASTA / "dashboard" / "exportar_gold_para_excel.py")
    saida = tmp_path / "indicadores.xlsx"
    rc = mod.main(["--gold-dir", str(gold), "--saida", str(saida)])
    assert rc in (0, None)
    abas = openpyxl.load_workbook(saida).sheetnames
    for esperada in ("Leia-me", "Bairros", "Categorias", "Status", "Triagem_da_foto"):
        assert esperada in abas


def test_links_de_entrega_vazios_ou_https():
    dados = yaml.safe_load((PASTA / "docs" / "links_entrega.yaml").read_text(encoding="utf-8"))
    for chave in ("url_video", "url_mvp", "url_repositorio"):
        valor = (dados.get(chave) or "").strip()
        assert valor == "" or re.match(r"^https://[^\s<>\[\]]+$", valor), f"{chave} inválido: {valor!r}"
