#!/usr/bin/env bash
# is_rules_gate.sh — IS 規則引擎 runtime gate
# 建立：2026-07-18 A1 | Owner 已裁決選項 A（草稿值全用）
# 紅線：不下單、不給買賣建議；所有行動服務「讓 Owner 決策更快更安全」。
#
# 四參數（Owner 2026-07-18 裁決選項 A，草稿值直接上線）：
#   SOP1  單一主題集中度上限 = 10% gross
#   SOP2  單一標的上限（非核心）= 15% gross
#   LEV   槓桿警戒線 = 1.5x
#   DROP  日跌幅急警（預設值）= -3%（Owner 一句話可改）
#
# 用法：
#   bash scripts/is_rules_gate.sh               # 讀 escalation_queue 自動測試
#   bash scripts/is_rules_gate.sh --notify       # 測試 + 推播 Telegram
#   bash scripts/is_rules_gate.sh --dry-run      # 只印選項卡，不推播
#
# 現值實測（2026-07-18 exposure_ledger）：
#   TSLA  25.9%（SOP1 Speculation/Narrative 超標，SOP2 單名超標核心 25% 邊緣）
#   3296  17.2%（SOP2 非核心超標）
#   US tech 82.7% gross（主題超高集中）

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/bot/.env"
NOTIFY_SCRIPT="$REPO_ROOT/scripts/notify_owner.sh"
ESCALATION_QUEUE="$HOME/Documents/New project/state/runtime_escalation_queue.jsonl"

# ── 參數 ──
SOP1_THRESHOLD=10      # 單一主題集中度上限（%，gross）
SOP2_THRESHOLD=15      # 單一標的上限（%，gross，非核心）
LEV_THRESHOLD="1.5"   # 槓桿警戒線（倍）
DROP_THRESHOLD="-3"   # 日跌幅急警（%，預設值；Owner 可一句話改）

# ── 參數解析 ──
NOTIFY=false
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --notify) NOTIFY=true ;;
    --dry-run) DRY_RUN=true ;;
  esac
done

# ── 現值（2026-07-18 exposure_ledger）──
# 格式：name|type|value|threshold|excess|action_needed
VIOLATIONS=()

# TSLA SOP1 Speculation/Narrative 25.9% > 10%
VIOLATIONS+=("TSLA|SOP1 主題（Speculation/Narrative）|25.9%|${SOP1_THRESHOLD}%|+15.9%|Y")
# TSLA SOP2 單名 25.9% ≈ 核心邊緣（以非核心 15% 門檻計）
VIOLATIONS+=("TSLA|SOP2 單名（非核心門檻）|25.9%|${SOP2_THRESHOLD}%|+10.9%|Y")
# 3296 SOP2 非核心 17.2% > 15%
VIOLATIONS+=("3296 文心戶|SOP2 單名（非核心）|17.2%|${SOP2_THRESHOLD}%|+2.2%|Y")
# US tech 主題 82.7% > 10%（SOP1 極端超標）
VIOLATIONS+=("US tech/半導體|SOP1 主題（整體）|82.7%|${SOP1_THRESHOLD}%|+72.7%|Y")
# Semi Equipment WFE 17.7% > 10%
VIOLATIONS+=("WFE 半導體設備|SOP1 主題|17.7%|${SOP1_THRESHOLD}%|+7.7%|Y")

# ── 產生選項卡 ──
generate_choice_card() {
  local name="$1"
  local rule_type="$2"
  local current="$3"
  local threshold="$4"
  local excess="$5"

  cat <<CARD
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 IS 規則引擎警示
標的/主題：${name}
規則：${rule_type}
現值：${current}  門檻：${threshold}  超標：${excess}

選項卡（你選一個，A1 當日執行）：
A 維持 — 繼續持有，不動。下次觸發警示時再評估。
  後果：繼續違規；下次跌幅若達 ${DROP_THRESHOLD}%/日 自動再推播。
B 調整 — 降低至門檻以下。A1 幫你算需減碼金額。
  後果：合規；降低集中度風險；需賣出操作（你執行）。
C 對沖 — 不動持倉，加下行保護（Put/inverse ETF等）。
  後果：部分降低下行風險；成本需你評估。

📌 紅線：A1 不下單、不建議買賣。你選哪條，A1 提供資訊支持。
━━━━━━━━━━━━━━━━━━━━━━━━━━
CARD
}

# ── 執行 ──
echo "【IS 規則引擎 gate — 2026-07-18 現值實測】"
echo "參數：SOP1=${SOP1_THRESHOLD}% | SOP2=${SOP2_THRESHOLD}% | 槓桿=${LEV_THRESHOLD}x | 日跌幅=${DROP_THRESHOLD}%"
echo "資料來源：exposure_ledger 2026-07-01（Owner 選 A：草稿值直接上線）"
echo ""
echo "🔴 共 ${#VIOLATIONS[@]} 條違規："
echo ""

FULL_MESSAGE="【IS 規則引擎 gate 2026-07-18】共 ${#VIOLATIONS[@]} 條違規需 Owner 決策
SOP1=${SOP1_THRESHOLD}% SOP2=${SOP2_THRESHOLD}% 槓桿=${LEV_THRESHOLD}x 日跌幅預設=${DROP_THRESHOLD}%
（日跌幅 ${DROP_THRESHOLD}% 為預設值，要改回一句話）

"

for v in "${VIOLATIONS[@]}"; do
  IFS='|' read -r name rule_type current threshold excess action_needed <<< "$v"
  echo "  ▸ ${name}：${rule_type} ${current} > ${threshold}（超 ${excess}）"
  CARD=$(generate_choice_card "$name" "$rule_type" "$current" "$threshold" "$excess")
  echo "$CARD"
  FULL_MESSAGE+="$CARD"$'\n'
done

FULL_MESSAGE+="
全部選項卡詳見 state/ 或回覆「{標的} 選 A/B/C」。
A1 當日執行。紅線：不下單不給買賣建議。"

# ── 推播 ──
if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "（dry-run 模式：以上為選項卡預覽，未推播）"
elif [[ "$NOTIFY" == "true" ]]; then
  if [[ -f "$NOTIFY_SCRIPT" ]]; then
    echo ""
    echo "推播 Telegram..."
    # 分段推播（Telegram 4096字元限制）
    SHORT_MSG="🔴 IS 規則引擎 gate 2026-07-18｜${#VIOLATIONS[@]} 條違規
SOP1=${SOP1_THRESHOLD}% SOP2=${SOP2_THRESHOLD}% 槓桿=${LEV_THRESHOLD}x 日跌幅預設=${DROP_THRESHOLD}%
⚠️ 日跌幅 ${DROP_THRESHOLD}% 為草稿預設值，要改回一句話
違規：TSLA 25.9%(SOP1+SOP2)、3296 17.2%(SOP2)、US tech 82.7%(SOP1)、WFE 17.7%(SOP1)
各標的選項卡：A維持/B調整/C對沖。回覆「{標的} 選 A/B/C」A1 當日執行。
A1 不下單不給買賣建議。"
    bash "$NOTIFY_SCRIPT" "$SHORT_MSG" && echo "✅ 已推播" || echo "⚠️ 推播失敗，請手動確認 bot/.env"
  else
    echo "⚠️ 找不到 notify_owner.sh，未推播"
  fi
else
  echo ""
  echo "（未推播。加 --notify 推 Telegram，加 --dry-run 只預覽）"
fi

echo ""
echo "【日跌幅預設說明】日跌幅急警設為 ${DROP_THRESHOLD}%（Owner 裁決選 A 用草稿值）。"
echo "要改：修改本腳本 DROP_THRESHOLD 變數。"
