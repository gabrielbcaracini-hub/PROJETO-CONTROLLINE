"""SQLite com chaves estrangeiras ativas e decimal exato.

O SQLite não possui tipo DECIMAL nativo. Peso e comprimento são
gravados como texto numérico de escala fixa para não perder o limite
exato (95,00 g, 10,00 cm) numa conversão para ponto flutuante.
"""

from __future__ import annotations

from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, event
from sqlalchemy.engine import Engine
from sqlalchemy.types import TypeDecorator

db = SQLAlchemy()


class DecimalTexto(TypeDecorator):
    """Decimal com escala fixa, persistido como texto."""

    impl = String(32)
    cache_ok = True

    def __init__(self, casas: int = 2) -> None:
        super().__init__()
        self.casas = casas

    def process_bind_param(self, value: object, dialect: object) -> str | None:
        if value is None:
            return None
        quantizado = Decimal(str(value)).quantize(Decimal(10) ** -self.casas)
        return f"{quantizado:.{self.casas}f}"

    def process_result_value(self, value: object, dialect: object) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))


@event.listens_for(Engine, "connect")
def _ativar_chaves_estrangeiras(dbapi_connection: object, _registro: object) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
