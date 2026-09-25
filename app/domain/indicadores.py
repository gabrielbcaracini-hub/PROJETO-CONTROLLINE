"""Cálculos de indicador que não dependem do banco."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def calcular_taxa_aprovacao(aprovadas: int, total: int) -> Decimal:
    if aprovadas < 0 or total < 0 or aprovadas > total:
        raise ValueError("Totais incoerentes para a taxa de aprovação.")
    if total == 0:
        return Decimal("0.0")
    return (Decimal(aprovadas) * Decimal(100) / Decimal(total)).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP,
    )
