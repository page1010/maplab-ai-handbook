# T-XXX — 任務標題

> **這是模板，不是任務卡。** 建立新任務時複製本檔到 `handoff/tasks/T-xxx.md`，
> 把下面所有 `[填: ...]` 換成實際內容。本模板擴充現有 task card 慣例，
> 不是另開一套系統——既有的「接續狀態 / 已完成 / Blockers / 接續 Prompt」
> 區塊照舊保留，只是新增 (A)(B)(C) 三個固定區塊與兩個固定欄位。
> 設計來源：`docs/references/ai-agent-long-running-go-feature-rubric.md`。

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**：[填: 🔲待開始 / 🔄進行中 / ⏸️阻塞 / ✅完成]
- **最後活動**：[填: YYYY-MM-DD commit-sha]
- **接續點**：[填: 上次做到哪、下一步是什麼]
- **阻塞**：[填: 無 / 具體阻塞]

---

建立：[填: YYYY-MM-DD] | **Owner 角色（executor）**：[填: 例如 B1] | **Reviewer 角色**：[填: 例如 B2]

---

## (A) Goal / Outcome

[填: 用一句話描述「完成時世界看起來是什麼樣子」，不是「做了什麼動作」。
跟 `templates/go-prompt-template.md` 的 Outcome 是同一件事，可直接複製。]

**範例**：`bot_a6/a5_quote_engine.py` 對任意人數/毛利需求都能產出合法
`createQuoteVariants` payload，且 GAS 回傳 Sheet 沒有空白品項列。

---

## (B) Definition of Done（GO Prompt 五要素）

> 完整填寫說明見 `templates/go-prompt-template.md`；這裡只放摘要 + 連結到實際驗證方式。

| 要素 | 內容 |
|------|------|
| Outcome | [填，同上 (A)，或直接寫「同上」] |
| Verification | [填: 客觀任務 → 寫測試/指令/指標；主觀任務 → 寫「依 `rubrics/<檔名>.md`」，不要把整份 rubric 複製進來] |
| Constraint | [填: 不能動什麼——至少要包含 runtime 資料 / secrets / main，見下方 (C)] |
| Iteration Policy | [填: 每輪 append 到哪份 log，格式同 `templates/go-prompt-template.md` 範例] |
| Error Handling | [填: 什麼情況要暫停回報，見下方 (C)] |

**Verification 類型**（二選一，刪掉不適用的）：
- **客觀任務**：[填: 測試指令 / API 回讀方式 / 量化指標門檻]
- **主觀任務**：依共用 rubric → `rubrics/[填: 檔名].md`
  （rubric 本體放 `rubrics/`，多張 task card 共用同一份，不要內聯複製）

---

## (C) Constraints + Error-handling / Escalation

**Constraints（不能碰什麼）**：
- [填: 本任務專屬禁區]
- 全域硬性禁止見 `AGENT_RULES.md` SECTION 8.5（不刪原始照片、不明文 commit 密碼、
  不自動發布 WP、repo 維持 private 等）
- 無人長跑/background task 額外規則見 `docs/governance/unattended-run-safety.md`

**Error Handling / Escalation（何時停下回報，回報給誰）**：
- [填: 連續 N 輪沒進展 / 碰到禁區 / 驗證工具壞掉 等具體條件]
- 阻塞審查走 `AGENT_RULES.md` SECTION 16 三層審查 SOP：先看自己能不能解
  → 角色內審核理由合理性 → 解除後要推動下一步，不是回報完就結束

---

## 目標

[填: 沿用既有慣例，可與 (A) 重複或更詳細展開]

## 已完成

| Commit | 日期 | 內容 |
|--------|------|------|
| | | |

## 現在卡在哪裡

[填]

## Blockers

[填: 無 / 具體列出]

## 接續 Prompt

```
[直接複製此段貼到下一個 session 即可接手]

你是 MAPLAB [角色編號]。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/T-xxx.md。

上次做到：[填]
下一步：[填]
Blocker：[填]

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
