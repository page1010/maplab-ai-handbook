#!/usr/bin/env bash
# cleanup-worktrees.sh — 清理 Claude Code 殘留的 git worktree
# 用法：
#   bash scripts/cleanup-worktrees.sh              # 預設：清理無變更的 worktree
#   bash scripts/cleanup-worktrees.sh --dry-run    # 只看不做
#   bash scripts/cleanup-worktrees.sh --all        # 強制清理全部（含有變更的）
#   bash scripts/cleanup-worktrees.sh --merged-only # 只清理已 merge 到 main 的 branch（launchd 推薦）
#
# 可掛 launchd 定時執行（每 30 分鐘檢查一次）
# plist 路徑：scripts/com.maplab.cleanup-worktrees.plist
# 安裝 launchd：cp scripts/com.maplab.cleanup-worktrees.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.maplab.cleanup-worktrees.plist
#
# 安全保護：
#   - 永遠跳過 locked worktree（git worktree lock 標記的）
#   - 永遠跳過 main branch 的 worktree（即 REPO_ROOT）
#   - 跳過有未提交變更的 worktree（除非 --all）
#   - launchd 建議使用 --merged-only，只清已確定完成的 branch

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKTREE_DIR="$REPO_ROOT/.claude/worktrees"
DRY_RUN=false
FORCE_ALL=false
MERGED_ONLY=false
LOG_FILE="$REPO_ROOT/logs/worktree-cleanup.log"

for arg in "$@"; do
  case "$arg" in
    --dry-run)      DRY_RUN=true ;;
    --all)          FORCE_ALL=true ;;
    --merged-only)  MERGED_ONLY=true ;;
  esac
done

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

log "=== Worktree 健康檢查 開始 ==="
log "REPO_ROOT: $REPO_ROOT"
log "模式: $([ "$DRY_RUN" = true ] && echo DRY-RUN || echo LIVE) | $([ "$MERGED_ONLY" = true ] && echo merged-only || echo all-clean) | $([ "$FORCE_ALL" = true ] && echo force-all || echo safe)"

# 先執行 git worktree prune，清掉目錄已不存在的 stale 引用
if [[ "$DRY_RUN" == false ]]; then
  git -C "$REPO_ROOT" worktree prune 2>/dev/null && log "git worktree prune 完成" || true
fi

# 列出所有 worktree（porcelain 格式，包含 locked 狀態）
log ""
log "--- 目前所有 worktree ---"
git -C "$REPO_ROOT" worktree list | while IFS= read -r line; do log "  $line"; done
log ""

# 取得 locked worktree 路徑清單
LOCKED_WORKTREES=$(git -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null | \
  awk '/^worktree /{wt=$2} /^locked/{print wt}' || echo "")

# 沒有 worktree 目錄 → 直接結束
if [[ ! -d "$WORKTREE_DIR" ]]; then
  log "無 worktree 目錄，跳過"
  log "=== 完成 ==="
  exit 0
fi

# 取得已 merge 到 main 的 branch 清單（用於 stale 判斷）
MERGED_BRANCHES=$(git -C "$REPO_ROOT" branch --merged main 2>/dev/null | sed 's/^[* ]*//' || echo "")

cleaned=0
skipped=0
stale_count=0
total=0

for wt in "$WORKTREE_DIR"/*/; do
  [[ -d "$wt" ]] || continue
  wt="${wt%/}"  # 去除尾部斜線
  total=$((total + 1))
  wt_name=$(basename "$wt")

  # === 安全保護：跳過 locked worktree ===
  if echo "$LOCKED_WORKTREES" | grep -qx "$wt"; then
    log "🔒 跳過 ${wt_name} — worktree 已鎖定（locked）"
    skipped=$((skipped + 1))
    continue
  fi

  # 取得 branch 名稱
  branch_name=""
  if cd "$wt" 2>/dev/null; then
    branch_name=$(git branch --show-current 2>/dev/null || echo "")
    cd "$REPO_ROOT"
  fi

  # 判斷是否已 merge 到 main
  is_merged=false
  if [[ -n "$branch_name" ]] && echo "$MERGED_BRANCHES" | grep -qx "$branch_name"; then
    is_merged=true
    stale_count=$((stale_count + 1))
    log "🔀 ${wt_name} (branch: ${branch_name}) — 已 merge 到 main"
  else
    log "📋 ${wt_name} (branch: ${branch_name:-unknown}) — 未 merge"
  fi

  # 檢查是否有未提交變更
  has_changes=false
  if cd "$wt" 2>/dev/null; then
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
      has_changes=true
      log "   ⚠️  有未提交變更"
    fi
    cd "$REPO_ROOT"
  fi

  # === --merged-only 模式：只清已 merge 的 ===
  if [[ "$MERGED_ONLY" == true ]] && [[ "$is_merged" == false ]]; then
    log "   ⏭️  跳過 — branch 未 merge（--merged-only 模式）"
    skipped=$((skipped + 1))
    continue
  fi

  # === 有未提交變更 → 跳過（除非 --all）===
  if [[ "$has_changes" == true ]] && [[ "$FORCE_ALL" == false ]]; then
    log "   ⚠️  跳過 — 有未提交變更（用 --all 強制清理）"
    skipped=$((skipped + 1))
    continue
  fi

  # === DRY-RUN 模式 ===
  if [[ "$DRY_RUN" == true ]]; then
    tags=""
    [[ "$has_changes" == true ]] && tags="${tags} [有變更]"
    [[ "$is_merged" == true ]]   && tags="${tags} [已 merge]"
    log "   [DRY-RUN] 會清理 ${wt_name}${tags}"
    cleaned=$((cleaned + 1))
    continue
  fi

  # === 執行清理 ===
  log "   🗑️  清理中..."

  if git -C "$REPO_ROOT" worktree remove "$wt" --force 2>/dev/null; then
    log "   ✅ worktree 已移除"
  else
    rm -rf "$wt"
    git -C "$REPO_ROOT" worktree prune 2>/dev/null || true
    log "   ✅ worktree 強制移除"
  fi

  # 清理本地 claude/ branch
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

log ""
log "=== 結果摘要 ==="
log "掃描 worktree：$total 個"
log "已清理：$cleaned 個"
log "已跳過：$skipped 個"
log "已 merge（stale）：$stale_count 個"
[[ "$cleaned" -gt 0 ]] && [[ "$DRY_RUN" == false ]] && \
  log "估計釋放 ~$((cleaned * 16))MB 磁碟空間"
log "=== 完成 ==="
