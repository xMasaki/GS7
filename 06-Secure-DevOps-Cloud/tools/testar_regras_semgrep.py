"""Testa as regras Semgrep customizadas da equipe (.semgrep/acessacidade.yml).

Por que existe: o "semgrep --test" falha no Windows (IndexError em relatively_eq)
e o Semgrep ignora por padrão a pasta ".semgrep/". Este script copia os arquivos
de teste (.semgrep/tests/) para uma pasta temporária, executa
"semgrep scan" e compara os achados com as anotações "ruleid:" (deve achar na
linha seguinte) e "ok:" (não deve achar na linha seguinte).

Uso (na raiz do repositório):
    python 06-Secure-DevOps-Cloud/tools/testar_regras_semgrep.py [--semgrep CAMINHO]

Código de saída: 0 = todas as regras se comportaram como esperado; 1 = divergência;
2 = semgrep não encontrado/erro de execução.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REGRAS = RAIZ / ".semgrep" / "acessacidade.yml"
TESTES = RAIZ / ".semgrep" / "tests"
ANOTACAO = re.compile(r"(ruleid|ok):\s*([\w-]+)")


def anotacoes(pasta: Path) -> tuple[set, set]:
    esperados, proibidos = set(), set()
    for arquivo in sorted(pasta.iterdir()):
        if not arquivo.is_file():
            continue
        for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            m = ANOTACAO.search(linha)
            if m:
                alvo = (arquivo.name, numero + 1, m.group(2))
                (esperados if m.group(1) == "ruleid" else proibidos).add(alvo)
    return esperados, proibidos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semgrep", default=shutil.which("semgrep") or "semgrep")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="semgrep-regras-") as tmp:
        alvo = Path(tmp) / "alvo"
        shutil.copytree(TESTES, alvo)
        saida = Path(tmp) / "resultado.json"
        comando = [args.semgrep, "scan", "--metrics=off", "--quiet",
                   "--config", str(REGRAS), "--json", "-o", str(saida), str(alvo)]
        try:
            # Ferramenta de desenvolvimento: o executável vem do próprio operador (--semgrep),
            # a lista de argumentos é fixa e shell=False. Exceção revisada e justificada.
            # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args
            subprocess.run(comando, check=False, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as erro:
            print(f"ERRO ao executar o semgrep: {erro}")
            return 2
        if not saida.exists():
            print("ERRO: o semgrep não gerou o resultado JSON.")
            return 2
        resultado = json.loads(saida.read_text(encoding="utf-8"))
        encontrados = {
            (Path(r["path"]).name, r["start"]["line"], r["check_id"].split(".")[-1])
            for r in resultado.get("results", [])
        }
        esperados, proibidos = anotacoes(alvo)

    faltando = sorted(esperados - encontrados)
    falsos_positivos = sorted(encontrados & proibidos)
    inesperados = sorted(encontrados - esperados - proibidos)
    print(f"Regras: {REGRAS.relative_to(RAIZ)}")
    print(f"Achados esperados: {len(esperados)} | encontrados: {len(encontrados)}")
    for titulo, itens in (("FALTANDO", faltando), ("FALSO POSITIVO", falsos_positivos),
                          ("INESPERADO", inesperados)):
        for arquivo, linha, regra in itens:
            print(f"  {titulo}: {arquivo}:{linha} {regra}")
    if faltando or falsos_positivos or inesperados or resultado.get("errors"):
        if resultado.get("errors"):
            print(f"  ERROS do semgrep: {resultado['errors'][:3]}")
        print("RESULTADO: FALHOU")
        return 1
    print("RESULTADO: OK — todas as regras customizadas se comportaram como esperado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
