#!/usr/bin/env bash
# patrol_grader.sh — 巡查的獨立客觀評分者（把「all clear 蓋章」變成有停止條件的關卡）
#
# 背景：patrol.sh 是任務卡狀態機，會輸出「差不多了」的 Owner 決策佇列，但它不查
#   repo 健康。文章（自我改進系統 14 步）第 6 步：獨立驗證者勝過自我批評。這支就是
#   那個獨立驗證者——只看客觀產出物（git 狀態、衝突標記、漂移、落後），不看誰做的。
#
# 用法：bash scripts/patrol_grader.sh            # 人看
#       bash scripts/patrol_grader.sh --quiet    # 只在有問題時輸出（適合排程）
# 退出碼：0 = PASS（無硬問題）；1 = FAIL（有硬問題，需處理）。供 patrol/CI 當關卡。
# 相容：macOS bash 3.2。

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 0
QUIET=false
[ "${1:-}" = "--quiet" ] && QUIET=true

fail=0
warn=0
report=""
add()  { report="${report}$1
"; }

# ── 1. 未解衝突標記（硬問題）──
# 只掃內容目錄，避免掃到 log/index 大檔
CONFLICT_PATHS="skills recalls docs handoff projects scripts CURRENT_STATUS.md AGENT_RULES.md README.md CLAUDE.md"
EXIST=""; for p in $CONFLICT_PATHS; do [ -e "$p" ] && EXIST="$EXIST $p"; done
if command -v rg >/dev/null 2>&1; then
  conf=$(rg -l --no-messages '^(<<<<<<<|=======|>>>>>>>)' $EXIST 2>/dev/null || true)
else
  conf=$(grep -rlE '^(<<<<<<<|=======|>>>>>>>)' $EXIST 2>/dev/null | sed 's#^\./##' || true)
fi
if [ -n "$conf" ]; then
  fail=1
  add "❌ FAIL：發現未解 git 衝突標記："
  add "$(echo "$conf" | sed 's/^/       - /')"
fi

# ── 1b. 進行中的 merge/rebase/cherry-pick（未收尾 = 硬問題）──
if [ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || [ -f .git/CHERRY_PICK_HEAD ]; then
  fail=1
  add "❌ FAIL：有未收尾的 merge/rebase/cherry-pick（解完衝突後要 git commit 收尾，或 --abort）"
fi

# ── 2. 本地落後/領先 origin/main（軟問題→落後過多升硬）──
if git rev-parse --git-dir >/dev/null 2>&1; then
  git fetch origin >/dev/null 2>&1 || add "⚠️  WARN：git fetch 失敗（可能離線），落後量未知"
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
    ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$behind" -ge 10 ]; then
      fail=1; add "❌ FAIL：本地 main 落後 origin ${behind} 個 commit（>=10，同步已失控，先 pull）"
    elif [ "$behind" -gt 0 ]; then
      warn=1; add "⚠️  WARN：本地 main 落後 origin ${behind} 個 commit（建議 pull）"
    fi
    [ "$ahead" -gt 0 ] && { warn=1; add "⚠️  WARN：本地有 ${ahead} 個未 push 的 commit"; }
  fi
fi

# ── 3. Stale git lock（自動化沒自癒的訊號）──
if [ -f .git/index.lock ]; then
  warn=1; add "⚠️  WARN：存在 .git/index.lock（可能是中斷的 git 操作，host 端 rm -f 清除）"
fi

# ── 4. 跨檔慣例漂移（呼叫 spec-drift 檢查器）──
if [ -f "$REPO_ROOT/scripts/check_spec_drift.sh" ]; then
  drift=$(bash "$REPO_ROOT/scripts/check_spec_drift.sh" 2>/dev/null || true)
  if echo "$drift" | grep -q '⚠️'; then
    warn=1
    add "⚠️  WARN：spec-drift 檢查發現已廢止慣例殘留（詳見 check_spec_drift.sh 輸出）"
  fi
fi

# ── 5. 逾期未 commit 的進行中任務（複用 patrol 的 48h 精神，這裡只點數）──
if [ -d handoff/tasks ]; then
  overdue=0
  now_ts=$(date +%s)
  for card in handoff/tasks/T-*.md; do
    [ -f "$card" ] || continue
    grep -q '🔄 進行中' "$card" 2>/dev/null || continue
    la=$(grep -m1 '^\- \*\*最後活動\*\*' "$card" 2>/dev/null | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    [ -n "$la" ] || continue
    then_ts=$(date -j -f "%Y-%m-%d" "$la" +%s 2>/dev/null || echo 0)
    [ "$then_ts" = "0" ] && continue
    hrs=$(( (now_ts - then_ts) / 3600 ))
    [ "$hrs" -gt 168 ] && overdue=$((overdue+1))
  done
  [ "$overdue" -gt 0 ] && { warn=1; add "⚠️  WARN：${overdue} 張進行中任務卡 >7 天無 commit（patrol.sh 詳列）"; }
fi

# ── 判定 ──
if [ "$fail" -eq 1 ]; then
  echo "🔴 PATROL GRADER：FAIL（有硬問題必須處理）"
  printf '%s' "$report"
  exit 1
fi
if [ "$warn" -eq 1 ]; then
  echo "🟡 PATROL GRADER：PASS with WARN"
  printf '%s' "$report"
  exit 0
fi
[ "$QUIET" = false ] && echo "🟢 PATROL GRADER：PASS（repo 健康，無衝突/漂移/失控落後）"
exit 0
