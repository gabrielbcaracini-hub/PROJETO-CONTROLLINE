"""Enumerações usadas pelo domínio e pela persistência."""

from __future__ import annotations

from enum import Enum


class ResultadoPeca(str, Enum):
    APROVADA = "APROVADA"
    REPROVADA = "REPROVADA"


class StatusCaixa(str, Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"


class AcaoAuditoria(str, Enum):
    CADASTRAR = "CADASTRAR"
    EXCLUIR = "EXCLUIR"
    CRIAR_CAIXA = "CRIAR_CAIXA"
    FECHAR_CAIXA = "FECHAR_CAIXA"
    REMOVER_CAIXA = "REMOVER_CAIXA"
    REORGANIZAR = "REORGANIZAR"


class EntidadeAuditoria(str, Enum):
    PECA = "PECA"
    CAIXA = "CAIXA"
