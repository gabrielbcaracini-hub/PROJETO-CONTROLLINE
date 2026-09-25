"""Visualização das caixas de armazenamento."""

from __future__ import annotations

from flask import Blueprint, render_template

from app.application.services import QualidadeService

bp = Blueprint("caixas", __name__, url_prefix="/caixas")


@bp.get("/", strict_slashes=False)
def lista():
    return render_template("caixas/lista.html", caixas=QualidadeService().listar_caixas())
