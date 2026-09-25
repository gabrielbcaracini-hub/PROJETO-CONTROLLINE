"""Relatório consolidado."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, send_file

from app.application.services import QualidadeService
from app.web.pdf_relatorio import gerar_pdf

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")
_SAO_PAULO = ZoneInfo("America/Sao_Paulo")


@bp.get("/", strict_slashes=False)
def ver():
    return render_template("relatorios/index.html", relatorio=QualidadeService().relatorio())


@bp.get("/pdf")
def baixar_pdf():
    relatorio = QualidadeService().relatorio()
    pdf = gerar_pdf(relatorio)
    data = datetime.now(timezone.utc).astimezone(_SAO_PAULO).strftime("%Y%m%d")
    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"relatorio-linecontrol-{data}.pdf",
    )
