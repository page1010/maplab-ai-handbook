#!/bin/bash
# B5 地端模型教材包打包腳本（骨架）
# 用法：bash scripts/b5-pack-teaching-package.sh [YYYY-MM]
# 產出：packages/local-model-teaching/[YYYY-MM]/
# 執行者：B5 影子系統總管（每月第一個週一）
# 建立：2026-07-11

set -e

MONTH="${1:-$(date +%Y-%m)}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG_DIR="$REPO_ROOT/packages/local-model-teaching/$MONTH"
INVENTORY="$REPO_ROOT/reports/capability-inventory/inventory_$MONTH.md"

echo "=== B5 教材包打包 $MONTH ==="
echo "目標目錄：$PKG_DIR"
echo ""

# 確認評分報告存在
if [ ! -f "$INVENTORY" ]; then
  echo "❌ 找不到評分報告：$INVENTORY"
  echo "   請先執行 B5 首次蒸餾評分，再跑打包腳本"
  exit 1
fi

# 建立目錄
mkdir -p "$PKG_DIR/recall_prompts"
mkdir -p "$PKG_DIR/top_jobs"
mkdir -p "$PKG_DIR/eval_cases"

# ── Step 1: pitfalls 蒸餾版 ──────────────────────────────────────
echo "[1/4] 提取 pitfalls 蒸餾版..."
PITFALLS_SRC="$REPO_ROOT/pitfalls.md"
PITFALLS_DEST="$PKG_DIR/pitfalls_digest.md"

cat > "$PITFALLS_DEST" << 'HEADER'
# pitfalls 蒸餾版（地端教材包）
# 來源：pitfalls.md | 蒸餾：B5 | 僅保留評分 ≥ 4 的通用規則

> 此版本已移除 GAS/Sheets/OAuth/MCP 特定內容，保留通用行為準則。
> 完整版見 repo pitfalls.md。

HEADER

# 提取評分 4+ 的條目標題（手動維護清單，下次優化為自動評分）
KEEP_PATTERNS=(
  "Unattended long-running tasks"
  "Test receipt must be written before claiming completion"
  "quote answers must come from a quote Sheet"
  "Telegram.*must create a dispatch receipt"
  "Quote trainee agents must not self-certify PASS"
  "quote trainees need fixed customer templates"
  "B3 archive is not the same thing as the B4 patrol verdict"
  "Repo extension update is not live Chrome proof"
  "babysitting cron"
)

for pattern in "${KEEP_PATTERNS[@]}"; do
  # 提取匹配條目（從 ## 標題到下一個 ## 標題）
  awk "/^## .*${pattern}/{found=1} found{print} /^## /{if(found && !/^## .*${pattern}/)found=0}" "$PITFALLS_SRC" >> "$PITFALLS_DEST" 2>/dev/null || true
done

echo "   ✅ pitfalls_digest.md 已生成（手動過濾模式）"

# ── Step 2: recall_prompts 精煉版 ────────────────────────────────
echo "[2/4] 精煉 recall prompts（移除 MCP/API 段落）..."

# fable-mindset 注入片段（地端版）
FABLE_INJECT='⚠️ 本教材包為地端版（無 MCP），核心思維框架見 docs/fable-mindset.md 10 條原則。'

# 只打包評分最高的幾個角色 recall（A6 業務 + A7 客服 + B5）
for role in A6 A7 B5; do
  src="$REPO_ROOT/recalls/${role}_recall.md"
  if [ -f "$src" ]; then
    dest="$PKG_DIR/recall_prompts/${role}_local.md"
    # 移除 MCP/OAuth/GAS 相關段落（簡單 grep 移除）
    grep -v "MCP 可用\|OAuth token\|curl \+.*token\|clasp push\|GAS trigger" "$src" > "$dest" 2>/dev/null || cp "$src" "$dest"
    echo "$FABLE_INJECT" >> "$dest"
    echo "   ✅ ${role}_local.md"
  fi
done

# ── Step 3: top_jobs 提取 ────────────────────────────────────────
echo "[3/4] 提取 top_jobs（評分 ≥ 4）..."

TOP_JOBS=(
  "JOB-A1-ALT-TEXT-STANDARD-20260630"
  "JOB-CODEX-B3-ADCOPY-20260710"
  "JOB-CODEX-CONTENT-AUDIT-20260710"
)

for job in "${TOP_JOBS[@]}"; do
  src="$REPO_ROOT/workbook/reviews/$job"
  if [ -d "$src" ]; then
    # 只複製 README 或 summary 文件
    for f in "$src/README.md" "$src/summary.md" "$src/output.md"; do
      if [ -f "$f" ]; then
        cp "$f" "$PKG_DIR/top_jobs/${job}-$(basename $f)"
        echo "   ✅ $job/$(basename $f)"
      fi
    done
  fi
done

# ── Step 4: 核心技能書直接複製（評分 5）────────────────────────
echo "[4/4] 複製評分 5 技能書..."

SKILLS_5=(
  "docs/fable-mindset.md"
  "skills/task-progress-guide.md"
  "skills/brand-voice-guide.md"
  "skills/a6-safety-boundaries.md"
  "skills/session-handoff.md"
)

for skill in "${SKILLS_5[@]}"; do
  src="$REPO_ROOT/$skill"
  if [ -f "$src" ]; then
    dest="$PKG_DIR/$(basename $skill)"
    cp "$src" "$dest"
    echo "   ✅ $(basename $skill)"
  fi
done

# ── 完成 ─────────────────────────────────────────────────────────
echo ""
echo "=== 完成 ==="
echo "教材包路徑：$PKG_DIR"
echo "內容："
ls "$PKG_DIR/"
echo ""
echo "下一步：Owner 確認後 → git add + commit → checkpoint.sh 存檔"
