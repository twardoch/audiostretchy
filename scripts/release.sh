#!/usr/bin/env bash
# this_file: scripts/release.sh
set -euo pipefail
exec "$(dirname "$0")/../publish.sh" "$@"
