#!/usr/bin/env bash
# this_file: scripts/test.sh
set -euo pipefail
exec "$(dirname "$0")/../test.sh" "$@"
