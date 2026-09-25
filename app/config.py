"""Configurações de desenvolvimento e de teste.

A chave secreta não fica no código. Em desenvolvimento, se SECRET_KEY
não vier do ambiente, a fábrica grava uma chave local em instance/.
"""

from __future__ import annotations

import os

from sqlalchemy.pool import StaticPool


class DevConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///qualidade.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    JSON_AS_ASCII = False


class TestConfig:
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    WTF_CSRF_ENABLED = True
