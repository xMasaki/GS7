"""Testes da observabilidade: Prometheus, regras de alerta, Grafana e gerador de tráfego."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

RAIZ = Path(__file__).resolve().parents[2]
MON = RAIZ / "06-Secure-DevOps-Cloud" / "monitoring"
METRICAS_CONTRATO = {
    "acessacidade_http_requests_total",
    "acessacidade_http_request_duration_seconds_bucket",
    "acessacidade_http_requests_in_progress",
    "acessacidade_denuncias_criadas_total",
    "acessacidade_visao_classificacoes_total",
    "acessacidade_assistente_respostas_total",
    "process_resident_memory_bytes",
    "process_cpu_seconds_total",
}


def _yaml(caminho: Path):
    return yaml.safe_load(caminho.read_text(encoding="utf-8"))


def test_prometheus_local_coleta_app_8000_e_carrega_regras():
    cfg = _yaml(MON / "prometheus" / "prometheus.yml")
    alvos = [alvo for job in cfg["scrape_configs"] for sc in job.get("static_configs", [])
             for alvo in sc["targets"]]
    assert "app:8000" in alvos
    assert any("alert_rules.yml" in r for r in cfg["rule_files"])


def test_prometheus_azure_tem_placeholder_e_nao_url_inventada():
    texto = (MON / "prometheus" / "prometheus.azure.yml").read_text(encoding="utf-8")
    _yaml(MON / "prometheus" / "prometheus.azure.yml")
    assert "[PREENCHER" in texto


def test_regras_de_alerta_obrigatorias_em_portugues():
    regras = {r["alert"]: r for g in _yaml(MON / "prometheus" / "alert_rules.yml")["groups"]
              for r in g["rules"]}
    for nome in ("AcessaCidadeIndisponivel", "AcessaCidadeTaxaErros5xxAlta",
                 "AcessaCidadeLatenciaP95Alta", "AcessaCidadeMuitas4xx"):
        assert nome in regras, nome
        assert regras[nome]["annotations"]["summary"]
        assert regras[nome]["annotations"]["description"]
        assert regras[nome]["labels"]["severity"]
    assert "up" in regras["AcessaCidadeIndisponivel"]["expr"]
    assert regras["AcessaCidadeIndisponivel"]["for"] == "1m"
    assert "histogram_quantile(0.95" in regras["AcessaCidadeLatenciaP95Alta"]["expr"]
    assert 'status=~"5..' in regras["AcessaCidadeTaxaErros5xxAlta"]["expr"]
    assert 'status=~"4..' in regras["AcessaCidadeMuitas4xx"]["expr"]


def test_dashboard_grafana_valido_com_sinais_de_ouro_e_metricas_do_contrato():
    painel = json.loads((MON / "grafana" / "dashboards" / "acessacidade-golden-signals.json")
                        .read_text(encoding="utf-8"))
    exprs = " ".join(t.get("expr", "") for p in painel["panels"] for t in p.get("targets", []))
    for metrica in METRICAS_CONTRATO:
        assert metrica in exprs, metrica
    for q in ("0.5", "0.95", "0.99"):
        assert f"histogram_quantile({q}" in exprs
    titulos = " ".join(p.get("title", "") for p in painel["panels"]).lower()
    for sinal in ("latência", "tráfego", "erros", "saturação"):
        assert sinal in titulos, sinal
    datasource = _yaml(MON / "grafana" / "provisioning" / "datasources" / "prometheus.yml")
    uid = datasource["datasources"][0]["uid"]
    usados = set(re.findall(r'"uid":\s*"([^"]+)"', json.dumps(painel)))
    assert uid in usados
    provider = _yaml(MON / "grafana" / "provisioning" / "dashboards" / "dashboards.yml")
    assert provider["providers"][0]["options"]["path"] == "/etc/grafana/dashboards"


def test_metricas_usadas_existem_no_contrato():
    contrato = (RAIZ / "docs" / "CONTRATOS_DE_INTEGRACAO.md").read_text(encoding="utf-8")
    textos = (MON / "prometheus" / "alert_rules.yml").read_text(encoding="utf-8") + \
        (MON / "grafana" / "dashboards" / "acessacidade-golden-signals.json").read_text(encoding="utf-8")
    for metrica in set(re.findall(r"acessacidade_[a-z_]+", textos)):
        base = re.sub(r"_(bucket|sum|count)$", "", metrica)
        assert base in contrato, f"{metrica} não está no contrato (seção 10)"


def test_gerador_de_trafego_tem_cli_documentada():
    script = RAIZ / "scripts" / "gerar_trafego_demo.py"
    saida = subprocess.run([sys.executable, str(script), "--help"], capture_output=True,
                           text=True, timeout=60, check=True,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    for opcao in ("--url", "--duracao", "--modo", "erros404"):
        assert opcao in saida.stdout


def test_scripts_de_execucao_local_existem():
    ps1 = (RAIZ / "scripts" / "run_local.ps1").read_text(encoding="utf-8")
    sh = (RAIZ / "scripts" / "run_local.sh").read_text(encoding="utf-8")
    for texto in (ps1, sh):
        assert "acessacidade_api.main:app" in texto
        assert "app/backend" in texto or "app\\backend" in texto
        assert ".env" in texto and "8000" in texto
