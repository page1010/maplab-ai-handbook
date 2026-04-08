#!/bin/bash
# approve.sh — Owner 審核後將 agent branch 合併進 main
# 用法：bash scripts/approve.sh <branch-name>
# 例如：bash scripts/approve.sh agent/A5-20260408

BRANCH="${1:-}"
REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"

if [ -z "$BRANCH" ]; then
  echo "❌ 用法：bash scripts/approve.sh <branch-name>"
  echo "   例如：bash scripts/approve.sh agent/A5-20260408"
  echo ""
  echo "現有 agent branches（remote）："
  git branch -r 2>/dev/null | grep 'agent/' | sed 's/.*origin\//  /'
  exit 1
fi

cd "$REPO_ROOT"

echo "======================================"
echo "✅ APPROVE — 合併 $BRANCH 進 main"
echo "======================================"

echo "📥 [1/3] 更新 main..."
if ! git checkout main; then
  echo "❌ 無法切換到 main"
  exit 1
fi
if ! git pull origin main; then
  echo "❌ 更新 main 失敗"
  exit 1
fi
echo "       ✅ 完成"

echo "🔀 [2/3] Merge $BRANCH..."
# 嘗試 local branch 先，否則用 origin/branch
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  MERGE_TARGET="$BRANCH"
elif git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  MERGE_TARGET="origin/$BRANCH"
else
  echo "❌ 找不到 branch: $BRANCH"
  echo "   確認名稱是否正確（大小寫、斜線）"
  exit 1
fi

if git merge --no-ff "$MERGE_TARGET" -m "approve($BRANCH): merge to main"; then
  echo "       ✅ Merge 完成"
else
  echo "❌ Merge 衝突，請手動解決："
  echo "   git merge --abort  # 放棄"
  echo "   # 或手動解決後 git add -A && git merge --continue"
  exit 1
fi

echo "🚀 [3/3] Push main..."
if git push origin main; then
  echo "       ✅ Push 完成"
else
  echo "❌ Push 失敗"
  exit 1
fi

echo ""
echo "======================================"
echo "✅ $BRANCH 已合併進 main 並 push"
echo "======================================"
