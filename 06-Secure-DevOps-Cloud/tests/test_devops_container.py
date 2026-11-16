"""Testes estáticos do container: Dockerfile, .dockerignore e docker-compose.yml.

Não exigem Docker instalado: validam o conteúdo dos arquivos contra os
requisitos da Disciplina 06 (imagem enxuta, não root, sem segredo, compose
endurecido, monitoramento só em 127.0.0.1) e o contrato de integração (seção 2.1).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

RAIZ = Path(__file__).resolve().parents[2]
DOCKERFILE = RAIZ / "06-Secure-DevOps-Cloud" / "docker" / "Dockerfile"
DOCKERIGNORE = RAIZ / ".dockerignore"
COMPOSE = RAIZ / "docker-compose.yml"
SENSIVEIS = re.compile(r"(SECRET|KEY|TOKEN|PASSWORD|SENHA)", re.IGNORECASE)


def _instrucoes(texto: str) -> list[tuple[str, str]]:
    """Junta linhas continuadas com "\\" e devolve (INSTRUÇÃO, argumentos)."""
    linhas, atual = [], ""
    for linha in texto.splitlines():
        if linha.strip().startswith("#") and not atual:
            continue
        if linha.rstrip().endswith("\\"):
            atual += linha.rstrip()[:-1] + " "
            continue
        atual += linha
        if atual.strip():
            partes = atual.strip().split(None, 1)
            linhas.append((partes[0].upper(), partes[1] if len(partes) > 1 else ""))
        atual = ""
    return linhas


@pytest.fixture(scope="module")
def dockerfile() -> list[tuple[str, str]]:
    return _instrucoes(DOCKERFILE.read_text(encoding="utf-8"))


def _estagio_final(instrucoes):
    indices = [i for i, (cmd, _) in enumerate(instrucoes) if cmd == "FROM"]
    return instrucoes[indices[-1]:]


def test_dockerfile_multi_stage_com_base_slim(dockerfile):
    froms = [arg for cmd, arg in dockerfile if cmd == "FROM"]
    assert len(froms) >= 2, "esperado build multi-stage (builder + runtime)"
    texto = DOCKERFILE.read_text(encoding="utf-8")
    assert "python:3.11-slim" in texto
    assert "/opt/venv" in texto


def test_dockerfile_usuario_nao_root_no_estagio_final(dockerfile):
    final = _estagio_final(dockerfile)
    users = [arg.strip() for cmd, arg in final if cmd == "USER"]
    assert users, "estágio final precisa de USER"
    ultimo = users[-1].split(":")[0]
    assert ultimo not in {"root", "0"}
    assert ultimo == "10001"


def test_dockerfile_healthcheck_expose_e_cmd(dockerfile):
    final = _estagio_final(dockerfile)
    comandos = {cmd for cmd, _ in final}
    assert {"HEALTHCHECK", "EXPOSE", "CMD"} <= comandos
    health = next(arg for cmd, arg in final if cmd == "HEALTHCHECK")
    assert "/health" in health and "urllib" in health
    assert any(cmd == "EXPOSE" and "8000" in arg.split() for cmd, arg in final)
    cmd = next(arg for c, arg in final if c == "CMD")
    assert "acessacidade_api.main:app" in cmd
    assert "8000" in cmd and "--proxy-headers" in cmd


def test_dockerfile_sem_segredos_em_env_ou_arg(dockerfile):
    for cmd, arg in dockerfile:
        if cmd not in {"ENV", "ARG"}:
            continue
        for nome in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", arg):
            assert not SENSIVEIS.search(nome), f"{cmd} {nome} parece sensível"
    texto = DOCKERFILE.read_text(encoding="utf-8")
    for variavel in ("ADMIN_TOKEN=", "PIPELINE_TOKEN=", "OPENROUTER_API_KEY="):
        assert variavel not in texto
    assert not any(cmd == "COPY" and ".env" in arg.split()[0] for cmd, arg in dockerfile)


def test_dockerfile_pythonpath_e_data_dir_do_contrato(dockerfile):
    texto = DOCKERFILE.read_text(encoding="utf-8")
    assert ("PYTHONPATH=\"/app/app/backend:/app/01-Generative-AI-Engineering/src:"
            "/app/04-Applied-Computer-Vision/src\"") in texto
    assert "DATA_DIR=/app/data/runtime" in texto
    final = _estagio_final(dockerfile)
    copias = " ".join(arg for cmd, arg in final if cmd == "COPY")
    for origem in ("app/backend", "app/frontend", "01-Generative-AI-Engineering/src",
                   "01-Generative-AI-Engineering/prompts", "04-Applied-Computer-Vision/src",
                   "data/samples/fotos"):
        assert origem in copias, f"estágio final deveria copiar {origem}"
    assert "--from=builder /opt/venv" in copias
    assert "chown -R 10001:10001 /app/data/runtime" in texto


def test_dockerfile_labels_oci(dockerfile):
    labels = " ".join(arg for cmd, arg in dockerfile if cmd == "LABEL")
    for chave in ("org.opencontainers.image.title", "org.opencontainers.image.source",
                  "org.opencontainers.image.revision"):
        assert chave in labels


def test_dockerignore_exclui_segredos_estado_e_peso():
    linhas = {l.strip() for l in DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")}
    for item in (".env", ".venv", ".git", "data/runtime", "**/*.duckdb", "**/*.tfstate",
                 "**/*.tfvars", "07-Project-Based-Maker-Lab", "**/*.pdf"):
        assert item in linhas, f".dockerignore deveria conter {item}"


@pytest.fixture(scope="module")
def compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def test_compose_servico_app_endurecido(compose):
    app = compose["services"]["app"]
    assert app["build"]["dockerfile"] == "06-Secure-DevOps-Cloud/docker/Dockerfile"
    assert app["build"]["context"] == "."
    assert "8000:8000" in app["ports"]
    assert app.get("read_only") is True
    assert "ALL" in app.get("cap_drop", [])
    assert any("no-new-privileges" in s for s in app.get("security_opt", []))
    assert any(str(v).endswith(":/app/data/runtime") for v in app["volumes"])
    assert app.get("restart") == "unless-stopped"
    assert "healthcheck" in app
    env_file = app.get("env_file")
    assert env_file and env_file[0].get("required") is False


def test_compose_monitoramento_no_profile_e_somente_localhost(compose):
    servicos = compose["services"]
    for nome in ("prometheus", "grafana"):
        assert nome in servicos
    for nome, servico in servicos.items():
        if nome == "app":
            continue
        assert "monitoring" in servico.get("profiles", []), nome
        for porta in servico.get("ports", []):
            assert str(porta).startswith("127.0.0.1:"), f"{nome} expõe {porta} fora do localhost"
        imagem = servico["image"]
        tag = imagem.rsplit(":", 1)[-1]
        assert ":" in imagem and tag not in {"latest", "main"}, f"{nome} sem versão fixa"


def test_compose_grafana_sem_senha_padrao(compose):
    grafana = compose["services"]["grafana"]
    senha = str(grafana["environment"]["GF_SECURITY_ADMIN_PASSWORD"])
    assert senha in {"${GRAFANA_ADMIN_PASSWORD:-}", "${GRAFANA_ADMIN_PASSWORD}",
                     "${GRAFANA_ADMIN_PASSWORD:?}"}, senha
    assert str(grafana["environment"]["GF_AUTH_ANONYMOUS_ENABLED"]).lower() == "false"


def test_compose_nao_contem_segredos_literais(compose):
    for nome, servico in compose["services"].items():
        ambiente = servico.get("environment") or {}
        for chave, valor in ambiente.items():
            if SENSIVEIS.search(chave):
                assert str(valor).startswith("${"), f"{nome}.{chave} com valor literal"
