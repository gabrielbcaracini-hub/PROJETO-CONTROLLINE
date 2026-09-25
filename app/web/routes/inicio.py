"""Painel inicial."""

from __future__ import annotations

from flask import Blueprint, render_template

from app.application.services import QualidadeService

bp = Blueprint("inicio", __name__)


@bp.get("/", strict_slashes=False)
def painel():
    return render_template("dashboard/index.html", painel=QualidadeService().painel())
