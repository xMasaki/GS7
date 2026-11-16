"""Funções de parsing TÉCNICO (parsing.py)."""
from datetime import datetime

import pytest

from acessacidade_pipeline.parsing import (
    limpar_espacos,
    normalizar_texto,
    parse_booleano,
    parse_coordenada,
    parse_data_multi,
    parse_decimal,
)


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("2026-10-14T16:22:05Z", datetime(2026, 10, 14, 16, 22, 5)),          # UTC explícito
        ("2026-10-14T13:22:05-03:00", datetime(2026, 10, 14, 16, 22, 5)),     # fuso explícito
        ("2026-10-14 13:22:05", datetime(2026, 10, 14, 16, 22, 5)),           # sem fuso = horário de Brasília
        ("2026-10-14", datetime(2026, 10, 14, 3, 0, 0)),
        ("14/10/2026", datetime(2026, 10, 14, 3, 0, 0)),
        ("14/10/2026 13:22", datetime(2026, 10, 14, 16, 22, 0)),
        ("14-10-2026 13:22", datetime(2026, 10, 14, 16, 22, 0)),
        ("14 de outubro de 2026", datetime(2026, 10, 14, 3, 0, 0)),
        ("1 de MARÇO de 2026", datetime(2026, 3, 1, 3, 0, 0)),
        ("  14/10/2026  ", datetime(2026, 10, 14, 3, 0, 0)),
        ("13/11/2026 22:30", datetime(2026, 11, 14, 1, 30, 0)),               # vira o dia em UTC
    ],
)
def test_parse_data_multi_formatos_validos(texto, esperado):
    assert parse_data_multi(texto) == esperado


@pytest.mark.parametrize("texto", [None, "", "   ", "ontem", "sem data", "31/09/2026", "2026-13-05",
                                   "15/10/26", "32 de outubro de 2026", "14 de outubrro de 2026"])
def test_parse_data_multi_invalidas_viram_none(texto):
    assert parse_data_multi(texto) is None


@pytest.mark.parametrize(
    "texto, esperado",
    [("-23,5505", -23.5505), ("-23.5505", -23.5505), (" -10.163919 ", -10.163919), ("0", 0.0),
     ("+5,2", 5.2), ("-123.4", -123.4)],
)
def test_parse_coordenada_virgula_ou_ponto(texto, esperado):
    assert parse_coordenada(texto) == pytest.approx(esperado)


@pytest.mark.parametrize("texto", [None, "", "abc", "-10.18.2", "1.234,5", "1,2,3", "10°S"])
def test_parse_coordenada_invalida(texto):
    assert parse_coordenada(texto) is None


def test_parse_decimal_pontuacao():
    assert parse_decimal("0,72") == pytest.approx(0.72)
    assert parse_decimal("1,70") == pytest.approx(1.70)  # faixa é validada na Bronze, não aqui


@pytest.mark.parametrize("texto, esperado", [("true", True), ("TRUE", True), ("1", True), ("sim", True),
                                             ("false", False), ("0", False), ("não", False), ("FALSE", False),
                                             ("talvez", None), ("", None), (None, None)])
def test_parse_booleano(texto, esperado):
    assert parse_booleano(texto) is esperado


def test_normalizacao_de_texto():
    assert normalizar_texto("  Jd. das  Flores ") == "jd das flores"
    assert normalizar_texto("SÃO JOSÉ") == "sao jose"
    assert normalizar_texto("BURACO_CALCADA") == "buraco calcada"
    assert normalizar_texto(" ... ") is None
    assert limpar_espacos("  Rua   das Acácias ") == "Rua das Acácias"
    assert limpar_espacos("   ") is None
