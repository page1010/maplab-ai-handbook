# Hermes LINE 業務回覆持續訓練計畫

版本：2026-08-28 v2
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

## Plateau 與方法重設規則

- 任兩個 qualification rounds 沒有 verified improvement，停止相同方法；不得只換 seed、sample 或版號繼續消耗 calls。
- Scheduled path 與人工 resume 都必須經 `hermes_line_training_supervisor.py`；任何直接呼叫 raw loop 的 launchd／cron／automation 都是 side door，必須 fail closed。
- `maplab.hermes.line-evaluator.v1` 只有 lexical／length 診斷價值，不能作 promotion gate。已證明無關內容可高分，裸數字也可能繞過 unsupported-money。
- 先用人工結構標籤把 rubric v2 校正到至少 18/20 exact agreement；校正不呼叫模型，也不消耗 training attempt。
- E1 預定只允許變更 `prompt_builder_contract_sha256`；但 v7 尚是 source-bound plan，baseline／candidate full messages 都 `NOT_RENDERED`、shared inputs `NOT_PINNED`、lesson snapshot `NOT_MATERIALIZED`，不得把它說成已可執行的單一變因實驗。
- 執行 E1 前須 materialize owner-only immutable lesson snapshot，對20案逐案render baseline／candidate；兩側的 user message、context、two-shot examples與lesson hashes必須相同，只有prompt-builder contract不同，並pin paired runner source SHA。
- E1 最多 40 次本機 inference；unsafe price／policy、private egress、customer send、manifest drift 任一發生即停。
- E1 的 20-case holdout 是 development evidence，不能算進七連勝；promotion 必須另用預先封存、互不重疊的 balanced panels。

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

- 每日 02:20 只能執行 `scripts/hermes_line_training_supervisor.py` 並帶 canonical job path；禁止 launchd 直接執行 `hermes_line_training_loop.py`。
- 主要狀態：`/Users/pagemacmini/.maplab/a6-hermes-training/loop_state.json`。
- 每輪收據：`/Users/pagemacmini/.maplab/a6-hermes-training/runs/`。
- Supervisor 收據：`/Users/pagemacmini/.maplab/a6-hermes-training/supervisor_jobs/<job_id>/receipt.json`。
- 下一輪教材：`/Users/pagemacmini/.maplab/a6-hermes-training/current_lessons.md`；method redesign 不直接使用這個可變檔，改 pin 最後一輪 immutable lesson delta。

Resume Prompt：

> 我是 Hermes LINE 業務教練。先讀 CURRENT_STATUS、pitfalls、active Task Card、durable job、supervisor receipt 與 v7 method redesign receipt。若 job 要求 schedule gate，先驗 launchd 只走 supervisor，kickstart 必須零新增 calls／round／attempt；不得先跑題。若 gate 已完成，依序完成 rubric calibration、immutable lesson snapshot、paired runner SHA 與共用輸入 rendered prompt manifest，五項 blockers全關閉後才可做唯一變因paired test。所有私密 LINE 素材留在本機，禁止 customer send；E1 dev holdout不得計入七連勝。
