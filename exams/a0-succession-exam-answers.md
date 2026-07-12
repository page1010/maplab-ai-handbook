# A0 繼任考試標準答案（不得考前公開）

> 版本：v1.0 | 建立：2026-07-12 | 維護者：A1

---

## Q1（1 分）

**北極星**：「每輪工作後，系統要比之前『更容易持續進步』」

**衡量標準**：複利迴圈是否轉了一圈：
```
輸出落檔 → 週複利蒸餾 → 技能書更新 → 教材固化 → 地端模型繼承
```
不是忙碌量，不是 commit 數，而是「迴圈轉了幾圈」。

來源：`docs/fable5-direction-and-guidance.md` §北極星

評分：1 分（說出量化標準：迴圈 + 不是忙碌量）；0 分（只說「讓系統進步」）

---

## Q2（1 分）

截至 2026-07-12 最新狀態：

**T-A7-001 🔴 ~182h**：
- 問題：A7 客服 FAQ Phase 3 仍未啟動（連續 6 次警告）
- Owner 需做：授權 Mina 使用 `data/a7-reply-templates.md`（5 分鐘）

**T-A6-001 🔴 ~134h**：
- 問題：LINE Webhook URL 未填（bot_a6 在線，但 LINE 方向仍空）
- Owner 需做：到 LINE Developers Console，Channel 1654658337，填入 Webhook URL

評分：1 分（兩個任務都說對 + Owner 行動各一條）；0 分（只說一個）

---

## Q3（1 分）

| | A0 | A1 |
|--|----|----|
| 平台 | Claude Desktop Cowork | Claude Code terminal |
| 特有能力 | Chrome MCP、Notion MCP、Gmail MCP、桌面控制 | git commit/push、shell 腳本、launchd 管理、Telegram bot |
| 不能做 | 直接修 repo（需委派 A1）| Chrome 桌面控制、Notion 直讀（需 A0）|
| 主要職責 | 跨系統橋接、任務派發、存檔監督 | 任務看板、巡檢、bot 維護、版本管理 |

評分：1 分（說出平台 + 至少 2 個「各自能做的差異」）；0 分（只說名稱）

---

## Q4（1 分）

**三類消音**（來源：`docs/fable5-direction-and-guidance.md` §三類消音）：

| 類型 | 定義 | MAPLAB 真實案例 |
|------|------|----------------|
| 第一類：做完沒人知道 | commit 進了 repo，Telegram 沒推播 | 2026-07-08：SEO 三人小組 5 個交付物完成，只用 session 內追蹤，patrol 掃不到，Owner 不知道 |
| 第二類：拍板沒人推進 | Owner 已決策，但沒人開任務卡 | A4 S11 驗收完成但未立即開下一個 Task Card（拖延 T-A4-003/004）|
| 第三類：宣稱未驗證 | 「已完成」但無 diff/log/截圖 | 2026-07-07 A6 bot 修復後腳本測試通過但 Telegram 端對端失敗（diagnose 腳本測錯路徑） |

評分：1 分（三類都對 + 各有 MAPLAB 案例）；0 分（只說定義沒有案例）

---

## Q5（1 分）

**路由規則（來源：`skills/codex-offload-guide.md` §九）：**

| 工具 | 適合任務 | 限制 |
|------|---------|------|
| Codex | 讀 repo、結構化 JSON、Task Card 分析 | 慢，不支援 o4-mini |
| agy | 快速文字生成、翻譯、Owner 問答 | 無法讀本機 repo |

**Claude 額度中斷第一步**：
1. 確認是哪個 Level（A0 中斷 / Claude Code 中斷 / 全部中斷）
2. 根據 `docs/quota-outage-failover-runbook.md` 選對應的接管指令
3. Level 2（Claude Code 中斷）：`codex exec -s read-only ... "$(cat distill/backup-recalls/A1-codex-backup-recall.md)"`

評分：1 分（說出路由差異 + 中斷時第一步查 runbook）；0 分（只說「用 Codex」）

---

## Q6（1 分）

**不算完成。**

閉環流程（來源：AGENT_RULES Section 20 + fable-mindset ⑧）：

1. 派任務（建立發案包：`handoff/dispatch/YYYY-MM-DD-[角色]-[任務].md`）
2. 等 A2 完成並 `checkpoint.sh --notify`（即時 Telegram 推播）
3. A0 在 patrol 稽核確認任務已進 repo（雙層確認）
4. 更新 CURRENT_STATUS.md 任務狀態
5. 如有 Owner 需知的里程碑 → 主動 Telegram 回報

**三類消音第一類的防守**：「派完就算完成」= 做完沒人知道的典型。

評分：1 分（說出發案包 + --notify + patrol 雙層 + CURRENT_STATUS 更新）；0 分（說「派完等回覆」）

---

## Q7（1 分）

**第一步**：先讀 `skills/pitfalls/SKILL.md`（GAS/Sheets/clasp 任務開始前必讀）

**不能直接去修的原因**：
1. GAS 任務前必讀 pitfalls/SKILL.md（CLAUDE.md 強制條款 ⛔）
2. 必須先確認 `.clasp.json` 的 scriptId 指向正確 GAS 專案（報價 vs LINE 對話）
3. 需要先閱讀 CURRENT_STATUS.md 確認 A5 當前狀態（禁止跳過必讀直接操作）

**正確第一步順序**：
1. 讀 `skills/pitfalls/SKILL.md`
2. 讀 `CURRENT_STATUS.md` A5 任務狀態
3. 確認 `.clasp.json scriptId = 1JIiPW_OUwNzB4VHS4k0K...`（報價系統）
4. 再動手

評分：1 分（說出 pitfalls 必讀 + scriptId 確認 + CURRENT_STATUS 先讀）；0 分（說「先診斷問題」但跳過 pitfalls）

---

## Q8（1 分）

**會發生**：
- Mac mini 故障時下一個 Claude Code 無法從紀錄接手（強制存檔規則核心目的）
- Session 內的工作輸出 session 結束後消失
- CURRENT_STATUS.md 可能未更新，下一個 agent 讀到過期資訊

**強制存檔規則（來源：CLAUDE.md）**：

1. 每次完成有意義的變更後執行：
   ```bash
   bash scripts/checkpoint.sh "角色名" "做了什麼"     # 直接進 main（預設）
   bash scripts/checkpoint.sh "角色名" "做了什麼" --notify  # 同時推 Telegram
   ```
2. Session 結束前**至少**執行一次
3. Extension 改動必須更新 CHANGELOG
4. 狀態變了必須更新 RECALL_PROMPTS + CURRENT_STATUS
5. `--notify` flag = 即時 Telegram 推播（防三類消音第一類）

評分：1 分（說出後果 + checkpoint.sh 完整規則 + --notify）；0 分（只說「要 checkpoint」）

---

## 不及格強制流程補讀指引

| 錯題 | 補讀路徑 |
|------|---------|
| Q1 | `docs/fable5-direction-and-guidance.md` §北極星 |
| Q2 | `CURRENT_STATUS.md` ##最緊急任務 + AGENT_RECALL_PROMPTS.md 最頂部狀態 |
| Q3 | `AGENT_RECALL_PROMPTS.md` ## A0 / ## A1 段落 |
| Q4 | `docs/fable5-direction-and-guidance.md` §三類消音 |
| Q5 | `docs/quota-outage-failover-runbook.md` + `skills/codex-offload-guide.md` §九 |
| Q6 | `AGENT_RULES.md` Section 20 + `docs/fable-mindset.md` ⑧ |
| Q7 | `CLAUDE.md` ⛔ 禁止事項段落 + `skills/pitfalls/SKILL.md` |
| Q8 | `CLAUDE.md` 強制存檔規則段落 |
