#!/bin/bash
# generate-skill.sh — 自動技能生成（Phase 4: Hermes 借鑒）
# 用法：
#   bash scripts/generate-skill.sh "技能名稱" "問題描述" "解法描述" ["觸發條件"]
#
# 例如：
#   bash scripts/generate-skill.sh "git-pull-path-fix" \
#     "launchd plist 用 /opt/homebrew/bin/git 但實際路徑是 /usr/bin/git" \
#     "建 wrapper script，不硬寫 git 路徑，改用 /usr/bin/git" \
#     "launchd 執行失敗 exit 78"
#
# 會產出：skills/auto/git-pull-path-fix.md

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUTO_DIR="$REPO_ROOT/skills/auto"

NAME="${1:-}"
PROBLEM="${2:-}"
SOLUTION="${3:-}"
TRIGGER="${4:-（未指定）}"

if [ -z "$NAME" ] || [ -z "$PROBLEM" ] || [ -z "$SOLUTION" ]; then
  echo "❌ 用法：bash scripts/generate-skill.sh \"名稱\" \"問題\" \"解法\" [\"觸發條件\"]"
  exit 1
fi

# 產出路徑
SKILL_FILE="$AUTO_DIR/${NAME}.md"

if [ -f "$SKILL_FILE" ]; then
  echo "⚠️  技能檔已存在：$SKILL_FILE"
  echo "   如果要更新，請手動編輯或先刪除。"
  exit 1
fi

TODAY=$(date +%Y-%m-%d)
COMMIT=$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")

cat > "$SKILL_FILE" << EOF
# 技能：${NAME}
> 自動生成於 ${TODAY}（commit ${COMMIT}）by generate-skill.sh

## 觸發條件
${TRIGGER}

## 問題
${PROBLEM}

## 解法
${SOLUTION}

## RED 情境（G1 技能 TDD — 必填後才可轉正）
<!-- 沒有這本技能書時，agent 會怎麼掉進坑？描述具體壓力情境與當時的合理化藉口。 -->
（待補：unverified）

## 封坑驗證（G1 — 必填後才可轉正）
<!-- 一條可執行指令或具體情境，證明讀了此技能後坑真的進不去。例：grep ... 應為 0。 -->
（待補：unverified）

## 背景
- 來源 commit: ${COMMIT}
- 生成日期: ${TODAY}
- 類型: 自動生成（可人工精修；RED 情境與封坑驗證補齊前視同 unverified 草稿）
EOF

echo "✅ 技能檔已生成：$SKILL_FILE"
echo ""
echo "📝 建議後續："
echo "   1. 檢查內容是否正確"
echo "   2. 補齊「RED 情境」與「封坑驗證」（G1 技能 TDD；補齊前是 unverified 草稿）"
echo "   3. 補充更多細節或範例"
echo "   4. 在 CLAUDE.md 技能索引表加入觸發條件（說明欄只寫觸發症狀，不寫流程摘要）"
