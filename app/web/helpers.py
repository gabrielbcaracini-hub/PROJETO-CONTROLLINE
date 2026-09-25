"""Montagem de dados de tela. Não reavalia a peça: lê o que foi gravado."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.constants import (
    COMPRIMENTO_MAX,
    COMPRIMENTO_MIN,
    MOTIVO_COMPRIMENTO_ABAIXO,
    MOTIVO_COMPRIMENTO_ACIMA,
    MOTIVO_COR,
    MOTIVO_PESO_ABAIXO,
    MOTIVO_PESO_ACIMA,
    PESO_MAX,
    PESO_MIN,
)
from app.infrastructure.models import Peca
from app.web.formatacao import formatar_decimal


@dataclass(frozen=True)
class ItemCriterio:
    nome: str
    valor: str
    regra: str
    aprovado: bool
    detalhe: str


def itens_avaliacao(peca: Peca) -> list[ItemCriterio]:
    motivos = set(peca.motivos_texto)
    peso_motivo = _primeiro(motivos, MOTIVO_PESO_ABAIXO, MOTIVO_PESO_ACIMA)
    cor_motivo = MOTIVO_COR if MOTIVO_COR in motivos else None
    comp_motivo = _primeiro(motivos, MOTIVO_COMPRIMENTO_ABAIXO, MOTIVO_COMPRIMENTO_ACIMA)
    return [
        ItemCriterio(
            nome="Peso",
            valor=f"{formatar_decimal(peca.peso)} g",
            regra=f"Entre {PESO_MIN} g e {PESO_MAX} g",
            aprovado=peso_motivo is None,
            detalhe=peso_motivo or "Critério atendido.",
        ),
        ItemCriterio(
            nome="Cor",
            valor=peca.cor,
            regra="Azul ou verde",
            aprovado=cor_motivo is None,
            detalhe=cor_motivo or "Critério atendido.",
        ),
        ItemCriterio(
            nome="Comprimento",
            valor=f"{formatar_decimal(peca.comprimento)} cm",
            regra=f"Entre {COMPRIMENTO_MIN} cm e {COMPRIMENTO_MAX} cm",
            aprovado=comp_motivo is None,
            detalhe=comp_motivo or "Critério atendido.",
        ),
    ]


def _primeiro(motivos: set[str], *opcoes: str) -> str | None:
    for opcao in opcoes:
        if opcao in motivos:
            return opcao
    return None
