#!/bin/bash
# checkpoint.sh — 一鍵存檔：commit → cherry-pick 到 main → push → 驗證
# 用法：bash scripts/checkpoint.sh "角色名" "做了什麼"
# 例如：bash scripts/checkpoint.sh "A4" "S11 照片分類完成 3000 張"

ROLE="${1:-}"
MESSAGE="${2:-}"
REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"

if [ -z "$ROLE" ] || [ -z "$MESSAGE" ]; then
  echo "❌ 用法：bash scripts/checkpoint.sh \"角色名\" \"做了什麼\""
  echo "   例如：bash scripts/checkpoint.sh \"A4\" \"S11 照片分類完成 3000 張\""
  echo "   角色名：A0 / A1 / A2 / A4 / A5 / A6 / A7 / A8"
  exit 1
fi

COMMIT_MSG="checkpoint($ROLE): $MESSAGE"
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

echo "======================================"
echo "🔄 CHECKPOINT 存檔流程啟動"
echo "   角色：$ROLE"
echo "   訊息：$MESSAGE"
echo "   分支：$CURRENT_BRANCH"
echo "======================================"
echo ""

# 確認有沒有變更
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  echo "ℹ️  沒有需要存檔的變更，跳過。"
  echo "   （如果你認為有變更，請確認 git status）"
  exit 0
fi

echo "📋 變更清單："
git status --short
echo ""

# Step 1: git add -A
echo "📁 [1/4] 暫存所有變更..."
if ! git add -A; then
  echo "❌ git add 失敗"
  exit 1
fi
echo "       ✅ 完成"

# Step 2: commit
echo "💾 [2/4] Commit..."
if ! git commit -m "$COMMIT_MSG"; then
  echo "❌ git commit 失敗"
  exit 1
fi
HASH=$(git rev-parse HEAD)
SHORT="${HASH:0:7}"
echo "       ✅ $SHORT — $COMMIT_MSG"
echo ""

# Step 3: cherry-pick 到 main（如果不在 main branch 上）
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "🍒 [3/4] Cherry-pick 到 main..."
  if ! cd "$REPO_ROOT"; then
    echo "❌ 無法切到 $REPO_ROOT"
    exit 1
  fi

  MAIN_BRANCH=$(git branch --show-current)
  if [ "$MAIN_BRANCH" != "main" ]; then
    if ! git checkout main; then
      echo "❌ git checkout main 失敗"
      exit 1
    fi
  fi

  if git cherry-pick "$HASH"; then
    echo "       ✅ Cherry-pick 完成"
  else
    echo "⚠️  發現衝突，嘗試自動解（theirs 策略）..."
    git checkout --theirs . 2>/dev/null || true
    git add -A
    if git cherry-pick --continue --no-edit; then
      echo "       ✅ 衝突已自動解決"
    else
      echo "❌ Cherry-pick 失敗，請手動解衝突："
      echo "   cd $REPO_ROOT"
      echo "   git cherry-pick --abort"
      echo "   git cherry-pick $HASH  # 或手動合併"
      git cherry-pick --abort 2>/dev/null || true
      exit 1
    fi
  fi
else
  echo "⏭️  [3/4] 已在 main branch，跳過 cherry-pick"
  cd "$REPO_ROOT"
fi

# Step 4: push main
echo "🚀 [4/4] Push main 到 remote..."
if git push origin main; then
  echo "       ✅ Push 完成"
else
  echo "⚠️  Push 失敗（remote 可能有更新），嘗試 pull --rebase..."
  if git pull --rebase origin main && git push origin main; then
    echo "       ✅ Push 完成（rebase 後）"
  else
    echo "❌ Push 失敗，請手動處理："
    echo "   cd $REPO_ROOT"
    echo "   git pull --rebase origin main"
    echo "   git push origin main"
    exit 1
  fi
fi

# 回到 worktree 目錄
cd "$WORKTREE_DIR"

# Step 5: 驗證
echo ""
echo "🔍 驗證 main 是否包含此次 commit..."
bash "$WORKTREE_DIR/scripts/verify-commit-on-main.sh" "$HASH"

echo ""
echo "======================================"
echo "✅ 存檔完成！"
echo "   Commit: $SHORT"
echo "   main 已同步到 remote。"
echo "======================================"
