#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv-build 2>/dev/null || true
source .venv-build/bin/activate
python -m pip install --upgrade pip
pip install -r gui/requirements-build.txt
pyinstaller --noconfirm --windowed --name "$(basename "$PWD")-gui" gui/app.py
echo "Build done: dist/"
