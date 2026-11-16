"""Testes do pipeline DevSecOps (GitHub Actions), Gitleaks e Semgrep."""
from __future__ import annotations

import re
import secrets
import string
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

RAIZ = Path(__file__).resolve().parents[2]
WORKFLOWS = RAIZ / ".github" / "workflows"
CI = WORKFLOWS / "ci-devsecops.yml"


@pytest.fixture(scope="module")
def ci() -> dict:
    return yaml.safe_load(CI.read_text(encoding="utf-8"))


def _gatilhos(doc: dict) -> dict:
    # PyYAML (YAML 1.1) interpreta a chave "on" como booleano True
    return doc.get("on", doc.get(True))


def test_todos_os_workflows_sao_yaml_validos():
    arquivos = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    assert arquivos, "nenhum workflow em .github/workflows"
    for arquivo in arquivos:
        doc = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        assert isinstance(doc, dict) and "jobs" in doc, arquivo.name


def test_gatilhos_push_em_todas_as_branches_pr_e_manual(ci):
    gatilhos = _gatilhos(ci)
    assert gatilhos["push"]["branches"] == ["**"]
    assert "pull_request" in gatilhos and "workflow_dispatch" in gatilhos


def test_permissoes_minimas_e_concurrency(ci):
    assert ci["permissions"] == {"contents": "read"}
    assert "concurrency" in ci
    deploy = ci["jobs"]["deploy"]
    assert deploy["permissions"]["id-token"] == "write"
    assert set(deploy["permissions"]) <= {"contents", "id-token"}


def test_jobs_de_seguranca_build_e_deploy(ci):
    texto = CI.read_text(encoding="utf-8")
    for job in ("testes", "gitleaks", "semgrep", "iac", "imagem", "deploy"):
        assert job in ci["jobs"], job
    assert "gitleaks\" git ." in texto and "--config .gitleaks.toml" in texto
    assert ci["jobs"]["gitleaks"]["steps"][0]["with"]["fetch-depth"] == 0
    for pacote in ("p/python", "p/javascript", "p/secrets", "p/dockerfile", ".semgrep/"):
        assert f"--config {pacote}" in texto
    assert "--error" in texto
    assert "docker build" in texto
    assert re.search(r"image\s+\\\s*\n\s*--input", texto), "trivy image deve escanear a imagem construída"
    assert "--severity CRITICAL,HIGH" in texto and "--ignore-unfixed" in texto
    assert texto.count("--exit-code 1") >= 3
    assert "config" in texto and "06-Secure-DevOps-Cloud/terraform" in texto
    assert "/health" in texto


def test_deploy_somente_main_com_flag_e_environment(ci):
    deploy = ci["jobs"]["deploy"]
    assert set(deploy["needs"]) == {"testes", "gitleaks", "semgrep", "iac", "imagem"}
    condicao = deploy["if"]
    assert "github.event_name == 'push'" in condicao
    assert "refs/heads/main" in condicao
    assert "vars.AZURE_DEPLOY_ENABLED == 'true'" in condicao
    assert deploy["environment"]["name"] == "production"
    texto = CI.read_text(encoding="utf-8")
    for segredo in ("AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID",
                    "TFSTATE_RESOURCE_GROUP", "TFSTATE_STORAGE_ACCOUNT", "TFSTATE_CONTAINER",
                    "TFSTATE_KEY", "OPENROUTER_API_KEY", "ADMIN_TOKEN", "PIPELINE_TOKEN"):
        assert f"secrets.{segredo}" in texto, segredo
    assert 'deploy_container=false' in texto and 'deploy_container=true' in texto
    assert 'image_tag=${GITHUB_SHA}' in texto
    assert "terraform output -raw app_url" in texto


def test_actions_com_versao_fixa(ci):
    texto = CI.read_text(encoding="utf-8")
    usos = re.findall(r"uses:\s*([^\s#]+)", texto)
    assert usos
    for uso in usos:
        _, _, versao = uso.partition("@")
        assert versao and versao not in {"main", "master", "latest"}, uso
    assert "trivy:latest" not in texto and "semgrep:latest" not in texto


def test_nenhum_segredo_literal_no_workflow():
    for arquivo in WORKFLOWS.glob("*.y*ml"):
        texto = arquivo.read_text(encoding="utf-8")
        for linha in texto.splitlines():
            m = re.match(r"\s*([A-Z_]*(TOKEN|KEY|SECRET|PASSWORD)[A-Z_]*):\s*(.+)", linha)
            if m:
                valor = m.group(3).strip().strip('"')
                assert valor == "" or valor.startswith("${{"), linha


def test_gitleaks_config_estende_padrao_e_tem_regra_demo():
    toml = (RAIZ / ".gitleaks.toml").read_text(encoding="utf-8")
    assert "useDefault = true" in toml
    assert 'id = "acessacidade-demo-token"' in toml
    regex = re.search(r"regex = '''(.+?)'''", toml).group(1)
    assert regex == "acd_demo_[a-z0-9]{32}"
    token = "acd_demo_" + "".join(secrets.choice(string.ascii_lowercase + string.digits)
                                  for _ in range(32))
    assert re.fullmatch(regex, token)
    assert r"\.venv" in toml


def test_nenhum_token_demo_completo_no_repositorio():
    padrao = re.compile(r"acd_demo_[a-z0-9]{32}")
    ignorar = {".venv", ".git", "node_modules", ".terraform", "data"}
    for arquivo in RAIZ.rglob("*"):
        if not arquivo.is_file() or ignorar & set(arquivo.relative_to(RAIZ).parts):
            continue
        if arquivo.suffix.lower() not in {".py", ".md", ".txt", ".yml", ".yaml", ".toml",
                                          ".json", ".env", ".example", ".tf", ".ps1", ".sh",
                                          ".js", ".html", ".hcl", ""}:
            continue
        if arquivo.stat().st_size > 2_000_000:
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="ignore")
        assert not padrao.search(texto), f"token de demonstração commitável em {arquivo}"


def test_regras_semgrep_customizadas_validas():
    doc = yaml.safe_load((RAIZ / ".semgrep" / "acessacidade.yml").read_text(encoding="utf-8"))
    ids = {regra["id"] for regra in doc["rules"]}
    for esperado in ("acessacidade-python-eval-exec", "acessacidade-python-requests-sem-timeout",
                     "acessacidade-python-subprocess-shell-true",
                     "acessacidade-python-segredo-hardcoded", "acessacidade-js-innerhtml"):
        assert esperado in ids
    for regra in doc["rules"]:
        assert regra["severity"] in {"ERROR", "WARNING", "INFO"}
        assert regra["languages"] and regra["message"]
    testes = (RAIZ / ".semgrep" / "tests" / "acessacidade.py").read_text(encoding="utf-8")
    assert "ruleid:" in testes and "ok:" in testes


def test_requirements_ci_sem_dependencias_pesadas():
    req = (RAIZ / "06-Secure-DevOps-Cloud" / "github-actions" / "requirements-ci.txt")
    linhas = [l.split("#")[0].strip() for l in req.read_text(encoding="utf-8").splitlines()]
    pacotes = {re.split(r"[=<>\s]", l)[0].lower() for l in linhas if l and not l.startswith("-")}
    assert "cadquery" not in pacotes and "playwright" not in pacotes
    assert "pytest" in pacotes
    assert "-r ../../requirements.txt" in linhas
