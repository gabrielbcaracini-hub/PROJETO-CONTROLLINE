"""Formatação de números e datas para a interface em português."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

_SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def formatar_decimal(valor: object) -> str:
    if valor is None or valor == "":
        return "—"
    numero = Decimal(str(valor)).quantize(Decimal("0.01"))
    return f"{numero:.2f}".replace(".", ",")


def formatar_percentual(valor: object) -> str:
    if valor is None or valor == "":
        return "—"
    numero = Decimal(str(valor)).quantize(Decimal("0.1"))
    return f"{numero:.1f}".replace(".", ",") + "%"


def formatar_data(valor: datetime | None) -> str:
    if valor is None:
        return "—"
    momento = valor if valor.tzinfo is not None else valor.replace(tzinfo=timezone.utc)
    return momento.astimezone(_SAO_PAULO).strftime("%d/%m/%Y %H:%M")
