#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

PYTHONPATH=src "$PYTHON_BIN" -m compileall src tests
PYTHONPATH=src "$PYTHON_BIN" -m unittest discover -s tests
