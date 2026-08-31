#!/usr/bin/env bash
# patrol.sh — 掃描 Task Card 接續狀態，驅動四態狀態機，輸出 Owner 決策佇列
# 用法：bash scripts/patrol.sh
# 整合入口：Telegram bot /patrol 指令
# 四態狀態機：IN_PROGRESS → STALLED(48h) → NEEDS_REVIEW(7d) → AUTO_CLOSED(7d)
# 見 AGENT_RULES.md SECTION 25

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_DIR="$REPO_ROOT/handoff/tasks"

# ── 日期計算 ──
now_ts=$(date +%s)
today=$(date '+%Y-%m-%d')

days_since() {
  local date_str="$1"
  # 接受 YYYY-MM-DD 格式
  local then_ts
  then_ts=$(date -j -f "%Y-%m-%d" "$date_str" +%s 2>/dev/null || echo 0)
  if [[ "$then_ts" == "0" ]]; then
    echo "?"
    return
  fi
  echo $(( (now_ts - then_ts) / 86400 ))
}

# ── 四態狀態機：寫回 Task Card 狀態欄位（可逆，SECTION 24）──
update_task_state() {
  local card="$1"
  local new_state="$2"
  local since_date="$3"
  local state_field=""

  case "$new_state" in
    STALLED)
      state_field="🟡 STALLED（since ${since_date}，48h 無 commit，Owner 可更新最後活動解除）"
      ;;
    NEEDS_REVIEW)
      state_field="🔍 NEEDS_REVIEW（since ${since_date}，停滯逾 7 天，Owner 決策急需或回覆「重開 $(basename "$card" .md)」）"
      ;;
    AUTO_CLOSED)
      state_field="🔒 AUTO_CLOSED（${since_date}，NEEDS_REVIEW 無回應逾 7 天，Owner 可回覆「重開 $(basename "$card" .md)」重啟）"
      ;;
  esac

  # macOS 相容：sed -i ''
  sed -i '' "s|^- \*\*狀態\*\*:.*|- **狀態**: ${state_field}|" "$card" 2>/dev/null || \
  sed -i "s|^- \*\*狀態\*\*:.*|- **狀態**: ${state_field}|" "$card"
}

# ── 四態狀態機：偵測並執行狀態遷移 ──
# 回傳：0=有遷移發生，1=無遷移
drive_state_transition() {
  local card="$1"
  local status="$2"
  local days_ago="$3"

  # IN_PROGRESS → STALLED（最後活動 ≥ 2 天）
  if echo "$status" | grep -q '🔄\|IN_PROGRESS\|進行中'; then
    if [[ "$days_ago" != "?" ]] && [[ "$days_ago" -ge 2 ]]; then
      update_task_state "$card" "STALLED" "$today"
      transitions+=("  🔄→🟡 STALLED: $(basename "$card" .md)（最後活動 ${days_ago}d 前）")
      return 0
    fi
  fi

  # STALLED → NEEDS_REVIEW（在 STALLED 狀態 ≥ 7 天）
  if echo "$status" | grep -q '🟡 STALLED'; then
    local stalled_since
    stalled_since=$(echo "$status" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1 || echo "")
    if [[ -n "$stalled_since" ]]; then
      local stalled_days
      stalled_days=$(days_since "$stalled_since")
      if [[ "$stalled_days" != "?" ]] && [[ "$stalled_days" -ge 7 ]]; then
        update_task_state "$card" "NEEDS_REVIEW" "$today"
        transitions+=("  🟡→🔍 NEEDS_REVIEW: $(basename "$card" .md)（停滯 ${stalled_days} 天）")
        return 0
      fi
    fi
  fi

  # NEEDS_REVIEW → AUTO_CLOSED（在 NEEDS_REVIEW 狀態 ≥ 7 天）
  if echo "$status" | grep -q '🔍 NEEDS_REVIEW'; then
    local review_since
    review_since=$(echo "$status" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1 || echo "")
    if [[ -n "$review_since" ]]; then
      local review_days
      review_days=$(days_since "$review_since")
      if [[ "$review_days" != "?" ]] && [[ "$review_days" -ge 7 ]]; then
        update_task_state "$card" "AUTO_CLOSED" "$today"
        transitions+=("  🔍→🔒 AUTO_CLOSED: $(basename "$card" .md)（NEEDS_REVIEW 逾 ${review_days} 天）")
        return 0
      fi
    fi
  fi

  return 1
}

# ── 掃描所有 Task Card ──
declare -a owner_actions=()
declare -a blocked=()
declare -a active=()
declare -a paused=()
declare -a done_tasks=()
declare -a auto_closed=()
declare -a transitions=()

for card in "$TASKS_DIR"/T-*.md; do
  [[ -f "$card" ]] || continue
  filename=$(basename "$card" .md)

  # 提取接續狀態區塊的關鍵欄位
  status=$(grep -m1 '^\- \*\*狀態\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "未標記")
  last_activity=$(grep -m1 '^\- \*\*最後活動\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "未知")
  next_step=$(grep -m1 '^\- \*\*接續點\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "")
  blocker=$(grep -m1 '^\- \*\*阻塞\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "無")

  # 提取日期（取前 10 字元 YYYY-MM-DD）
  activity_date=$(echo "$last_activity" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1 || echo "")
  if [[ -n "$activity_date" ]]; then
    days_ago=$(days_since "$activity_date")
    age_label="${days_ago}d ago"
  else
    days_ago="?"
    age_label="日期不明"
  fi

  # 提取 agent 代號（從檔名 T-A5-002 → A5）
  agent=$(echo "$filename" | grep -oE 'A[0-9]+' | head -1 || echo "??")

  # ── 四態狀態機：先嘗試驅動狀態遷移（SECTION 25）──
  # 只對 IN_PROGRESS / STALLED / NEEDS_REVIEW 執行（BLOCKED / DONE / FROZEN 略過）
  if echo "$status" | grep -qv '✅\|⏸️\|阻塞\|⏳\|💤\|暫停\|🔲\|待開始\|🔒'; then
    if drive_state_transition "$card" "$status" "$days_ago"; then
      # 遷移後重新讀取狀態
      status=$(grep -m1 '^\- \*\*狀態\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "未標記")
    fi
  fi

  # ── 分類（基於最新狀態）──
  if echo "$status" | grep -q '✅'; then
    done_tasks+=("  ✅ $filename ($agent): 已完成")
  elif echo "$status" | grep -q '🔒 AUTO_CLOSED'; then
    auto_closed+=("  🔒 $filename ($agent): 自動關閉（Owner 可回覆「重開 $filename」重啟）")
  elif echo "$status" | grep -q '🔍 NEEDS_REVIEW'; then
    blocked+=("  🔍 $filename ($agent): NEEDS_REVIEW — $blocker [$age_label]")
    owner_actions+=("  → $filename [NEEDS_REVIEW]: $blocker（停滯逾 7 天，需 Owner 決策）")
  elif echo "$status" | grep -q '🟡 STALLED'; then
    active+=("  🟡 $filename ($agent): STALLED — ${next_step:0:60} [$age_label]")
  elif echo "$status" | grep -q '⏸️\|阻塞\|⏳'; then
    # ⏳ = 等外部條件（等同 ⏸️ 阻塞，不走 AUTO_CLOSE）
    blocked+=("  ⏸️ $filename ($agent): $blocker [$age_label]")
    if echo "$blocker" | grep -qi 'Owner'; then
      owner_actions+=("  → $filename: $blocker")
    fi
  elif echo "$status" | grep -q '💤\|暫停'; then
    paused+=("  💤 $filename ($agent): 暫停中 [$age_label]")
  elif echo "$status" | grep -q '🔄\|IN_PROGRESS\|進行中'; then
    active+=("  ⏳ $filename ($agent): IN_PROGRESS — ${next_step:0:60} [$age_label]")
  elif echo "$status" | grep -q '🔲\|待開始'; then
    paused+=("  🔲 $filename ($agent): 待開始")
  else
    # 舊格式或未標記 → 顯示但不觸發狀態機
    active+=("  ❓ $filename ($agent): 狀態未標記 [$age_label]")
  fi
done

# ── Log 輪轉 ──
bash "$REPO_ROOT/scripts/rotate-bot-logs.sh" 2>/dev/null | grep -v "nothing to do" || true

# ── Token 過期偵測 ──
check_token_expiry() {
    local TOKEN_FILE="$HOME/.claude/mcp-keys/google-token.json"
    if [ ! -f "$TOKEN_FILE" ]; then
        echo "⚠️ Google token file not found: $TOKEN_FILE"
        return
    fi

    local EXPIRY
    EXPIRY=$(python3 -c "
import json
from datetime import datetime, timezone
d = json.load(open('$TOKEN_FILE'))
expiry_str = d.get('expiry', '')
if expiry_str:
    expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    hours_left = (expiry - now).total_seconds() / 3600
    if hours_left < 0:
        print('EXPIRED')
    elif hours_left < 6:
        print(f'WARNING:{hours_left:.1f}h')
    else:
        print(f'OK:{hours_left:.1f}h')
else:
    print('NO_EXPIRY')
" 2>/dev/null || echo "ERROR")

    case "$EXPIRY" in
        EXPIRED|WARNING:*)
            local label="🔴 EXPIRED"
            [[ "$EXPIRY" == WARNING:* ]] && label="🟡 expires in ${EXPIRY#WARNING:}"
            echo "[$label] Google OAuth token — auto-refreshing..."
            python3 - "$TOKEN_FILE" << 'PYEOF' 2>&1 || echo "⛔ Token refresh failed — invalid_grant: refresh token 已失效，需重新授權 (Owner 執行 OAuth flow)"
import sys, json, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
TOKEN_PATH = sys.argv[1]
d = json.load(open(TOKEN_PATH))
data = urllib.parse.urlencode({
    'client_id': d['client_id'],
    'client_secret': d['client_secret'],
    'refresh_token': d['refresh_token'],
    'grant_type': 'refresh_token'
}).encode()
req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
try:
    resp = urllib.request.urlopen(req)
    new = json.loads(resp.read())
    d['token'] = new['access_token']
    d['expiry'] = (datetime.now(timezone.utc) + timedelta(seconds=new['expires_in'])).isoformat()
    json.dump(d, open(TOKEN_PATH, 'w'), indent=2)
    print(f'✅ Token refreshed, new expiry: {d["expiry"]}')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    sys.exit(f'HTTP {e.code}: {body}')
PYEOF
            ;;
        OK:*)
            echo "🟢 Google OAuth token OK (${EXPIRY#OK:} remaining)"
            ;;
        NO_EXPIRY)
            echo "⚠️ Google token: no expiry field found"
            ;;
        *)
            echo "⚠️ Google token check error: $EXPIRY"
            ;;
    esac
}

# ── 輸出 ──
echo "=== MAPLAB 系統巡查 $(date '+%Y-%m-%d %H:%M') ==="
echo ""

# ── 📌 TL;DR 行動摘要（Owner 2026-07-07 回饋：報告要能一眼行動）──
# 純新增；只讀既有陣列，不改下方任何區塊。完整清單見本摘要之後。
echo "📌 【今天你要做的】"
if [[ ${#owner_actions[@]} -gt 0 ]]; then
  i=0
  for entry in "${owner_actions[@]}"; do
    i=$((i+1)); [[ $i -gt 3 ]] && break
    # 相容兩種格式：「  → filename: blocker」與「days|filename|blocker」
    if [[ "$entry" == *"|"* && "$entry" != *"→"* ]]; then
      IFS='|' read -r _d _f _b <<< "$entry"; echo "  ${i}. ${_f}：${_b}"
    else
      echo "  ${i}. ${entry#  → }"
    fi
  done
  [[ ${#owner_actions[@]} -gt 3 ]] && echo "  …另有 $(( ${#owner_actions[@]} - 3 )) 件（見下方【Owner 行動項】）"
else
  echo "  ✅ 無待你決策事項"
fi
echo "  ─ 統計：進行中 ${#active[@]}｜阻塞 ${#blocked[@]}｜暫停/待開始 ${#paused[@]}｜完成 ${#done_tasks[@]}｜本輪狀態遷移 ${#transitions[@]}"
echo ""

# Token 檢查
check_token_expiry
echo ""

# 狀態遷移報告（本輪 patrol 自動執行的狀態機推進）
if [[ ${#transitions[@]} -gt 0 ]]; then
  echo "【⚡ 本輪狀態遷移（四態狀態機，SECTION 25）】"
  printf '%s\n' "${transitions[@]}"
  echo "  → 已自動寫回 Task Card，無需 Owner 操作（可逆，SECTION 24）"
  echo ""
fi

if [[ ${#owner_actions[@]} -gt 0 ]]; then
  echo "【Owner 行動項】"
  printf '%s\n' "${owner_actions[@]}"
  echo ""
fi

if [[ ${#blocked[@]} -gt 0 ]]; then
  echo "【阻塞中 — 等外部條件（⏸️/⏳/🔍）】"
  printf '%s\n' "${blocked[@]}"
  echo ""
fi

if [[ ${#active[@]} -gt 0 ]]; then
  echo "【進行中（🔄 IN_PROGRESS / 🟡 STALLED）】"
  printf '%s\n' "${active[@]}"
  echo ""
fi

if [[ ${#paused[@]} -gt 0 ]]; then
  echo "【暫停/待開始】"
  printf '%s\n' "${paused[@]}"
  echo ""
fi

if [[ ${#auto_closed[@]} -gt 0 ]]; then
  echo "【自動關閉（🔒 AUTO_CLOSED — Owner 可回覆「重開 T-XXX」重啟）】"
  printf '%s\n' "${auto_closed[@]}"
  echo ""
fi

echo "【已完成】${#done_tasks[@]} 張 Task Card"
if [[ ${#done_tasks[@]} -le 5 ]]; then
  printf '%s\n' "${done_tasks[@]}"
else
  # 2026-07-08：超過 5 張時，改列「最近修改的 3 張」而非整批消音，
  # 避免多步驟派工完成後被算進總數但從沒被點名過（見 AGENT_RULES.md SECTION 20）。
  echo "  （最近異動 3 張，其餘見 handoff/tasks/）"
  ls -t "$TASKS_DIR"/T-*.md 2>/dev/null | while read -r card; do
    filename=$(basename "$card" .md)
    status=$(grep -m1 '^\- \*\*狀態\*\*' "$card" 2>/dev/null | sed 's/.*\*\*: //' || echo "")
    echo "$status" | grep -q '✅' && echo "  ✅ $filename"
  done | head -3 || true
fi

# ── Investment OS nightwatch 自健檢 + IS-HS 健康分數 ──
NIGHTWATCH_LATEST="$HOME/.local/share/investmentos-telegram-operator/reports/nightwatch/nightwatch_$(date '+%Y-%m-%d').md"
ESCALATION_QUEUE="$HOME/Documents/New project/state/runtime_escalation_queue.jsonl"
IS_HS_LOG="$HOME/maplab-ai-handbook/state/is_health_trend.jsonl"
echo ""
echo "【投資 OS 守夜人 + IS-HS】"

# nightwatch 新鮮度檢查
if [[ -f "$NIGHTWATCH_LATEST" ]]; then
  ALERTS=$(grep '🔴 需要處理' -A 99 "$NIGHTWATCH_LATEST" 2>/dev/null | tail -n +2 | head -5 || true)
  if [[ -n "$ALERTS" && "$ALERTS" != "---" ]]; then
    echo "  🔴 nightwatch 今日有警示："
    echo "$ALERTS" | sed 's/^/    /'
    FRESH_SCORE=50
  else
    echo "  🟢 nightwatch 今日正常（0 警示）"
    FRESH_SCORE=100
  fi
else
  echo "  🔴 nightwatch 今日報告缺失 → 請檢查 launchctl list | grep nightwatch"
  FRESH_SCORE=0
fi

# escalation_queue 逾期警報檢查
if [[ -f "$ESCALATION_QUEUE" ]]; then
  TODAY=$(date '+%Y-%m-%d')
  OPEN_COUNT=$(python3 -c "
import json, sys
q=open('$ESCALATION_QUEUE')
count=0
for line in q:
    try:
        r=json.loads(line.strip())
        if r.get('status')=='open' and not r.get('escalated',False):
            count+=1
    except: pass
print(count)
" 2>/dev/null || echo "?")
  if [[ "$OPEN_COUNT" != "0" && "$OPEN_COUNT" != "?" ]]; then
    echo "  🔴 escalation_queue: ${OPEN_COUNT} 條 open+未推播（見 projects/investment-os-continuous-iteration-plan.md ④）"
    ESCAL_SCORE=0
  else
    echo "  🟢 escalation_queue: 無逾期未推警報"
    ESCAL_SCORE=100
  fi
else
  echo "  ⚪ escalation_queue 路徑不可讀"
  ESCAL_SCORE=50
fi

# IS-HS 計算（簡化版：資料新鮮度 50% + 警報通暢度 50%）
IS_HS=$(( (FRESH_SCORE + ESCAL_SCORE) / 2 ))
if [[ $IS_HS -ge 70 ]]; then
  HS_LABEL="🟢"
elif [[ $IS_HS -ge 40 ]]; then
  HS_LABEL="🟡"
else
  HS_LABEL="🔴"
fi
echo "  ${HS_LABEL} IS-HS: ${IS_HS}/100（新鮮度=${FRESH_SCORE}% 警報通暢度=${ESCAL_SCORE}%）"

# 記錄趨勢
if [[ -n "$IS_HS_LOG" ]]; then
  echo "{\"date\":\"$(date '+%Y-%m-%d %H:%M')\",\"is_hs\":${IS_HS},\"freshness\":${FRESH_SCORE},\"escalation\":${ESCAL_SCORE}}" >> "$IS_HS_LOG" 2>/dev/null || true
fi

# ── B3 廣告觀察（Owner 2026-07-18 裁決 A：自己去 Meta 建受眾包）──
echo ""
echo "【B3 廣告觀察】"
B3_SIGNAL_FILE="$REPO_ROOT/state/b3_ads_signal.log"
# 偵測方式：(1) Owner 主動回報 → 寫入 b3_ads_signal.log  (2) GA4/UTM 有 b3 流量
if [[ -f "$B3_SIGNAL_FILE" ]]; then
  LAST_B3=$(tail -1 "$B3_SIGNAL_FILE" 2>/dev/null || echo "")
  if [[ -n "$LAST_B3" ]]; then
    echo "  🟢 B3 廣告已啟動訊號偵測到："
    echo "     $LAST_B3"
    echo "  → 已觸發每日成效摘要模式（花費/曝光/點擊/詢價 UTM 進例會）"
    echo "  → 每日成效追蹤：bash scripts/b3_ads_daily_summary.sh"
  fi
else
  echo "  ⚪ B3 廣告尚未啟動（Owner 去 Meta 建受眾包後，回報一句話或 UTM 有 b3 流量自動偵測）"
  echo "  → 啟動後：回報「B3 開始跑了」或 GA4 出現 utm_source=meta_b3 流量"
  echo "  → A1 偵測到後自動開始每日成效摘要並進例會"
fi
