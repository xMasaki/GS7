# Arquivo de TESTE das regras Semgrep da equipe (não é código da aplicação).
# Excluído das varreduras do CI (--exclude .semgrep/tests) e da imagem Docker.
# Executar: semgrep --test --config .semgrep/acessacidade.yml .semgrep/tests/
# Os valores abaixo são FICTÍCIOS e servem apenas para exercitar as regras.
import os
import subprocess

import httpx
import requests


def avaliar(entrada):
    # ruleid: acessacidade-python-eval-exec
    eval(entrada)
    # ruleid: acessacidade-python-eval-exec
    exec(entrada)
    # ok: acessacidade-python-eval-exec
    return int(entrada)


def http():
    # ruleid: acessacidade-python-requests-sem-timeout
    requests.get("http://localhost:8000/health")
    # ok: acessacidade-python-requests-sem-timeout
    requests.get("http://localhost:8000/health", timeout=5)
    # ruleid: acessacidade-python-httpx-timeout-none
    httpx.get("http://localhost:8000/health", timeout=None)
    # ok: acessacidade-python-httpx-timeout-none
    httpx.get("http://localhost:8000/health", timeout=10)


def comandos(arquivo):
    # ruleid: acessacidade-python-subprocess-shell-true
    subprocess.run("ls " + arquivo, shell=True)
    # ruleid: acessacidade-python-subprocess-shell-true
    os.system("ls " + arquivo)
    # ok: acessacidade-python-subprocess-shell-true
    subprocess.run(["ls", arquivo], check=True)


# ruleid: acessacidade-python-segredo-hardcoded
ADMIN_TOKEN = "ficticio-nao-usar"
# ruleid: acessacidade-python-segredo-hardcoded
OPENROUTER_API_KEY = "exemplo-ficticio-nao-usar"
# ok: acessacidade-python-segredo-hardcoded
PIPELINE_TOKEN = ""
# ok: acessacidade-python-segredo-hardcoded
OPENROUTER_API_KEY_DOC = "[PREENCHER]"
# ok: acessacidade-python-segredo-hardcoded
ADMIN_TOKEN_HEADER = "X-Admin-Token"

# ruleid: acessacidade-python-segredo-default-env
token = os.environ.get("ADMIN_TOKEN", "padraoficticio")
# ok: acessacidade-python-segredo-default-env
token = os.environ.get("ADMIN_TOKEN", "")
# ok: acessacidade-python-segredo-default-env
porta = os.getenv("APP_PORT", "8000")
