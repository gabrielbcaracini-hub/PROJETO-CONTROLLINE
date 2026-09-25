"""Registro dos blueprints."""

from __future__ import annotations

from flask import Flask

from app.web.routes.caixas import bp as caixas_bp
from app.web.routes.inicio import bp as inicio_bp
from app.web.routes.pecas import bp as pecas_bp
from app.web.routes.relatorios import bp as relatorios_bp


def registrar_rotas(app: Flask) -> None:
    app.register_blueprint(inicio_bp)
    app.register_blueprint(pecas_bp)
    app.register_blueprint(caixas_bp)
    app.register_blueprint(relatorios_bp)
