#!/usr/bin/env bash
set -euo pipefail
APP="$1"
BIN="$HOME/.local/bin"
mkdir -p "$BIN"
cp -r "dist/$APP" "$BIN/"
ln -sf "$BIN/$APP/$APP" "$BIN/$APP-launcher"
echo "Installed to $BIN/$APP"
