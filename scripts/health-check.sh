#!/bin/bash
# MAPLAB Health Check — A1 啟動時第一步執行
# 顯示所有服務真實狀態，不靠文件猜

REPO="/Users/pagemacmini/maplab-ai-handbook"

echo "============================================"
echo "  MAPLAB HEALTH CHECK — $(date '+%Y-%m-%d %H:%M')"
echo "============================================"

# ── 1. LaunchAgents ──────────────────────────────
echo ""
echo "【LaunchAgents 狀態】"
printf "%-35s %-8s %s\n" "服務名稱" "PID" "狀態"
printf "%-35s %-8s %s\n" "---" "---" "---"

while IFS=$'\t' read -r pid status label; do
  if [[ "$label" != *maplab* ]]; then continue; fi
  if [[ "$pid" == "-" ]]; then
    printf "%-35s %-8s %s\n" "$label" "-" "❌ 未執行 (exit $status)"
  else
    printf "%-35s %-8s %s\n" "$label" "$pid" "✅ 執行中"
  fi
done < <(launchctl list | grep maplab)

# ── 2. Bot 進程 ───────────────────────────────────
echo ""
echo "【Bot 進程 (ps)】"
BOTS=$(ps aux | grep -E "bot\.py|bot_a6" | grep -v grep)
if [[ -z "$BOTS" ]]; then
  echo "  ⚠️  沒有偵測到 bot 進程"
else
  echo "$BOTS" | awk '{print "  PID " $2 " → " $11 " " $12}'
fi

# ── 3. .env 存在檢查 ──────────────────────────────
echo ""
echo "【.env 存在檢查】"
for f in "$REPO/bot/.env" "$REPO/bot_a6/.env"; do
  if [[ -f "$f" ]]; then
    echo "  ✅ $f"
  else
    echo "  ❌ 缺少 $f"
  fi
done

# ── 4. Colab / A4 最後進度 ────────────────────────
echo ""
echo "【A4 最後進度 (git log)】"
cd "$REPO" && git log --oneline --all | grep -iE "A4|S11|S12|S13|照片" | head -5 | sed 's/^/  /'

# ── 5. Worktree 概況 ──────────────────────────────
echo ""
echo "【Worktree 概況】"
WT_COUNT=$(git worktree list | wc -l | tr -d ' ')
echo "  總數：$WT_COUNT 個 worktree"
DIRTY=$(git worktree list --porcelain | grep -c "^worktree" || true)
echo "  (含主 repo)"

# ── 6. 各 Agent 狀態（最後 checkpoint）────────────
echo ""
echo "【各 Agent 最後 Checkpoint】"
for agent in A0 A1 A2 A3 A4 A5 A6 A7; do
  last=$(git log --oneline --all --grep="$agent" | head -1)
  if [[ -n "$last" ]]; then
    echo "  $agent: $last"
  else
    echo "  $agent: (無紀錄)"
  fi
done

echo ""
echo "============================================"
echo "  Health Check 完成"
echo "============================================"
