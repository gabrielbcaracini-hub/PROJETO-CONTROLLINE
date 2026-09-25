"""Validação de entrada compartilhada pela interface web e pela CLI.

Valor fora do critério de qualidade não é erro de formulário: a peça
é gravada como reprovada. Aqui só se bloqueia entrada inutilizável.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from app.domain.constants import CASAS_DECIMAIS, CODIGO_MAX, COR_MAX, VALOR_MAXIMO
from app.domain.exceptions import DadosInvalidos
from app.domain.quality import normalizar_cor

_CODIGO = re.compile(rf"^[A-Za-z0-9][A-Za-z0-9_-]{{0,{CODIGO_MAX - 1}}}$")
_NUMERO = re.compile(r"^\d+(\.\d+)?$")


@dataclass(frozen=True)
class DadosPeca:
    codigo: str
    peso: Decimal
    cor: str
    comprimento: Decimal


def _mensagem_numero(nome: str) -> str:
    return f"Informe {nome} com até {CASAS_DECIMAIS} casas decimais, usando ponto ou vírgula."


def _ler_numero(bruto: object, campo: str, nome: str, erros: dict[str, str]) -> Decimal | None:
    if bruto is None or str(bruto).strip() == "":
        erros[campo] = f"Informe {nome}."
        return None

    texto = str(bruto).strip().replace(",", ".")
    if not _NUMERO.fullmatch(texto):
        erros[campo] = _mensagem_numero(nome)
        return None

    numero = Decimal(texto)
    if not numero.is_finite():
        erros[campo] = _mensagem_numero(nome)
        return None
    if numero <= 0:
        erros[campo] = f"{nome.capitalize()} deve ser maior que zero."
        return None
    if numero > VALOR_MAXIMO:
        erros[campo] = f"{nome.capitalize()} ultrapassa o limite aceito neste cadastro."
        return None

    casas = 0 if "." not in texto else len(texto.split(".", maxsplit=1)[1])
    if casas > CASAS_DECIMAIS:
        erros[campo] = f"Use no máximo {CASAS_DECIMAIS} casas decimais em {nome}."
        return None
    return numero


def validar_cadastro(codigo: object, peso: object, cor: object, comprimento: object) -> DadosPeca:
    erros: dict[str, str] = {}

    codigo_limpo = "" if codigo is None else str(codigo).strip()
    if not codigo_limpo:
        erros["codigo"] = "Informe o ID da peça."
    elif not _CODIGO.fullmatch(codigo_limpo):
        erros["codigo"] = (
            f"Use de 1 a {CODIGO_MAX} caracteres: letras, números, hífen ou sublinhado, "
            "começando por letra ou número."
        )

    peso_decimal = _ler_numero(peso, "peso", "o peso em gramas", erros)
    comprimento_decimal = _ler_numero(comprimento, "comprimento", "o comprimento em centímetros", erros)

    cor_bruta = "" if cor is None else str(cor).strip()
    if not cor_bruta:
        erros["cor"] = "Informe a cor."
    elif len(cor_bruta) > COR_MAX:
        erros["cor"] = f"A cor deve ter no máximo {COR_MAX} caracteres."

    if erros or peso_decimal is None or comprimento_decimal is None:
        raise DadosInvalidos(erros)

    return DadosPeca(
        codigo=codigo_limpo,
        peso=peso_decimal,
        cor=normalizar_cor(cor_bruta),
        comprimento=comprimento_decimal,
    )
