#!/usr/bin/env bash
# kol_chain_health.sh — 一眼看出「每日財經吸收鏈」哪幾條是真的在動,哪幾條只是在假裝活著。
#
# 為什麼要有這支(制度 E,把教訓寫進程式不是寫進筆記):
#   launchctl 顯示 exit 0 不等於有產出。2026-09-23 實查抓到:
#   com.investmentos.fb-shadow-refresh 每天 03:00 跑、每天 exit 0,
#   但 payload 自 2026-06-02 起逐字相同——它在重播一份三到四月的舊 corpus,
#   真正的 FB 抓取最後一次是 2026-06-11。
#   T-IOS-KOL-001 明文寫「不得用舊 corpus 假裝今日報告」,我們自己的排程正在違反它。
#   所以健康判準不是「有沒有跑」,是「今天的產出跟昨天是不是同一份」。
#
# 用法: bash scripts/kol_chain_health.sh
# 退出碼: 0=全部有新鮮產出 / 1=至少一條在重播或過期(細節看輸出)

set -uo pipefail

IOS="${INVESTMENT_OS_ROOT:-$HOME/investment-os}"
LOGDIR="${CLAUDE_LOGS:-$HOME/.claude/logs}"
TODAY=$(date +%Y-%m-%d)
RC=0

age_days () {  # $1=檔案路徑 -> 印出「距今幾天」
  if [ ! -e "$1" ]; then echo "-"; return; fi
  local m now
  m=$(stat -f %m "$1" 2>/dev/null) || { echo "-"; return; }
  now=$(date +%s)
  echo $(( (now - m) / 86400 ))
}

newest_in () {  # $1=目錄 $2=glob pattern -> 印出最新檔路徑
  find "$1" -maxdepth 1 -name "$2" -type f 2>/dev/null | sort | tail -1
}

echo "== 每日財經吸收鏈健康檢查 ($TODAY) =="
echo "investment-os: $IOS"
if [ ! -d "$IOS" ]; then
  echo "✗ 找不到 investment-os,以下全部無效"
  exit 1
fi
echo

# ── 1. FB 實際抓取 ────────────────────────────────────────────────
echo "--- 1. FB 實際抓取(normalized 產出)"
FBN="$IOS/fb_kol_intel/normalized"
if [ -d "$FBN" ]; then
  latest=$(find "$FBN" -type f -name '*.json' 2>/dev/null | sort | tail -1)
  if [ -n "$latest" ]; then
    d=$(age_days "$latest")
    echo "  最新:$(basename "$latest")(距今 ${d} 天)"
    if [ "$d" != "-" ] && [ "$d" -gt 2 ]; then
      echo "  ✗ 超過 2 天沒有新的 FB 抓取產出 = 這條鏈實質停擺"
      RC=1
    fi
  else
    echo "  ✗ 目錄存在但沒有任何產出檔"
    RC=1
  fi
else
  echo "  ✗ 找不到 $FBN"
  RC=1
fi
echo

# ── 2. 抓「假裝活著」:同一份 payload 重播 ──────────────────────────
echo "--- 2. fb-shadow-refresh 是不是在重播舊 corpus"
SHLOG="$LOGDIR/fb-shadow-refresh.log"
if [ -f "$SHLOG" ]; then
  # 取最後 30 筆含 draft_tasks 的 payload,看有幾種不同的內容
  distinct=$(grep -o '{"draft_tasks".*}' "$SHLOG" 2>/dev/null | tail -30 | sort -u | wc -l | tr -d ' ')
  total=$(grep -c -o '{"draft_tasks".*}' "$SHLOG" 2>/dev/null | tr -d ' ')
  echo "  近 30 次執行的 payload 種類數:${distinct}(全檔執行次數 ${total})"
  if [ "${distinct:-0}" -le 1 ]; then
    echo "  ✗ 每次 payload 逐字相同 = 在重播同一份舊 corpus,不是今天的資料"
    echo "    T-IOS-KOL-001:「不得用舊 corpus 假裝今日報告」——這條正在被自家排程違反"
    RC=1
  fi
else
  echo "  (查無 $SHLOG,略過)"
fi
echo

# ── 3. 蛛網新鮮度 ────────────────────────────────────────────────
echo "--- 3. 蛛網 state/spiderweb_*.md"
SW=$(newest_in "$IOS/state" 'spiderweb_*.md')
if [ -n "$SW" ]; then
  d=$(age_days "$SW")
  n=$(find "$IOS/state" -maxdepth 1 -name 'spiderweb_*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  最新:$(basename "$SW")(距今 ${d} 天);歷來總份數:${n}"
  if [ "$d" != "-" ] && [ "$d" -gt 1 ]; then
    echo "  ✗ 蛛網不是每日產出"
    RC=1
  fi
else
  echo "  ✗ 一份都沒有"
  RC=1
fi
echo

# ── 4. KOL leaderboard 新鮮度自評 ────────────────────────────────
echo "--- 4. KOL leaderboard 自評健康度"
LB="$IOS/reports/kol_intel/leaderboards/kol_leaderboard_freshness_latest.json"
if [ -f "$LB" ]; then
  grep -o '"status"[^,]*' "$LB" | head -1 | sed 's/^/  /'
  grep -o '"recommendation_extraction_as_of"[^,]*' "$LB" | head -1 | sed 's/^/  /'
  grep -o '"recommendation_extraction_lag_days"[^,}]*' "$LB" | head -1 | sed 's/^/  /'
  if grep -q '"status": *"unhealthy"' "$LB"; then
    echo "  ✗ 自評 unhealthy"
    RC=1
  fi
else
  echo "  (查無 $LB)"
fi
echo

# ── 5. KOL 逐字稿路由:有檔不等於有內容 ──────────────────────────
echo "--- 5. KOL 逐字稿路由(有檔 vs 有內容)"
RT="$IOS/reports/kol_intel/daily_analysis"
if [ -d "$RT" ]; then
  latest=$(find "$RT" -maxdepth 1 -name 'kol_transcript_routing_*.md' -type f 2>/dev/null | sort | tail -1)
  if [ -n "$latest" ]; then
    echo "  最新:$(basename "$latest")"
    if grep -q '今日無 completed transcript' "$latest" 2>/dev/null; then
      echo "  ✗ 檔案天天有,內容天天空(今日無 completed transcript)= 有檔不等於有料"
      RC=1
    fi
  fi
fi
echo

if [ "$RC" = "0" ]; then
  echo "== 結論:鏈上各段都有新鮮產出 =="
else
  echo "== 結論:至少一段在重播或已過期,上面標 ✗ 的就是斷點 =="
fi
exit $RC
