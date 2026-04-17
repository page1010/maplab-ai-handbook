#!/bin/bash
# git-pull.sh — launchd 定期拉取 main 的 wrapper
# 解決直接呼叫 git 的問題：git 路徑、dirty worktree、衝突
# 被 com.maplab.git-pull.plist 呼叫

REPO="/Users/pagemacmini/maplab-ai-handbook"
LOG="/Users/pagemacmini/.claude/logs/git-pull.log"
GIT="/usr/bin/git"

cd "$REPO" || exit 1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] git-pull 開始" >> "$LOG"

# 確認在 main branch
BRANCH=$($GIT branch --show-current 2>/dev/null)
if [ "$BRANCH" != "main" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 不在 main（目前: $BRANCH），跳過" >> "$LOG"
  exit 0
fi

# 如果有未提交的變更，先 stash
DIRTY=false
if [ -n "$($GIT status --porcelain 2>/dev/null)" ]; then
  DIRTY=true
  $GIT stash push -m "auto-stash-before-pull-$(date +%Y%m%d%H%M)" >> "$LOG" 2>&1
fi

# Pull with rebase
if $GIT pull --rebase origin main >> "$LOG" 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] pull 成功" >> "$LOG"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] pull 失敗，abort rebase" >> "$LOG"
  $GIT rebase --abort >> "$LOG" 2>&1
fi

# 恢復 stash
if [ "$DIRTY" = true ]; then
  $GIT stash pop >> "$LOG" 2>&1 || echo "[$(date '+%Y-%m-%d %H:%M:%S')] stash pop 衝突，保留在 stash" >> "$LOG"
fi

exit 0
