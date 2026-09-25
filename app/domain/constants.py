"""Constantes das regras de qualidade e de armazenamento.

Os limites do critério acadêmico ficam somente neste módulo.
"""

from __future__ import annotations

PESO_MIN = 95
PESO_MAX = 105
COMPRIMENTO_MIN = 10
COMPRIMENTO_MAX = 20
CORES_PERMITIDAS = frozenset({"azul", "verde"})
CAPACIDADE_CAIXA = 10

VALOR_MAXIMO = 1_000_000
CASAS_DECIMAIS = 2
CODIGO_MAX = 32
COR_MAX = 32

MOTIVO_PESO_ABAIXO = "Peso abaixo do permitido"
MOTIVO_PESO_ACIMA = "Peso acima do permitido"
MOTIVO_COR = "Cor não permitida"
MOTIVO_COMPRIMENTO_ABAIXO = "Comprimento abaixo do permitido"
MOTIVO_COMPRIMENTO_ACIMA = "Comprimento acima do permitido"

MOTIVOS_CANONICOS = (
    MOTIVO_PESO_ABAIXO,
    MOTIVO_PESO_ACIMA,
    MOTIVO_COR,
    MOTIVO_COMPRIMENTO_ABAIXO,
    MOTIVO_COMPRIMENTO_ACIMA,
)
