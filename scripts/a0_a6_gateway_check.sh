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
# 最後兩個是經驗庫的尾段(§3.2 與 §5 收尾):它們在 prompt 裡才代表沒被截斷。
for marker in ('內部試算', '報價經驗庫', 'Owner msg 5774', '外帶售價', '已作廢', '需人工',
               'Owner msg 5824', '算完之後的固定收尾',
               '方法一：用外帶單反推 item 成本', '方法二：雷同品項類推',
               '資訊不全時怎麼交件', '算不出來的不給單價'):
    print(('OK   ' if marker in p else 'MISS ') + marker)
print('system_prompt chars:', len(p))
print('playbook chars:', len(g.load_quote_playbook()))
"

    echo "--- 成本佔比帶 (Owner msg 5845 SOP 方法二的機械煞車:跳出帶外=抓錯單位/品項) ---"
    cd "$REPO" && "$PY" -c "
import bot_a6.quote_calc as q
b = q.cost_share_band()
print('帶 %.0f%%-%.0f%%  實際 %.1f%%-%.1f%%' % (b['low']*100, b['high']*100, b['min_share']*100, b['max_share']*100))
print('帶外品項:', [r['key'] for r in b['outliers']] or '無')
for r in sorted(q.margin_table(), key=lambda r: r['margin_rate']):
    print('  %-22s 成本佔比 %5.1f%%  %s' % (r['key'], (1-r['margin_rate'])*100, '推估' if r['estimated'] else '實數'))
"

    echo "--- ref H4-OWNER (Owner msg 5824:砍蝦棗、多澱粉類；外帶推導成本必須被點名) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref H4-OWNER

    echo "--- ref H5-OWNER (Owner msg 5846:蝦棗鎖 60；拼盤不在表=不編價，只算剩餘額度) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py ref H5-OWNER
    echo "--- headroom H5-OWNER (拼盤可用食材額度與每件成本上限) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py headroom H5-OWNER
    echo "--- 拼盤本身仍必須擋下來 (不在價目表) ---"
    cd "$REPO" && "$PY" bot_a6/quote_calc.py items --item 混合炸物拼盤=1 --package-price 30000 --pax 100
    echo "exit=$?"

    # 每輪續接必看：收據上向 Owner 承諾「A0 下一輪續接時會看到這筆」，不查就是空頭承諾。
    # 只列檔名與時間，案卷內容含客人需求＝不進 repo、不進 Telegram（2026-09-22）。
    echo "--- quote_intake 新案卷 (只列檔名時間，不印內容) ---"
    ls -l "$HOME/.maplab/quote_intake" 2>&1 | tail -n 10 || echo "no intake dir"

    echo "--- unittest (test_hermes*) ---"
    # tail 要夠長：只留 25 行時第二個 FAIL 會被切掉，害我以為只壞一項（2026-09-22）。
    cd "$REPO" && "$PY" -m unittest discover -s tests -p 'test_hermes*.py' 2>&1 | tail -n 120

    # SECTION 27 第三節的機械檢查（2026-09-22 落成）：五欄模板與 check_work_order.py
    # 走這裡是因為沙盒只放行本腳本這條 Python 通道，不是因為它跟 a6 同一套。
    echo "--- unittest (test_work_order_template) ---"
    cd "$REPO" && "$PY" -m unittest discover -s tests -p 'test_work_order_template.py' 2>&1 | tail -n 40

    echo "--- 派工檢查器實跑：模板本身必須被擋 (exit 2 = 不准派工) ---"
    cd "$REPO" && "$PY" scripts/check_work_order.py handoff/tasks/_WORK_ORDER_TEMPLATE.md
    echo "exit=$?"

    echo "--- 派工檢查器實跑：現行工作單 JOB-1 必須過 (exit 0 = 可派工) ---"
    cd "$REPO" && "$PY" scripts/check_work_order.py handoff/tasks/T-HERMES-SYSTEMATIZE-001-JOB-1.md
    echo "exit=$?"

    echo "=== end ==="
} >"$LOG" 2>&1

chmod 600 "$LOG"
