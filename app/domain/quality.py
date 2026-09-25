"""Avaliação automática de qualidade.

A peça é aprovada somente quando peso, cor e comprimento passam juntos.
Cada critério falho gera um motivo canônico, na ordem peso, cor e comprimento.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.constants import (
    COMPRIMENTO_MAX,
    COMPRIMENTO_MIN,
    CORES_PERMITIDAS,
    MOTIVO_COMPRIMENTO_ABAIXO,
    MOTIVO_COMPRIMENTO_ACIMA,
    MOTIVO_COR,
    MOTIVO_PESO_ABAIXO,
    MOTIVO_PESO_ACIMA,
    PESO_MAX,
    PESO_MIN,
)
from app.domain.enums import ResultadoPeca


@dataclass(frozen=True)
class Avaliacao:
    resultado: ResultadoPeca
    motivos: tuple[str, ...]

    @property
    def aprovada(self) -> bool:
        return self.resultado is ResultadoPeca.APROVADA


def normalizar_cor(cor: str) -> str:
    return cor.strip().lower()


def _como_decimal(valor: Decimal | int | str) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    return Decimal(str(valor))


def avaliar_peca(peso: Decimal | int | str, cor: str, comprimento: Decimal | int | str) -> Avaliacao:
    """Avalia uma peça já considerada uma entrada numérica válida."""
    peso_decimal = _como_decimal(peso)
    comprimento_decimal = _como_decimal(comprimento)
    motivos: list[str] = []

    if peso_decimal < PESO_MIN:
        motivos.append(MOTIVO_PESO_ABAIXO)
    elif peso_decimal > PESO_MAX:
        motivos.append(MOTIVO_PESO_ACIMA)

    if normalizar_cor(cor) not in CORES_PERMITIDAS:
        motivos.append(MOTIVO_COR)

    if comprimento_decimal < COMPRIMENTO_MIN:
        motivos.append(MOTIVO_COMPRIMENTO_ABAIXO)
    elif comprimento_decimal > COMPRIMENTO_MAX:
        motivos.append(MOTIVO_COMPRIMENTO_ACIMA)

    if motivos:
        return Avaliacao(ResultadoPeca.REPROVADA, tuple(motivos))
    return Avaliacao(ResultadoPeca.APROVADA, ())
