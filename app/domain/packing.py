"""Alocação determinística das peças aprovadas em caixas.

A ordem é a data/hora de cadastro e, em empate, o ID da peça.
A peça de índice i ocupa a caixa i // capacidade. Caixas anteriores
à última ficam cheias. A última fica aberta quando ainda há espaço.
Caixas fechadas não são tratadas como lotes imutáveis: depois de uma
exclusão, o plano é recalculado sobre as aprovadas que restaram.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.constants import CAPACIDADE_CAIXA
from app.domain.enums import StatusCaixa


@dataclass(frozen=True)
class PecaAlocavel:
    codigo: str
    cadastrada_em: datetime


def plano_alocacao(pecas: list[PecaAlocavel], capacidade: int = CAPACIDADE_CAIXA) -> list[list[str]]:
    """Devolve a lista de caixas, cada uma com os IDs na ordem estável."""
    if capacidade < 1:
        raise ValueError("A capacidade da caixa precisa ser positiva.")

    ordenadas = sorted(pecas, key=lambda peca: (peca.cadastrada_em, peca.codigo))
    caixas: list[list[str]] = []
    for indice, peca in enumerate(ordenadas):
        posicao = indice // capacidade
        if posicao == len(caixas):
            caixas.append([])
        caixas[posicao].append(peca.codigo)
    return caixas


def status_para_quantidade(quantidade: int, capacidade: int = CAPACIDADE_CAIXA) -> StatusCaixa:
    """Define o status de uma caixa que permanece no plano."""
    if quantidade < 1 or quantidade > capacidade:
        raise ValueError("Quantidade incompatível com uma caixa ativa.")
    if quantidade == capacidade:
        return StatusCaixa.FECHADA
    return StatusCaixa.ABERTA
