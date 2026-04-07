#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOT_PID=""

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

clear_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      printf 'Releasing port %s: %s\n' "$port" "$pids"
      kill $pids >/dev/null 2>&1 || true
      sleep 1
    fi
  fi
}

cleanup() {
  if [[ -n "$BOT_PID" ]] && kill -0 "$BOT_PID" >/dev/null 2>&1; then
    kill "$BOT_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR"
clear_port 8000
clear_port 1313
"$PYTHON_BIN" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 >/tmp/knockoff-bot.log 2>&1 &
BOT_PID=$!

printf 'Bot API: http://127.0.0.1:8000/api/health\n'
printf 'Docs site: http://127.0.0.1:1313/\n'
printf 'LLM provider: %s\n' "${LLM_PROVIDER:-openai}"
printf 'LLM model: %s\n' "${OPENAI_MODEL:-${LLM_MODEL:-default}}"

exec hugo server --bind 127.0.0.1 --port 1313 --disableKinds rss
