#!/bin/bash
# verify-commit-on-main.sh
# 檢查指定 commit（或 HEAD）的內容是否已在 main branch
# cherry-pick 後 hash 會改變，所以用 patch-id 或 commit message 比對
# 用法：
#   bash scripts/verify-commit-on-main.sh              # 檢查 HEAD
#   bash scripts/verify-commit-on-main.sh <commit-hash>

REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"
TARGET="${1:-HEAD}"

# 解析 hash（支援 HEAD、短 hash、完整 hash）
HASH=$(git rev-parse "$TARGET" 2>/dev/null) || {
  echo "❌ 無法解析 commit: $TARGET"
  exit 1
}
SHORT="${HASH:0:7}"

echo "🔍 檢查 commit $SHORT 是否已反映在 main..."

# 方法 1：直接 hash 比對（在 main 上 commit 時 hash 相同）
MAIN_COMMITS=$(git -C "$REPO_ROOT" log main --format="%H" 2>/dev/null) || {
  echo "❌ 無法讀取 $REPO_ROOT 的 main branch"
  exit 1
}

if echo "$MAIN_COMMITS" | grep -q "$HASH"; then
  echo "✅ commit $SHORT 直接存在於 main — 可以安心結束 session"
  exit 0
fi

# 方法 2：用 commit message 比對（cherry-pick 後 hash 改變，但 message 相同）
MSG=$(git log -1 --format="%s" "$HASH")
MAIN_MSG=$(git -C "$REPO_ROOT" log main --format="%s" | grep -F "$MSG" || true)

if [ -n "$MAIN_MSG" ]; then
  echo "✅ commit $SHORT 已 cherry-pick 到 main（message 吻合）— 可以安心結束 session"
  exit 0
fi

# 找不到
echo "❌ commit $SHORT 不在 main — 請立即 cherry-pick！"
echo "   Commit message: $MSG"
echo ""
echo "建議動作："
echo "  cd $REPO_ROOT"
echo "  git checkout main"
echo "  git cherry-pick $HASH"
echo "  git push origin main"
echo "  cd -"
exit 1
