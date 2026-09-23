#!/usr/bin/env bash
# check_work_order_selftest.sh — check_work_order.py 的自測
#
# 為什麼有這支:`python3 scripts/check_work_order.py` 這個呼叫形式不在白名單,
# A0 在 headless 輪次裡跑不了,等於「改了但沒驗」。依 CULTURE_DECISION_LOGIC.md 制度 A
# (修完必附驗證、同一輪交付),把驗證本身放進白名單涵蓋得到的 scripts/*.sh 裡。
#
# 驗三件:
#   A. 五欄齊全的正常卡 -> exit 0(不能因為新增的檢查而誤殺既有卡)
#   B. 「結果」欄要求登入的卡 -> exit 2,且訊息含「派工無效類」
#   C. 「權限」欄寫「不碰金鑰」但結果正常的卡 -> exit 0(證明只掃結果欄、不掃全文,沒有誤殺)
set -uo pipefail

REPO="$HOME/maplab-ai-handbook"
CHECKER="$REPO/scripts/check_work_order.py"
TMPD="$(mktemp -d -t wocheck.XXXXXX)"
trap 'rm -rf "$TMPD"' EXIT

fail=0
note() { printf '%-4s %s\n' "$1" "$2"; }

mkcard() {
  # $1=檔名 $2=結果 $3=權限
  cat > "$TMPD/$1" <<EOF
# 測試卡

- **結果**: $2
- **指標**: 回執 state=done 且 evidence 非空
- **期限**: 2026-09-23 23:59
- **權限**: $3
- **回報點**: 改完回一次、驗完回一次;done=驗證通過,blocked=缺前提時寫明缺什麼
- **動作可逆性**: 可逆(改動前先備份)
EOF
}

run_case() {
  # $1=標題 $2=檔名 $3=期望 exit code $4=期望訊息片段(可空)
  local title="$1" file="$2" want="$3" needle="${4:-}"
  local out rc
  out="$(python3 "$CHECKER" "$TMPD/$file" 2>&1)"; rc=$?
  if [ "$rc" != "$want" ]; then
    note "FAIL" "$title — 期望 exit=$want,實得 exit=$rc"
    printf '%s\n' "$out" | sed 's/^/       /'
    fail=1
    return
  fi
  if [ -n "$needle" ] && ! printf '%s' "$out" | grep -q "$needle"; then
    note "FAIL" "$title — exit 對了但訊息沒帶「$needle」(制度 E:教訓要挪進錯誤訊息)"
    printf '%s\n' "$out" | sed 's/^/       /'
    fail=1
    return
  fi
  note "ok" "$title (exit=$rc)"
}

# 帶一個檔案參數時 = 直接驗那張真卡(而不是跑自測)。
# 為什麼放這裡:python3 那個呼叫形式在 headless 輪次跑不了,所以真卡永遠沒被 gate 驗過,
# 等於寫了 gate 卻只驗假卡。把真卡入口併進同一支白名單腳本,新卡才真的過得了關。
if [ -n "${1:-}" ]; then
  echo "=== 驗真卡:$1 ==="
  python3 "$CHECKER" "$1"
  exit $?
fi

echo "=== check_work_order.py 自測 ==="

mkcard A.md "把 hermes 壓縮模型換成 context >= 64000 的免費模型,並留備份" "只改該設定鍵;不碰金鑰、不碰金融、不對外發布"
run_case "A 正常卡應可派工" A.md 0

mkcard B.md "在 win-01 重新登入 Claude,讓排程恢復" "只在該機操作"
run_case "B 結果欄要求登入應被擋" B.md 2 "派工無效類"

mkcard C.md "修正 photo_alt_index 的 scene 分類並重寫 alt" "唯讀讀取 Drive;不碰金鑰、不碰帳密、不動 cookie"
run_case "C 權限欄提到金鑰帳密但結果正常,不得誤殺" C.md 0

echo
if [ "$fail" = 0 ]; then
  echo "PASS:三個案例全過。新增的「派工無效類」檢查會擋該擋的,且沒有誤殺既有卡。"
else
  echo "FAIL:有案例沒過,上面有細節。改到全過之前,不得宣稱這條 gate 已生效。"
fi
exit "$fail"
