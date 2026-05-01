#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()  { echo -e "${CYAN}[bot]${RESET} $*"; }
ok()   { echo -e "${GREEN}[bot]${RESET} $*"; }
warn() { echo -e "${YELLOW}[bot]${RESET} $*"; }
err()  { echo -e "${RED}[bot]${RESET} $*" >&2; }

PIDS=()
cleanup() {
  echo ""
  log "Stopping…"
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  ok "Done."
}
trap cleanup EXIT INT TERM

# Venv
VENV="$ROOT/venv"
if [[ ! -d "$VENV" ]]; then
  warn "No venv — creating…"
  python3 -m venv "$VENV"
  ok "Venv created."
fi
source "$VENV/bin/activate"

# Deps
log "Installing deps…"
[[ -f "$ROOT/requirements.txt" ]] && pip install -q -r "$ROOT/requirements.txt" 2>/dev/null || true
ok "Deps OK."

# Flask
log "Starting Flask…"
python3 main.py 2>&1 &
BACKEND_PID=$!
PIDS+=("$BACKEND_PID")

sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  err "Flask died — check imports in main.py"
  exit 1
fi

ok "Backend (PID $BACKEND_PID) → http://localhost:5010"

echo ""
echo -e "${BOLD}🤖 theBot running${RESET}"
echo -e "  API   → ${CYAN}http://localhost:5010/api${RESET}"
echo -e "  Dash  → ${CYAN}http://localhost:5010${RESET}"
echo -e "  Ctrl+C to stop"
echo ""

wait "${PIDS[@]}" 2>/dev/null || true
