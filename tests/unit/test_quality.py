"""Avaliação de qualidade, sem banco."""

from decimal import Decimal

from app.domain.constants import (
    MOTIVO_COMPRIMENTO_ABAIXO,
    MOTIVO_COMPRIMENTO_ACIMA,
    MOTIVO_COR,
    MOTIVO_PESO_ABAIXO,
    MOTIVO_PESO_ACIMA,
)
from app.domain.quality import avaliar_peca, normalizar_cor


def test_peso_minimo_aprova():
    assert avaliar_peca(95, "azul", 15).aprovada


def test_peso_maximo_aprova():
    assert avaliar_peca(Decimal("105"), "verde", 15).aprovada


def test_peso_abaixo():
    avaliacao = avaliar_peca("94.99", "azul", 15)
    assert not avaliacao.aprovada
    assert avaliacao.motivos == (MOTIVO_PESO_ABAIXO,)


def test_peso_acima():
    avaliacao = avaliar_peca(105.01, "verde", 12)
    assert avaliacao.motivos == (MOTIVO_PESO_ACIMA,)


def test_cores_validas_com_maiusculas_e_espacos():
    assert normalizar_cor("  Azul ") == "azul"
    assert avaliar_peca(100, "AZUL", 15).aprovada
    assert avaliar_peca(100, "  Verde  ", 15).aprovada


def test_cor_invalida():
    avaliacao = avaliar_peca(100, "vermelho", 15)
    assert avaliacao.motivos == (MOTIVO_COR,)


def test_comprimento_minimo_e_maximo():
    assert avaliar_peca(100, "azul", 10).aprovada
    assert avaliar_peca(100, "verde", 20).aprovada


def test_comprimento_invalido():
    assert avaliar_peca(100, "azul", 9.99).motivos == (MOTIVO_COMPRIMENTO_ABAIXO,)
    assert avaliar_peca(100, "azul", 20.01).motivos == (MOTIVO_COMPRIMENTO_ACIMA,)


def test_multiplos_motivos_na_ordem_canonica():
    avaliacao = avaliar_peca(80, "amarelo", 4)
    assert avaliacao.motivos == (
        MOTIVO_PESO_ABAIXO,
        MOTIVO_COR,
        MOTIVO_COMPRIMENTO_ABAIXO,
    )


def test_peso_acima_e_comprimento_acima():
    avaliacao = avaliar_peca(120, "azul", 30)
    assert avaliacao.motivos == (MOTIVO_PESO_ACIMA, MOTIVO_COMPRIMENTO_ACIMA)
