"""Dados fictícios para demonstração.

Não roda junto com a aplicação. Se o banco já tiver peças, não grava nada.
"""

from __future__ import annotations

import sys

from flask_migrate import upgrade

from app import create_app
from app.application.services import QualidadeService
from app.infrastructure.models import Peca

# 15 aprovadas fecham uma caixa e deixam outra com 5 peças.
# 6 reprovadas cobrem os cinco motivos, inclusive falhas combinadas.
PECAS = [
    ("QA-001", "100", "azul", "15"),
    ("QA-002", "100", "verde", "15"),
    ("QA-003", "98", "azul", "12"),
    ("QA-004", "102", "verde", "18"),
    ("QA-005", "95", "azul", "10"),
    ("QR-001", "90", "azul", "15"),
    ("QA-006", "105", "verde", "20"),
    ("QA-007", "99", "azul", "14"),
    ("QR-002", "130", "verde", "15"),
    ("QA-008", "101", "verde", "16"),
    ("QA-009", "100", "azul", "11"),
    ("QA-010", "100", "verde", "19"),
    ("QR-003", "100", "vermelho", "15"),
    ("QR-004", "100", "azul", "7"),
    ("QA-011", "97", "azul", "13"),
    ("QA-012", "103", "verde", "17"),
    ("QR-005", "100", "verde", "28"),
    ("QA-013", "100", "Azul", "15"),
    ("QA-014", "100", "VERDE", "15"),
    ("QR-006", "70", "amarelo", "4"),
    ("QA-015", "96,50", "azul", "10,50"),
]


def main() -> int:
    app = create_app()
    with app.app_context():
        upgrade()
        if Peca.query.count():
            print("O banco já possui peças. Nada foi alterado.")
            print("Para uma base só de demonstração, apague instance/qualidade.db e execute de novo.")
            return 1
        servico = QualidadeService()
        for codigo, peso, cor, comprimento in PECAS:
            servico.cadastrar(codigo, peso, cor, comprimento)
        relatorio = servico.relatorio()
        print(f"Peças: {relatorio.total}")
        print(f"Aprovadas: {relatorio.aprovadas}")
        print(f"Reprovadas: {relatorio.reprovadas}")
        print(f"Caixas: {relatorio.total_caixas} (abertas {relatorio.caixas_abertas}, fechadas {relatorio.caixas_fechadas})")
        for nome, quantidade in relatorio.motivos:
            print(f"- {nome}: {quantidade}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
