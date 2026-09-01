# Hermes LINE → Sheets checkpoint handoff

Checkpoint: 2026-09-01 Asia/Taipei
Owner boundary: Hermes only asks one question at a time and invokes Sheets. It does **not** quote, choose menus, promise availability or booking, or declare dietary safety.

## Saved and locally verified

- Workbook requested by Owner is closed; no replacement workbook was opened.
- Executable intake state machine, summary confirmation receipt, template router, non-commercial payload and HMAC envelope are saved in `bot_a6/hermes_sheets_assistant.py`.
- Contract/template inventory is saved in `config/hermes-line-sheets-assistant-v1.json`.
- Isolated two-action GAS source is saved under `scripts/apps-script-hermes-sheets/`; it creates a sterile spreadsheet and never copies the legacy master.
- Latest focused run: `15/15 PASS`; nine-turn synthetic intake: one question per turn, complete receipt, no price/menu, network writes `0`.
- Red-team result superseded the earlier `LOCAL_CONTRACT_PASS`: current deploy verdict is `BLOCKED` until the steps below finish.

## Do not stage or deploy

- `scripts/apps-script/Code.gs` still contains the abandoned anonymous-endpoint experiment from the first draft. Restore only this task's diff to `HEAD`; do not deploy or stage it.
- `scripts/apps-script/ApiEndpoint.gs` has already been restored to its prior content.
- No `clasp push`, real Sheet creation, LINE send, customer data egress, model call, optimizer, or Ollama run is authorized.

## Assigned next bounded plan

Assignee: next Codex A1 / Hermes Sheets boundary reviewer.

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`, this checkpoint, the flow doc and machine contract.
2. Remove only the abandoned Hermes hunks from legacy `scripts/apps-script/Code.gs`; prove both legacy GAS files have no task diff.
3. Align isolated GAS and Python exact schemas; re-run JSON, Python AST, Node syntax and focused tests.
4. Add local mocked GAS behavior tests for bad signature, wrong actor/action, expired/replayed nonce, invalid date/headcount, formula injection, idempotent retry and wrong case↔quote lineage.
5. Update `validation_report.md` with fresh commands, counts and hashes; keep verdict `DEPLOYMENT_BLOCKED` unless every local gate passes.
6. Only after explicit Owner authorization: configure an isolated synthetic deployment and read back one sterile Sheet. Never use a real customer or the legacy master.

## Resume Prompt

我是接手 Hermes LINE→Sheets 邊界修正的 Codex / A1，環境 `/Users/pagemacmini/maplab-ai-handbook`。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`、`workbook/reviews/JOB-A6-HERMES-SHEETS-ASSISTANT-20260901/checkpoint_handoff.md`、`docs/hermes-line-sheets-assistant-flow-v1.md`、`config/hermes-line-sheets-assistant-v1.json`。Owner 邊界是「一問一答，只協助調用 Sheets」；禁止報價、選菜、承諾檔期／訂單、飲食安全判定。先清除 legacy `scripts/apps-script/Code.gs` 的 abandoned task diff，再對獨立 `scripts/apps-script-hermes-sheets/` 跑簽章、重放、乾淨表、冪等與 lineage mocked tests。未獲 Owner 明確授權不得 deploy、建立真實 Sheet、開 LINE sender 或外送客資。
