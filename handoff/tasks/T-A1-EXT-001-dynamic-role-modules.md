# T-A1-EXT-001 — GitHub Dynamic Role Task Modules

## 接續狀態
- **狀態**: 🔄 進行中
- **最後活動**: 2026-07-16 c35f0ee
- **接續點**: （checkpoint.sh 自動補建，請 agent 填寫）
- **阻塞**: 無

狀態：🔄 in_progress
Owner request：把網路上 GitHub Chrome Extension 動態連結改成任務模組，讓 Gemini / Codex / OpenClaw 都能接角色、知道讀什麼、影響誰、產出去哪裡。

## Scope

- 建立平台中立的 role task module，不再把 Claude tab 注入當唯一入口。
- 全角色覆蓋：A0, A1, A2, A3, A4, A5, A6, A7, A8, B1, B2, B3, B4, IOS-MOMENTUM, IOS-KOL, IOS-FB, IOS-ALPHA, IOS-BLACKSWAN, IOS-INVENTORY, IOS-MACRO, IOS-CHIP, IOS-LEFT, IOS-RIGHT, IOS-EVIDENCE, IOS-SIM, IOS-FAMILY, IOS-HEDGE, IOS-SURFACE, IOS-HYGIENE, IOS-SELL, WIN。
- 輸出指向性關聯圖、Excel/CSV 對照表、程式檔關聯面。

## Generated Outputs

- `docs/extension/dynamic-role-task-modules.md`
- `chrome-extension/config/task-modules.json`
- `chrome-extension/task-modules/index.json`
- `chrome-extension/task-modules/{role}.json` for every generated role module
- `workbook/task_modules/role_module_relation_graph.json`
- `workbook/task_modules/role_module_relationships.csv`
- `workbook/task_modules/role_module_relationships.xlsx`

## Guardrails

- GitHub dynamic link = data/config only, not remote JS.
- Credential docs are restricted references, not prompt payload.
- Public/外部 runtime must not receive secrets or internal-only facts.
- Live external systems must be verified via API/UI before treating repo notes as current facts.

## Next Implementation Step

Update Chrome extension UI to add:

1. role module selector
2. runtime target selector: Gemini / Codex / OpenClaw / legacy Claude
3. impact preview panel
4. one-click copy of platform-neutral handoff pack
5. Markdown freshness check so changed `.md` files are detected before dispatch

## Resume Prompt

我是 A1/Codex。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-EXT-001-dynamic-role-modules.md`。
接著讀 `docs/extension/dynamic-role-task-modules.md` 與 `workbook/task_modules/role_module_relationships.csv`。
下一步是修改 `chrome-extension/popup.html` / `popup.js`，讓側邊欄可讀 `chrome-extension/task-modules/index.json`，顯示角色模組、影響關係、runtime target、Markdown freshness，並產生 Gemini/Codex/OpenClaw 共用的 handoff prompt。
