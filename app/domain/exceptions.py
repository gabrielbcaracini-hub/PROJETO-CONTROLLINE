"""Erros de regra e de validação compartilhados pela web e pela CLI."""

from __future__ import annotations


class ErroAplicacao(Exception):
    """Base das falhas esperadas da aplicação."""


class DadosInvalidos(ErroAplicacao):
    """Entrada rejeitada antes de qualquer gravação."""

    def __init__(self, erros: dict[str, str]) -> None:
        self.erros = erros
        texto = "; ".join(f"{campo}: {mensagem}" for campo, mensagem in erros.items())
        super().__init__(texto or "Dados inválidos.")


class CodigoDuplicado(ErroAplicacao):
    """O ID informado já pertence a outra peça."""

    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"O ID {codigo} já está cadastrado.")


class PecaNaoEncontrada(ErroAplicacao):
    """Não existe peça com o ID pedido."""

    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"Peça {codigo} não encontrada.")
