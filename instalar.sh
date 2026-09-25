#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --find-links=dependencias -r requirements.txt
echo "Instalacao concluida. Rode: .venv/bin/python run.py"
