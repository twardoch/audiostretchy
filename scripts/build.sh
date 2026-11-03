#!/usr/bin/env bash
# this_file: scripts/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
uv build
uvx twine check --strict dist/*.whl dist/*.tar.gz
