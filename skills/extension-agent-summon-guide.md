# Extension Agent 召喚技能書 — MAPLAB Agent Commander

版本：v2.2 | 更新：2026-07-18 | 維護者：A1

## 目的

Chrome Extension（MAPLAB Agent Commander）現在以 dynamic role task modules 為主，不再只從 `AGENT_RECALL_PROMPTS.md` 抽一段 prompt。

Extension 會讀：

- `chrome-extension/task-modules/index.json`
- `chrome-extension/task-modules/{role}.json`
- `CURRENT_STATUS.md`
- `recalls/{role}_recall.md`

召喚結果是一份 platform-neutral runtime handoff，可貼給 Gemini / Codex / OpenClaw / legacy Claude tab。

2026-07-18 起，Remote Codex／CLI 另有 file-backed launcher，使用相同 role modules，再加入：

- `SYSTEM_DIRECTORY_INDEX.md`
- `workbook/system_index/system_relation_index.csv`
- `skills/system-directory-index/SKILL.md`
- 該角色的 upstream／downstream、Drive sources、credential routes、incidents 與 loops

## 召喚步驟

### Step 0. Agent 先讀技能，不准卡在 UI

如果 Owner 提到 `extension`、`召喚`、`Agent Commander`、`角色通路`、`handoff`、`A2/A4/A8/B1 交接`、`Remote Codex`、`冷啟動`，目前負責的 agent 必須先讀本技能書，再決定怎麼召喚角色。

Chrome Extension 是通路與介面，不是唯一可操作表面。若 Codex / OpenClaw / 其他 runtime 不能直接打開 `chrome-extension://.../popup.html`，不得把這當成 blocker，也不得要求 Owner 代替 agent 做本來可由檔案完成的交接。

請改走 file-backed summon：

1. 讀 `chrome-extension/task-modules/index.json`。
2. 讀 `chrome-extension/task-modules/{role}.json`。
3. 讀 `workbook/task_modules/role_module_build_report.json`，確認 module 產物存在。
4. 讀 `SYSTEM_DIRECTORY_INDEX.md` 與 `workbook/system_index/system_relation_index.csv`。
5. 依 `popup.js` 的 `buildModuleHandoff()` 結構組成 runtime handoff。
6. 把本次召喚任務放進 `## 0. 本次召喚任務`。
7. 加入該角色匹配的來源、upstream、downstream、Drive、credential、incident 與 loop。
8. 直接交給相應 runtime / subagent，並要求它先回覆 Startup Check 與交接驗收。
9. 任務清楚且沒有高風險 blocker 時，Startup Check 後直接執行，不等待 Owner 重複確認。

判準：有沒有完成「角色收到 handoff、讀懂全貌、回報 Startup Check 並開始執行」；不是有沒有成功打開 extension popup。

### Step 1. 開啟 Extension

在 Chrome 點擊 MAPLAB Agent Commander 圖示。

### Step 2. 確認 GitHub 連線

Extension 預設從：

`https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main`

讀取 module index 與 `CURRENT_STATUS.md`。若頂部顯示載入失敗，先檢查 Raw Base URL 或 GitHub token。

### Step 3. 選角色

下拉選單由 `chrome-extension/task-modules/index.json` 動態生成。A 系列是 MAPLAB 角色；B 系列是 Investment OS / cross-project 角色。

### Step 4. 輸入召喚任務

在 `召喚任務` 欄位輸入本次要交辦的目標。若不確定該選哪個角色，按 `自動選角`；Extension 會依任務文字切到 A2 / B1 / B2 / B3 / B4 與已登記的 IOS 角色。

### Step 5. 選 runtime target

可選：

- Claude Code
- Codex
- GPT / ChatGPT
- Claude Chrome tab
- Antigravity
- Gemini
- OpenClaw
- Hermes
- Gemini Chrome tab

### Step 6. 複製任務模組 Handoff

點「複製任務模組 Handoff」。被召喚的 agent 必須先回答：

1. 我是什麼角色。
2. 我會先讀哪些來源。
3. 哪些部門／角色會使用這些資料。
4. upstream 與 downstream 是什麼。
5. 這次產出會影響哪些角色/檔案/系統。
6. 產出會寫到哪裡。
7. 有哪些 Drive operational sources 與 credential routes。
8. 有哪些高風險動作需要 Owner/A1 批准。
9. 如何驗證與 Loop Back。

## Remote Codex／CLI 一鍵召喚

### 最短路徑

將 `REMOTE_CODEX_ROLE_LAUNCHER_PROMPT.md` 全文貼入 Remote Codex，替換最後的任務。

Remote Codex 應執行：

```bash
cd /Users/pagemacmini/maplab-ai-handbook
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO \
  --runtime codex \
  --task "[任務]" \
  --output /tmp/maplab-role-handoff.md \
  --explain-route
cat /tmp/maplab-role-handoff.md
```

然後讀取該 handoff、切換成選中的角色並直接執行；不得只產生 prompt 後停止。

### 指定角色

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role A6 \
  --runtime codex \
  --task "檢查報價流程並留下驗證 receipt" \
  --output /tmp/maplab-a6-handoff.md
```

### 操作手冊

完整說明：`docs/remote-role-cold-start-launcher.md`。

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
| B5 | index/module 尚需同步 | Shadow Distillation；Remote launcher 可在 module 建立後使用 |

## B Role Routing

| 任務 | 召喚 |
|------|------|
| 寫功能、修 bug、接 runtime surface | B1 Builder |
| 查資料流、錯誤、freshness、報告契約 | B2 Reviewer |
| 寫版本紀錄、交接紀錄、resume prompt | B3 Archivist |
| 問系統是否還適合、是否要暫停/縮小/重構 | B4 System Patrol |
| Recall 品質、能力蒸餾、地端教材 | B5 Shadow Distillation |

## Markdown Freshness

Extension 可檢查 module JSON 內的 `source_sha256` 是否與 GitHub raw Markdown 相同。

v5.6.0 起 task module 會先讀本機 extension 內建檔案，GitHub raw 只作 fallback。本機 repo 改版後只要 reload 現有 unpacked extension，不需要重新下載或重新設定。Role recall 也會在 module 內保留 fallback excerpt，避免 GitHub raw 尚未同步時出現假的 404。

若顯示 Markdown 已變更：

1. 請 A1 在正式 repo 執行 `python3 tools/ai_workbook/build_extension_task_modules.py`。
2. commit / push。
3. reload Extension。

Remote launcher 若 relation rows 為空，必須標 `relation_index_gap=true`，不得猜測；若 Drive 無 live access，標 `drive_live_access=false`。

## Guardrails

- GitHub dynamic link 只載入 JSON/Markdown data，不執行 remote JS。
- Credential docs、secrets、`.env`、API keys 不得貼給外部 runtime。
- WordPress 發布、Ads 設定、投資下單、broker/runtime 高風險操作都需要 Owner/A1 批准。
- 召喚 prompt 是 routing envelope；真正 facts 要讀 linked sources。
- 自動選角若不合理，必須依 module、關聯與任務證據明確改派，不得靜默換角色。
- 召喚成功的標準包括：全貌讀取、關聯載入、Startup Check、開始執行、驗證 receipt 與 Loop Back。
