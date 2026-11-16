"""Camada SILVER — regras de NEGÓCIO (documentadas em docs/REGRAS_DE_NEGOCIO.md).

Entrada: bronze.denuncias (tipada, sem duplicata técnica, com flags).
Saídas:
- silver.ref_*                  — tabelas de referência do contrato (chave, rótulo, ordem) e
                                  o dicionário de bairros (RN-01);
- silver.denuncias              — uma linha por denúncia ÚNICA, padronizada, com
                                  `registro_valido` e `motivos_invalidade`;
- silver.denuncias_duplicadas   — quase-duplicatas removidas pela dedup de negócio (RN-11),
                                  com a chave do registro mantido (auditoria).

Nenhuma coluna de dado pessoal: o nome do denunciante já ficou na RAW; aqui só há
`flag_possui_nome`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import pandas as pd

from .dominio import IMPACTO, STATUS, TIPO_OBSTACULO, VISAO_CLASSIFICACAO
from .regras import BAIRROS_CANONICOS
from .warehouse import contar

log = logging.getLogger("acessacidade_pipeline")

TABELA_SILVER = "silver.denuncias"
TABELA_DUPLICADAS = "silver.denuncias_duplicadas"

# RN-10 — área de atendimento: território brasileiro (caixa envolvente aproximada,
# inclui ilhas oceânicas). Coordenada fora dela é descartada e sinalizada.
LIMITES_BRASIL = {"lat_min": -33.8, "lat_max": 5.3, "lon_min": -74.0, "lon_max": -28.8}
# RN-09 — datas plausíveis: não antes do início deste histórico, nem no futuro.
DATA_MINIMA = "2020-01-01"
# Diferença do horário de Brasília para UTC (horas) usada para obter a data LOCAL do registro.
HORAS_UTC_PARA_LOCAL = 3
DESCRICAO_MIN = 10
LOGRADOURO_MIN = 3


def criar_referencias(con) -> None:
    """Tabelas de referência derivadas do contrato (seção 3) — usadas para rótulos e ordem."""
    def _ref(nome: str, mapa: dict) -> None:
        df = pd.DataFrame(
            [{"chave": k, "rotulo": v, "ordem": i + 1} for i, (k, v) in enumerate(mapa.items())]
        )
        con.register("_df_ref", df)
        try:
            con.execute(f"CREATE OR REPLACE TABLE silver.{nome} AS "
                        "SELECT CAST(chave AS VARCHAR) AS chave, CAST(rotulo AS VARCHAR) AS rotulo, "
                        "CAST(ordem AS INTEGER) AS ordem FROM _df_ref ORDER BY ordem")
        finally:
            con.unregister("_df_ref")

    _ref("ref_tipo_obstaculo", TIPO_OBSTACULO)
    _ref("ref_impacto", IMPACTO)
    _ref("ref_status", STATUS)
    _ref("ref_visao_classificacao", VISAO_CLASSIFICACAO)

    df_b = pd.DataFrame([{"chave_normalizada": k, "bairro_oficial": v} for k, v in BAIRROS_CANONICOS.items()])
    con.register("_df_bairros", df_b)
    try:
        con.execute("CREATE OR REPLACE TABLE silver.ref_bairros AS "
                    "SELECT CAST(chave_normalizada AS VARCHAR) AS chave_normalizada, "
                    "CAST(bairro_oficial AS VARCHAR) AS bairro_oficial FROM _df_bairros ORDER BY 2")
    finally:
        con.unregister("_df_bairros")


def construir_silver(con, referencia: datetime | None = None) -> dict:
    """Constrói silver.denuncias e silver.denuncias_duplicadas a partir de bronze.denuncias.
    `referencia` = instante da execução (UTC), usado na regra de data futura (RN-09)."""
    referencia = referencia or datetime.now(timezone.utc).replace(tzinfo=None)
    limite_futuro = (referencia + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    criar_referencias(con)
    L = LIMITES_BRASIL

    con.execute(f"""
    CREATE OR REPLACE TEMP TABLE _silver_base AS
    WITH padronizado AS (
        SELECT
            b.fonte || ':' || lpad(CAST(b._row_id AS VARCHAR), 6, '0')     AS chave_denuncia,
            b.fonte, b.id_origem, b.protocolo,
            -- RN-09: data válida = reconhecida e dentro de [{DATA_MINIMA}, execução + 1 dia]
            CASE WHEN b.criado_em >= TIMESTAMP '{DATA_MINIMA}'
                  AND b.criado_em <= TIMESTAMP '{limite_futuro}' THEN b.criado_em END AS criado_em,
            b.atualizado_em,
            limpar_espacos(b.logradouro)                                    AS logradouro,
            normalizar_logradouro(b.logradouro)                             AS logradouro_normalizado,
            normalizar_numero(b.numero)                                     AS numero,
            padronizar_bairro(b.bairro)                                     AS bairro,          -- RN-01
            b.bairro                                                        AS bairro_original,
            COALESCE(b.bairro IS NOT NULL AND NOT bairro_reconhecido(b.bairro), false) AS flag_bairro_nao_padronizado,
            COALESCE(padronizar_cidade(b.cidade), 'Não informada')          AS cidade,          -- RN-02
            limpar_espacos(b.ponto_referencia)                              AS ponto_referencia,
            mapear_tipo_obstaculo(b.tipo_obstaculo)                         AS tipo_obstaculo,  -- RN-04
            COALESCE(b.tipo_obstaculo IS NOT NULL
             AND NOT tipo_obstaculo_reconhecido(b.tipo_obstaculo), false)   AS flag_tipo_nao_reconhecido,
            limpar_espacos(b.descricao)                                     AS descricao,
            mapear_impacto(b.impacto)                                       AS impacto,         -- RN-05
            (b.impacto IS NOT NULL AND mapear_impacto(b.impacto) IS NULL)   AS flag_impacto_nao_reconhecido,
            COALESCE(mapear_status(b.status), 'RECEBIDA')                   AS status,          -- RN-06
            (mapear_status(b.status) IS NULL)                               AS flag_status_inferido,
            mapear_origem(b.origem)                                         AS origem,          -- RN-08
            (COALESCE(b.simulado, false)
             OR upper(COALESCE(b.origem_dado, '')) = 'SIMULADO'
             OR COALESCE(mapear_origem(b.origem), '') = 'SIMULADO')         AS dado_simulado,   -- RN-08
            -- RN-07: possui_imagem não informado -> deduzido da existência de classificação
            COALESCE(b.possui_imagem, mapear_visao(b.visao_classificacao) IS NOT NULL) AS possui_imagem,
            mapear_visao(b.visao_classificacao)                             AS _visao,
            b.visao_pontuacao                                               AS _pontuacao,
            COALESCE(b.possui_imagem = false AND b.visao_classificacao IS NOT NULL, false) AS flag_visao_inconsistente,
            mapear_revisao(b.revisao_humana)                                AS revisao_humana,
            -- RN-10: coordenada válida tecnicamente E dentro do Brasil
            (b.latitude IS NOT NULL AND NOT (
                b.latitude BETWEEN {L['lat_min']} AND {L['lat_max']}
                AND b.longitude BETWEEN {L['lon_min']} AND {L['lon_max']}))  AS flag_coordenada_fora_area,
            b.latitude AS _lat, b.longitude AS _lon,
            b.flag_coordenada_invalida, b.flag_possui_nome,
            (b.criado_em IS NULL OR b.criado_em < TIMESTAMP '{DATA_MINIMA}'
             OR b.criado_em > TIMESTAMP '{limite_futuro}')                   AS flag_data_invalida,
            b._row_id, b._batch_id
        FROM bronze.denuncias b
    ),
    enriquecido AS (
        SELECT *,
            CAST(criado_em - INTERVAL {HORAS_UTC_PARA_LOCAL} HOUR AS DATE)   AS data_registro,  -- RN-09 data local
            CASE WHEN possui_imagem THEN _visao END                          AS visao_classificacao,
            CASE WHEN possui_imagem AND _visao IS NOT NULL THEN _pontuacao END AS visao_pontuacao,
            CASE WHEN NOT flag_coordenada_fora_area THEN _lat END            AS latitude,
            CASE WHEN NOT flag_coordenada_fora_area THEN _lon END            AS longitude,
            -- RN-12: regra de registro válido
            concat_ws('; ',
                CASE WHEN flag_data_invalida THEN 'data de registro ausente ou inválida' END,
                CASE WHEN logradouro IS NULL OR length(logradouro) < {LOGRADOURO_MIN}
                     THEN 'logradouro ausente' END,
                CASE WHEN bairro IS NULL THEN 'bairro ausente' END,
                CASE WHEN tipo_obstaculo IS NULL THEN 'tipo de obstáculo ausente' END,
                CASE WHEN impacto IS NULL THEN 'impacto ausente ou não reconhecido' END,
                CASE WHEN descricao IS NULL OR length(descricao) < {DESCRICAO_MIN}
                     THEN 'descrição ausente ou com menos de {DESCRICAO_MIN} caracteres' END
            ) AS _motivos
        FROM padronizado
    ),
    chaveado AS (
        SELECT *,
            NULLIF(_motivos, '')                                             AS motivos_invalidade,
            (_motivos = '')                                                  AS registro_valido,
            CASE WHEN logradouro_normalizado IS NOT NULL AND bairro IS NOT NULL
                  THEN logradouro_normalizado || '|' || COALESCE(numero, '') || '|' || normalizar_texto(bairro)
            END                                                              AS chave_endereco
        FROM enriquecido
    )
    SELECT *,
        -- RN-11: mesma ocorrência = mesmo endereço normalizado + mesmo tipo + mesma data local
        CASE WHEN chave_endereco IS NOT NULL AND tipo_obstaculo IS NOT NULL AND data_registro IS NOT NULL
             THEN chave_endereco || '|' || tipo_obstaculo || '|' || CAST(data_registro AS VARCHAR)
             ELSE chave_denuncia END                                         AS _chave_ocorrencia
    FROM chaveado
    """)
    con.execute("""
    CREATE OR REPLACE TEMP TABLE _silver_rank AS
    SELECT *,
        row_number() OVER w  AS _rank_ocorrencia,
        first_value(chave_denuncia) OVER w AS chave_denuncia_mantida
    FROM _silver_base
    WINDOW w AS (PARTITION BY _chave_ocorrencia
                 ORDER BY registro_valido DESC, criado_em NULLS LAST, fonte DESC, _row_id)
    """)

    colunas_finais = """
        s.chave_denuncia, s.fonte, s.id_origem, s.protocolo, s.criado_em, s.data_registro,
        strftime(s.data_registro, '%Y-%m')                                       AS ano_mes,
        CASE WHEN s.data_registro IS NOT NULL
             THEN CAST(isoyear(s.data_registro) AS VARCHAR) || '-W' || lpad(CAST(week(s.data_registro) AS VARCHAR), 2, '0')
        END                                                                     AS semana_iso,
        s.atualizado_em, s.logradouro, s.logradouro_normalizado, s.numero, s.bairro, s.bairro_original,
        s.cidade, s.ponto_referencia, s.descricao,
        s.tipo_obstaculo, rt.rotulo AS tipo_obstaculo_rotulo,
        s.impacto, ri.rotulo AS impacto_rotulo,
        s.status, rs.rotulo AS status_rotulo,
        s.origem, s.dado_simulado, s.possui_imagem,
        s.visao_classificacao,
        CASE WHEN s.visao_classificacao IS NULL THEN 'Sem fotografia (não analisada)' ELSE rv.rotulo END AS visao_rotulo,
        s.visao_pontuacao, s.revisao_humana, s.latitude, s.longitude, s.chave_endereco,
        s.flag_possui_nome, s.flag_bairro_nao_padronizado, s.flag_tipo_nao_reconhecido,
        s.flag_impacto_nao_reconhecido, s.flag_status_inferido, s.flag_visao_inconsistente,
        s.flag_coordenada_invalida, s.flag_coordenada_fora_area, s.flag_data_invalida,
        s.registro_valido, s.motivos_invalidade,
        s._row_id, s._batch_id
    """
    joins = """
        FROM _silver_rank s
        LEFT JOIN silver.ref_tipo_obstaculo rt ON rt.chave = s.tipo_obstaculo
        LEFT JOIN silver.ref_impacto ri ON ri.chave = s.impacto
        LEFT JOIN silver.ref_status rs ON rs.chave = s.status
        LEFT JOIN silver.ref_visao_classificacao rv ON rv.chave = s.visao_classificacao
    """
    con.execute(f"CREATE OR REPLACE TABLE {TABELA_SILVER} AS SELECT {colunas_finais} {joins} "
                "WHERE s._rank_ocorrencia = 1 ORDER BY s.criado_em NULLS LAST, s.chave_denuncia")
    con.execute(f"CREATE OR REPLACE TABLE {TABELA_DUPLICADAS} AS "
                f"SELECT s.chave_denuncia_mantida, {colunas_finais} {joins} "
                "WHERE s._rank_ocorrencia > 1 ORDER BY s.chave_denuncia")
    con.execute("DROP TABLE IF EXISTS _silver_rank")
    con.execute("DROP TABLE IF EXISTS _silver_base")

    resultado = {
        "linhas_silver": contar(con, TABELA_SILVER),
        "duplicatas_negocio_removidas": contar(con, TABELA_DUPLICADAS),
        "registros_validos": contar(con, TABELA_SILVER, "registro_valido"),
        "registros_invalidos": contar(con, TABELA_SILVER, "NOT registro_valido"),
    }
    log.info("[silver] %s", resultado)
    return resultado
