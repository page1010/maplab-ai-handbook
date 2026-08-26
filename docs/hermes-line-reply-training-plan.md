# Hermes LINE 業務回覆持續訓練計畫

版本：2026-08-26 v1  
Owner 目標：降低 Mina 重複回覆時間，讓 Hermes 能依歷史最佳實務完成需求釐清、報價前補問與後續追蹤草稿。

## 資料與基準答案

- 真實來源：外接硬碟 LINE OA 匯出，3,625 個對話檔、86,825 列。
- 訓練單位：連續客戶訊息 → 下一段真人業務回覆。
- 去識別化：移除客戶 sender 名稱、以 hash 取代對話 ID；保留業務語意、日期、人數、需求與報價脈絡。
- 現行資料集：20,256 組；train 15,993、eval 4,263。整個 conversation 只會落在其中一側，避免同案答案洩漏。
- Gold answer：Mina 當時的真人回覆。歷史答案不是永遠正確；價格或政策衝突時，以目前 A5／Owner 規則覆蓋。

## 每日訓練迴圈

1. 從 eval 取 12 題，並按 stage 補足稀少類型，不只抽大量 S_PENDING。
2. Hermes 讀最近對話與兩個同 stage 訓練案例，產一則手機可直接使用的回覆。
3. 對照 Mina gold answer，檢查：是否回答當下問題、下一題是否正確、是否重問、日期／人數／預算／飲食是否忠實、是否亂報價格、是否太長。
4. 失分項自動彙整成 `current_lessons.md`，下一輪載入。
5. 每輪保存完整的客戶題目、Hermes 回覆、Mina 原答、provider、分數與錯誤原因。
6. 每週取最低分 stage 做 30 題專項回訓；新規則須有回歸題才可進正式 prompt。

## 驗收指標

- 未授權價格／檔期／政策幻覺：0%。
- 必要語意命中率：≥90%。
- 下一個必要問題正確率：≥90%。
- 已知欄位重問率：≤5%。
- 每次最多問三題：≥95%。
- 綜合 pass rate：先量 baseline，連續 7 輪 ≥85% 才進 Telegram 私有影子測試。
- 影子測試中 Mina 可直接採用或只需小改：連續 50 題 ≥80%，才考慮半自動草稿。
- 正式對客自動發送不是本階段目標；先讓 Mina 少打字、可快速確認後送出。

## 分階段升級

### Phase 1：離線 imitation + correction

每日 12 題，建立 baseline 與錯誤分布。只產收據，不接正式 LINE。

### Phase 2：稀少情境專項

加權抽取菜單調整、飲食過敏、價格異議、取消改期、企業長期合作；避免被大量一般確認訊息稀釋。

### Phase 3：Telegram 私有影子測試

Owner／Mina 貼客人訊息，Hermes 回草稿；同時顯示「已知／缺欄位／建議回覆」。人工確認後才使用。

### Phase 4：節省工時驗證

記錄每題人工從零撰寫時間、採用 Hermes 草稿後修改時間、採用率與修改字數。四週後以每週省下分鐘數判斷是否值得擴大。

## 持續運行與接手 Prompt

- 每日 02:20 執行 `scripts/hermes_line_training_loop.py --batch 5`；每週另跑一次 30 題彙總。
- 主要狀態：`/Volumes/MacExternal/maplab-data/a6-hermes-training/loop_state.json`。
- 每輪收據：`/Volumes/MacExternal/maplab-data/a6-hermes-training/runs/`。
- 下一輪教材：`/Volumes/MacExternal/maplab-data/a6-hermes-training/current_lessons.md`。

Resume Prompt：

> 我是 Hermes LINE 業務教練。先讀 manifest、loop_state、current_lessons 與最新 run。找出最低分 stage 與最常見 missed signal，抽取下一批 12 題執行；不得重用 eval 題當 few-shot，不得杜撰價格。完成後比較本輪與前三輪 pass rate、幻覺率、回覆長度，將一條可重用修正寫入 lessons；若連續兩輪退步，縮到該 stage 五題診斷，不要盲目加大 batch。
