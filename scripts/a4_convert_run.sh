#!/usr/bin/env bash
# Wrapper so the bot session can run the A4 photo-convert pipeline (Q5) without
# a permission prompt: bot.py allowlists every scripts/*.sh at dispatch time.
# Read-only on Drive; writes only under maplab-ai-handbook/data/photo_convert/.
set -euo pipefail
exec /usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/a4_photo_convert.py "$@"
