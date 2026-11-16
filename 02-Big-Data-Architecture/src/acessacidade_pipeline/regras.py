"""Regras de NEGÓCIO da camada Silver (padronização e mapeamento de domínio).

Diferente de `parsing.py` (só formato), aqui mora o conhecimento do domínio AcessaCidade:
quais grafias são o mesmo bairro, que texto livre corresponde a qual categoria do
contrato, qual status assumir quando ele não veio etc. Cada regra tem um código RN-xx
documentado em 02-Big-Data-Architecture/docs/REGRAS_DE_NEGOCIO.md.

As funções são registradas no DuckDB (create_function) e usadas no SQL da Silver.
"""
from __future__ import annotations

from .dominio import (
    CIDADE_NAO_INFORMADA,
    CIDADE_PADRAO,
    IMPACTO,
    STATUS,
    TIPO_OBSTACULO,
    VISAO_CLASSIFICACAO,
)
from .parsing import limpar_espacos, normalizar_texto

# ---------------------------------------------------------------------------
# RN-01 — Bairros: dicionário de bairros conhecidos da Cidade Exemplo (fictícia)
# ---------------------------------------------------------------------------
# Abreviações expandidas antes da consulta ao dicionário (token a token).
ABREVIACOES_BAIRRO = {
    "jd": "jardim", "jdm": "jardim", "jard": "jardim",
    "v": "vila", "vl": "vila",
    "s": "sao", "sto": "santo", "sta": "santa",
    "pq": "parque", "pque": "parque", "prq": "parque",
    "res": "residencial", "conj": "conjunto", "cj": "conjunto",
}

# chave normalizada (sem acento, minúscula, abreviações expandidas) -> nome oficial
BAIRROS_CANONICOS = {
    "centro": "Centro",
    "jardim das flores": "Jardim das Flores",
    "vila nova": "Vila Nova",
    "sao jose": "São José",
    "bela vista": "Bela Vista",
    "parque das arvores": "Parque das Árvores",
    "santa luzia": "Santa Luzia",
    "nova esperanca": "Nova Esperança",
}

_MINUSCULAS = {"da", "das", "de", "do", "dos", "e"}


def chave_bairro(valor: str | None) -> str | None:
    base = normalizar_texto(valor)
    if base is None:
        return None
    return " ".join(ABREVIACOES_BAIRRO.get(t, t) for t in base.split())


def _titulo(texto: str) -> str:
    palavras = texto.split(" ")
    return " ".join(
        p.lower() if (i > 0 and p.lower() in _MINUSCULAS) else p[:1].upper() + p[1:].lower()
        for i, p in enumerate(palavras)
    )


def padronizar_bairro(valor: str | None) -> str | None:
    """RN-01: grafia oficial do bairro. Conhecido -> nome do dicionário; desconhecido ->
    texto limpo em "Título" (sem inventar correspondência). Vazio -> None."""
    chave = chave_bairro(valor)
    if chave is None:
        return None
    if chave in BAIRROS_CANONICOS:
        return BAIRROS_CANONICOS[chave]
    return _titulo(limpar_espacos(str(valor)).strip(" .,;-"))


def bairro_reconhecido(valor: str | None) -> bool | None:
    chave = chave_bairro(valor)
    if chave is None:
        return None
    return chave in BAIRROS_CANONICOS


# ---------------------------------------------------------------------------
# RN-02 — Cidade
# ---------------------------------------------------------------------------
CIDADES_CANONICAS = {"cidade exemplo": CIDADE_PADRAO}
ABREVIACOES_CIDADE = {"cid": "cidade", "cd": "cidade"}


def padronizar_cidade(valor: str | None) -> str:
    base = normalizar_texto(valor)
    if base is None:
        return CIDADE_NAO_INFORMADA
    chave = " ".join(ABREVIACOES_CIDADE.get(t, t) for t in base.split())
    return CIDADES_CANONICAS.get(chave) or _titulo(limpar_espacos(str(valor)))


# ---------------------------------------------------------------------------
# RN-03 — Endereço normalizado (chave para a deduplicação de negócio)
# ---------------------------------------------------------------------------
ABREVIACOES_LOGRADOURO = {
    "r": "rua", "av": "avenida", "avn": "avenida", "tv": "travessa", "trav": "travessa",
    "al": "alameda", "pc": "praca", "pca": "praca", "pr": "praca", "est": "estrada",
    "rod": "rodovia", "lgo": "largo",
}


def normalizar_logradouro(valor: str | None) -> str | None:
    base = normalizar_texto(valor)
    if base is None:
        return None
    tokens = base.split()
    tokens[0] = ABREVIACOES_LOGRADOURO.get(tokens[0], tokens[0])
    return " ".join(tokens)


def normalizar_numero(valor: str | None) -> str | None:
    """"S/N", "s/n", "SN" -> "S/N"; "120 a" -> "120A"; vazio -> None."""
    base = normalizar_texto(valor)
    if base is None:
        return None
    compacto = base.replace(" ", "")
    if compacto in {"sn", "semnumero", "snumero"}:
        return "S/N"
    return compacto.upper()


# ---------------------------------------------------------------------------
# RN-04 — Tipo de obstáculo -> chave do contrato 3.1
# ---------------------------------------------------------------------------
_TIPO_POR_TEXTO = {normalizar_texto(k): k for k in TIPO_OBSTACULO}
_TIPO_POR_TEXTO.update({normalizar_texto(v): k for k, v in TIPO_OBSTACULO.items()})

# Regras por palavra-chave, avaliadas EM ORDEM (a primeira que casar vence).
REGRAS_TIPO_PALAVRAS: tuple[tuple[tuple[str, ...], tuple[str, ...], str], ...] = (
    # (todas estas palavras, pelo menos uma destas (vazio = nenhuma exigida), chave)
    (("tatil",), (), "PISO_TATIL"),
    (("rampa",), (), "RAMPA_IRREGULAR"),
    (("buraco",), ("via", "rua", "travessia", "asfalto", "pista", "faixa"), "BURACO_VIA"),
    (("buraco",), (), "BURACO_CALCADA"),
    ((), ("quebrada", "quebrado", "desnivel", "desnivelada", "danificada", "rachada", "solto", "solta", "irregular"), "CALCADA_DANIFICADA"),
    ((), ("poste", "lixeira", "placa", "orelhao", "hidrante", "banco fixo"), "OBSTACULO_FIXO"),
    ((), ("entulho", "veiculo", "carro", "moto", "obra", "tapume", "cacamba", "temporario"), "OBSTACULO_TEMPORARIO"),
    (("outro",), (), "OUTRO"),
    (("outros",), (), "OUTRO"),
)


def _casa(texto: str, todas: tuple[str, ...], alguma: tuple[str, ...]) -> bool:
    palavras = f" {texto} "
    if any(f" {p} " not in palavras for p in todas):
        return False
    if alguma and not any(f" {p} " in palavras for p in alguma):
        return False
    return bool(todas or alguma)


def mapear_tipo_obstaculo(valor: str | None) -> str | None:
    """RN-04: chave exata, rótulo exato ou palavras-chave -> chave do contrato.
    Texto informado que não casa com nenhuma regra -> "OUTRO" (sinalizado por
    tipo_obstaculo_reconhecido = false). Vazio -> None (campo obrigatório ausente)."""
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    if texto in _TIPO_POR_TEXTO:
        return _TIPO_POR_TEXTO[texto]
    for todas, alguma, chave in REGRAS_TIPO_PALAVRAS:
        if _casa(texto, todas, alguma):
            return chave
    return "OUTRO"


def tipo_obstaculo_reconhecido(valor: str | None) -> bool | None:
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    if texto in _TIPO_POR_TEXTO:
        return True
    return any(_casa(texto, todas, alguma) for todas, alguma, _ in REGRAS_TIPO_PALAVRAS)


# ---------------------------------------------------------------------------
# RN-05 — Impacto -> chave do contrato 3.2
# ---------------------------------------------------------------------------
_IMPACTO_POR_TEXTO = {normalizar_texto(k): k for k in IMPACTO}
_IMPACTO_POR_TEXTO.update({normalizar_texto(v): k for k, v in IMPACTO.items()})
REGRAS_IMPACTO = (
    (("impede", "bloqueia", "intransitavel"), "IMPEDE_PASSAGEM"),
    (("dificulta", "atrapalha"), "DIFICULTA_PASSAGEM"),
    (("risco", "queda", "acidente", "perigo"), "RISCO_QUEDA"),
    (("baixo", "leve", "pequeno"), "BAIXO_IMPACTO"),
)


def mapear_impacto(valor: str | None) -> str | None:
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    if texto in _IMPACTO_POR_TEXTO:
        return _IMPACTO_POR_TEXTO[texto]
    for palavras, chave in REGRAS_IMPACTO:
        if any(f" {p} " in f" {texto} " for p in palavras):
            return chave
    return None


# ---------------------------------------------------------------------------
# RN-06 — Status -> chave do contrato 3.3
# ---------------------------------------------------------------------------
_STATUS_POR_TEXTO = {normalizar_texto(k): k for k in STATUS}
_STATUS_POR_TEXTO.update({normalizar_texto(v): k for k, v in STATUS.items()})
_STATUS_POR_TEXTO.update({
    "recebido": "RECEBIDA", "nova": "RECEBIDA", "novo": "RECEBIDA", "aberta": "RECEBIDA",
    "analise": "EM_ANALISE", "em analise": "EM_ANALISE", "analisando": "EM_ANALISE",
    "aguardando": "AGUARDANDO_REVISAO", "aguardando revisao humana": "AGUARDANDO_REVISAO",
    "revisao": "AGUARDANDO_REVISAO",
    "encaminhado": "ENCAMINHADA", "resolvido": "RESOLVIDA", "concluida": "RESOLVIDA",
})


def mapear_status(valor: str | None) -> str | None:
    """RN-06: devolve a chave do contrato ou None (não informado / não reconhecido).
    O SQL da Silver aplica a regra de status inicial (RECEBIDA) quando o retorno é None."""
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    return _STATUS_POR_TEXTO.get(texto)


# ---------------------------------------------------------------------------
# RN-07 — Classificação da visão computacional -> chave do contrato 3.4
# ---------------------------------------------------------------------------
_VISAO_POR_TEXTO = {normalizar_texto(k): k for k in VISAO_CLASSIFICACAO if k}
_VISAO_POR_TEXTO.update({normalizar_texto(v): k for k, v in VISAO_CLASSIFICACAO.items() if k})
_VISAO_POR_TEXTO.update({
    "possivel buraco": "POSSIBLE_POTHOLE", "buraco": "POSSIBLE_POTHOLE",
    "nao identificado": "NOT_IDENTIFIED", "nao identificada": "NOT_IDENTIFIED",
    "inconclusiva": "INCONCLUSIVE", "inconclusivo": "INCONCLUSIVE",
})


def mapear_visao(valor: str | None) -> str | None:
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    return _VISAO_POR_TEXTO.get(texto)


# ---------------------------------------------------------------------------
# RN-08 — Origem -> contrato 3.5
# ---------------------------------------------------------------------------
_ORIGEM_POR_TEXTO = {
    "web": "WEB", "formulario": "WEB", "site": "WEB",
    "rpa": "RPA", "robo": "RPA", "uipath": "RPA",
    "simulado": "SIMULADO", "simulada": "SIMULADO", "seed": "SIMULADO",
    "api": "API",
}


def mapear_origem(valor: str | None) -> str | None:
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    return _ORIGEM_POR_TEXTO.get(texto)


def mapear_revisao(valor: str | None) -> str | None:
    texto = normalizar_texto(valor)
    if texto is None:
        return None
    if texto.startswith("confirm"):
        return "CONFIRMADO"
    if texto.startswith("descart"):
        return "DESCARTADO"
    return None


FUNCOES_SQL = (
    ("padronizar_bairro", padronizar_bairro, ["VARCHAR"], "VARCHAR"),
    ("bairro_reconhecido", bairro_reconhecido, ["VARCHAR"], "BOOLEAN"),
    ("padronizar_cidade", padronizar_cidade, ["VARCHAR"], "VARCHAR"),
    ("normalizar_logradouro", normalizar_logradouro, ["VARCHAR"], "VARCHAR"),
    ("normalizar_numero", normalizar_numero, ["VARCHAR"], "VARCHAR"),
    ("mapear_tipo_obstaculo", mapear_tipo_obstaculo, ["VARCHAR"], "VARCHAR"),
    ("tipo_obstaculo_reconhecido", tipo_obstaculo_reconhecido, ["VARCHAR"], "BOOLEAN"),
    ("mapear_impacto", mapear_impacto, ["VARCHAR"], "VARCHAR"),
    ("mapear_status", mapear_status, ["VARCHAR"], "VARCHAR"),
    ("mapear_visao", mapear_visao, ["VARCHAR"], "VARCHAR"),
    ("mapear_origem", mapear_origem, ["VARCHAR"], "VARCHAR"),
    ("mapear_revisao", mapear_revisao, ["VARCHAR"], "VARCHAR"),
)
