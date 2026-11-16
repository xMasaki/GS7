"""Integração com a API do AcessaCidade (extração e publicação) usando httpx.MockTransport.

Nenhuma chamada de rede real: o transporte simulado responde como o backend descrito nos
contratos 4.7 (GET /api/export/denuncias?formato=csv) e 4.8 (POST /api/pipeline/gold).
O token usado aqui é um valor de teste, não uma credencial.
"""
import csv
import io
import json
from datetime import datetime, timezone

import duckdb
import httpx
import pytest

from acessacidade_pipeline.dominio import COLUNAS_EXPORTACAO_API
from acessacidade_pipeline.extract import exportar_denuncias_api
from acessacidade_pipeline.publish import PublicacaoError, publicar_snapshot
from acessacidade_pipeline.run_pipeline import executar_pipeline

TOKEN_TESTE = "token-de-teste-nao-e-segredo"
URL = "http://api.teste.local"


def _csv_exportacao(bom: bool = False) -> bytes:
    linhas = [
        {"id": "1", "protocolo": "AC-2026-000001", "criado_em": "2026-11-10T13:00:00Z",
         "atualizado_em": "2026-11-10T13:00:01Z", "logradouro": "Rua Exemplo", "numero": "120", "bairro": "Centro",
         "cidade": "Cidade Exemplo", "ponto_referencia": "", "tipo_obstaculo": "BURACO_CALCADA",
         "descricao": "Buraco grande na calçada em frente ao ponto de ônibus.", "impacto": "IMPEDE_PASSAGEM",
         "latitude": "-10.18", "longitude": "-48.33", "status": "AGUARDANDO_REVISAO", "origem": "WEB",
         "simulado": "false", "possui_imagem": "true", "visao_classificacao": "POSSIBLE_POTHOLE",
         "visao_pontuacao": "0.81", "revisao_humana": ""},
        {"id": "2", "protocolo": "AC-2026-000002", "criado_em": "2026-11-11T15:30:00Z",
         "atualizado_em": "2026-11-11T15:30:00Z", "logradouro": "Avenida Central", "numero": "S/N",
         "bairro": "Vila Nova", "cidade": "Cidade Exemplo", "ponto_referencia": "Perto da praça",
         "tipo_obstaculo": "RAMPA_IRREGULAR", "descricao": "Rampa com degrau no final, cadeira não sobe.",
         "impacto": "DIFICULTA_PASSAGEM", "latitude": "", "longitude": "", "status": "RECEBIDA", "origem": "RPA",
         "simulado": "true", "possui_imagem": "false", "visao_classificacao": "", "visao_pontuacao": "",
         "revisao_humana": ""},
        {"id": "3", "protocolo": "AC-2026-000003", "criado_em": "2026-11-12T10:00:00Z",
         "atualizado_em": "2026-11-12T10:00:00Z", "logradouro": "Rua das Acácias", "numero": "45",
         "bairro": "Bairro do App", "cidade": "Cidade Exemplo", "ponto_referencia": "",
         "tipo_obstaculo": "PISO_TATIL", "descricao": "Piso tátil interrompido antes da faixa de pedestres.",
         "impacto": "RISCO_QUEDA", "latitude": "", "longitude": "", "status": "EM_ANALISE", "origem": "WEB",
         "simulado": "false", "possui_imagem": "false", "visao_classificacao": "", "visao_pontuacao": "",
         "revisao_humana": ""},
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(COLUNAS_EXPORTACAO_API), lineterminator="\r\n")
    w.writeheader()
    w.writerows(linhas)
    return (("﻿" if bom else "") + buf.getvalue()).encode("utf-8")


class ApiFalsa:
    """Backend simulado: registra as chamadas recebidas."""

    def __init__(self, status_export=200, status_gold=200, corpo_export=None):
        self.status_export = status_export
        self.status_gold = status_gold
        self.corpo_export = corpo_export if corpo_export is not None else _csv_exportacao(bom=True)
        self.chamadas: list[httpx.Request] = []
        self.snapshot_recebido = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.chamadas.append(request)
        if request.headers.get("X-Pipeline-Token") != TOKEN_TESTE:
            return httpx.Response(401, json={"detail": "Token inválido"})
        if request.method == "GET" and request.url.path == "/api/export/denuncias":
            assert request.url.params["formato"] == "csv"
            return httpx.Response(self.status_export, content=self.corpo_export,
                                  headers={"content-type": "text/csv; charset=utf-8"})
        if request.method == "POST" and request.url.path == "/api/pipeline/gold":
            self.snapshot_recebido = json.loads(request.content)
            return httpx.Response(self.status_gold, json={"detail": "ok"})
        return httpx.Response(404, json={"detail": "Rota não encontrada"})


def _cliente(api: ApiFalsa) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(api))


@pytest.fixture
def cfg_api(cfg_tmp):
    return cfg_tmp.com(api_url=URL, pipeline_token=TOKEN_TESTE)


def test_extracao_salva_copia_em_data_exports(cfg_api):
    api = ApiFalsa()
    res = exportar_denuncias_api(cfg_api, client=_cliente(api),
                                 agora=datetime(2026, 11, 14, 13, 39, 0, tzinfo=timezone.utc))
    assert res.status == "OK" and res.linhas == 3
    assert res.arquivo.endswith("denuncias_api_20261114T133900Z.csv")
    assert (cfg_api.exports_dir / "denuncias_api_20261114T133900Z.csv").exists()
    assert api.chamadas[0].headers["X-Pipeline-Token"] == TOKEN_TESTE


@pytest.mark.parametrize("cfg_mudanca, esperado", [({"api_url": None}, "PULADA"), ({"pipeline_token": None}, "PULADA")])
def test_extracao_pulada_sem_configuracao(cfg_api, cfg_mudanca, esperado):
    res = exportar_denuncias_api(cfg_api.com(**cfg_mudanca), client=_cliente(ApiFalsa()))
    assert res.status == esperado and res.arquivo is None


def test_extracao_falhas_nao_derrubam(cfg_api):
    assert exportar_denuncias_api(cfg_api.com(pipeline_token="errado"), client=_cliente(ApiFalsa())).status == "FALHOU"
    assert "403" in exportar_denuncias_api(cfg_api, client=_cliente(ApiFalsa(status_export=403))).mensagem
    sem_coluna = "id,protocolo\n1,AC-2026-000001\n".encode()
    res = exportar_denuncias_api(cfg_api, client=_cliente(ApiFalsa(corpo_export=sem_coluna)))
    assert res.status == "FALHOU" and "contrato" in res.mensagem

    def fora_do_ar(request):
        raise httpx.ConnectError("conexão recusada", request=request)

    res = exportar_denuncias_api(cfg_api, client=httpx.Client(transport=httpx.MockTransport(fora_do_ar)))
    assert res.status == "FALHOU" and "indisponível" in res.mensagem
    assert not list(cfg_api.exports_dir.glob("*.csv"))


def test_pipeline_completo_com_api_simulada(cfg_api):
    api = ApiFalsa()
    estado = executar_pipeline(usar_api=True, execucao_id="manual__api", cfg=cfg_api, client=_cliente(api))
    assert estado["extracao_api"]["status"] == "OK"
    assert estado["linhas_raw_app"] == 3 and estado["linhas_raw"] == 271 + 3
    assert estado["publicacao"]["status"] == "OK"
    assert [(c.method, c.url.path) for c in api.chamadas] == [("GET", "/api/export/denuncias"),
                                                               ("POST", "/api/pipeline/gold")]
    snap = api.snapshot_recebido
    assert snap["execucao_id"] == "manual__api" and "gerado_em" in snap
    assert snap["fontes"] == [{"nome": "denuncias_simuladas.csv", "linhas": 271}, {"nome": "api_export", "linhas": 3}]
    with duckdb.connect(str(cfg_api.warehouse_path), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM bronze.denuncias WHERE fonte = 'api_export'").fetchone()[0] == 3
        origem, bairro = con.execute("SELECT origem, bairro FROM silver.denuncias WHERE protocolo = 'AC-2026-000003'"
                                     ).fetchone()
    assert origem == "WEB" and bairro == "Bairro do App"
    assert {b["bairro"] for b in snap["denuncias_por_bairro"]} >= {"Centro", "Bairro do App"}


def test_pipeline_segue_quando_api_esta_fora(cfg_api):
    def fora_do_ar(request):
        raise httpx.ConnectError("conexão recusada", request=request)

    cliente = httpx.Client(transport=httpx.MockTransport(fora_do_ar))
    with pytest.raises(PublicacaoError):
        # extração degrada (só fonte simulada); a publicação, configurada, falha de forma explícita
        executar_pipeline(usar_api=True, execucao_id="manual__fora", cfg=cfg_api, client=cliente)
    snap = json.loads(cfg_api.snapshot_path.read_text(encoding="utf-8"))
    assert snap["fontes"][1] == {"nome": "api_export", "linhas": 0}


def test_publicacao(cfg_api, pipeline_sem_api):
    cfg_pronto, _ = pipeline_sem_api
    cfg = cfg_api.com(gold_dir=cfg_pronto.gold_dir)
    api = ApiFalsa()
    assert publicar_snapshot(cfg, client=_cliente(api))["status"] == "OK"
    assert api.chamadas[0].headers["X-Pipeline-Token"] == TOKEN_TESTE
    assert api.chamadas[0].headers["content-type"].startswith("application/json")
    assert api.snapshot_recebido["disponivel"] is True

    assert publicar_snapshot(cfg.com(pipeline_token=None))["status"] == "PULADA"
    with pytest.raises(PublicacaoError, match="401"):
        publicar_snapshot(cfg.com(pipeline_token="errado"), client=_cliente(ApiFalsa()))
    with pytest.raises(PublicacaoError, match="403"):
        publicar_snapshot(cfg, client=_cliente(ApiFalsa(status_gold=403)))
