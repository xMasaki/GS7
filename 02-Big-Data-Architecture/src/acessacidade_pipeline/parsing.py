"""Funções de parsing TÉCNICO (reconhecer formato -> converter).

Mesma ideia do notebook da Aula 06 (parse_data_multi / parse_valor_brl): funções
puras em Python, registradas no DuckDB com `create_function` e usadas dentro do SQL
da camada Bronze. Elas NÃO tomam decisões de negócio — só entendem formatos.

Convenção de datas: todo TIMESTAMP gravado no warehouse está em UTC (sem fuso).
- Texto com fuso explícito ("2026-10-14T16:22:05Z", "+00:00") -> convertido para UTC.
- Texto sem fuso ("14/10/2026 13:22") -> interpretado no horário de Brasília (UTC-3,
  sem horário de verão desde 2019) e convertido para UTC.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta, timezone

FUSO_LOCAL = timezone(timedelta(hours=-3), "BRT")

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

_RE_ISO = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?)?(?:Z|[+-]\d{2}:?\d{2})?",
    re.IGNORECASE,
)
_RE_BR = re.compile(r"(\d{1,2})([/-])(\d{1,2})\2(\d{4})(?:[ T]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?")
_RE_EXTENSO = re.compile(
    r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})(?:\s*(?:,|as|-)?\s*(\d{1,2})(?::|h)(\d{2})?)?",
    re.IGNORECASE,
)
_RE_NUMERO = re.compile(r"[+-]?\d+(?:\.\d+)?")

_VERDADEIRO = {"true", "t", "1", "sim", "s", "yes", "y", "verdadeiro", "v"}
_FALSO = {"false", "f", "0", "nao", "n", "no", "falso"}


def remover_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def normalizar_texto(valor: str | None) -> str | None:
    """Chave de comparação: sem acento, minúsculas, pontuação/underscore viram espaço,
    espaços colapsados. Ex.: "  Jd. das  Flores " -> "jd das flores". Vazio -> None."""
    if valor is None:
        return None
    texto = remover_acentos(str(valor)).lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    return texto or None


def limpar_espacos(valor: str | None) -> str | None:
    """Remove espaços nas pontas e colapsa espaços internos. Vazio -> None."""
    if valor is None:
        return None
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    return texto or None


def _para_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=FUSO_LOCAL)
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def parse_data_multi(valor: str | None) -> datetime | None:
    """Reconhece os formatos de data/hora vistos nas fontes e devolve TIMESTAMP UTC (naive).

    Formatos aceitos:
      - ISO 8601: 2026-10-14 | 2026-10-14T13:22:05Z | 2026-10-14 13:22:05 | ...+00:00
      - dd/mm/aaaa [hh:mm[:ss]]
      - dd-mm-aaaa [hh:mm[:ss]]
      - "14 de outubro de 2026" [", 13:22" | " às 13h22"]
    Qualquer outra coisa (texto livre, data impossível como 31/09/2026) -> None.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    try:
        if _RE_ISO.fullmatch(texto):
            iso = texto.replace(" ", "T", 1) if len(texto) > 10 else texto
            if iso[-1] in "zZ":
                iso = iso[:-1] + "+00:00"
            return _para_utc(datetime.fromisoformat(iso))
        m = _RE_BR.fullmatch(texto)
        if m:
            dia, _, mes, ano, hh, mi, ss = m.groups()
            dt = datetime(int(ano), int(mes), int(dia), int(hh or 0), int(mi or 0), int(ss or 0))
            return _para_utc(dt)
        m = _RE_EXTENSO.fullmatch(remover_acentos(texto).lower())
        if m:
            dia, mes_nome, ano, hh, mi = m.groups()
            mes = MESES.get(mes_nome)
            if mes:
                return _para_utc(datetime(int(ano), mes, int(dia), int(hh or 0), int(mi or 0)))
    except (ValueError, OverflowError):
        return None
    return None


def parse_decimal(valor: str | None) -> float | None:
    """Número decimal com ponto ou vírgula: "-23,55" / "-23.55" / " 0,72 " -> float.
    Formatos ambíguos ("-23.5.1", "1.234,5", "abc") -> None."""
    if valor is None:
        return None
    texto = str(valor).strip().replace(" ", "")
    if not texto:
        return None
    if "," in texto:
        if "." in texto or texto.count(",") > 1:
            return None
        texto = texto.replace(",", ".")
    if not _RE_NUMERO.fullmatch(texto):
        return None
    return float(texto)


def parse_coordenada(valor: str | None) -> float | None:
    """Coordenada em graus decimais escrita como texto (vírgula ou ponto decimal).
    Só converte o formato; a validação de faixa é feita na Bronze (flag_coordenada_invalida)."""
    return parse_decimal(valor)


def parse_booleano(valor: str | None) -> bool | None:
    """'true'/'TRUE'/'1'/'sim'/'não'/'false'/'0' -> bool. Não reconhecido -> None."""
    chave = normalizar_texto(valor)
    if chave is None:
        return None
    if chave in _VERDADEIRO:
        return True
    if chave in _FALSO:
        return False
    return None


# Registro das funções no DuckDB: (nome SQL, função, parâmetros, retorno)
FUNCOES_SQL = (
    ("parse_data_multi", parse_data_multi, ["VARCHAR"], "TIMESTAMP"),
    ("parse_coordenada", parse_coordenada, ["VARCHAR"], "DOUBLE"),
    ("parse_decimal", parse_decimal, ["VARCHAR"], "DOUBLE"),
    ("parse_booleano", parse_booleano, ["VARCHAR"], "BOOLEAN"),
    ("normalizar_texto", normalizar_texto, ["VARCHAR"], "VARCHAR"),
    ("limpar_espacos", limpar_espacos, ["VARCHAR"], "VARCHAR"),
)
