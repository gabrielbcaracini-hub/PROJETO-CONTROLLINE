"""Log técnico de falhas. A trilha de negócio fica na tabela de auditoria."""

from __future__ import annotations

import logging

from flask import Flask


def configurar_logs(app: Flask) -> None:
    app.logger.setLevel(logging.INFO)
