# Extension Agent 召喚技能書 — MAPLAB Agent Commander

版本：v2.1 | 更新：2026-05-29 | 維護者：A1

## 目的

Chrome Extension（MAPLAB Agent Commander）現在以 dynamic role task modules 為主，不再只從 `AGENT_RECALL_PROMPTS.md` 抽一段 prompt。

Extension 會讀：

- `chrome-extension/task-modules/index.json`
- `chrome-extension/task-modules/{role}.json`
- `CURRENT_STATUS.md`
- `recalls/{role}_recall.md`

召喚結果是一份 platform-neutral runtime handoff，可貼給 Gemini / Codex / OpenClaw / legacy Claude tab。

## 召喚步驟

### Step 0. Agent 先讀技能，不准卡在 UI

如果 Owner 提到 `extension`、`召喚`、`Agent Commander`、`角色通路`、`handoff`、`A2/A4/A8/B1 交接`，目前負責的 agent 必須先讀本技能書，再決定怎麼召喚角色。

Chrome Extension 是通路與介面，不是唯一可操作表面。若 Codex / OpenClaw / 其他 runtime 不能直接打開 `chrome-extension://.../popup.html`，不得把這當成 blocker，也不得要求 Owner 代替 agent 做本來可由檔案完成的交接。

請改走 file-backed summon：

1. 讀 `chrome-extension/task-modules/index.json`。
2. 讀 `chrome-extension/task-modules/{role}.json`。
3. 讀 `workbook/task_modules/role_module_build_report.json`，確認 module 產物存在。
4. 依 `popup.js` 的 `buildModuleHandoff()` 結構組成 runtime handoff。
5. 把本次召喚任務放進 `## 1.1 本次召喚任務`。
6. 直接交給相應 runtime / subagent，並要求它先回覆 Startup Check 與交接驗收。

判準：有沒有完成「角色收到 handoff 並回報」；不是有沒有成功打開 extension popup。

### Step 1. 開啟 Extension

在 Chrome 點擊 MAPLAB Agent Commander 圖示。

### Step 2. 確認 GitHub 連線

Extension 預設從：

`https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main`

讀取 module index 與 `CURRENT_STATUS.md`。若頂部顯示載入失敗，先檢查 Raw Base URL 或 GitHub token。

### Step 3. 選角色

下拉選單由 `chrome-extension/task-modules/index.json` 動態生成。A 系列是 MAPLAB 角色；B 系列是 Investment OS / cross-project 角色。

### Step 4. 輸入召喚任務

在 `召喚任務` 欄位輸入本次要交辦的目標。若不確定該選哪個角色，按 `自動選角`；Extension 會依任務文字切到 A2 / B1 / B2 / B3 / B4。

### Step 5. 選 runtime target

可選：

- Gemini 側邊欄
- Codex / A1
- OpenClaw / A6
- Claude tab（legacy）

### Step 6. 複製任務模組 Handoff

點「複製任務模組 Handoff」。被召喚的 agent 必須先回答：

1. 我是什麼角色。
2. 我會先讀哪些來源。
3. 這次產出會影響哪些角色/檔案/系統。
4. 產出會寫到哪裡。
5. 有哪些高風險動作需要 Owner/A1 批准。

## 角色可用清單

| 角色 | Extension 可用 | 正確貼到哪裡 |
|------|---------------|-------------|
| A0 | yes | Cowork / Gemini / Codex |
| A1 | yes | Codex / OpenClaw |
| A2 | yes | Ads / SEO / WordPress patrol；可貼 Chrome/Gemini/Codex |
| A3 | yes | Chrome/Gemini/Codex |
| A4 | yes | Chrome/Gemini/Codex |
| A5 | yes | Chrome/Gemini/Codex |
| A6 | yes | Telegram/OpenClaw/Codex |
| A7 | yes | Chrome/Gemini/Codex |
| A8 | yes | Chrome/Gemini/Codex |
| B1 | yes | Investment OS Builder |
| B2 | yes | Investment OS Reviewer |
| B3 | yes | Investment OS Archivist |
| B4 | yes | Investment OS System Patrol |

## B Role Routing

| 任務 | 召喚 |
|------|------|
| 寫功能、修 bug、接 runtime surface | B1 Builder |
| 查資料流、錯誤、freshness、報告契約 | B2 Reviewer |
| 寫版本紀錄、交接紀錄、resume prompt | B3 Archivist |
| 問系統是否還適合、是否要暫停/縮小/重構 | B4 System Patrol |

## Markdown Freshness

Extension 可檢查 module JSON 內的 `source_sha256` 是否與 GitHub raw Markdown 相同。

v5.6.0 起 task module 會先讀本機 extension 內建檔案，GitHub raw 只作 fallback。本機 repo 改版後只要 reload 現有 unpacked extension，不需要重新下載或重新設定。Role recall 也會在 module 內保留 fallback excerpt，避免 GitHub raw 尚未同步時出現假的 404。

若顯示 Markdown 已變更：

1. 請 A1 在正式 repo 執行 `python3 tools/ai_workbook/build_extension_task_modules.py`。
2. commit / push。
3. reload Extension。

## Guardrails

- GitHub dynamic link 只載入 JSON/Markdown data，不執行 remote JS。
- Credential docs、secrets、`.env`、API keys 不得貼給外部 runtime。
- WordPress 發布、Ads 設定、投資下單、broker/runtime 高風險操作都需要 Owner/A1 批准。
- 召喚 prompt 是 routing envelope；真正 facts 要讀 linked sources。
