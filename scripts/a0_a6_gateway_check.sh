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

    echo "--- quote calc smoke (Owner msg 5774:a6 要能幫 Owner 算報價) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py margin-table | head -n 24
    echo "--- ref H3-OWNER (Owner msg 5800 件數法:薄餅100片/便宜多貴少/三明治切小) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref H3-OWNER
    echo "--- ref H1-80 replay (套 5800 三明治成本後掉到 79.8%,跌破 80% 下限) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref H1-80 | head -n 6
    echo "--- ref H2-85 ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref H2-85 | head -n 6
    echo "--- 作廢配置必須擋下來 (Owner msg 5800:why 開了 60% 的) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref A-60 ; echo "exit=$?"
    echo "--- scale:人給比例,程式放大到 80% ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py scale --item "梅子醬蝦棗=10" "綠咖喱小鹹派=4" "沙嗲雞肉披薩=1" --package-price 30000 --pax 100 --margin 0.8 | head -n 8
    echo "--- brief parse ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py brief "用預算反推 30000塊 人數100人 毛利要80% 10月上旬"
    echo "--- unknown item must say 需人工 ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py items --item "神秘新菜=1" ; echo "exit=$?"

    echo "--- system prompt 真的載到經驗庫了嗎 (Owner msg 5774 的回寫要能生效) ---"
    cd "$REPO" && "$PY" -c "
import bot_a6.hermes_telegram_gateway as g
p = g.system_prompt()
for marker in ('內部試算', '報價經驗庫', 'Owner msg 5774', '外帶售價', '已作廢', '需人工'):
    print(('OK   ' if marker in p else 'MISS ') + marker)
print('system_prompt chars:', len(p))
print('playbook chars:', len(g.load_quote_playbook()))
"

    echo "--- unittest (test_hermes*) ---"
    # tail 要夠長：只留 25 行時第二個 FAIL 會被切掉，害我以為只壞一項（2026-09-22）。
    cd "$REPO" && "$PY" -m unittest discover -s tests -p 'test_hermes*.py' 2>&1 | tail -n 120

    echo "=== end ==="
} >"$LOG" 2>&1

chmod 600 "$LOG"
