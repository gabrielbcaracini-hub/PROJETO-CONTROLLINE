from decimal import Decimal

from app.domain.indicadores import calcular_taxa_aprovacao


def test_taxa_zero_sem_pecas():
    assert calcular_taxa_aprovacao(0, 0) == Decimal("0.0")


def test_taxa_arredonda_uma_casa():
    assert calcular_taxa_aprovacao(2, 3) == Decimal("66.7")
    assert calcular_taxa_aprovacao(15, 21) == Decimal("71.4")
