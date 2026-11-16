"""Regras de negócio da Silver (regras.py): padronização e mapeamento para o contrato."""
import pytest

from acessacidade_pipeline import regras, simulate
from acessacidade_pipeline.dominio import IMPACTO, STATUS, TIPO_OBSTACULO, VISAO_CLASSIFICACAO


@pytest.mark.parametrize("oficial", [b for b in simulate.BAIRROS if b != "Recanto Verde"])
def test_rn01_todas_as_grafias_de_bairro_viram_o_nome_oficial(oficial):
    for variacao in simulate.BAIRROS[oficial][1]:
        assert regras.padronizar_bairro(variacao) == oficial, variacao
        assert regras.bairro_reconhecido(variacao) is True


def test_rn01_bairro_fora_do_dicionario_nao_e_inventado():
    for variacao in simulate.BAIRROS["Recanto Verde"][1]:
        assert regras.padronizar_bairro(variacao) == "Recanto Verde"
        assert regras.bairro_reconhecido(variacao) is False
    assert regras.padronizar_bairro("   ") is None


def test_rn02_cidade():
    for v in ("Cidade Exemplo", "cidade exemplo", "CIDADE EXEMPLO", "Cid. Exemplo", "Cidade Exemplo "):
        assert regras.padronizar_cidade(v) == "Cidade Exemplo"
    assert regras.padronizar_cidade(None) == "Não informada"


@pytest.mark.parametrize("oficial", list(simulate.LOGRADOUROS))
def test_rn03_logradouro_normalizado_igual_para_todas_as_grafias(oficial):
    chaves = {regras.normalizar_logradouro(v) for v in simulate.LOGRADOUROS[oficial]}
    assert len(chaves) == 1, chaves


def test_rn03_numero():
    assert regras.normalizar_numero("s/n") == regras.normalizar_numero("SN") == "S/N"
    assert regras.normalizar_numero(" 120 a ") == "120A"
    assert regras.normalizar_numero("") is None


@pytest.mark.parametrize("chave", list(simulate.TIPOS))
def test_rn04_variacoes_de_tipo_mapeiam_para_a_chave_do_contrato(chave):
    for variacao in simulate.TIPOS[chave][1]:
        assert regras.mapear_tipo_obstaculo(variacao) == chave, variacao


def test_rn04_chaves_e_rotulos_do_contrato_e_texto_desconhecido():
    for chave, rotulo in TIPO_OBSTACULO.items():
        assert regras.mapear_tipo_obstaculo(chave) == chave
        assert regras.mapear_tipo_obstaculo(rotulo) == chave
        assert regras.tipo_obstaculo_reconhecido(rotulo) is True
    assert regras.mapear_tipo_obstaculo("falta de iluminação na travessia") == "OUTRO"
    assert regras.tipo_obstaculo_reconhecido("falta de iluminação na travessia") is False
    assert regras.mapear_tipo_obstaculo("") is None


def test_rn05_impacto():
    for chave, (_, variacoes) in simulate.IMPACTOS.items():
        for v in variacoes:
            assert regras.mapear_impacto(v) == chave, v
    for chave, rotulo in IMPACTO.items():
        assert regras.mapear_impacto(rotulo) == chave
    assert regras.mapear_impacto("muito ruim") is None


def test_rn06_status():
    for chave, variacoes in simulate.STATUS_VARIACOES.items():
        for v in variacoes:
            assert regras.mapear_status(v) == chave, v
    for chave, rotulo in STATUS.items():
        assert regras.mapear_status(rotulo) == chave
    assert regras.mapear_status("pendente") is None
    assert regras.mapear_status(None) is None


def test_rn07_visao():
    for chave, variacoes in simulate.VISAO_VARIACOES.items():
        for v in variacoes:
            assert regras.mapear_visao(v) == chave, v
    assert set(simulate.VISAO_VARIACOES) == {k for k in VISAO_CLASSIFICACAO if k}
    assert regras.mapear_visao("") is None


def test_rn08_origem_e_revisao():
    assert regras.mapear_origem(" simulado ") == "SIMULADO"
    assert regras.mapear_origem("WEB") == "WEB"
    assert regras.mapear_revisao("confirmado") == "CONFIRMADO"
    assert regras.mapear_revisao("Descartado") == "DESCARTADO"
    assert regras.mapear_revisao("") is None
