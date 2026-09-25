"""Aplicação de teste com SQLite em memória."""

from __future__ import annotations

import pytest

from app import create_app, db
from app.application.services import QualidadeService
from app.config import TestConfig


@pytest.fixture
def app():
    aplicacao = create_app(TestConfig)
    with aplicacao.app_context():
        db.create_all()
        yield aplicacao
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def servico(app):
    return QualidadeService()
