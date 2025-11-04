#!/usr/bin/env bash
# Build script for Render

set -e

echo "==> Updating pip..."
pip install --upgrade pip setuptools wheel

echo "==> Installing dependencies (binary only)..."
pip install --only-binary :all: -r requirements.txt || pip install -r requirements.txt

echo "==> Build completed successfully!"
