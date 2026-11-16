"""Conexão com o warehouse DuckDB e registro das funções Python usadas no SQL."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import duckdb

from . import parsing, regras
from .config import PipelineConfig

log = logging.getLogger("acessacidade_pipeline")

SCHEMAS = ("raw", "bronze", "silver", "gold")


def registrar_funcoes(con: duckdb.DuckDBPyConnection) -> None:
    """Registra as funções de parsing (técnicas) e de regras (negócio) como funções SQL.
    Mesma técnica do notebook da Aula 06 (con.create_function)."""
    for nome, funcao, parametros, retorno in (*parsing.FUNCOES_SQL, *regras.FUNCOES_SQL):
        # null_handling="special": NULL chega à função como None e ela pode devolver None.
        con.create_function(nome, funcao, parametros, retorno, null_handling="special")


@contextmanager
def conectar(cfg: PipelineConfig, *, read_only: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
    """Abre o arquivo DuckDB (cria pastas/schemas se preciso), registra as UDFs e fecha ao final.
    Cada tarefa da DAG abre e fecha sua própria conexão (as tasks rodam em processos separados)."""
    Path(cfg.warehouse_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(cfg.warehouse_path), read_only=read_only)
    try:
        if not read_only:
            for schema in SCHEMAS:
                con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        registrar_funcoes(con)
        yield con
    finally:
        con.close()


def contar(con: duckdb.DuckDBPyConnection, tabela: str, where: str | None = None) -> int:
    sql = f"SELECT count(*) FROM {tabela}" + (f" WHERE {where}" if where else "")
    return int(con.execute(sql).fetchone()[0])


def colunas(con: duckdb.DuckDBPyConnection, tabela: str) -> list[str]:
    schema, nome = tabela.split(".")
    linhas = con.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = ? AND table_name = ? ORDER BY ordinal_position",
        [schema, nome],
    ).fetchall()
    return [l[0] for l in linhas]


def tabela_existe(con: duckdb.DuckDBPyConnection, tabela: str) -> bool:
    schema, nome = tabela.split(".")
    return bool(
        con.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = ? AND table_name = ?",
            [schema, nome],
        ).fetchone()[0]
    )


def ident(nome: str) -> str:
    """Identificador SQL entre aspas duplas (colunas vindas de arquivos externos)."""
    return '"' + nome.replace('"', '""') + '"'
