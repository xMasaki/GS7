"""Criação, validação, fotos, imagens das etapas, consulta, listagem e mudança de status."""
from __future__ import annotations

import re
import sqlite3

import pytest

from acessacidade_api import REPO_ROOT

FOTOS = REPO_ROOT / "data" / "samples" / "fotos"
FOTO_BURACO = FOTOS / "sintetica_buraco_01.jpg"
ETAPAS = ["original", "cinza", "filtrada", "contraste", "bordas", "mascara", "contornos"]
TOKEN_TESTE = "token-de-teste-somente-local"

precisa_foto = pytest.mark.skipif(not FOTO_BURACO.is_file(), reason="imagens sintéticas ausentes")


def _campos_com_erro(r):
    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list) and detail
    for item in detail:
        assert item["msg"] and not re.search(r"\b(Field required|Input should|String should)\b", item["msg"])
    return {item["campo"]: item["msg"] for item in detail}


# --------------------------------------------------------------------------- criação sem foto
def test_criar_sem_foto(client, criar):
    r = criar(client)
    assert r.status_code == 201, r.text
    j = r.json()
    assert re.fullmatch(r"AC-\d{4}-\d{6}", j["protocolo"])
    assert j["protocolo"].endswith(f"-{j['id']:06d}")
    assert j["status"] == "RECEBIDA" and j["status_rotulo"] == "Recebida"
    assert j["tipo_obstaculo_rotulo"] == "Buraco na calçada"
    assert j["impacto_rotulo"] == "Impede a passagem"
    assert j["origem"] == "WEB" and j["simulado"] is False
    assert j["possui_imagem"] is False and j["visao"] is None
    assert j["historico"][0]["observacao"] == "Denúncia registrada"
    assert j["mensagem"]
    assert "nome" not in j and "Apelido Teste" not in r.text
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", j["criado_em"])


def test_nome_armazenado_mas_nunca_retornado(client, criar):
    j = criar(client, nome="Apelido Secreto").json()
    banco = client.app_settings.database_path
    with sqlite3.connect(banco) as con:
        assert con.execute("SELECT nome FROM denuncias WHERE id=?", (j["id"],)).fetchone()[0] == "Apelido Secreto"
    for caminho in (f"/api/denuncias/{j['id']}", "/api/denuncias", "/api/indicadores"):
        assert "Apelido Secreto" not in client.get(caminho).text


def test_cidade_vazia_usa_padrao(make_client, criar):
    with make_client(CIDADE_PADRAO="Cidade Exemplo") as c:
        assert criar(c, cidade="").json()["cidade"] == "Cidade Exemplo"
    with make_client() as c:
        assert criar(c, cidade="").json()["cidade"] == "Não informada"


def test_origem_rpa_e_coordenadas(client, criar):
    j = criar(client, origem="RPA", latitude="-23,5", longitude="-46.6").json()
    assert j["origem"] == "RPA"
    assert j["latitude"] == -23.5 and j["longitude"] == -46.6


# --------------------------------------------------------------------------- criação com foto
@precisa_foto
def test_criar_com_foto_sintetica(client, criar):
    r = criar(client, foto=FOTO_BURACO)
    assert r.status_code == 201, r.text
    j = r.json()
    assert j["status"] == "AGUARDANDO_REVISAO"
    assert j["possui_imagem"] is True
    v = j["visao"]
    assert v["classificacao"] in ("POSSIBLE_POTHOLE", "NOT_IDENTIFIED", "INCONCLUSIVE")
    assert 0.0 <= v["pontuacao"] <= 1.0
    assert v["explicacao"] and isinstance(v["metricas"], dict)
    assert v["aviso"].startswith("Triagem automática inicial")
    assert v["versao_algoritmo"] == "1.0.0"
    assert list(v["imagens"]) == ETAPAS
    assert [h["status"] for h in j["historico"]] == ["RECEBIDA", "AGUARDANDO_REVISAO"]
    assert j["historico"][1]["observacao"] == "Triagem automática da fotografia concluída; aguardando revisão humana"
    for etapa, url in v["imagens"].items():
        assert url == f"/api/denuncias/{j['id']}/imagens/{etapa}"
        img = client.get(url)
        assert img.status_code == 200, etapa
        assert img.headers["content-type"] == "image/jpeg"
        assert img.content[:2] == b"\xff\xd8"
        assert "max-age" in img.headers["cache-control"]
    # pasta uuid4 (hex), só as 7 etapas e nenhum arquivo bruto
    uploads = client.app_settings.uploads_dir
    pastas = [p for p in uploads.iterdir() if p.is_dir()]
    assert len(pastas) == 1 and re.fullmatch(r"[0-9a-f]{32}", pastas[0].name)
    assert sorted(p.name for p in pastas[0].iterdir()) == sorted(f"{e}.jpg" for e in ETAPAS)
    assert FOTO_BURACO.read_bytes() not in [p.read_bytes() for p in pastas[0].iterdir()]


def test_arquivo_nao_imagem_rejeitado(client, criar):
    r = criar(client, foto=b"isto nao e uma imagem, apenas texto" * 10, nome_arquivo="falsa.jpg")
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str) and "JPEG" in r.json()["detail"]
    assert client.get("/api/denuncias").json()["total"] == 0


@precisa_foto
def test_arquivo_grande_rejeitado(make_client, criar):
    with make_client(MAX_UPLOAD_MB="0.1") as c:  # ~100 KB; a foto sintética tem ~190 KB
        r = criar(c, foto=FOTO_BURACO)
        assert r.status_code == 413
        assert "tamanho máximo" in r.json()["detail"]
        assert c.get("/api/denuncias").json()["total"] == 0


def test_corpo_gigante_rejeitado_pelo_content_length(make_client, criar):
    with make_client(MAX_UPLOAD_MB="0.1") as c:
        r = criar(c, foto=b"\xff\xd8" + b"0" * (1_300_000))
        assert r.status_code == 413


def test_campo_foto_vazio_equivale_a_sem_foto(client, form_valido):
    r = client.post("/api/denuncias", data=form_valido, files={"foto": ("", b"", "application/octet-stream")})
    assert r.status_code == 201, r.text
    assert r.json()["possui_imagem"] is False and r.json()["status"] == "RECEBIDA"


# --------------------------------------------------------------------------- validações 422
def test_campos_obrigatorios_faltando(client):
    r = client.post("/api/denuncias", data={"numero": "1"})
    erros = _campos_com_erro(r)
    for campo in ("logradouro", "bairro", "tipo_obstaculo", "descricao", "impacto", "consentimento"):
        assert campo in erros, campo
        assert erros[campo] == "Campo obrigatório."


def test_tipo_e_impacto_invalidos(client, criar):
    erros = _campos_com_erro(criar(client, tipo_obstaculo="BURACO_NA_LUA", impacto="XYZ"))
    assert "Tipo de obstáculo inválido" in erros["tipo_obstaculo"]
    assert "Impacto inválido" in erros["impacto"]


def test_consentimento_falso(client, criar):
    erros = _campos_com_erro(criar(client, consentimento="false"))
    assert "aceitar os termos" in erros["consentimento"]


def test_descricao_curta_e_em_branco(client, criar):
    assert "pelo menos 10" in _campos_com_erro(criar(client, descricao="curta"))["descricao"]
    assert "obrigatóri" in _campos_com_erro(criar(client, descricao="          "))["descricao"]


def test_limites_de_tamanho(client, criar):
    erros = _campos_com_erro(criar(client, logradouro="R", bairro="B", numero="12345678901", nome="x" * 81,
                                   descricao="d" * 1001))
    assert set(erros) >= {"logradouro", "bairro", "numero", "nome", "descricao"}


def test_latitude_sem_longitude(client, criar):
    erros = _campos_com_erro(criar(client, latitude="-23.55"))
    assert "latitude e longitude juntas" in erros["longitude"]


def test_coordenadas_invalidas(client, criar):
    erros = _campos_com_erro(criar(client, latitude="abc", longitude="200"))
    assert "número" in erros["latitude"]
    assert "-180 e 180" in erros["longitude"]


def test_origem_invalida(client, criar):
    assert "WEB ou RPA" in _campos_com_erro(criar(client, origem="SIMULADO"))["origem"]


# --------------------------------------------------------------------------- consulta
def test_detalhe_por_id_e_por_protocolo(client, criar):
    j = criar(client).json()
    por_id = client.get(f"/api/denuncias/{j['id']}")
    por_prot = client.get(f"/api/denuncias/{j['protocolo']}")
    minusculo = client.get(f"/api/denuncias/{j['protocolo'].lower()}")
    assert por_id.status_code == por_prot.status_code == minusculo.status_code == 200
    assert por_id.json()["protocolo"] == por_prot.json()["protocolo"] == j["protocolo"]
    assert "historico" in por_id.json() and "mensagem" not in por_id.json()


@pytest.mark.parametrize("ref", ["999", "AC-2026-999999", "qualquer-coisa"])
def test_detalhe_404(client, ref):
    r = client.get(f"/api/denuncias/{ref}")
    assert r.status_code == 404
    assert "não encontrada" in r.json()["detail"]


def test_listagem_filtros_e_paginacao(client, criar):
    criar(client, bairro="Centro", tipo_obstaculo="BURACO_CALCADA")
    criar(client, bairro="Vila Esperança", tipo_obstaculo="PISO_TATIL")
    terceira = criar(client, bairro="Jardim Centro Novo", tipo_obstaculo="BURACO_CALCADA").json()

    tudo = client.get("/api/denuncias").json()
    assert tudo["total"] == 3 and tudo["pagina"] == 1 and tudo["limite"] == 20
    assert tudo["itens"][0]["id"] == terceira["id"]  # mais recentes primeiro
    assert all("historico" not in i for i in tudo["itens"])

    centro = client.get("/api/denuncias", params={"bairro": "centro"}).json()
    assert centro["total"] == 2
    tipo = client.get("/api/denuncias", params={"tipo_obstaculo": "PISO_TATIL"}).json()
    assert tipo["total"] == 1 and tipo["itens"][0]["bairro"] == "Vila Esperança"
    st = client.get("/api/denuncias", params={"status": "RECEBIDA"}).json()
    assert st["total"] == 3
    prot = client.get("/api/denuncias", params={"protocolo": terceira["protocolo"]}).json()
    assert prot["total"] == 1

    p1 = client.get("/api/denuncias", params={"limite": 2, "pagina": 1}).json()
    p2 = client.get("/api/denuncias", params={"limite": 2, "pagina": 2}).json()
    assert len(p1["itens"]) == 2 and len(p2["itens"]) == 1 and p2["total"] == 3
    assert {i["id"] for i in p1["itens"]}.isdisjoint({i["id"] for i in p2["itens"]})

    assert client.get("/api/denuncias", params={"limite": 101}).status_code == 422
    assert client.get("/api/denuncias", params={"pagina": 0}).status_code == 422
    assert client.get("/api/denuncias", params={"status": "INEXISTENTE"}).status_code == 422


# --------------------------------------------------------------------------- imagens
@precisa_foto
def test_path_traversal_em_imagens_bloqueado(client, criar):
    j = criar(client, foto=FOTO_BURACO).json()
    base = f"/api/denuncias/{j['id']}/imagens"
    for etapa in ("..%2F..%2Facessacidade.db", "%2e%2e", "original.jpg", "ORIGINAL", "acessacidade.db"):
        r = client.get(f"{base}/{etapa}")
        assert r.status_code == 404, etapa
        assert r.headers["content-type"].startswith("application/json")
    # "../" literal é normalizado pelo cliente HTTP; de qualquer forma nunca devolve o banco nem uma imagem
    r = client.get(f"/api/denuncias/{j['id']}/imagens/../../acessacidade.db")
    assert r.status_code == 404 and not r.headers["content-type"].startswith("image/")
    assert b"SQLite format" not in r.content


def test_imagem_de_denuncia_sem_foto_404(client, criar):
    j = criar(client).json()
    assert client.get(f"/api/denuncias/{j['id']}/imagens/original").status_code == 404
    assert client.get("/api/denuncias/9999/imagens/original").status_code == 404


# --------------------------------------------------------------------------- status (PATCH)
def test_patch_sem_token_configurado_403(client, criar):
    j = criar(client).json()
    r = client.patch(f"/api/denuncias/{j['id']}/status", json={"status": "EM_ANALISE"},
                     headers={"X-Admin-Token": "qualquer"})
    assert r.status_code == 403
    assert "desativada" in r.json()["detail"]


def test_patch_token_errado_401_e_certo_200(make_client, criar):
    with make_client(ADMIN_TOKEN=TOKEN_TESTE) as c:
        j = criar(c).json()
        url = f"/api/denuncias/{j['id']}/status"
        assert c.patch(url, json={"status": "EM_ANALISE"}).status_code == 401
        assert c.patch(url, json={"status": "EM_ANALISE"}, headers={"X-Admin-Token": "errado"}).status_code == 401
        r = c.patch(url, json={"status": "EM_ANALISE", "observacao": "Verificando"},
                    headers={"X-Admin-Token": TOKEN_TESTE})
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["status"] == "EM_ANALISE" and d["status_rotulo"] == "Em análise"
        assert d["historico"][-1] == {**d["historico"][-1], "status": "EM_ANALISE", "observacao": "Verificando"}
        assert len(d["historico"]) == 2


def test_patch_regras_de_observacao_e_revisao(make_client, criar):
    with make_client(ADMIN_TOKEN=TOKEN_TESTE) as c:
        j = criar(c).json()
        url = f"/api/denuncias/{j['id']}/status"
        h = {"X-Admin-Token": TOKEN_TESTE}
        for status in ("ENCAMINHADA", "RESOLVIDA"):
            r = c.patch(url, json={"status": status}, headers=h)
            assert r.status_code == 422
            assert "observação é obrigatória" in r.json()["detail"][0]["msg"]
            r = c.patch(url, json={"status": status, "observacao": "   "}, headers=h)
            assert r.status_code == 422
        r = c.patch(url, json={"status": "ENCAMINHADA", "observacao": "Encaminhada à equipe responsável",
                                "revisao_humana": "CONFIRMADO"}, headers=h)
        assert r.status_code == 200
        assert r.json()["revisao_humana"] == "CONFIRMADO"
        r = c.patch(url, json={"status": "RESOLVIDA", "observacao": "Registro da equipe"}, headers=h)
        assert r.json()["status"] == "RESOLVIDA" and r.json()["revisao_humana"] == "CONFIRMADO"
        r = c.patch(url, json={"status": "RESOLVIDA", "observacao": "Revisão desfeita", "revisao_humana": None},
                    headers=h)
        assert r.json()["revisao_humana"] is None
        assert [x["status"] for x in r.json()["historico"]] == ["RECEBIDA", "ENCAMINHADA", "RESOLVIDA", "RESOLVIDA"]
        assert c.patch(url, json={"status": "INVALIDO"}, headers=h).status_code == 422
        assert c.patch(url, json={"status": "EM_ANALISE", "revisao_humana": "TALVEZ"}, headers=h).status_code == 422
        assert c.patch("/api/denuncias/9999/status", json={"status": "EM_ANALISE"}, headers=h).status_code == 404
