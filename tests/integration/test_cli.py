"""A CLI reutiliza o serviço, sem regra própria."""

from app.cli import processar_opcao
from app.infrastructure.models import Peca


def test_menu_cadastra_pelo_servico(servico):
    entradas = iter(["QA-1", "100", "azul", "15"])
    saidas: list[str] = []
    continua = processar_opcao("1", servico, lambda _prompt: next(entradas), saidas.append)
    assert continua is True
    assert Peca.query.filter_by(codigo="QA-1").one().resultado == "APROVADA"
    assert any("PEÇA APROVADA" in linha for linha in saidas)


def test_menu_sair():
    class ServicoNaoUsado:
        def cadastrar(self, *_args):
            raise AssertionError("sair não cadastra")

    saidas: list[str] = []
    assert processar_opcao("6", ServicoNaoUsado(), input, saidas.append) is False


def test_remocao_na_cli_pede_confirmacao(servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    entradas = iter(["QA-1", "n"])
    saidas: list[str] = []
    processar_opcao("3", servico, lambda _prompt: next(entradas), saidas.append)
    assert Peca.query.count() == 1
    assert any("cancelada" in linha.lower() for linha in saidas)
