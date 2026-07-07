#!/usr/bin/env bash
# patrol.sh — 掃描 Task Card 接續狀態，輸出 Owner 決策佇列
# 用法：bash scripts/patrol.sh            → Owner 摘要版（預設；最多 3 件行動項 + 一行統計）
#       bash scripts/patrol.sh --full     → 完整清單（原始格式，給 A1/工程用）
# 設計原則（2026-07-07 Owner feedback）：報告要能行動，不要清單轟炸；
# 與上次巡查相同且無 Owner 行動項 → 一行帶過。
# 整合入口：Telegram bot /patrol 指令

set -euo pipefail
FULL_MODE=0
[[ "${1:-}" == "--full" ]] && FULL_MODE=1
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_DIR="$REPO_ROOT/handoff/tasks"

# ── 日期計算 ──
now_ts=$(date +%s)

days_since() {
  local date_str="$1"
  # 接受 YYYY-MM-DD 格式
  local then_ts
  then_ts=$(date -j -f "%Y-%m-%d" "$date_str" +%s 2>/dev/null || date -d "$date_str" +%s 2>/dev/null || echo 0)
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
    # 阻塞中有 Owner 字樣 → 加入 Owner 行動項（前綴天數供排序，? 視為 -1 排最後）
    if echo "$blocker" | grep -qi 'Owner'; then
      sort_days="$days_ago"; [[ "$sort_days" == "?" ]] && sort_days=-1
      owner_actions+=("${sort_days}|$filename|$blocker")
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

# ── Owner 行動項排序（卡最久的在前）──
declare -a owner_sorted=()
if [[ ${#owner_actions[@]} -gt 0 ]]; then
  while IFS= read -r line; do owner_sorted+=("$line"); done < <(printf '%s\n' "${owner_actions[@]}" | sort -t'|' -k1,1nr)
fi

# 進行中超過 48h 的數量
stale_count=0
for a in ${active[@]+"${active[@]}"}; do
  [[ "$a" == *"⚠️"* ]] && stale_count=$((stale_count+1))
done

# Token 狀態（只在異常時進摘要；OK 就沉默）
token_line=$(check_token_expiry)
token_alert=""
echo "$token_line" | grep -qE "🔴|🟡|⚠️|⛔" && token_alert="$token_line"

# ── 完整模式（原始格式，工程用）──
if [[ "$FULL_MODE" == "1" ]]; then
  echo "=== MAPLAB 系統巡查（完整）$(date '+%Y-%m-%d %H:%M') ==="
  echo ""
  echo "$token_line"
  echo ""
  if [[ ${#owner_sorted[@]} -gt 0 ]]; then
    echo "【Owner 行動項】"
    for entry in "${owner_sorted[@]}"; do
      IFS='|' read -r d f b <<< "$entry"
      echo "  → $f: $b [${d}d]"
    done
    echo ""
  fi
  [[ ${#blocked[@]} -gt 0 ]] && { echo "【阻塞中 — 等外部條件】"; printf '%s\n' "${blocked[@]}"; echo ""; }
  [[ ${#active[@]} -gt 0 ]] && { echo "【進行中】"; printf '%s\n' "${active[@]}"; echo ""; }
  [[ ${#paused[@]} -gt 0 ]] && { echo "【暫停/待開始】"; printf '%s\n' "${paused[@]}"; echo ""; }
  echo "【已完成】${#done_tasks[@]} 張 Task Card"
  [[ ${#done_tasks[@]} -le 5 ]] && printf '%s\n' ${done_tasks[@]+"${done_tasks[@]}"}
  exit 0
fi

# ── 摘要模式（預設，Owner 看的）──
SUMMARY=""

if [[ -n "$token_alert" ]]; then
  SUMMARY+="$token_alert"$'\n\n'
fi

if [[ ${#owner_sorted[@]} -gt 0 ]]; then
  SUMMARY+="【今天只需要你做這幾件】"$'\n'
  i=0
  for entry in "${owner_sorted[@]}"; do
    i=$((i+1)); [[ $i -gt 3 ]] && break
    IFS='|' read -r d f b <<< "$entry"
    age=""; [[ "$d" != "-1" ]] && age="（卡 ${d} 天）"
    SUMMARY+="  ${i}. ${f}${age}：${b}"$'\n'
  done
  extra=$(( ${#owner_sorted[@]} - 3 ))
  [[ $extra -gt 0 ]] && SUMMARY+="  …另有 ${extra} 件較不急（/patrol full 看全部）"$'\n'
  SUMMARY+=$'\n'
fi

SUMMARY+="其他：進行中 ${#active[@]}（⚠️超48h ${stale_count}）｜阻塞 ${#blocked[@]}｜暫停/待開始 ${#paused[@]}｜完成 ${#done_tasks[@]}"

# ── 去重：跟上次巡查一模一樣且無行動項 → 一行帶過 ──
SNAP_FILE="$HOME/.maplab_patrol_snapshot"
snap_now=$(echo "$SUMMARY" | md5 2>/dev/null || echo "$SUMMARY" | md5sum | cut -d' ' -f1)
snap_prev=$(cat "$SNAP_FILE" 2>/dev/null || echo "")
echo "$snap_now" > "$SNAP_FILE"

echo "=== MAPLAB 巡查 $(date '+%m-%d %H:%M') ==="
if [[ "$snap_now" == "$snap_prev" && ${#owner_sorted[@]} -eq 0 && -z "$token_alert" ]]; then
  echo "✅ all clear，與上次巡查相同，無需你動作。"
elif [[ "$snap_now" == "$snap_prev" ]]; then
  echo "（與上次巡查相同，以下為重複提醒）"
  echo "$SUMMARY"
else
  echo "$SUMMARY"
fi
