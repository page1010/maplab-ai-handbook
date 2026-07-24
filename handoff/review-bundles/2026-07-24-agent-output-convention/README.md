# Review Bundle — Agent 固定存檔規範（2026-07-24）

> **狀態：DRAFT，待 Owner 批准。未 push main、未改動任何既有真相文件。**

## 這個 bundle 提案什麼

把「所有 agent 固定存檔規範」正式寫進治理。規範本體已為草案：
`skills/agent-output-convention.md`（DRAFT）。本 bundle 內是三個**尚未套用**的插入區塊，
每個都標明「插到哪個既有真相文件的哪個位置」，等 Owner 批准後才實際套用。

**未直接改動的既有真相文件**（故意）：`AGENT_STARTUP_PROTOCOL.md`、`AGENT_RULES.md`、
`docs/OPERATING_CULTURE.md`。本 bundle 只提供要插入的文字，不覆蓋原檔。

## 內容

- `AGENT_STARTUP_PROTOCOL.insert.md` — **治本的開工硬檢查**：Step 6 Startup Check 新增
  必填欄 `輸出根目錄`，缺欄或指向他處＝開工檢查不過。
- `AGENT_RULES.insert.md` — 新增 SECTION 26 指向 `skills/agent-output-convention.md`。
- `OPERATING_CULTURE.insert.md` — 新增「原則 5 — 固定存檔」指向同一規範。

## 已完成（可逆、已落地在外接硬碟，非治理文件）

- 建 `/Volumes/MacExternal/MAPLAB_WORKSPACE/{outputs,state,tools,index}` ＋ `README_存檔規範.md`。
- 階段2 複製散落產出進去（複製不刪，原檔全留）；紀錄見該處 `MANIFEST_搬移紀錄.md`。

## Owner 批准清單

- [ ] 同意 `skills/agent-output-convention.md` 去掉 DRAFT 檔頭、進正式技能索引。
- [ ] 同意套用 `AGENT_STARTUP_PROTOCOL.insert.md` 的 Step 6 硬檢查欄。
- [ ] 同意套用 `AGENT_RULES.insert.md`（SECTION 26）。
- [ ] 同意套用 `OPERATING_CULTURE.insert.md`（原則 5）。
- [ ] 批准後另行確認：可清理 `~/.claude/state`、`~/.claude/tools` 及已複製的 session 原檔。
