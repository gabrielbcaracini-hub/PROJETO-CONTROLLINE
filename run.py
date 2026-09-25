"""Sobe a aplicação web e aplica as migrações pendentes."""

from __future__ import annotations

import os

from flask_migrate import upgrade

from app import create_app

app = create_app()


def main() -> None:
    with app.app_context():
        upgrade()
    porta = int(os.environ.get("PORT", "8741"))
    app.run(host="0.0.0.0", port=porta, debug=os.environ.get("FLASK_DEBUG") == "1")


if __name__ == "__main__":
    main()
