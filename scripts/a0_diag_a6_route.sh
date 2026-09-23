#!/usr/bin/env bash
# 診斷用:重放某筆 A6-HERMES-TASKS 的 request,印出 gateway 路由判定(純函式,不連網)。
set -euo pipefail
REPO="/Users/pagemacmini/maplab-ai-handbook"
cd "$REPO"
exec "$REPO/bot/venv/bin/python3" "$REPO/scripts/a0_diag_a6_route.py" "$@"
