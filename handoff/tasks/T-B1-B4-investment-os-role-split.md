# T-B1-B4-001 — Investment OS B1-B4 Role Split + Chrome Extension Summon

## 接續狀態
- **狀態**: 🟡 STALLED（since 2026-07-19，48h 無 commit，Owner 可更新最後活動解除）
- **最後活動**: 2026-06-18 B1 Recursive Self-Improvement loop v0
- **接續點**: B1-B4 已不只做角色拆分；新增 RSI-like 成長閉環，下一步是把 scorer 接進排程/Telegram first-screen red item 摘要。
- **阻塞**: 無
- **assigned_session**: 2026-06-11 / B1
- **last_committed_by**: B1 49906f4

建立：2026-05-29
負責：A1 / B role family
狀態：🟢 READY

## Owner Request

Investment OS 接下來固定有四種角色：

- Builder：負責寫功能。
- Reviewer：負責檢查資料流與錯誤。
- Archivist：負責寫版本紀錄與交接紀錄。
- System Patrol：負責定期問「這套東西還適合嗎？」

要求把目前 B1 任務拆成 B1-B4 身份與角色，並讓 Chrome Extension 可召喚。召喚後要認清任務、直接巡查並往目標前進。

## Scope

- 新增 B1-B4 role docs、recalls、shared skill。
- 更新 Chrome Extension dynamic role module generator。
- 重新產出 `chrome-extension/task-modules/B1.json` 到 `B4.json`、index、relation graph。
- 保留原 B1 Investment OS logic bridge 作為 shared source context。
- 不恢復 InnerFlowLab 內容發文。

## Role Mapping

| Role | Name | Output |
|------|------|--------|
| B1 | Investment OS Builder | implementation + validation |
| B2 | Investment OS Reviewer | dataflow/error/freshness review |
| B3 | Investment OS Archivist | version notes + handoff |
| B4 | Investment OS System Patrol | system fitness patrol |

## Done Criteria

- [x] Chrome Extension module index 出現 B1-B4。
- [x] popup 下拉選單可從 module index 讀到 B1-B4。
- [x] B1-B4 handoff 會列出必讀來源、技能組、輸出契約、禁止事項。
- [x] `CURRENT_STATUS.md` / `AGENT_RULES.md` / `AGENT_RECALL_PROMPTS.md` 有 durable 狀態。
- [x] 驗證 JSON / Python / popup JS 皆通過。
- [x] 留下 git commit。

## Active Extension — 2026-06-18 Recursive Self-Improvement

Owner 要求 B1-B4 不只被召喚，而要「像 RSI 一樣」能看出每輪是否更強。B1 v0
落地方向：

- 新增 `projects/invest-os-b-role-recursive-self-improvement.md`，定義 RSI 是 Recursive Self-Improvement。
- 新增 `tools/invest_os/b_role_recursive_self_improvement.py`，讀 nightwatch、background job state、
  local model shadow findings、B1-B4 review bundle recency，輸出 JSON/Markdown。
- B2/B3/B4 角色文件加入 RSI loop 責任：B2 分類 raw finding，B3 保存趨勢與 resume，B4 判讀 continue / pause / refactor。
- 驗收標準：下一輪不能只說「有在跑」；必須用 scorer 證明紅燈變少、分數變高、或明確選擇 pause/refactor。

## Current State — 2026-05-29

- `projects/invest-os-b-role-system.md` 建立 B1-B4 共用底座。
- `projects/b1-invest-os-builder.md` / `b2-invest-os-reviewer.md` / `b3-invest-os-archivist.md` / `b4-invest-os-system-patrol.md` 已建立。
- `recalls/B1_recall.md` 改為 Builder，新增 `recalls/B2_recall.md`、`recalls/B3_recall.md`、`recalls/B4_recall.md`。
- `skills/invest-os-b-role-system.md` 已建立。
- `chrome-extension/task-modules/B1.json` 到 `B4.json` 已重建，`index.json` 顯示 13 modules。
- `popup.js` 會依 module index 動態產生 A/B role groups。

## Guardrails

- 不下單、不建立模擬單、不給買賣建議。
- 不讀 secrets / `.env` / API keys / cookies。
- 不操作 Investment OS broker/runtime 高風險 surface。
- 不把 repo 舊記錄當 live fact。

## Resume Prompt

我是 B1/Codex，接手 `T-B1-B4-001` 的 Recursive Self-Improvement loop。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-B1-B4-investment-os-role-split.md`、`projects/invest-os-b-role-system.md`、`projects/invest-os-b-role-recursive-self-improvement.md`、`skills/invest-os-b-role-system.md`。下一步先跑 `python3 tools/invest_os/b_role_recursive_self_improvement.py --repo-root /Users/pagemacmini/maplab-ai-handbook --output-dir workbook/reviews/JOB-B1-B4-RSI-YYYYMMDD`，再由 B2 分類 shadow concern、B1 修最高影響紅燈、B3 保存本輪趨勢、B4 判斷 continue / pause / refactor。
