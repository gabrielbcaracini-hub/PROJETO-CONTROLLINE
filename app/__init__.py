"""Fábrica da aplicação Flask."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

from app.config import DevConfig
from app.infrastructure.database import db
from app.infrastructure.logging import configurar_logs
from app.web.formatacao import formatar_data, formatar_decimal, formatar_percentual

load_dotenv()

csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_class: type = DevConfig) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = _carregar_ou_criar_segredo(Path(app.instance_path))

    configurar_logs(app)
    db.init_app(app)
    from app.infrastructure import models  # noqa: F401  (metadata do Alembic)

    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.web.routes import registrar_rotas

    registrar_rotas(app)
    _registrar_filtros(app)
    _registrar_contexto(app)
    _registrar_erros(app)

    @app.after_request
    def cabecalhos_de_protecao(resposta):
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "SAMEORIGIN"
        resposta.headers["Referrer-Policy"] = "same-origin"
        return resposta

    return app


def _carregar_ou_criar_segredo(instance_path: Path) -> str:
    caminho = instance_path / "secret_key"
    if caminho.exists():
        existente = caminho.read_text(encoding="utf-8").strip()
        if existente:
            return existente
    chave = secrets.token_hex(32)
    caminho.write_text(chave, encoding="utf-8")
    return chave


def _registrar_filtros(app: Flask) -> None:
    app.add_template_filter(formatar_decimal, "br_numero")
    app.add_template_filter(formatar_data, "br_data")
    app.add_template_filter(formatar_percentual, "br_percentual")


def _registrar_contexto(app: Flask) -> None:
    from app.domain.constants import (
        CAPACIDADE_CAIXA,
        CODIGO_MAX,
        COMPRIMENTO_MAX,
        COMPRIMENTO_MIN,
        CORES_PERMITIDAS,
        COR_MAX,
        PESO_MAX,
        PESO_MIN,
        VALOR_MAXIMO,
    )

    @app.context_processor
    def injetar_regras() -> dict[str, object]:
        return {
            "regras_qualidade": {
                "pesoMin": PESO_MIN,
                "pesoMax": PESO_MAX,
                "comprimentoMin": COMPRIMENTO_MIN,
                "comprimentoMax": COMPRIMENTO_MAX,
                "cores": sorted(CORES_PERMITIDAS),
                "capacidade": CAPACIDADE_CAIXA,
                "codigoMax": CODIGO_MAX,
                "corMax": COR_MAX,
                "valorMaximo": VALOR_MAXIMO,
                "casasDecimais": 2,
            }
        }


def _registrar_erros(app: Flask) -> None:
    @app.errorhandler(CSRFError)
    def erro_csrf(_erro: CSRFError) -> tuple[str, int]:
        return render_template(
            "errors/400.html",
            titulo="Formulário recusado",
            mensagem="A proteção do formulário expirou ou está ausente. Recarregue a página e tente de novo.",
        ), 400

    @app.errorhandler(404)
    def erro_404(_erro: Exception) -> tuple[str, int]:
        return render_template(
            "errors/404.html",
            titulo="Página não encontrada",
            mensagem="O endereço não corresponde a nenhuma tela deste sistema.",
        ), 404

    @app.errorhandler(405)
    def erro_405(_erro: Exception) -> tuple[str, int]:
        return render_template(
            "errors/400.html",
            titulo="Operação não permitida",
            mensagem="Essa ação precisa ser enviada pelo formulário correspondente.",
        ), 405

    @app.errorhandler(500)
    def erro_500(_erro: Exception) -> tuple[str, int]:
        app.logger.exception("Falha interna ao atender a requisição.")
        return render_template(
            "errors/500.html",
            titulo="Falha interna",
            mensagem="A operação não foi concluída. Nenhuma alteração parcial deve permanecer gravada.",
        ), 500
