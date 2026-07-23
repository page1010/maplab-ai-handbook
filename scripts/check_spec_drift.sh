#!/usr/bin/env bash
# check_spec_drift.sh — 跨檔慣例漂移檢查器（非阻塞警告）
#
# 目的：把「已廢止/已統一的規範」被 live 檔違反的情況自動抓出來，避免像
#   alt 兩式衝突那樣漂了 5 個檔卻沒人發現、每個碰到的 agent 都要重判一次。
# 觸發：checkpoint.sh 存檔前自動跑（非阻塞）；也可手動 `bash scripts/check_spec_drift.sh`。
# 設計：資料驅動——要新增一條規範，只在 RULES 陣列加一行，不用改邏輯。
# 相容：macOS bash 3.2（不用關聯陣列）。
#
# 規範來源：
#   - alt 單一標準（2026-06-30 統一，B 式作廢）→ recalls/A2_recall.md §D
#   - 已知 404 planned slug（禁當 live target）→ docs/seo-keyword-map.md §4
#
# 退出碼：一律 0（純警告，不擋存檔）。要當硬性關卡請由 patrol_grader.sh 呼叫。

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 0

# 只掃「放慣例規範」的內容目錄（不掃 data/logs/state 等大檔，快又少誤報）。
# 要擴掃其他目錄，往這裡加即可。
SCAN_PATHS="skills recalls docs handoff chrome-extension/task-modules projects AGENT_RULES.md AGENT_RECALL_PROMPTS.md CLAUDE.md README.md CURRENT_STATUS.md"
# 收斂成實際存在的路徑
EXIST_PATHS=""
for p in $SCAN_PATHS; do [ -e "$p" ] && EXIST_PATHS="$EXIST_PATHS $p"; done

# 每條規則格式："正則pattern|||人看得懂的說明|||正解指引"
# 排除「說明用」的檔（本身在講規範的檔）避免自我誤報。
RULES=(
  'MAPLAB Kitchen \{場景\}｜|||已廢止的 alt B 式（品牌名開頭）仍出現在 live 檔|||改用 A 式 `台南{場景}外燴—{描述}`，品牌名移檔名/caption（recalls/A2_recall.md §D）'
)

# 講規範本身、允許出現舊式當反例的檔（白名單，不誤報）
ALLOW_REGEX='seo-keyword-map\.md|alt-text-standard-proposal\.md|check_spec_drift\.sh|CHANGELOG\.md|decisions\.md|pitfalls\.md'
# 「退役說明」語境的行不算違反（是在告訴大家別用，不是在用）
RETIRE_CTX='作廢|舊式|已統一|deprecated|B 式|正解|漂移|禁用|勿用|不要用'

command -v rg >/dev/null 2>&1 && GREP=rg || GREP=grep
found_any=0

echo "🔎 spec-drift 檢查（跨檔慣例漂移）..."
for rule in "${RULES[@]}"; do
  pat="${rule%%|||*}"
  rest="${rule#*|||}"
  desc="${rest%%|||*}"
  fix="${rest#*|||}"

  # 行級比對：抓到 pattern 的行，先剔除「退役說明」語境行，再去掉白名單檔，最後留唯一檔名
  if [ "$GREP" = "rg" ]; then
    hits=$(rg -n --no-messages -- "$pat" $EXIST_PATHS 2>/dev/null | grep -vE "$RETIRE_CTX" | grep -vE "$ALLOW_REGEX" | cut -d: -f1 | sort -u || true)
  else
    hits=$(grep -rnE -- "$pat" $EXIST_PATHS 2>/dev/null | sed 's#^\./##' | grep -vE "$RETIRE_CTX" | grep -vE "$ALLOW_REGEX" | cut -d: -f1 | sort -u || true)
  fi

  if [ -n "$hits" ]; then
    found_any=1
    echo "⚠️  漂移：$desc"
    echo "$hits" | sed 's/^/     - /'
    echo "     正解：$fix"
  fi
done

if [ "$found_any" -eq 0 ]; then
  echo "✅ spec-drift 檢查通過（無已廢止慣例殘留在 live 檔）。"
fi
exit 0
