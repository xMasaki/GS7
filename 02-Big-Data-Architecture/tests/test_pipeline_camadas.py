"""Camadas raw / bronze / silver executadas de ponta a ponta sobre a fonte simulada."""
import duckdb
import pandas as pd

from acessacidade_pipeline import simulate
from acessacidade_pipeline.dominio import COLUNAS_FONTE_SIMULADA, STATUS, TIPO_OBSTACULO, VISAO_CLASSIFICACAO
from acessacidade_pipeline.regras import BAIRROS_CANONICOS

MARCADOR = "Pessoa Simulada"


def _con(cfg):
    return duckdb.connect(str(cfg.warehouse_path), read_only=True)


def _csv(cfg) -> pd.DataFrame:
    return pd.read_csv(cfg.samples_csv, dtype=str, keep_default_na=False)


def test_fonte_simulada_identificada_e_no_tamanho_esperado(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    df = _csv(cfg)
    assert list(df.columns) == list(COLUNAS_FONTE_SIMULADA)
    assert 240 <= len(df) <= 300
    assert (df["origem_dado"] == "SIMULADO").all()
    assert df["nome_denunciante"].str.startswith(MARCADOR).sum() > 0
    assert df.duplicated().sum() == simulate.DUPLICATAS_EXATAS


def test_raw_fiel_a_fonte(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    df = _csv(cfg)
    with _con(cfg) as con:
        assert con.execute("SELECT count(*) FROM raw.denuncias_simuladas").fetchone()[0] == len(df)
        tipos = dict(con.execute("SELECT column_name, data_type FROM information_schema.columns "
                                 "WHERE table_schema='raw' AND table_name='denuncias_simuladas'").fetchall())
        raw = con.execute("SELECT * EXCLUDE (_source_file, _ingested_at, _row_id, _batch_id) "
                          "FROM raw.denuncias_simuladas ORDER BY _row_id").df()
        meta = con.execute("SELECT DISTINCT _source_file, _batch_id FROM raw.denuncias_simuladas").fetchall()
    assert all(tipos[c] == "VARCHAR" for c in COLUNAS_FONTE_SIMULADA)  # all_varchar / schema-on-read
    assert {"_source_file", "_ingested_at", "_row_id", "_batch_id"} <= set(tipos)
    assert meta == [("data/samples/denuncias_simuladas.csv", "manual__teste")]
    # valor a valor igual ao arquivo (vazio no CSV = NULL na raw); espaços e grafias preservados
    pd.testing.assert_frame_equal(raw.fillna(""), df, check_dtype=False)
    assert raw["bairro"].nunique() > len(BAIRROS_CANONICOS)  # a bagunça continua lá


def test_bronze_dedup_tecnico_e_tipos(pipeline_sem_api):
    cfg, estado = pipeline_sem_api
    with _con(cfg) as con:
        n_raw = con.execute("SELECT count(*) FROM raw.denuncias_simuladas").fetchone()[0]
        n_bronze = con.execute("SELECT count(*) FROM bronze.denuncias").fetchone()[0]
        tipos = dict(con.execute("SELECT column_name, data_type FROM information_schema.columns "
                                 "WHERE table_schema='bronze' AND table_name='denuncias'").fetchall())
        repetidas = con.execute("""
            SELECT count(*) FROM (SELECT fonte, _row_id FROM bronze.denuncias GROUP BY ALL HAVING count(*) > 1)
        """).fetchone()[0]
    assert n_raw - n_bronze == simulate.DUPLICATAS_EXATAS == estado["duplicatas_removidas"]
    assert repetidas == 0
    assert tipos["criado_em"] == "TIMESTAMP"
    assert tipos["latitude"] == tipos["longitude"] == tipos["visao_pontuacao"] == "DOUBLE"
    assert tipos["simulado"] == tipos["possui_imagem"] == "BOOLEAN"
    assert tipos["id_origem"] == "BIGINT"


def test_bronze_flags_sinalizam_sem_resolver(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    with _con(cfg) as con:
        f = con.execute("""
            SELECT count(*) FILTER (WHERE flag_data_invalida), count(*) FILTER (WHERE flag_data_ausente),
                   count(*) FILTER (WHERE flag_coordenada_invalida),
                   count(*) FILTER (WHERE flag_coordenada_invalida AND latitude IS NOT NULL),
                   count(*) FILTER (WHERE flag_campo_obrigatorio_ausente),
                   count(*) FILTER (WHERE flag_pontuacao_invalida AND visao_pontuacao IS NOT NULL),
                   count(*) FILTER (WHERE latitude NOT BETWEEN -90 AND 90),
                   count(DISTINCT bairro)
            FROM bronze.denuncias
        """).fetchone()
    data_inv, data_aus, coord_inv, coord_inv_com_valor, obrig, pont_inv_com_valor, fora_faixa, bairros = f
    assert data_inv >= 2 and data_aus >= 1
    assert coord_inv >= 4 and coord_inv_com_valor == 0 and fora_faixa == 0
    assert obrig > 0 and pont_inv_com_valor == 0
    assert bairros > len(BAIRROS_CANONICOS)  # bronze NÃO padroniza bairro (regra de negócio)


def test_nome_do_denunciante_nao_passa_da_raw(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    with _con(cfg) as con:
        assert con.execute("SELECT count(*) FROM raw.denuncias_simuladas "
                           f"WHERE nome_denunciante LIKE '{MARCADOR}%'").fetchone()[0] > 0
        colunas = con.execute("""
            SELECT table_schema, table_name, column_name, data_type FROM information_schema.columns
            WHERE table_schema IN ('bronze', 'silver', 'gold')
        """).fetchall()
        assert not [c for c in colunas if "nome" in c[2] and not c[2].startswith("flag_")]
        assert con.execute("SELECT count(*) FROM bronze.denuncias WHERE flag_possui_nome").fetchone()[0] > 0
        # nenhum valor de texto em bronze/silver/gold contém o nome
        for schema, tabela, coluna, tipo in colunas:
            if tipo == "VARCHAR":
                n = con.execute(f'SELECT count(*) FROM {schema}.{tabela} WHERE "{coluna}" LIKE ?',
                                [f"%{MARCADOR}%"]).fetchone()[0]
                assert n == 0, f"{schema}.{tabela}.{coluna}"


def test_silver_padronizacao(pipeline_sem_api):
    cfg, _ = pipeline_sem_api
    with _con(cfg) as con:
        bairros = {r[0] for r in con.execute("SELECT DISTINCT bairro FROM silver.denuncias WHERE bairro IS NOT NULL").fetchall()}
        tipos = {r[0] for r in con.execute("SELECT DISTINCT tipo_obstaculo FROM silver.denuncias "
                                           "WHERE tipo_obstaculo IS NOT NULL").fetchall()}
        status = {r[0] for r in con.execute("SELECT DISTINCT status FROM silver.denuncias").fetchall()}
        visao = {r[0] for r in con.execute("SELECT DISTINCT visao_classificacao FROM silver.denuncias").fetchall()}
        cidades = {r[0] for r in con.execute("SELECT DISTINCT cidade FROM silver.denuncias").fetchall()}
        rotulos_ok = con.execute("""
            SELECT bool_and(tipo_obstaculo_rotulo IS NOT NULL) FROM silver.denuncias WHERE tipo_obstaculo IS NOT NULL
        """).fetchone()[0]
        sem_imagem_com_visao = con.execute(
            "SELECT count(*) FROM silver.denuncias WHERE NOT possui_imagem AND visao_classificacao IS NOT NULL").fetchone()[0]
        fora_brasil = con.execute("""
            SELECT count(*) FROM silver.denuncias
            WHERE latitude IS NOT NULL AND NOT (latitude BETWEEN -33.8 AND 5.3 AND longitude BETWEEN -74 AND -28.8)
        """).fetchone()[0]
        invalidos_sem_motivo = con.execute(
            "SELECT count(*) FROM silver.denuncias WHERE NOT registro_valido AND motivos_invalidade IS NULL").fetchone()[0]
    assert bairros == set(BAIRROS_CANONICOS.values()) | {"Recanto Verde"}
    assert tipos <= set(TIPO_OBSTACULO) and status <= set(STATUS)
    assert visao <= set(VISAO_CLASSIFICACAO)
    assert cidades <= {"Cidade Exemplo", "Não informada"}
    assert rotulos_ok and sem_imagem_com_visao == 0 and fora_brasil == 0 and invalidos_sem_motivo == 0
    assert "ENCAMINHADA" not in status and "RESOLVIDA" not in status  # dados simulados nunca usam


def test_silver_dedup_de_negocio_remove_quase_duplicatas(pipeline_sem_api):
    cfg, estado = pipeline_sem_api
    with _con(cfg) as con:
        n_bronze = con.execute("SELECT count(*) FROM bronze.denuncias").fetchone()[0]
        n_silver = con.execute("SELECT count(*) FROM silver.denuncias").fetchone()[0]
        n_dup = con.execute("SELECT count(*) FROM silver.denuncias_duplicadas").fetchone()[0]
        repetidas = con.execute("""
            SELECT count(*) FROM (
                SELECT chave_endereco, tipo_obstaculo, data_registro FROM silver.denuncias
                WHERE chave_endereco IS NOT NULL AND tipo_obstaculo IS NOT NULL AND data_registro IS NOT NULL
                GROUP BY ALL HAVING count(*) > 1)
        """).fetchone()[0]
        mantidas_existem = con.execute("""
            SELECT bool_and(d.chave_denuncia_mantida IN (SELECT chave_denuncia FROM silver.denuncias))
            FROM silver.denuncias_duplicadas d
        """).fetchone()[0]
    assert n_dup == simulate.QUASE_DUPLICATAS == estado["duplicatas_negocio_removidas"]
    assert n_silver + n_dup == n_bronze
    assert repetidas == 0 and mantidas_existem
