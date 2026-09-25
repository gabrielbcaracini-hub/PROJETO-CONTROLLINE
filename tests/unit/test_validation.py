"""Entradas inválidas não viram peça."""

import pytest

from app.domain.exceptions import DadosInvalidos
from app.domain.validation import validar_cadastro


def _valida(peso="100", cor="azul", comprimento="15", codigo="QA-1"):
    return validar_cadastro(codigo, peso, cor, comprimento)


def test_normaliza_id_e_cor():
    dados = _valida(codigo="  QA-1  ", cor="  Azul ")
    assert dados.codigo == "QA-1"
    assert dados.cor == "azul"


def test_campos_vazios():
    with pytest.raises(DadosInvalidos) as erro:
        validar_cadastro("  ", "", "", "")
    assert set(erro.value.erros) == {"codigo", "peso", "cor", "comprimento"}


def test_numero_negativo_zero_texto_e_valor_enorme():
    for peso in ("-1", "0", "abc", "1000001", "10.555"):
        with pytest.raises(DadosInvalidos) as erro:
            _valida(peso=peso)
        assert "peso" in erro.value.erros


def test_cor_fora_do_criterio_ainda_e_entrada_valida():
    dados = _valida(cor="vermelho")
    assert dados.cor == "vermelho"


def test_id_invalido():
    with pytest.raises(DadosInvalidos) as erro:
        _valida(codigo="com espaço")
    assert "codigo" in erro.value.erros


def test_aceita_virgula_decimal():
    dados = _valida(peso="95,5", comprimento="10,25")
    assert str(dados.peso) == "95.5"
    assert str(dados.comprimento) == "10.25"
