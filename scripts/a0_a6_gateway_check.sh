#!/usr/bin/env bash
# a0_a6_gateway_check.sh — A6 閘道改動後的靜態+測試驗證(不連網、不重啟任何進程)
#
# 2026-09-22:修掉「拒絕理由被二次分類覆寫」「歷史含憑證字樣就永久拒絕 Owner」
# 兩個問題並新增 quote-intake 受理動作後,用這支驗證語法與既有測試。
# 產出:~/.maplab/a6_gateway_check.log(逐次覆寫)
set -uo pipefail

REPO="/Users/pagemacmini/maplab-ai-handbook"
PY="$REPO/bot/venv/bin/python3"
LOG="$HOME/.maplab/a6_gateway_check.log"
mkdir -p "$HOME/.maplab"

{
    echo "=== a6 gateway check $(date '+%Y-%m-%d %H:%M:%S') ==="

    echo "--- py_compile ---"
    "$PY" -m py_compile \
        "$REPO/bot_a6/hermes_telegram_gateway.py" \
        "$REPO/bot_a6/hermes_task_executor.py" \
        && echo "py_compile OK" || echo "py_compile FAILED"

    echo "--- route replay (rejected quote request 2026-09-21 19:18) ---"
    cd "$REPO" && "$PY" "$REPO/scripts/a0_diag_a6_route.py" A6H-20260921-191808-317428 \
        || echo "route replay FAILED"

    echo "--- unittest (test_hermes*) ---"
    cd "$REPO" && "$PY" -m unittest discover -s tests -p 'test_hermes*.py' 2>&1 | tail -n 25

    echo "=== end ==="
} >"$LOG" 2>&1

chmod 600 "$LOG"
