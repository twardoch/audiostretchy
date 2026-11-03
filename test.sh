#!/usr/bin/env bash
# this_file: test.sh
set -euo pipefail
cd "$(dirname "$0")"
uv sync --frozen
uv run --frozen ruff check src tests scripts hatch_build.py
uv run --frozen ruff format --check src tests scripts hatch_build.py
uv run --frozen pytest "$@"
