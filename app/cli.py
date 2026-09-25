"""Menu de terminal. Toda regra fica em QualidadeService."""

from __future__ import annotations

from collections.abc import Callable

from app.application.services import QualidadeService
from app.domain.exceptions import CodigoDuplicado, DadosInvalidos, PecaNaoEncontrada
from app.web.formatacao import formatar_data, formatar_decimal, formatar_percentual

Ler = Callable[[str], str]
Escrever = Callable[[str], None]


def processar_opcao(opcao: str, servico: QualidadeService, ler: Ler, escrever: Escrever) -> bool:
    """Executa um item do menu. Devolve False quando a opção é sair."""
    escolha = opcao.strip()
    if escolha == "1":
        _cadastrar(servico, ler, escrever)
    elif escolha == "2":
        _listar(servico, escrever)
    elif escolha == "3":
        _remover(servico, ler, escrever)
    elif escolha == "4":
        _caixas_fechadas(servico, escrever)
    elif escolha == "5":
        _relatorio(servico, escrever)
    elif escolha == "6":
        escrever("Encerrando.")
        return False
    else:
        escrever("Opção inválida. Escolha um número de 1 a 6.")
    return True


def _cadastrar(servico: QualidadeService, ler: Ler, escrever: Escrever) -> None:
    try:
        resultado = servico.cadastrar(
            ler("ID da peça: "),
            ler("Peso em gramas: "),
            ler("Cor: "),
            ler("Comprimento em centímetros: "),
        )
    except DadosInvalidos as erro:
        for mensagem in erro.erros.values():
            escrever(mensagem)
        return
    except CodigoDuplicado as erro:
        escrever(str(erro))
        return

    peca = resultado.peca
    if resultado.aprovada:
        caixa = f" Caixa {peca.caixa_id}." if peca.caixa_id else ""
        escrever(f"PEÇA APROVADA. Todos os critérios de qualidade foram atendidos.{caixa}")
        return
    escrever("PEÇA REPROVADA.")
    escrever("Motivos:")
    for motivo in resultado.motivos:
        escrever(f"- {motivo}")


def _listar(servico: QualidadeService, escrever: Escrever) -> None:
    aprovadas, _ = servico.listar_pecas("aprovadas", None, None)
    reprovadas, _ = servico.listar_pecas("reprovadas", None, None)
    escrever("Aprovadas")
    _imprimir_pecas(aprovadas, escrever)
    escrever("Reprovadas")
    _imprimir_pecas(reprovadas, escrever)


def _imprimir_pecas(pecas: list, escrever: Escrever) -> None:
    if not pecas:
        escrever("Nenhuma peça neste grupo.")
        return
    for peca in pecas:
        motivos = "; ".join(peca.motivos_texto) if peca.motivos_texto else "—"
        caixa = str(peca.caixa_id) if peca.caixa_id else "—"
        escrever(
            f"{peca.codigo} | {formatar_decimal(peca.peso)} g | {peca.cor} | "
            f"{formatar_decimal(peca.comprimento)} cm | {peca.resultado} | {motivos} | caixa {caixa}"
        )


def _remover(servico: QualidadeService, ler: Ler, escrever: Escrever) -> None:
    codigo = ler("ID da peça: ").strip()
    confirmacao = ler(f"Confirma a exclusão de {codigo}? (s/n): ").strip().lower()
    if confirmacao != "s":
        escrever("Exclusão cancelada.")
        return
    try:
        resultado = servico.excluir(codigo)
    except PecaNaoEncontrada as erro:
        escrever(str(erro))
        return
    escrever(resultado.mensagem)


def _caixas_fechadas(servico: QualidadeService, escrever: Escrever) -> None:
    caixas = servico.listar_caixas_fechadas()
    if not caixas:
        escrever("Nenhuma caixa fechada.")
        return
    for caixa in caixas:
        codigos = ", ".join(peca.codigo for peca in caixa.pecas) or "—"
        escrever(
            f"Caixa {caixa.id} | {caixa.resumo_ocupacao} | {formatar_data(caixa.criada_em)} | {codigos}"
        )


def _relatorio(servico: QualidadeService, escrever: Escrever) -> None:
    relatorio = servico.relatorio()
    escrever("Relatório final")
    escrever(f"Peças cadastradas: {relatorio.total}")
    escrever(f"Aprovadas: {relatorio.aprovadas}")
    escrever(f"Reprovadas: {relatorio.reprovadas}")
    escrever(f"Aprovação: {formatar_percentual(relatorio.taxa)}")
    escrever("Motivos de reprovação:")
    if not relatorio.motivos:
        escrever("- Nenhum motivo registrado.")
    for nome, quantidade in relatorio.motivos:
        escrever(f"- {nome} — {quantidade}")
    escrever(f"Caixas utilizadas: {relatorio.total_caixas}")
    escrever(f"Abertas: {relatorio.caixas_abertas}")
    escrever(f"Fechadas: {relatorio.caixas_fechadas}")
    escrever(f"Peças armazenadas: {relatorio.pecas_armazenadas}")


def _loop(servico: QualidadeService, ler: Ler, escrever: Escrever) -> None:
    continuar = True
    while continuar:
        escrever("")
        escrever("1. Cadastrar nova peça")
        escrever("2. Listar peças aprovadas/reprovadas")
        escrever("3. Remover peça cadastrada")
        escrever("4. Listar caixas fechadas")
        escrever("5. Gerar relatório final")
        escrever("6. Sair")
        continuar = processar_opcao(ler("Opção: "), servico, ler, escrever)


def main() -> None:
    from flask_migrate import upgrade

    from app import create_app

    app = create_app()
    with app.app_context():
        upgrade()
        _loop(QualidadeService(), input, print)


if __name__ == "__main__":
    main()
