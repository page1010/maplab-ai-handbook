#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/pagemacmini/maplab-ai-handbook"
PANEL="$REPO/local-control-plane/panel.html"

if [[ ! -f "$PANEL" ]]; then
  echo "Panel not found: $PANEL" >&2
  exit 1
fi

case "${1:-open}" in
  open)
    open "$PANEL"
    echo "Opened MAPLAB Agent Runtime Panel: $PANEL"
    ;;
  reveal)
    open -R "$PANEL"
    echo "Revealed MAPLAB Agent Runtime Panel in Finder: $PANEL"
    ;;
  serve)
    cd "$REPO/local-control-plane"
    echo "Serving MAPLAB Agent Runtime Panel at http://127.0.0.1:8787/panel.html"
    python3 -m http.server 8787 --bind 127.0.0.1
    ;;
  *)
    echo "Usage: $0 [open|reveal|serve]" >&2
    exit 2
    ;;
esac
