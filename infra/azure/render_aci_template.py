#!/usr/bin/env python3
"""Renderiza infra/aci-deployment.template.yaml a partir de variáveis de ambiente.

[SOMENTE LEITURA] — não acessa a Azure; apenas gera um arquivo YAML local.

    python infra/azure/render_aci_template.py --saida "%TEMP%/aci-acessacidade.yaml"

Regras:
  * ${VAR} é substituído pelo valor de VAR no ambiente.
  * Variáveis obrigatórias ausentes -> erro (nada é gerado).
  * Itens de environmentVariables cujo secureValue ficaria vazio são REMOVIDOS
    (a aplicação trata token vazio como funcionalidade desativada).
  * O arquivo de saída deve ficar FORA do repositório (contém segredos em texto):
    o script recusa gravar dentro da pasta do repositório.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TEMPLATE = RAIZ / "infra" / "aci-deployment.template.yaml"
OBRIGATORIAS = ("AZ_LOCATION", "ACI_NAME", "IDENTITY_ID", "ACR_LOGIN_SERVER", "IMAGE_NAME", "IMAGE_TAG", "DNS_LABEL")
SECRETAS = ("ADMIN_TOKEN", "PIPELINE_TOKEN", "OPENROUTER_API_KEY")
_VAR = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


def renderizar(texto: str, ambiente: dict[str, str]) -> str:
    faltando = [v for v in OBRIGATORIAS if not ambiente.get(v)]
    if faltando:
        raise ValueError("Variáveis obrigatórias não definidas: " + ", ".join(faltando))

    # Remove o par "- name: X / secureValue: ${X}" quando o segredo está vazio
    linhas = texto.splitlines()
    saida: list[str] = []
    i = 0
    while i < len(linhas):
        atual = linhas[i]
        prox = linhas[i + 1] if i + 1 < len(linhas) else ""
        m = re.match(r"\s*secureValue:\s*\$\{([A-Z_][A-Z0-9_]*)\}\s*$", prox)
        if atual.strip().startswith("- name:") and m and not ambiente.get(m.group(1)):
            i += 2
            continue
        saida.append(atual)
        i += 1
    texto = "\n".join(saida) + "\n"

    def _sub(match: re.Match[str]) -> str:
        nome = match.group(1)
        valor = ambiente.get(nome, "")
        if nome in SECRETAS:
            # aspas simples YAML: duplica apóstrofos
            return "'" + valor.replace("'", "''") + "'"
        return valor

    # Não substitui dentro de comentários
    resultado = []
    for linha in texto.splitlines():
        if linha.lstrip().startswith("#"):
            continue
        resultado.append(_VAR.sub(_sub, linha))
    return "\n".join(resultado) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", required=True, help="arquivo YAML de saída (FORA do repositório)")
    parser.add_argument("--template", default=str(TEMPLATE))
    args = parser.parse_args(argv)

    destino = Path(args.saida).resolve()
    if RAIZ == destino or RAIZ in destino.parents:
        print("ERRO: grave o arquivo renderizado fora do repositório (ele contém segredos).", file=sys.stderr)
        return 2
    try:
        conteudo = renderizar(Path(args.template).read_text(encoding="utf-8"), dict(os.environ))
    except ValueError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")
    print(f"Template renderizado em {destino} (apague após o deploy).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
