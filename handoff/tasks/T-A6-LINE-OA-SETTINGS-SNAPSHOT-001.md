# T-A6-LINE-OA-SETTINGS-SNAPSHOT-001

- Owner: Mina / MAPLAB
- Role: Codex A0/A1 system administrator
- Status: `COMPLETE_LOCAL_DB_IMPORTED / LINE_UNCHANGED / AUTO_SEND_DISABLED`
- Started: 2026-10-02
- Completed: 2026-10-02

## Goal / Outcome

以 Chrome 已登入的 LINE Official Account 為眼見來源，唯讀盤點「標籤」與「預設訊息」，加入本機 A6 客服資料庫；不修改 LINE 設定、不發訊、不啟用任何自動回覆。

## Definition of Done

- [x] LINE Chat 設定頁回讀 16 個標籤與聊天室數量。
- [x] LINE Chat 設定頁回讀 28 組預設訊息標題與原文。
- [x] 寫入 gitignored A6 SQLite snapshot，檔案權限為 `0600`。
- [x] 每組預設訊息保留明示使用場景（LINE 標題），政策固定為歷史參考、Mina 人工確認。
- [x] 所有預設訊息 `allowed_for_auto_send=0`；含財務／商務資訊不出現在 Git 或 receipt。
- [x] LINE 帳號零設定修改、零訊息發送、零自動回覆啟用。
- [x] DB 回讀與 17 項相關測試通過。

## Implementation

- Local DB: `data/case-store/a6_case_store.sqlite3`（gitignored）
- Schema / API: `bot_a6/case_store.py`
- One-shot local importer: `scripts/import_line_oa_settings.py`
- Tests: `tests/test_line_oa_settings_import.py`
- Receipt: `workbook/reviews/A6-LINE-OA-SETTINGS-SNAPSHOT-20261002/validation_receipt.md`

## Safety Boundary

- LINE OA 頁面只讀；建立／編輯／刪除／送出／啟用操作皆為 0。
- 原文不進 Git、不送第三方模型、不寫 Google Sheets。
- 舊訊息可能含價格、日期、低消、檔期、訂金、服務承諾與匯款資訊；只作歷史語料，不是現行政策。
- 現行 Hermes contract 仍優先：每輪一題，不報價、不選菜、不承諾檔期／訂單、不判定飲食安全。

## Evidence

- Chrome readback: tags `16`, saved replies `28`.
- Local DB readback: snapshot `1`, tags `16`, saved replies `28`.
- Policy readback: auto-send `0`, human-review `28`, financial-sensitive `4`.
- DB mode: `0600`.
- Focused + adjacent tests: `17 passed`.

## Next Bounded Action

本任務已完成。若 Owner 另行要求 Hermes 使用這批資料，先做離線 title/scenario 檢索與現行 contract 差異報告；未經核准不得接 live LINE sender。

## Resume Prompt

我是接手 A6 LINE OA 設定快照的 Codex。先讀 `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/data-locations.md` 與 `config/hermes-line-sheets-assistant-v1.json`。本機 DB 已有 16 個標籤與 28 組預設訊息，但全部只屬歷史參考且 `allowed_for_auto_send=0`。若要往下做，只能先離線比對現行 Hermes contract 與舊範本風險，不得修改 LINE、發訊、啟用自動回覆或把私密原文送第三方。
