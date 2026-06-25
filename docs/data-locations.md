# MAPLAB 訓練資料位置 & PII 政策

> 建立：2026-06-23 | 維護：A1/A6
> 本文件只記錄路徑與政策，零敏感內容。

---

## LINE 對話原始資料（PII — 絕對本機、永不 push）

| 資料集 | 路徑 | 說明 |
|---|---|---|
| LINE OA 對話 CSV（完整批次） | `/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421/` | 3,625 個 CSV；2026-06-22 匯出；含雙向對話（Account+User）；**唯讀外接硬碟** |
| LINE 配對索引 | `data/line_booking_pairs.csv` | 檔名/日期/confirmed 標記；**不含對話內容**；已 gitignore |
| Case Store SQLite | `data/case-store/a6_case_store.sqlite3` | 案件索引；已 gitignore |
| 對話 seed（本機測試用） | `data/case-store/conversation_log_seed.json` | 已 gitignore |

---

## LINE 訓練產物（去識別化、本機 only、永不 push）

| 產物 | 路徑 | 說明 |
|---|---|---|
| 銷售對話 SOP 狀態機 | `workbook/a6-training/line_sales_sop_state_machine.md` | 7 段狀態機、觸發條件、業務回法；已去識別化；**已 gitignore** |
| QA 訓練範例（去識別化） | `workbook/a6-training/qa_examples_deidentified.json` | 77 筆 stage-labelled 配對；手機/帳號已遮蔽；**已 gitignore** |
| 訓練對原始標籤 | `workbook/a6-training/training_pairs_raw.json` | 150 筆 stage 標籤；供 A6/Owner 審查；**已 gitignore** |

---

## 報價單訓練副本（本機 SSD）

| 資料集 | 路徑 | 說明 |
|---|---|---|
| 本機報價 review bundle | `workbook/reviews/A5-QUOTE-*/` | 50 個資料夾（2026-05 起）；含 draft.md/output.json；**不含 PII**；已進 git |
| 歷史報價檔（待配對） | `/Volumes/MacExternal/` 或 Google Drive `MAPLAB_報價單/` | ~1,250 份；需 orchestrator 橋接 Drive 清單 |
| TimeTree 出餐事件 | `data/timetree_events_2022_2026.json` | 746 events / 392 dates；2022-03 to 2025-06；已進 git（無 PII，只有活動類型/日期）|

---

## PII 政策（所有 Agent 必須遵守）

1. **LINE 對話原始內容**：只在本機讀取，禁止 push、禁止 copy 到 repo 任何路徑、禁止出現在 commit diff
2. **去識別化產物**：即使去識別化，仍視為訓練資料，保持 gitignore、不 push public repo
3. **報價單**：可進 git，但不得包含客戶姓名/電話/地址，只含品項/金額/日期
4. **配對索引（line_booking_pairs.csv）**：已 gitignore；如要修改配對規則，在本機執行腳本，不直接 push 有 contact_name 欄的版本
5. **外接硬碟**：唯讀掛載，禁止任何寫入操作（包括產生 .DS_Store）

---

## 相關技能書

- `skills/a6-local-quote-model-tuning.md` — A6 地端模型調教
- `docs/business-requirements/a6-training-methodology.md` — 訓練方法論（三件套）
- `docs/business-requirements/a6-usage-scenarios.md` — 使用場景 + 14 份歷史報價 sample 分析
- `handoff/tasks/T-A6-001.md` — A6 系統任務卡
- `handoff/tasks/T-A6-002.md` — LINE 對話訓練資料任務卡（暫停，等 Owner 決定匯出方式）
