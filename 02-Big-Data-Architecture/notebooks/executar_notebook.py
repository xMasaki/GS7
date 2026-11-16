"""Executa o notebook da disciplina 02 com nbclient e salva COM as saídas.

Uso (na raiz do repositório):
    .\.venv\Scripts\python.exe 02-Big-Data-Architecture/notebooks/executar_notebook.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

NOTEBOOK = Path(__file__).resolve().parent / "AcessaCidade_ELT_Raw_Bronze_Silver_Gold.ipynb"


def main() -> int:
    nb = nbformat.read(NOTEBOOK, as_version=4)
    NotebookClient(nb, timeout=300, kernel_name="python3",
                   resources={"metadata": {"path": str(NOTEBOOK.parent)}}).execute()
    nbformat.write(nb, NOTEBOOK)
    erros = sum(1 for c in nb.cells if c.cell_type == "code"
                for o in c.get("outputs", []) if o.get("output_type") == "error")
    print(f"Notebook executado e salvo: {NOTEBOOK.name} | células: {len(nb.cells)} | erros: {erros}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
