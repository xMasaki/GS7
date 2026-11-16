"""Testes estáticos do Terraform e dos arquivos de infra (sem nuvem, sem credenciais)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
TF = RAIZ / "06-Secure-DevOps-Cloud" / "terraform"
INFRA = RAIZ / "infra"


def _tf(nome: str) -> str:
    return (TF / nome).read_text(encoding="utf-8")


def _todos_tf() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(TF.glob("*.tf")))


def test_arquivos_obrigatorios_existem():
    for nome in ("versions.tf", "providers.tf", "backend.tf", "variables.tf", "main.tf",
                 "outputs.tf", "terraform.tfvars.example"):
        assert (TF / nome).is_file(), nome


def test_versoes_e_backend_parcial():
    versoes = _tf("versions.tf")
    assert re.search(r'required_version\s*=\s*">=\s*1\.6', versoes)
    assert re.search(r'version\s*=\s*"~>\s*4\.', versoes)
    assert 'backend "azurerm" {}' in _tf("backend.tf")


def test_nenhum_segredo_ou_state_versionavel():
    texto = _todos_tf() + _tf("terraform.tfvars.example")
    assert not re.search(r"(password|client_secret|access_key)\s*=\s*\"[^\"$]{6,}\"", texto,
                         re.IGNORECASE)
    for nome in ("openrouter_api_key", "admin_token", "pipeline_token"):
        bloco = re.search(r'variable "%s" \{(.*?)\n\}' % nome, _tf("variables.tf"), re.S).group(1)
        assert "sensitive   = true" in bloco or "sensitive = true" in bloco
        assert re.search(r'default\s*=\s*""', bloco)
    exemplo = _tf("terraform.tfvars.example")
    for linha in exemplo.splitlines():
        if re.match(r"\s*(openrouter_api_key|admin_token|pipeline_token)\s*=", linha):
            pytest.fail(f"segredo atribuído no tfvars.example: {linha}")
    assert not list(TF.glob("*.tfstate")) and not list(TF.glob("*.tfvars"))


def test_somente_porta_8000_e_nenhuma_porta_admin():
    main = _tf("main.tf")
    assert main.count("exposed_port {") == 1
    portas = re.findall(r"port\s*=\s*(\S+)", main)
    assert set(portas) <= {"var.app_port", '"/health"'} or all(p == "var.app_port" for p in portas)
    for proibida in ("22", "3389", "5985", "5986"):
        assert not re.search(rf"port\s*=\s*{proibida}\b", main)
    validacao = re.search(r'variable "app_port" \{(.*?)\n\}', _tf("variables.tf"), re.S).group(1)
    assert "== 8000" in validacao
    assert "0.0.0.0/0" not in _todos_tf()


def test_acr_sem_admin_e_pull_por_identidade_gerenciada():
    main = _tf("main.tf")
    assert "admin_enabled = false" in main
    assert 'role_definition_name = "AcrPull"' in main
    assert "user_assigned_identity_id = azurerm_user_assigned_identity.aci.id" in main
    assert "secure_environment_variables = local.app_secrets" in main
    assert "liveness_probe" in main and "readiness_probe" in main
    assert 'restart_policy      = "Always"' in main
    assert "count = var.deploy_container ? 1 : 0" in main


def test_outputs_esperados():
    saidas = set(re.findall(r'output "([a-z_]+)"', _tf("outputs.tf")))
    assert {"resource_group_name", "acr_login_server", "acr_name", "container_fqdn",
            "app_url", "health_url"} <= saidas


def test_gitignore_cobre_state_tfvars_e_env():
    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    for padrao in ("*.tfstate", "*.tfstate.*", "*.tfvars", "!*.tfvars.example", ".env",
                   "**/.terraform/*", "data/runtime/"):
        assert padrao in gitignore, padrao


def test_template_aci_sem_segredos_e_so_porta_8000():
    yaml = pytest.importorskip("yaml")
    texto = (INFRA / "aci-deployment.template.yaml").read_text(encoding="utf-8")
    doc = yaml.safe_load(texto)
    portas = doc["properties"]["ipAddress"]["ports"]
    assert [p["port"] for p in portas] == [8000]
    for item in re.findall(r"secureValue:\s*(.+)", texto):
        assert item.strip().strip("'\"").startswith("${"), item


def test_scripts_azure_classificam_comandos():
    scripts = sorted((INFRA / "azure").glob("*.ps1")) + sorted((INFRA / "azure").glob("*.sh"))
    assert len(scripts) >= 10
    for script in scripts:
        texto = script.read_text(encoding="utf-8")
        assert re.search(r"\[(SOMENTE LEITURA|CRIA RECURSOS/CUSTO|REMOVE RECURSOS)", texto), script.name
    limpeza = (INFRA / "azure" / "99_limpeza.sh").read_text(encoding="utf-8")
    assert "NÃO EXECUTAR ANTES DO FIM DA CORREÇÃO" in limpeza
