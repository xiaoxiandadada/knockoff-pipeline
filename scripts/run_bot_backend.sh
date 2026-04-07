#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

load_env_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$file"
    set +a
  fi
}

load_env_file "$ROOT_DIR/.env"
load_env_file "$ROOT_DIR/.env.local"

if /Users/bytedance/miniconda3/bin/python3 -c 'import uvicorn' >/dev/null 2>&1; then
  PYTHON_BIN=/Users/bytedance/miniconda3/bin/python3
else
  PYTHON_BIN=python3
fi

exec "$PYTHON_BIN" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
