#!/usr/bin/env bash
# patrol.sh — 掃描 Task Card 接續狀態，輸出 Owner 決策佇列
# 用法：bash scripts/patrol.sh
# 整合入口：Telegram bot /patrol 指令

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_DIR="$REPO_ROOT/handoff/tasks"

# ── 日期計算 ──
now_ts=$(date +%s)

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

# ── 掃描所有 Task Card ──
declare -a owner_actions=()
declare -a blocked=()
declare -a active=()
declare -a paused=()
declare -a done_tasks=()

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

  # 分類
  if echo "$status" | grep -q '✅'; then
    done_tasks+=("  ✅ $filename ($agent): 已完成")
  elif echo "$status" | grep -q '⏸️\|阻塞'; then
    blocked+=("  ⏸️ $filename ($agent): $blocker [$age_label]")
    # 阻塞中有 Owner 字樣 → 加入 Owner 行動項
    if echo "$blocker" | grep -qi 'Owner'; then
      owner_actions+=("  → $filename: $blocker")
    fi
  elif echo "$status" | grep -q '💤\|暫停'; then
    paused+=("  💤 $filename ($agent): 暫停中 [$age_label]")
  elif echo "$status" | grep -q '🔄\|進行中'; then
    local_status="⏳"
    # 超過 48h 無活動 + 進行中 → 需注意
    if [[ "$days_ago" != "?" ]] && [[ "$days_ago" -ge 2 ]]; then
      local_status="⚠️"
    fi
    active+=("  $local_status $filename ($agent): ${next_step:0:80} [$age_label]")
  elif echo "$status" | grep -q '🔲\|待開始'; then
    paused+=("  🔲 $filename ($agent): 待開始")
  else
    # 沒有接續狀態區塊的舊格式 Task Card
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

# Token 檢查
check_token_expiry
echo ""

if [[ ${#owner_actions[@]} -gt 0 ]]; then
  echo "【Owner 行動項】"
  printf '%s\n' "${owner_actions[@]}"
  echo ""
fi

if [[ ${#blocked[@]} -gt 0 ]]; then
  echo "【阻塞中 — 等外部條件】"
  printf '%s\n' "${blocked[@]}"
  echo ""
fi

if [[ ${#active[@]} -gt 0 ]]; then
  echo "【進行中】"
  printf '%s\n' "${active[@]}"
  echo ""
fi

if [[ ${#paused[@]} -gt 0 ]]; then
  echo "【暫停/待開始】"
  printf '%s\n' "${paused[@]}"
  echo ""
fi

echo "【已完成】${#done_tasks[@]} 張 Task Card"
if [[ ${#done_tasks[@]} -le 5 ]]; then
  printf '%s\n' "${done_tasks[@]}"
fi
