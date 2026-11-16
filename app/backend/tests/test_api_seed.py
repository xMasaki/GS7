"""Seed de demonstração: tudo simulado, status permitidos, triagem real das fotos e idempotência."""
from __future__ import annotations

import json
import sqlite3

from acessacidade_api.seed import SEED_PATH


def _todas(c):
    return c.get("/api/denuncias", params={"limite": 100}).json()


def test_arquivo_seed_valido():
    doc = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    itens = doc["denuncias"]
    assert 25 <= len(itens) <= 30
    assert doc["simulado"] is True and doc["origem"] == "SIMULADO"
    bairros = {"Centro", "Vila Esperança", "Jardim Primavera", "Parque das Flores", "Vila Nova", "Jardim Aurora"}
    for i in itens:
        assert i["cidade"] == "Cidade Exemplo"
        assert i["bairro"] in bairros
        assert "2026-09-01" <= i["criado_em"][:10] <= "2026-11-13"
        assert i["status"] in ("RECEBIDA", "EM_ANALISE", "AGUARDANDO_REVISAO")
        assert "nome" not in i
    com_foto = sum(1 for i in itens if i.get("foto"))
    assert len(itens) // 4 <= com_foto <= len(itens) // 2


def test_seed_carrega_tudo_simulado(make_client):
    with make_client(SEED_DEMO_DATA="true") as c:
        j = _todas(c)
        doc = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        assert j["total"] == len(doc["denuncias"])
        assert all(i["simulado"] is True and i["origem"] == "SIMULADO" for i in j["itens"])
        assert all(i["cidade"] == "Cidade Exemplo" for i in j["itens"])
        assert {i["status"] for i in j["itens"]} <= {"RECEBIDA", "EM_ANALISE", "AGUARDANDO_REVISAO"}
        com_imagem = [i for i in j["itens"] if i["possui_imagem"]]
        if c.app_settings.seed_fotos_dir.is_dir():
            assert len(com_imagem) == sum(1 for i in doc["denuncias"] if i.get("foto"))
            for i in com_imagem:  # resultado real da triagem
                assert i["visao"]["classificacao"] in ("POSSIBLE_POTHOLE", "NOT_IDENTIFIED", "INCONCLUSIVE")
                img = c.get(i["visao"]["imagens"]["contornos"])
                assert img.status_code == 200 and img.headers["content-type"] == "image/jpeg"
        assert c.get("/api/denuncias", params={"incluir_simulados": "false"}).json()["total"] == 0
        # datas fixas do seed preservadas e protocolos com o ano da data
        assert all(i["protocolo"].startswith("AC-2026-") for i in j["itens"])
        det = c.get(f"/api/denuncias/{j['itens'][-1]['id']}").json()
        assert det["criado_em"] == "2026-09-02T13:10:00Z"


def test_seed_sem_pasta_de_fotos_cria_sem_foto(make_client, tmp_path):
    with make_client(SEED_DEMO_DATA="true", SEED_FOTOS_DIR=str(tmp_path / "nao-existe")) as c:
        j = _todas(c)
        assert j["total"] > 0
        assert not any(i["possui_imagem"] for i in j["itens"])
        assert "AGUARDANDO_REVISAO" not in {i["status"] for i in j["itens"]}


def test_seed_idempotente(make_client, tmp_path):
    dados = tmp_path / "persistente"
    with make_client(data_dir=dados, SEED_DEMO_DATA="true") as c:
        total1 = _todas(c)["total"]
    with make_client(data_dir=dados, SEED_DEMO_DATA="true") as c:
        assert _todas(c)["total"] == total1
    with sqlite3.connect(dados / "acessacidade.db") as con:
        assert con.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 1
        assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_seed_nao_roda_se_ja_ha_dados(make_client, tmp_path, criar):
    dados = tmp_path / "comdados"
    with make_client(data_dir=dados, SEED_DEMO_DATA="false") as c:
        criar(c)
    with make_client(data_dir=dados, SEED_DEMO_DATA="true") as c:
        assert _todas(c)["total"] == 1
