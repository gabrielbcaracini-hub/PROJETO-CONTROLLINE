"""Dados de saída dos casos de uso."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.infrastructure.models import Auditoria, Caixa, Peca


@dataclass(frozen=True)
class RegistroAuditoria:
    acao: str
    entidade: str
    entidade_id: str
    descricao: str


@dataclass
class CadastroRealizado:
    peca: Peca
    motivos: tuple[str, ...]
    aprovada: bool


@dataclass
class ExclusaoRealizada:
    codigo: str
    mensagem: str


@dataclass
class Painel:
    total: int
    aprovadas: int
    reprovadas: int
    taxa: Decimal
    caixas_abertas: int
    caixas_fechadas: int
    total_caixas: int
    pecas_armazenadas: int
    atividade: list[Auditoria]
    motivos: list[tuple[str, int]]


@dataclass
class Relatorio:
    total: int
    aprovadas: int
    reprovadas: int
    taxa: Decimal
    motivos: list[tuple[str, int]]
    total_caixas: int
    caixas_abertas: int
    caixas_fechadas: int
    pecas_armazenadas: int
    caixas: list[Caixa]
