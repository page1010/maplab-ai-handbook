# T-B1-B4-001 — Investment OS B1-B4 Role Split + Chrome Extension Summon

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

我是 A1/Codex，接手 `T-B1-B4-001`。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-B1-B4-investment-os-role-split.md`、`projects/invest-os-b-role-system.md`、`skills/invest-os-b-role-system.md`，再檢查 `tools/ai_workbook/build_extension_task_modules.py` 與 `chrome-extension/popup.js`。下一步是確認 B1-B4 module 是否已重新產生、Chrome Extension 是否可召喚 B1-B4、驗證結果是否已寫入 review/commit。
