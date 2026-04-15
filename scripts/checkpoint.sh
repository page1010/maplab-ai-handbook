#!/bin/bash
# checkpoint.sh — 一鍵存檔
# 預設：commit 到 agent branch，等 Owner 執行 approve.sh 才進 main
# 加 --fast：直接 push 到 main（信任模式，適合 A1 本身操作）
#
# 用法：
#   bash scripts/checkpoint.sh "角色名" "做了什麼"           # 預設 branch 模式
#   bash scripts/checkpoint.sh "角色名" "做了什麼" --fast    # 直接進 main
#
# 例如：
#   bash scripts/checkpoint.sh "A5" "修正 QUOTE_DRAFT 公式"
#   bash scripts/checkpoint.sh "A1" "更新 CURRENT_STATUS" --fast

ROLE="${1:-}"
MESSAGE="${2:-}"
FAST_MODE=false
REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"
TASKS_DIR="$REPO_ROOT/handoff/tasks"

# === 自動更新 Task Card「最後活動」欄位 ===
_inject_status_block() {
  # 對缺接續狀態區塊的 Task Card 補上空白模板
  local card="$1"
  local today=$(date +%Y-%m-%d)

  # 已有接續狀態區塊 → 跳過
  grep -q '^\- \*\*狀態\*\*' "$card" && return 1

  # 在第一個 --- 或 ## 之後插入（跳過標題行）
  # 找到第一個非標題、非空行的位置，在檔案開頭的標題後插入
  local tmp="${card}.tmp"
  local inserted=false

  while IFS= read -r line; do
    echo "$line" >> "$tmp"
    # 在第一個 # 標題行之後插入
    if [[ "$inserted" == false ]] && echo "$line" | grep -q '^# '; then
      inserted=true
      cat >> "$tmp" << BLOCK

## 接續狀態
- **狀態**: 🔄 進行中
- **最後活動**: ${today}
- **接續點**: （checkpoint.sh 自動補建，請 agent 填寫）
- **阻塞**: 無
BLOCK
    fi
  done < "$card"

  if [[ "$inserted" == true ]]; then
    mv "$tmp" "$card"
    return 0
  else
    rm -f "$tmp"
    return 1
  fi
}

_update_task_cards() {
  local role="$1"
  local short_hash="$2"
  local today=$(date +%Y-%m-%d)
  local updated=0
  local injected=0

  # 找該角色的進行中 (🔄) 或任何 Task Card
  for card in "$TASKS_DIR"/T-${role}-*.md "$TASKS_DIR"/T-${role}[A-Z]*-*.md; do
    [ -f "$card" ] || continue

    # 偵測缺接續區塊 → 自動補上
    if ! grep -q '^\- \*\*最後活動\*\*' "$card"; then
      if _inject_status_block "$card"; then
        injected=$((injected + 1))
        echo "🔧 Task Card 自動補建接續區塊：$(basename "$card")"
      fi
    fi

    if grep -q '🔄 進行中' "$card"; then
      # 更新「最後活動」行
      if grep -q '^\- \*\*最後活動\*\*' "$card"; then
        sed -i '' "s/^- \*\*最後活動\*\*:.*/- **最後活動**: ${today} ${short_hash}/" "$card"
        updated=$((updated + 1))
        echo "📝 Task Card 更新：$(basename "$card") → 最後活動 ${today} ${short_hash}"
      fi
    fi
  done

  if [ "$injected" -gt 0 ]; then
    echo ""
    echo "⚠️  ${injected} 張 Task Card 缺接續區塊，已自動補建。請檢查內容是否正確。"
  fi

  if [ "$updated" -gt 0 ]; then
    echo ""
    echo "⚠️  Task Card「最後活動」已更新（本地）。下次 checkpoint 會一起提交。"
    echo "⚠️  請同時更新 Task Card 的「接續點」欄位（做到哪、下一步做什麼）。"
  elif [ "$injected" -eq 0 ]; then
    echo "ℹ️  未找到 ${role} 的 🔄 進行中 Task Card，跳過自動更新。"
  fi
}

# Parse --fast flag（位置不限）
for arg in "$@"; do
  [ "$arg" = "--fast" ] && FAST_MODE=true
done

if [ -z "$ROLE" ] || [ -z "$MESSAGE" ]; then
  echo "❌ 用法：bash scripts/checkpoint.sh \"角色名\" \"做了什麼\" [--fast]"
  echo "   角色名：A0 / A1 / A2 / A4 / A5 / A6 / A7 / A8"
  exit 1
fi

COMMIT_MSG="checkpoint($ROLE): $MESSAGE"
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
TODAY=$(date +%Y%m%d)
AGENT_BRANCH="agent/$ROLE-$TODAY"

echo "======================================"
echo "🔄 CHECKPOINT 存檔流程啟動"
echo "   角色：$ROLE"
echo "   訊息：$MESSAGE"
if [ "$FAST_MODE" = true ]; then
  echo "   模式：⚡ --fast（直接進 main）"
else
  echo "   模式：🔒 branch 模式（需 Owner approve 才進 main）"
fi
echo "======================================"
echo ""

# 確認有沒有變更
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  echo "ℹ️  沒有需要存檔的變更，跳過。"
  exit 0
fi

echo "📋 變更清單："
git status --short
echo ""

# ============================================================
# FAST MODE：直接 commit → cherry-pick 到 main → push（原有行為）
# ============================================================
if [ "$FAST_MODE" = true ]; then

  echo "📁 [1/4] 暫存所有變更..."
  git add -A && echo "       ✅ 完成" || { echo "❌ git add 失敗"; exit 1; }

  echo "💾 [2/4] Commit..."
  git commit -m "$COMMIT_MSG" || { echo "❌ git commit 失敗"; exit 1; }
  HASH=$(git rev-parse HEAD)
  SHORT="${HASH:0:7}"
  echo "       ✅ $SHORT — $COMMIT_MSG"
  echo ""

  if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🍒 [3/4] Cherry-pick 到 main..."
    cd "$REPO_ROOT"
    [ "$(git branch --show-current)" != "main" ] && git checkout main
    if git cherry-pick "$HASH"; then
      echo "       ✅ Cherry-pick 完成"
    else
      echo "⚠️  發現衝突，嘗試自動解（theirs 策略）..."
      git checkout --theirs . 2>/dev/null || true
      git add -A
      if git cherry-pick --continue --no-edit; then
        echo "       ✅ 衝突已自動解決"
      else
        echo "❌ Cherry-pick 失敗，請手動處理"
        git cherry-pick --abort 2>/dev/null || true
        exit 1
      fi
    fi
  else
    echo "⏭️  [3/4] 已在 main branch，跳過 cherry-pick"
    cd "$REPO_ROOT"
  fi

  echo "🚀 [4/4] Push main 到 remote..."
  if git push origin main; then
    echo "       ✅ Push 完成"
  else
    echo "⚠️  Push 失敗，嘗試 pull --rebase..."
    if git pull --rebase origin main && git push origin main; then
      echo "       ✅ Push 完成（rebase 後）"
    else
      echo "❌ Push 失敗，請手動處理"
      exit 1
    fi
  fi

  cd "$WORKTREE_DIR"

  echo ""
  echo "🔍 驗證 main 是否包含此次 commit..."
  bash "$WORKTREE_DIR/scripts/verify-commit-on-main.sh" "$HASH"

  # === 自動更新 Task Card 最後活動 ===
  _update_task_cards "$ROLE" "$SHORT"

  echo ""
  echo "======================================"
  echo "✅ 存檔完成（fast mode）"
  echo "   Commit: $SHORT"
  echo "   main 已同步到 remote。"
  echo "======================================"

# ============================================================
# 預設模式：commit 到 agent branch，push branch，等 Owner approve
# ============================================================
else

  # 如果在 main，切換到 agent branch（uncommitted changes 會跟過去）
  if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "🌿 [1/3] 切換到 agent branch: $AGENT_BRANCH"
    if git checkout -b "$AGENT_BRANCH" 2>/dev/null || git checkout "$AGENT_BRANCH" 2>/dev/null; then
      echo "       ✅ 完成"
    else
      echo "❌ 無法切換到 $AGENT_BRANCH"
      exit 1
    fi
  else
    # 已在 agent branch 或其他 branch，直接用
    AGENT_BRANCH="$CURRENT_BRANCH"
    echo "🌿 [1/3] 使用現有 branch: $AGENT_BRANCH"
  fi

  echo "💾 [2/3] 暫存 + Commit..."
  git add -A && git commit -m "$COMMIT_MSG" || { echo "❌ commit 失敗"; exit 1; }
  HASH=$(git rev-parse HEAD)
  SHORT="${HASH:0:7}"
  echo "       ✅ $SHORT — $COMMIT_MSG"
  echo ""

  echo "🚀 [3/3] Push $AGENT_BRANCH 到 remote..."
  if git push origin "$AGENT_BRANCH" 2>/dev/null || git push --set-upstream origin "$AGENT_BRANCH"; then
    echo "       ✅ Push 完成"
  else
    echo "❌ Push 失敗"
    exit 1
  fi

  # === 自動更新 Task Card 最後活動 ===
  _update_task_cards "$ROLE" "$SHORT"

  echo ""
  echo "======================================"
  echo "✅ 存檔完成（branch 模式）"
  echo "   Commit: $SHORT"
  echo "   Branch: $AGENT_BRANCH"
  echo ""
  echo "⚠️  尚未進入 main。Owner 確認後執行："
  echo "   bash scripts/approve.sh $AGENT_BRANCH"
  echo "======================================"
fi
