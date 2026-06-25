# Culture Compounding Loop — 治理 Skill

版本：v1.0 | 建立：2026-06-26 | 維護：A1
觸發條件：任何「失敗回收→規則蒸餾→複利寫回」需求；每日地端例行巡查閉環

> **核心設計原則**（照 company-values.md §8）：
> 地端模型跑 routine 評分/分類/寫回。
> Claude 只在「蒸餾規則」「例外判斷」介入。
> 製作者不評自己——獨立驗證者是沒做這件事的另一個模型呼叫。

---

## 蓋在現有迴圈上（不另起爐灶）

現有 reaction ledger 迴圈（T-A1-LEARNING-LOOP-001）：
```
感測 → 分流 → 執行 → 人工確認 → 失敗回收 → 版本更新
```

本 Skill 在現有迴圈「確認」和「回收」之間插入三層：
```
感測 → 分流 → 執行 →【②獨立驗證評分】→【③五階段記憶】→【④複利寫回】→ ⑤閉環路由 → 版本更新
```

reaction_ledger.jsonl 仍是唯一真相源；本 Skill 只 **追加** STATE + 規則，不取代任何既有欄位。

---

## ① 感測（眼見為憑）

**只接受可驗證的硬證據，禁收 agent 自述。**

### 合法證據來源（按優先順序）

| 來源 | 讀法 | 禁忌 |
|------|------|------|
| `git log --oneline -10` | 實際 commit hash + 訊息 | 不算「我做了這件事」 |
| `workbook/learning_loop/reaction_ledger.jsonl` | open reaction 原始 JSON | 不算 summary 的二次摘要 |
| `workbook/hermes/patrol/latest.json` | patrol 產出的 JSON state | 不算 latest.md（二次渲染） |
| Task card 原文 | 讀 `handoff/tasks/T-*.md` 的 `狀態` / `最後活動` | 不算 agent 口頭描述 |
| Telegram readback | bot log 或截圖路徑 | 不算「我有發」 |
| 測試 receipt 檔案 | `workbook/reviews/JOB-*/` 的 `Tests run` 區塊 | 不算 task card 裡的「已測試」字樣 |

### 感測腳本（§8 地端執行）

```bash
cd /Users/pagemacmini/maplab-ai-handbook
python3 scripts/culture_loop_runner.py --mode sense --output workbook/learning_loop/culture_loop_state.md
```

sense 模式輸出：
- 最新 10 個 commit（hash + msg）
- 所有 `status=open` 的 reaction 條目
- 每個 reaction 對應的 `evidence_path` 檔案內容摘要

---

## ② 獨立驗證者評分

**製作者不評自己。用一個「沒做這件事」的地端模型呼叫，只看證據。**

### 評分維度

每個 open reaction 獨立打分（0-5 整數）：

| 維度 | 說明 | 0 | 5 |
|------|------|---|---|
| **evidence_quality** | 有沒有 repo artifact 作為證據 | 只有 agent 說「做了」 | commit + receipt + readback 三層都有 |
| **pltr_readiness** | PLTR 前線測試：今晚客戶現場要用，資料流/介面/證據/操作節點修好了嗎？ | 還沒 | 全部可驗證 |
| **rule_compliance** | 符合 company-values.md 哪條原則，違反了哪條 | 違反多條 | 完全符合 |

**PLTR 前線測試定義**（每次必答）：
> 假設今晚 Owner 要現場向客戶展示或操作這個功能，以下四點全部為 Yes 才算通過：
> 1. 資料流：輸入→處理→輸出路徑可走通（有 DB preview 或 receipt）
> 2. 介面：owner-facing surface（Telegram/Sheet/Extension/Dashboard）有可驗證截圖或 readback
> 3. 操作節點：所有需要 Owner 手動執行的步驟都已明確列出且可做到
> 4. 文件：有 task card 接續點 + 下一步，不需要讀 agent 記憶

### 地端 Ollama 呼叫格式

```python
# runner 內部用法（不需 Claude）
ollama run qwen2.5:14b \
  --system "你是 MAPLAB 獨立稽核員。你沒有參與本輪任何工作。只看證據，不接受 agent 自述。按格式輸出 JSON，不加任何說明。" \
  "$EVIDENCE_PROMPT"
```

輸出格式（只輸出 JSON）：
```json
{
  "reaction_id": "...",
  "evidence_quality": 0-5,
  "pltr_readiness": true/false,
  "rule_compliance": 0-5,
  "pltr_fail_reasons": ["..."],
  "violated_principles": ["company-values §N: ..."],
  "verified_facts": ["..."],
  "escalate": true/false,
  "escalate_reason": "..."
}
```

`escalate = true` 條件：`evidence_quality <= 1` 或 `pltr_readiness = false 且 severity=high` 或 `rule_compliance <= 1`

---

## ③ 五階段記憶

reaction 從 open 到 closed 必須走完五階段。跳段不算完成。

```
Fail        → 記錄在 reaction_ledger.jsonl（已有）
Investigate → 問「為什麼壞？根因在哪個系統層？」（runner 填 investigated_at + root_cause）
Verify      → 診斷變查核過的事實（填 verified_facts，必須有 commit/file/log 作為指向）
Distill     → 升通則：「下次遇到 X 情境，應該做 Y，不做 Z」（填 distilled_rule）
Consult     → 寫回 pitfalls.md 或對應 Skill，下輪 cold-start 先讀
```

STATE 檔格式（`workbook/learning_loop/culture_loop_state.md`）：

```markdown
## Verified facts
[只放已有 evidence 指向的確認事實]

## General rules（蒸餾通則）
[每條通則一行，格式：情境 | 規則 | 出處 reaction_id]

## Open failures
[未進入 Verify 的 open reactions，含 stage 標記]

## Lessons learned
[已 Distill 並已 Consult（寫回）的規則，含日期]

## Last session
[上次 runner 執行時間 + 輸入 + 輸出摘要]
```

---

## ④ 複利寫回

蒸餾出的通則**不只寫 log**，必須 append 到可被 cold-start 讀到的位置。

### 寫回規則

| 通則類型 | 寫回目標 | 格式 |
|---------|---------|------|
| 跨任務失敗模式 | `pitfalls.md` | `## YYYY-MM-DD — 標題 \n 觸發條件 / 根因 / 解法 / 預防` |
| 角色特定操作規則 | `skills/{對應 skill}/SKILL.md` 末尾 | `### 補充規則 YYYY-MM-DD` |
| 企業文化違反 | `docs/company-values.md` 變更紀錄 + 對應段落 | 版本 + 日期 + 新條款 |
| IOS 路徑的規則 | `pitfalls.md` + T-A1-LEARNING-LOOP-001 備註 | 同 pitfalls 格式 |

### 觸發條件

- `distilled_rule` 不為空 且 `evidence_quality >= 3`  → runner 自動 append 到 pitfalls.md
- `distilled_rule` 不為空 且 `evidence_quality >= 4` 且 涉及特定 Skill → runner append 到 Skill
- `rule_compliance <= 2` 且有 verified_facts → ESCALATE 給 Claude，Claude 決定是否更新 company-values

### 禁止事項

- 禁止只把規則寫進 STATE 檔或 reaction log 而不寫到 pitfalls/skill
- 禁止把「建議以後這樣做」放在 Telegram 或聊天訊息就算數
- 禁止重複 append 相同通則（runner 先 grep pitfalls.md 確認唯一性）

---

## ⑤ 閉環 + 成本路由

### 停止條件（/goal）

以下任一條件滿足才算「本輪 reaction 完成」，否則不得關閉：
1. **修好附證據**：`evidence_quality >= 3` 且 `pltr_readiness = true` 且 commit hash 指向修復
2. **寫成規則升級**：`distilled_rule` 已 append 到 pitfalls.md / Skill（附行號驗證）

若兩條都不滿足：reaction 維持 `status=open`，進入 escalation_queue.jsonl。

### 成本路由表

| 任務類型 | 執行者 | 頻率 |
|---------|-------|------|
| 感測 + 讀 ledger + 產 evidence_prompt | 地端 qwen2.5 | 每日 launchd |
| 獨立評分（evidence/pltr/rule） | 地端 qwen2.5 | 每日 launchd |
| Append pitfalls / STATE 更新 | 地端 Python3 script | 每日 launchd |
| Escalation queue 消化 | **Claude** | escalate=true 時通知 |
| 蒸餾規則（判斷是否升 company-values） | **Claude** | escalation 時 |
| Owner 5min actions（OAuth/Telegram/物理操作） | **Owner** | 只在 owner_5min 決策時 |

### Escalation 格式（`workbook/learning_loop/escalation_queue.jsonl`）

```json
{
  "reaction_id": "...",
  "escalated_at": "ISO8601",
  "escalate_reason": "...",
  "evidence_quality": 0-5,
  "pltr_readiness": false,
  "verified_facts": ["..."],
  "suggested_next": "請 Claude/Owner 做：...",
  "status": "pending"
}
```

---

## 地端 Handoff Prompt（可直接貼給 qwen2.5）

```
你是 MAPLAB Culture Compounding Loop 獨立稽核員。
你沒有參與任何本輪的 MAPLAB 工作任務。

你的唯一任務：依據以下「證據清單」和「評分基準」對每個 open reaction 評分。

【評分基準】
- evidence_quality (0-5): 是否有 commit hash / receipt file / DB preview / readback 作為證據？只有 agent 自述 = 0。
- pltr_readiness (true/false): 假設今晚客戶現場要操作此功能，資料流/介面/操作節點/文件是否全部可驗證？
- rule_compliance (0-5): 是否符合 company-values.md 核心原則（增量保存/回報/不做白工/記錄/測試 receipt）？
- escalate (true/false): evidence_quality<=1 或 (pltr_readiness=false 且 severity=high) 或 rule_compliance<=1

【禁止事項】
- 不接受「agent 說做了」作為證據
- 不給比證據更高的分數
- 不輸出 JSON 以外的任何文字

【輸出格式】
[{"reaction_id":"...","evidence_quality":N,"pltr_readiness":true/false,"rule_compliance":N,"pltr_fail_reasons":["..."],"violated_principles":["..."],"verified_facts":["..."],"distilled_rule":"...或空","escalate":true/false,"escalate_reason":"...或空"}]

【證據清單】
{EVIDENCE_JSON}
```

---

## 接上現有 ledger 的操作

```bash
# 1. 感測 + 評分（地端，不需 Claude）
python3 scripts/culture_loop_runner.py --mode full \
  --ledger workbook/learning_loop/reaction_ledger.jsonl \
  --output workbook/learning_loop/culture_loop_state.md

# 2. 手動觸發（測試用）
python3 scripts/culture_loop_runner.py --mode dry-run

# 3. 查看 escalation queue
cat workbook/learning_loop/escalation_queue.jsonl | python3 -m json.tool

# 4. 查看 distilled rules（已 append 到 pitfalls）
grep -A5 "culture-compounding" /Users/pagemacmini/maplab-ai-handbook/pitfalls.md
```

*觸發條件：reaction ledger 有 open 項、或 patrol 有 severity=high 新偵測、或 Owner 要求審計*
*地端模型：qwen2.5:14b via Ollama（http://127.0.0.1:11434）*
*Claude 介入條件：escalate=true 或蒸餾規則需要判斷是否升 company-values*
