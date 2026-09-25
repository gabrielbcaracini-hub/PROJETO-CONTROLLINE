"""Formulários com proteção CSRF. A regra de negócio fica no domínio."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired


class FormPeca(FlaskForm):
    codigo = StringField("ID da peça")
    peso = StringField("Peso em gramas")
    cor = StringField("Cor")
    comprimento = StringField("Comprimento em centímetros")


class FormExclusao(FlaskForm):
    confirmar = BooleanField(
        "Confirmo a exclusão desta peça",
        validators=[DataRequired(message="Confirme a exclusão para continuar.")],
    )
