"""Camada Gold: tabelas, CSVs e snapshot JSON no formato do contrato 4.8."""
import json
import re

import duckdb

from acessacidade_pipeline.dominio import STATUS, TIPO_OBSTACULO, VISAO_CLASSIFICACAO
from acessacidade_pipeline.gold import TABELAS_GOLD

CHAVES_TOPO = {"disponivel", "gerado_em", "execucao_id", "inclui_simulados", "fontes", "denuncias_por_bairro",
               "denuncias_por_categoria", "denuncias_por_periodo", "denuncias_por_status", "resultado_visao",
               "qualidade"}
CHAVES_QUALIDADE = {"linhas_raw", "linhas_bronze", "duplicatas_removidas", "datas_invalidas",
                    "coordenadas_invalidas", "campos_obrigatorios_ausentes", "percentual_registros_validos"}


def _snapshot(cfg) -> dict:
    return json.loads(cfg.snapshot_path.read_text(encoding="utf-8"))


def test_snapshot_formato_contrato_4_8(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    s = _snapshot(cfg)
    assert CHAVES_TOPO <= set(s)
    assert s["disponivel"] is True and s["inclui_simulados"] is True
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s["gerado_em"])
    assert s["execucao_id"] == "manual__teste"
    assert s["fontes"] == [{"nome": "denuncias_simuladas.csv", "linhas": 271}, {"nome": "api_export", "linhas": 0}]

    formatos = {
        "denuncias_por_bairro": {"bairro": str, "total": int, "possiveis_buracos": int},
        "denuncias_por_categoria": {"categoria": str, "rotulo": str, "total": int},
        "denuncias_por_periodo": {"periodo": str, "total": int},
        "denuncias_por_status": {"status": str, "rotulo": str, "total": int},
        "resultado_visao": {"classificacao": (str, type(None)), "rotulo": str, "total": int},
    }
    for lista, campos in formatos.items():
        assert s[lista], lista
        for item in s[lista]:
            assert set(item) == set(campos), (lista, item)
            for campo, tipo in campos.items():
                assert isinstance(item[campo], tipo) and not isinstance(item[campo], bool), (lista, campo)

    assert {i["categoria"] for i in s["denuncias_por_categoria"]} == set(TIPO_OBSTACULO)
    assert all(i["rotulo"] == TIPO_OBSTACULO[i["categoria"]] for i in s["denuncias_por_categoria"])
    assert [i["status"] for i in s["denuncias_por_status"]] == list(STATUS)
    assert [i["classificacao"] for i in s["resultado_visao"]] == list(VISAO_CLASSIFICACAO)
    assert all(re.fullmatch(r"2026-(08|09|10|11)", i["periodo"]) for i in s["denuncias_por_periodo"])

    q = s["qualidade"]
    assert CHAVES_QUALIDADE <= set(q)
    assert all(isinstance(q[k], int) for k in CHAVES_QUALIDADE - {"percentual_registros_validos"})
    assert isinstance(q["percentual_registros_validos"], float) and 0 < q["percentual_registros_validos"] <= 100
    assert q["linhas_raw"] == 271 and q["linhas_raw"] - q["linhas_bronze"] == q["duplicatas_removidas"]
    validos = q["registros_validos"]
    for lista in ("denuncias_por_bairro", "denuncias_por_categoria", "denuncias_por_periodo",
                  "denuncias_por_status", "resultado_visao"):
        assert sum(i["total"] for i in s[lista]) == validos, lista


def test_snapshot_sem_dados_pessoais_nem_texto_livre(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    texto = cfg.snapshot_path.read_text(encoding="utf-8")
    assert "Pessoa Simulada" not in texto
    assert "nome_denunciante" not in texto and "descricao" not in texto and "logradouro" not in texto
    # a única chave "nome" do snapshot é o nome da FONTE de dados (contrato 4.8, campo "fontes")
    assert {f["nome"] for f in json.loads(texto)["fontes"]} == {"denuncias_simuladas.csv", "api_export"}


def test_tabelas_e_csvs_gold(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    with duckdb.connect(str(cfg.warehouse_path), read_only=True) as con:
        for tabela in TABELAS_GOLD:
            n = con.execute(f"SELECT count(*) FROM gold.{tabela}").fetchone()[0]
            csv = cfg.gold_dir / f"{tabela}.csv"
            assert csv.exists() and n > 0
            linhas = csv.read_text(encoding="utf-8").strip().splitlines()
            assert len(linhas) == n + 1  # cabeçalho + linhas
        granularidades = {r[0] for r in con.execute(
            "SELECT DISTINCT granularidade FROM gold.denuncias_por_periodo").fetchall()}
        metricas = {r[0] for r in con.execute("SELECT metrica FROM gold.qualidade_registros").fetchall()}
    assert granularidades == {"mensal", "semanal"}
    assert CHAVES_QUALIDADE <= metricas


def test_relatorio_de_qualidade_aprovado(pipeline_sem_api):
    cfg, estado = pipeline_sem_api
    rel = json.loads(cfg.relatorio_json_path.read_text(encoding="utf-8"))
    assert rel["situacao"] == "APROVADO" == estado["situacao_qualidade"]
    assert all(v["ok"] for v in rel["verificacoes"])
    assert cfg.relatorio_md_path.read_text(encoding="utf-8").startswith("# Relatório de qualidade")
    assert estado["publicacao"]["status"] == "PULADA"
