#!/usr/bin/env bash
# Small helper to create a virtualenv and install deps in this project
set -euo pipefail

if [ -z "${PYTHON:-}" ]; then
  PYTHON=python3
fi

echo "Creating virtual environment at .venv using ${PYTHON}..."
${PYTHON} -m venv .venv
echo "Activating and upgrading pip..."
source .venv/bin/activate
pip install --upgrade pip
echo "Installing runtime requirements..."
pip install -r requirements.txt || true
echo "Installing dev requirements..."
pip install -r requirements-dev.txt || true

echo "Done. To activate: source .venv/bin/activate"
