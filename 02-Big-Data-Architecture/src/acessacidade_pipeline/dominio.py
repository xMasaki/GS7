"""Enumerações do domínio AcessaCidade (chave -> rótulo).

Fonte normativa: docs/CONTRATOS_DE_INTEGRACAO.md, seção 3. A ordem dos dicionários
é a ordem de exibição usada nas tabelas Gold.
"""
from __future__ import annotations

TIPO_OBSTACULO: dict[str, str] = {
    "BURACO_CALCADA": "Buraco na calçada",
    "BURACO_VIA": "Buraco na via ou travessia",
    "CALCADA_DANIFICADA": "Calçada quebrada ou desnivelada",
    "RAMPA_IRREGULAR": "Rampa ausente ou irregular",
    "PISO_TATIL": "Piso tátil ausente ou danificado",
    "OBSTACULO_FIXO": "Obstáculo fixo (poste, lixeira, placa)",
    "OBSTACULO_TEMPORARIO": "Obstáculo temporário (entulho, veículo, obra)",
    "OUTRO": "Outro",
}

IMPACTO: dict[str, str] = {
    "IMPEDE_PASSAGEM": "Impede a passagem",
    "DIFICULTA_PASSAGEM": "Dificulta a passagem",
    "RISCO_QUEDA": "Risco de queda ou acidente",
    "BAIXO_IMPACTO": "Baixo impacto",
}

STATUS: dict[str, str] = {
    "RECEBIDA": "Recebida",
    "EM_ANALISE": "Em análise",
    "AGUARDANDO_REVISAO": "Aguardando revisão",
    "ENCAMINHADA": "Encaminhada",
    "RESOLVIDA": "Resolvida",
}

# Chave None = denúncia sem fotografia (não analisada) — contrato 3.4.
VISAO_CLASSIFICACAO: dict[str | None, str] = {
    "POSSIBLE_POTHOLE": "Possível buraco identificado",
    "NOT_IDENTIFIED": "Nenhum indício suficiente de buraco",
    "INCONCLUSIVE": "Análise inconclusiva",
    None: "Sem fotografia (não analisada)",
}

ORIGEM: tuple[str, ...] = ("WEB", "RPA", "SIMULADO", "API")

REVISAO_HUMANA: tuple[str, ...] = ("CONFIRMADO", "DESCARTADO")

# Colunas da exportação da API (contrato 4.7) — ordem fixa, sem nome do denunciante.
COLUNAS_EXPORTACAO_API: tuple[str, ...] = (
    "id", "protocolo", "criado_em", "atualizado_em", "logradouro", "numero", "bairro",
    "cidade", "ponto_referencia", "tipo_obstaculo", "descricao", "impacto", "latitude",
    "longitude", "status", "origem", "simulado", "possui_imagem", "visao_classificacao",
    "visao_pontuacao", "revisao_humana",
)

# Fonte simulada = colunas da exportação + nome_denunciante (para demonstrar a minimização
# LGPD na passagem raw -> bronze) + origem_dado (marca explícita de dado SIMULADO).
COLUNAS_FONTE_SIMULADA: tuple[str, ...] = COLUNAS_EXPORTACAO_API + ("nome_denunciante", "origem_dado")

# Nomes das fontes, iguais aos usados no snapshot Gold (contrato 4.8, campo "fontes").
FONTE_SIMULADA = "denuncias_simuladas.csv"
FONTE_API = "api_export"

CIDADE_PADRAO = "Cidade Exemplo"
CIDADE_NAO_INFORMADA = "Não informada"
