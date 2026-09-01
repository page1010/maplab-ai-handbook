# Hermes 客服需求釐清到報價 Gym SOP

版本：v2.0（2026-09-01）
範圍：A7／Hermes 客服補問、A6 案件整理、A4 Google Sheets、Mina 人工報價

## 角色與單一真相

- A7／Hermes：對客溝通、辨識意圖、逐輪只問一個缺欄；不得報價、選菜、承諾檔期或判定飲食安全。
- A6：彙整案件欄位、建立可追蹤的 `case_id`，只形成 Sheets intake shell payload。
- A4：以 Google Sheets 保存案件與 Mina 的正式報價；不接受 Hermes 預填價格、菜單、費用、訂金或條款。
- Mina／Owner：確認服務範圍、檔期、價格、菜單、飲食可行性、條款、正式發送與成交狀態。
- A5 舊自動報價引擎不在 Hermes 對客 route 內；`createQuote`／`createQuoteVariants` 均不得由此流程呼叫。

## 需求釐清順序

一次只問目前最前面的缺欄位；不得合併兩題以上。已知資料不得重問。

1. 業務類別：外燴、外帶／餐盒、Candy Bar／甜品桌、企業長期合作。
2. 活動日期。
3. 開始與結束時間。
4. 場地名稱與完整地址。
5. 室內或戶外。
6. 總參加人數。
7. 服務形式：現場外燴、送達擺盤、自取／外帶。
8. 飲食禁忌、過敏、素食與宗教限制；只記客人原話，交真人確認可行性。
9. 樓層、電梯、停車／卸貨、搬運協助。

客人自願提供的預算可保存為 `customer_budget_verbatim`，但不是 Hermes 必問欄位，不得正規化後拿去計價，也不在對客回覆重複金額。

## Sheets-ready 閘門

九類必要欄位全部明示，且客人確認摘要後，才可形成 `createQuoteShell`。缺資料時只輸出：已知欄位、缺欄位、下一題。禁止用今天代替活動日；禁止把「4 位素食」視為總人數；禁止杜撰菜單、價格、檔期、飲食安全與服務承諾。

通過後，A6 形成含 `case_id` 的 intake-only payload，只建立無價格、無菜單、無訂金、無費用、無條款的 Google Sheets 內部空殼。Mina 填寫並核准後才可正式對客發送。

## 報價與日後對帳鍵

最低必要鍵：`case_id + event_date + headcount + business_category`。Mina 建立正式報價後另記 `quote_id`、`quote_url`、`created_at`、`approved_by`。議價／調整固定以 `case_id + quote_id + revision_no` 寫入同一 lineage；Hermes 只附客人原話，不生成新價格或替代菜單。

## Hermes 教學迴圈

1. 教材：抽取已去識別化的欄位模式與 QA 規則，不把客戶姓名、電話、地址送往外部模型。
2. 模擬：以虛構案例逐輪扮演客戶；Hermes 每輪只能問下一個缺欄位。
3. 驗證：檢查欄位正確、無重問、單輪一題、三類越權雷句 hard fail、Sheets-ready 閘門與 payload exact allowlist。
4. 回訓：每一錯誤寫成「觸發條件／錯誤輸出／正確規則／回歸測試」。
5. 升級：連續通過多種業務類別後，才進 Telegram 私有測試對話；正式客戶、正式 Sheet、GAS 部署與 LINE 發送另行授權。

完整流程、Mina 樣板 `*` 盤點與 Mermaid 圖見 `docs/hermes-line-sheets-assistant-flow-v1.md`。

本機單案例：`python3 scripts/run_hermes_intake_gym.py`。此命令零網路、零 Telegram、零 Google Sheet 寫入。
