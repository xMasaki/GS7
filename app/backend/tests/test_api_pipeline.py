"""Exportação para o pipeline, snapshot Gold, indicadores operacionais e triagem avulsa."""
from __future__ import annotations

import csv
import io
import json

import pytest

from acessacidade_api import REPO_ROOT

FOTO = REPO_ROOT / "data" / "samples" / "fotos" / "sintetica_buraco_01.jpg"
TOKEN = "token-pipeline-somente-teste"
COLUNAS = ["id", "protocolo", "criado_em", "atualizado_em", "logradouro", "numero", "bairro", "cidade",
           "ponto_referencia", "tipo_obstaculo", "descricao", "impacto", "latitude", "longitude", "status",
           "origem", "simulado", "possui_imagem", "visao_classificacao", "visao_pontuacao", "revisao_humana"]

GOLD = {
    "gerado_em": "2026-11-14T13:40:00Z",
    "execucao_id": "teste__2026-11-14",
    "inclui_simulados": True,
    "denuncias_por_bairro": [{"bairro": "Centro", "total": 3, "possiveis_buracos": 1}],
    "qualidade": {"linhas_raw": 10, "linhas_bronze": 9},
}


def test_export_exige_token(make_client):
    with make_client() as c:
        assert c.get("/api/export/denuncias").status_code == 403
    with make_client(PIPELINE_TOKEN=TOKEN) as c:
        assert c.get("/api/export/denuncias").status_code == 401
        assert c.get("/api/export/denuncias", headers={"X-Pipeline-Token": "errado"}).status_code == 401


def test_export_csv_e_json_sem_nome(make_client, criar):
    with make_client(PIPELINE_TOKEN=TOKEN) as c:
        criar(c, nome="Nome Que Nao Pode Vazar")
        criar(c, nome="Outro Apelido", bairro="Vila Nova", latitude="-10.5", longitude="-20.25")
        h = {"X-Pipeline-Token": TOKEN}
        r = c.get("/api/export/denuncias", params={"formato": "csv"}, headers=h)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/csv")
        assert "Nome Que Nao Pode Vazar" not in r.text and "Outro Apelido" not in r.text
        linhas = list(csv.reader(io.StringIO(r.text)))
        assert linhas[0] == COLUNAS and "nome" not in linhas[0]
        assert len(linhas) == 3
        reg = dict(zip(COLUNAS, linhas[2]))
        assert reg["simulado"] == "false" and reg["possui_imagem"] == "false"
        assert reg["latitude"] == "-10.5" and reg["criado_em"].endswith("Z")

        j = c.get("/api/export/denuncias", params={"formato": "json"}, headers=h).json()
        assert j["colunas"] == COLUNAS and len(j["linhas"]) == 2 and j["exportado_em"].endswith("Z")
        assert all("nome" not in linha for linha in j["linhas"])
        assert j["linhas"][0]["simulado"] is False
        assert "Nome Que Nao Pode Vazar" not in json.dumps(j)
        assert c.get("/api/export/denuncias", params={"formato": "xml"}, headers=h).status_code == 422


def test_gold_publicar_e_consultar(make_client):
    with make_client(PIPELINE_TOKEN=TOKEN) as c:
        vazio = c.get("/api/indicadores/analiticos")
        assert vazio.status_code == 200
        assert vazio.json()["disponivel"] is False and vazio.json()["mensagem"]

        assert c.post("/api/pipeline/gold", json=GOLD).status_code == 401
        h = {"X-Pipeline-Token": TOKEN}
        assert c.post("/api/pipeline/gold", json={"sem": "data"}, headers=h).status_code == 422
        assert c.post("/api/pipeline/gold", json=[1, 2], headers=h).status_code == 422
        assert c.post("/api/pipeline/gold", content=b"{invalido", headers=h).status_code == 422
        r = c.post("/api/pipeline/gold", json=GOLD, headers=h)
        assert r.status_code == 200, r.text

        salvo = c.app_settings.gold_snapshot_path
        assert salvo.is_file() and json.loads(salvo.read_text(encoding="utf-8"))["execucao_id"] == "teste__2026-11-14"
        assert not list(salvo.parent.glob(".gold_*.tmp"))
        a = c.get("/api/indicadores/analiticos").json()
        assert a["disponivel"] is True and a["gerado_em"] == GOLD["gerado_em"]
        assert a["denuncias_por_bairro"] == GOLD["denuncias_por_bairro"]


def test_gold_desativado_sem_token(client):
    assert client.post("/api/pipeline/gold", json=GOLD, headers={"X-Pipeline-Token": "x"}).status_code == 403


@pytest.mark.skipif(not FOTO.is_file(), reason="imagens sintéticas ausentes")
def test_indicadores_operacionais(client, criar):
    criar(client, bairro="Centro")
    criar(client, bairro="Centro", tipo_obstaculo="PISO_TATIL", origem="RPA")
    criar(client, bairro="Vila Nova", foto=FOTO)
    r = client.get("/api/indicadores")
    assert r.status_code == 200
    j = r.json()
    assert j["total"] == 3 and j["inclui_simulados"] is True
    assert j["sem_imagem"] == 2
    assert j["possiveis_buracos"] + j["inconclusivas"] + j["nao_identificadas"] == 1
    assert j["por_bairro"][0] == {"chave": "Centro", "rotulo": "Centro", "total": 2}
    cat = {i["chave"]: i for i in j["por_categoria"]}
    assert cat["BURACO_CALCADA"]["total"] == 2 and cat["BURACO_CALCADA"]["rotulo"] == "Buraco na calçada"
    st = {i["chave"]: i["total"] for i in j["por_status"]}
    assert st["RECEBIDA"] == 2 and st["AGUARDANDO_REVISAO"] == 1
    assert {i["chave"]: i["total"] for i in j["por_origem"]} == {"WEB": 2, "RPA": 1}
    vis = {i["chave"]: i["total"] for i in j["por_resultado_visao"]}
    assert sum(vis.values()) == 3
    assert [x["data"] for x in j["por_dia"]] == sorted(x["data"] for x in j["por_dia"])
    assert sum(x["total"] for x in j["por_dia"]) == 3
    assert len(j["recentes"]) == 3 and j["recentes"][0]["bairro"] == "Vila Nova"
    assert "nome" not in json.dumps(j["recentes"])


def test_indicadores_sem_simulados(make_client):
    with make_client(SEED_DEMO_DATA="true") as c:
        com = c.get("/api/indicadores").json()
        sem = c.get("/api/indicadores", params={"incluir_simulados": "false"}).json()
        assert com["total"] > 0 and sem["total"] == 0 and sem["inclui_simulados"] is False


@pytest.mark.skipif(not FOTO.is_file(), reason="imagens sintéticas ausentes")
def test_visao_analisar_nao_persiste(client):
    r = client.post("/api/visao/analisar", files={"foto": ("f.jpg", FOTO.read_bytes(), "image/jpeg")})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["classificacao"] in ("POSSIBLE_POTHOLE", "NOT_IDENTIFIED", "INCONCLUSIVE")
    assert list(j["imagens"]) == ["original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos"]
    assert all(v.startswith("data:image/jpeg;base64,") for v in j["imagens"].values())
    assert j["aviso"].startswith("Triagem automática inicial")
    assert client.get("/api/denuncias").json()["total"] == 0
    assert not any(client.app_settings.uploads_dir.iterdir())


def test_visao_analisar_rejeita_nao_imagem_e_ausencia(client):
    r = client.post("/api/visao/analisar", files={"foto": ("a.png", b"GIF89a texto qualquer", "image/png")})
    assert r.status_code == 422 and isinstance(r.json()["detail"], str)
    r = client.post("/api/visao/analisar")
    assert r.status_code == 422 and r.json()["detail"][0]["campo"] == "foto"
