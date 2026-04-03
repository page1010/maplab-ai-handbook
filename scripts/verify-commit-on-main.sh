#!/bin/bash
# verify-commit-on-main.sh
# 檢查指定 commit（或 HEAD）是否已在 main branch
# 用法：
#   bash scripts/verify-commit-on-main.sh              # 檢查 HEAD
#   bash scripts/verify-commit-on-main.sh <commit-hash>

set -e

REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"
TARGET="${1:-HEAD}"

# 解析 hash（支援 HEAD、短 hash、完整 hash）
HASH=$(git rev-parse "$TARGET" 2>/dev/null) || {
  echo "❌ 無法解析 commit: $TARGET"
  exit 1
}
SHORT="${HASH:0:7}"

echo "🔍 檢查 commit $SHORT 是否在 main..."

# 取得 main 上的 commit 列表（從父 repo）
MAIN_COMMITS=$(git -C "$REPO_ROOT" log main --format="%H" 2>/dev/null) || {
  echo "❌ 無法讀取 $REPO_ROOT 的 main branch"
  echo "   請確認 $REPO_ROOT 存在且是 git repo"
  exit 1
}

if echo "$MAIN_COMMITS" | grep -q "$HASH"; then
  echo "✅ commit $SHORT 已在 main — 可以安心結束 session"
else
  echo "❌ commit $SHORT 不在 main — 請立即 cherry-pick！"
  echo ""
  echo "建議動作："
  echo "  cd $REPO_ROOT"
  echo "  git checkout main"
  echo "  git cherry-pick $HASH"
  echo "  git push origin main"
  echo "  cd -"
  exit 1
fi
