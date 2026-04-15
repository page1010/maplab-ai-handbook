#!/usr/bin/env bash
# cleanup-worktrees.sh — 清理 Claude Code 殘留的 git worktree
# 用法：
#   bash scripts/cleanup-worktrees.sh          # 預設：清理無變更的 worktree
#   bash scripts/cleanup-worktrees.sh --dry-run # 只看不做
#   bash scripts/cleanup-worktrees.sh --all     # 強制清理全部（含有變更的）
#
# 可掛 launchd 定時執行（每 30 分鐘檢查一次）

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKTREE_DIR="$REPO_ROOT/.claude/worktrees"
DRY_RUN=false
FORCE_ALL=false
LOG_FILE="$REPO_ROOT/logs/worktree-cleanup.log"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --all)     FORCE_ALL=true ;;
  esac
done

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

# 沒有 worktree 目錄 → 直接結束
if [[ ! -d "$WORKTREE_DIR" ]]; then
  log "無 worktree 目錄，跳過"
  exit 0
fi

# 列出所有 worktree 子目錄
cleaned=0
skipped=0
total=0

for wt in "$WORKTREE_DIR"/*/; do
  [[ -d "$wt" ]] || continue
  total=$((total + 1))
  wt_name=$(basename "$wt")

  # 檢查是否有未提交變更
  has_changes=false
  if cd "$wt" 2>/dev/null; then
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
      has_changes=true
    fi
    cd "$REPO_ROOT"
  fi

  if [[ "$has_changes" == true ]] && [[ "$FORCE_ALL" == false ]]; then
    log "⚠️  跳過 ${wt_name} — 有未提交變更"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$DRY_RUN" == true ]]; then
    if [[ "$has_changes" == true ]]; then
      log "[DRY-RUN] 會清理 ${wt_name} (有變更, --all 強制)"
    else
      log "[DRY-RUN] 會清理 ${wt_name} (無變更)"
    fi
    cleaned=$((cleaned + 1))
    continue
  fi

  # 取得 worktree 對應的 branch 名稱
  branch_name=$(cd "$wt" && git branch --show-current 2>/dev/null || echo "")

  # 移除 worktree
  log "🗑️  清理 ${wt_name}..."
  if git -C "$REPO_ROOT" worktree remove "$wt" --force 2>/dev/null; then
    log "   ✅ worktree 已移除"
  else
    # fallback：手動刪除
    rm -rf "$wt"
    git -C "$REPO_ROOT" worktree prune 2>/dev/null || true
    log "   ✅ worktree 已強制移除"
  fi

  # 清理對應的遠端 branch（只清 claude/ 開頭的）
  if [[ -n "$branch_name" ]] && echo "$branch_name" | grep -q '^claude/'; then
    git -C "$REPO_ROOT" branch -D "$branch_name" 2>/dev/null && \
      log "   🌿 本地 branch $branch_name 已刪除" || true
  fi

  cleaned=$((cleaned + 1))
done

# 最終 prune
if [[ "$DRY_RUN" == false ]]; then
  git -C "$REPO_ROOT" worktree prune 2>/dev/null || true
fi

log "完成：掃描 $total 個 worktree，清理 $cleaned 個，跳過 $skipped 個"

# 回報記憶體釋放量（估算）
if [[ "$cleaned" -gt 0 ]] && [[ "$DRY_RUN" == false ]]; then
  log "估計釋放 ~$((cleaned * 16))MB 磁碟空間"
fi
