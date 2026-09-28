# shellcheck shell=bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER="${CLUSTER:-preview}"
DOMAIN="${PREVIEW_DOMAIN:-preview.localhost}"
PORT="${PREVIEW_PORT:-8080}"

require_pr() {
  if [[ ! "${1:-}" =~ ^[0-9]+$ ]]; then
    echo "usage: $(basename "$0") <pr-number> [...]" >&2
    exit 2
  fi
}

namespace() { echo "pr-$1"; }
preview_url() { echo "http://pr-$1.$DOMAIN:$PORT"; }
