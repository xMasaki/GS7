"""Transform (dentro do warehouse): camada BRONZE — só a parte TÉCNICA.

O que a Bronze faz (mesmos princípios do notebook da Aula 06):
- une as duas fontes RAW em uma única tabela, com a coluna `fonte`;
- remove DUPLICATAS TÉCNICAS: linha de origem 100% idêntica a outra, campo a campo
  (row_number() OVER (PARTITION BY todas as colunas de origem)), por fonte;
- tipa as colunas: datas -> TIMESTAMP UTC (parse_data_multi), coordenadas e pontuação ->
  DOUBLE, booleanos -> BOOLEAN, id -> BIGINT (TRY_CAST: valor ruim vira NULL, a carga não cai);
- SINALIZA problemas em colunas flag_* em vez de resolvê-los;
- MINIMIZAÇÃO LGPD: `nome_denunciante` NÃO passa da RAW; só o indicador flag_possui_nome.

O que a Bronze NÃO faz: padronizar bairro/categoria/status (regra de negócio -> Silver),
decidir se coordenada fora do Brasil é aceitável, deduplicar a "mesma ocorrência" registrada
duas vezes com grafias diferentes.
"""
from __future__ import annotations

import logging

from .dominio import FONTE_API, FONTE_SIMULADA
from .raw import METADADOS, TABELA_APP, TABELA_SIMULADA
from .warehouse import colunas, contar, ident

log = logging.getLogger("acessacidade_pipeline")

TABELA_BRONZE = "bronze.denuncias"


def _cte_fonte(con, tabela: str, fonte: str, alias: str) -> str:
    cols_origem = [c for c in colunas(con, tabela) if c not in METADADOS]
    particao = ", ".join(ident(c) for c in cols_origem)
    nome = "nome_denunciante" if "nome_denunciante" in cols_origem else "NULL"
    origem_dado = "origem_dado" if "origem_dado" in cols_origem else "NULL"
    return f"""
    {alias}_dedup AS (
        -- dedup TÉCNICO: linha de origem idêntica a outra, campo a campo (mantém a 1ª ocorrência)
        SELECT *, row_number() OVER (PARTITION BY {particao} ORDER BY _row_id) AS _dedup_rank
        FROM {tabela}
    ),
    {alias} AS (
        SELECT '{fonte}' AS fonte,
               id, protocolo, criado_em, atualizado_em, logradouro, numero, bairro, cidade,
               ponto_referencia, tipo_obstaculo, descricao, impacto, latitude, longitude, status,
               origem, simulado, possui_imagem, visao_classificacao, visao_pontuacao, revisao_humana,
               CAST({nome} AS VARCHAR)        AS _nome_somente_para_flag,
               CAST({origem_dado} AS VARCHAR) AS origem_dado,
               _source_file, _ingested_at, _row_id, _batch_id
        FROM {alias}_dedup
        WHERE _dedup_rank = 1
    )"""


def construir_bronze(con) -> dict:
    sql = f"""
    CREATE OR REPLACE TABLE {TABELA_BRONZE} AS
    WITH
    {_cte_fonte(con, TABELA_SIMULADA, FONTE_SIMULADA, 'sim')},
    {_cte_fonte(con, TABELA_APP, FONTE_API, 'app')},
    uniao AS (
        SELECT * FROM sim
        UNION ALL BY NAME
        SELECT * FROM app
    ),
    tipado AS (
        SELECT
            fonte,
            TRY_CAST(trim(id) AS BIGINT)            AS id_origem,
            NULLIF(trim(protocolo), '')             AS protocolo,
            parse_data_multi(criado_em)             AS criado_em,
            parse_data_multi(atualizado_em)         AS atualizado_em,
            NULLIF(trim(logradouro), '')            AS logradouro,
            NULLIF(trim(numero), '')                AS numero,
            NULLIF(trim(bairro), '')                AS bairro,          -- grafia crua: padronizar é regra de negócio (Silver)
            NULLIF(trim(cidade), '')                AS cidade,
            NULLIF(trim(ponto_referencia), '')      AS ponto_referencia,
            NULLIF(trim(tipo_obstaculo), '')        AS tipo_obstaculo,  -- texto cru: mapear para o contrato é Silver
            NULLIF(trim(descricao), '')             AS descricao,
            NULLIF(trim(impacto), '')               AS impacto,
            NULLIF(trim(status), '')                AS status,
            NULLIF(trim(origem), '')                AS origem,
            parse_booleano(simulado)                AS simulado,
            parse_booleano(possui_imagem)           AS possui_imagem,
            NULLIF(trim(visao_classificacao), '')   AS visao_classificacao,
            NULLIF(trim(revisao_humana), '')        AS revisao_humana,
            NULLIF(trim(origem_dado), '')           AS origem_dado,
            parse_coordenada(latitude)              AS _lat,
            parse_coordenada(longitude)             AS _lon,
            NULLIF(trim(latitude), '') IS NOT NULL  AS _lat_informada,
            NULLIF(trim(longitude), '') IS NOT NULL AS _lon_informada,
            parse_decimal(visao_pontuacao)          AS _pontuacao,
            NULLIF(trim(visao_pontuacao), '') IS NOT NULL AS _pontuacao_informada,
            NULLIF(trim(criado_em), '') IS NULL     AS flag_data_ausente,
            NULLIF(trim(_nome_somente_para_flag), '') IS NOT NULL AS flag_possui_nome,
            _source_file, _ingested_at, _row_id, _batch_id
        FROM uniao
    ),
    validado AS (
        SELECT *,
            COALESCE(_lat BETWEEN -90 AND 90 AND _lon BETWEEN -180 AND 180, false) AS _coord_ok,
            COALESCE(_pontuacao BETWEEN 0 AND 1, false)                           AS _pontuacao_ok
        FROM tipado
    )
    SELECT
        fonte, id_origem, protocolo, criado_em, atualizado_em, logradouro, numero, bairro, cidade,
        ponto_referencia, tipo_obstaculo, descricao, impacto,
        CASE WHEN _coord_ok THEN _lat END        AS latitude,
        CASE WHEN _coord_ok THEN _lon END        AS longitude,
        status, origem, simulado, possui_imagem, visao_classificacao,
        CASE WHEN _pontuacao_ok THEN _pontuacao END AS visao_pontuacao,
        revisao_humana, origem_dado,
        flag_possui_nome,
        flag_data_ausente,
        (NOT flag_data_ausente AND criado_em IS NULL)                  AS flag_data_invalida,
        (NOT _lat_informada AND NOT _lon_informada)                    AS flag_coordenada_ausente,
        ((_lat_informada OR _lon_informada) AND NOT _coord_ok)         AS flag_coordenada_invalida,
        (_pontuacao_informada AND NOT _pontuacao_ok)                   AS flag_pontuacao_invalida,
        (logradouro IS NULL)                                           AS flag_logradouro_ausente,
        (bairro IS NULL)                                               AS flag_bairro_ausente,
        (tipo_obstaculo IS NULL)                                       AS flag_tipo_ausente,
        (descricao IS NULL)                                            AS flag_descricao_ausente,
        (impacto IS NULL)                                              AS flag_impacto_ausente,
        (logradouro IS NULL OR bairro IS NULL OR tipo_obstaculo IS NULL OR descricao IS NULL
         OR impacto IS NULL OR flag_data_ausente)                      AS flag_campo_obrigatorio_ausente,
        _source_file, _ingested_at, _row_id, _batch_id
    FROM validado
    ORDER BY fonte DESC, _row_id
    """
    con.execute(sql)

    n_raw_sim = contar(con, TABELA_SIMULADA)
    n_raw_app = contar(con, TABELA_APP)
    n_br_sim = contar(con, TABELA_BRONZE, f"fonte = '{FONTE_SIMULADA}'")
    n_br_app = contar(con, TABELA_BRONZE, f"fonte = '{FONTE_API}'")
    resultado = {
        "linhas_raw": n_raw_sim + n_raw_app,
        "linhas_bronze": n_br_sim + n_br_app,
        "duplicatas_tecnicas_simuladas": n_raw_sim - n_br_sim,
        "duplicatas_tecnicas_app": n_raw_app - n_br_app,
        "duplicatas_removidas": (n_raw_sim + n_raw_app) - (n_br_sim + n_br_app),
    }
    log.info("[bronze] %s", resultado)
    return resultado
