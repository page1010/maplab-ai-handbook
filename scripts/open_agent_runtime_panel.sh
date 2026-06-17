#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/pagemacmini/maplab-ai-handbook"
PANEL="$REPO/local-control-plane/panel.html"
HERMES_PANEL="$REPO/local-control-plane/hermes.html"

if [[ ! -f "$PANEL" ]]; then
  echo "Panel not found: $PANEL" >&2
  exit 1
fi

ensure_hermes_panel() {
  if [[ -f "$HERMES_PANEL" && -f "$REPO/local-control-plane/hermes_status.js" ]]; then
    return 0
  fi
  local patrol_log="$REPO/logs/runtime/patrol-scheduled.log"
  if [[ ! -f "$patrol_log" && -f "$REPO/logs/patrol-scheduled.log" ]]; then
    patrol_log="$REPO/logs/patrol-scheduled.log"
  fi
  if [[ -f "$patrol_log" ]]; then
    python3 "$REPO/tools/hermes_patrol_bridge.py" --repo "$REPO" --raw-text-file "$patrol_log" --quiet || true
  else
    python3 "$REPO/tools/hermes_patrol_bridge.py" --repo "$REPO" --quiet || true
  fi
  [[ -f "$HERMES_PANEL" ]]
}

case "${1:-open}" in
  open)
    open "$PANEL"
    echo "Opened MAPLAB Agent Runtime Panel: $PANEL"
    ;;
  hermes)
    ensure_hermes_panel || { echo "Hermes panel not found: $HERMES_PANEL" >&2; exit 1; }
    open "$HERMES_PANEL"
    echo "Opened MAPLAB Hermes Patrol Panel: $HERMES_PANEL"
    ;;
  reveal)
    open -R "$PANEL"
    echo "Revealed MAPLAB Agent Runtime Panel in Finder: $PANEL"
    ;;
  hermes-reveal)
    ensure_hermes_panel || { echo "Hermes panel not found: $HERMES_PANEL" >&2; exit 1; }
    open -R "$HERMES_PANEL"
    echo "Revealed MAPLAB Hermes Patrol Panel in Finder: $HERMES_PANEL"
    ;;
  serve)
    cd "$REPO/local-control-plane"
    echo "Serving MAPLAB Agent Runtime Panel at http://127.0.0.1:8787/panel.html"
    python3 -m http.server 8787 --bind 127.0.0.1
    ;;
  hermes-serve)
    ensure_hermes_panel || { echo "Hermes panel not found: $HERMES_PANEL" >&2; exit 1; }
    cd "$REPO/local-control-plane"
    echo "Serving MAPLAB Hermes Patrol Panel at http://127.0.0.1:8787/hermes.html"
    python3 -m http.server 8787 --bind 127.0.0.1
    ;;
  *)
    echo "Usage: $0 [open|hermes|reveal|hermes-reveal|serve|hermes-serve]" >&2
    exit 2
    ;;
esac
