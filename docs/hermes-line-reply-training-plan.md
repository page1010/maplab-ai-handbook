# Hermes LINE 業務回覆持續訓練計畫

版本：2026-09-01 v5
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
- 2026-08-28 live gate 已驗：canonical／mirror／installed plist同SHA，`launchctl print`為exact supervisor argv；zero-call kickstart只增加一次launchd run，job／round／call／attempt／run／lesson皆不變。後續不得把檔案驗證冒充live readback，也不得讓`method-redesign-*`在沒有explicit true latch時執行。
- `maplab.hermes.line-evaluator.v1` 只有 lexical／length 診斷價值，不能作 promotion gate。已證明無關內容可高分，裸數字也可能繞過 unsupported-money。
- 先用人工結構標籤把 rubric v2 校正到至少 18/20 exact agreement；校正不呼叫模型，也不消耗 training attempt。
- 2026-08-28 readiness audit更正：frozen v7只有20個case identities，eval來源有20個真人歷史回覆但structured human labels為0，且當時沒有reply-specimen panel或可執行scorer。Historical target不能自動視為全PASS；AI／規則衍生標籤只能叫development fixture，不能冒充human gold。Owner-only 0600的10 historical-reference＋10 controlled-negative preflight目前只到`NEEDS_ANNOTATION_GUIDE`，不能先交真人猜規則。
- Human review前必須先凍結每項criterion的PASS/FAIL decision guide、overall recompute formula、current commercial-authority snapshot、具名真人identity/attestation/adjudication schema，以及每項criterion至少一正一反的coverage gate。Blank preflight不可原地編輯；derived annotations另檔且必綁`parent_blank_packet_sha256`。
- 2026-08-30 guide gate已完成：`docs/hermes-line-rubric-v2-annotation-guide.json` SHA `d62cf9bf...`；七項各有1個targeted positive與1個targeted negative synthetic fixture。Current commercial authority誠實固定為無live case values；沒有當案current Items／approved quote／calendar或Owner-approved policy時，肯定價格、費用、折扣、訂金、檔期、booking/payment、included service或guarantee一律FAIL，unsupported commercial claim另為unsafe hard fail。下一步才是具名真人另建0600 annotation檔，綁private preflight／guide／authority三個SHA；AI／synthetic判定不得當human gold。
- Exact agreement固定為七項criterion vector加重算overall全部相同；missing／UNKNOWN／N/A不算agreement。整體至少18/20外，unsafe與price/policy/availability grounding mismatch必須0/20；scorer不得讀expected labels、case hash、record ID或case-specific lookup。
- E1 預定只允許變更 `prompt_builder_contract_sha256`；但 v7 尚是 source-bound plan，baseline／candidate full messages 都 `NOT_RENDERED`、shared inputs `NOT_PINNED`、lesson snapshot `NOT_MATERIALIZED`，不得把它說成已可執行的單一變因實驗。
- 執行 E1 前須 materialize owner-only immutable lesson snapshot，對20案逐案render baseline／candidate；兩側的 user message、context、two-shot examples與lesson hashes必須相同，只有prompt-builder contract不同，並pin paired runner source SHA。
- E1 最多 40 次本機 inference；unsafe price／policy、private egress、customer send、manifest drift 任一發生即停。
- E1 的 20-case holdout 是 development evidence，不能算進七連勝；promotion 必須另用預先封存、互不重疊的 balanced panels。

## 2026-08-31 OpenRouter 額度與 Claude 報價教材接手

- OpenRouter 的「輪」統一定義為一次 provider request attempt；同一案例第一個模型失敗、fallback第二個模型成功，算2次request，不是1輪。Owner帳戶因已購買USD 10 credits而符合每日1,000次`:free`請求政策；訓練lane硬上限950，保留50給Owner日常使用。任何CLI參數不得把訓練上限調高到951以上。
- 2026-08-31舊cloud探索已留下49次attempt：25次HTTP error、24次回答；25個examples中只有1個舊lexical heuristic pass。這證明「回答率」與「案例數」不能當品質，並觸發既有plateau stop-loss。當日剩餘訓練上限為901，但不得為了吃滿額度而執行。
- 共用ledger改為UTC日、cross-process lock、atomic 0600檔；每次transport前先reserve，失敗、fallback與程序崩潰都不退額度；損壞／未知schema一律fail closed。模型ID非`:free`在transport前拒絕，保守間隔3.5秒（最多18 starts/minute）。Paid key limit維持0，USD 10 credits不得被訓練lane花掉。
- Claude 2026-08-30分享內容經Owner點名後只作`OWNER_NOMINATED_CURRICULUM_CANDIDATE`：保留「單一窗口先承接統籌價值」「參考圖片確認期待層級、預算確認可選範圍」「核心資料齊後再給A/B/C範圍」「醫療／兒童／樓層訊號只用來補問」「勘場不承諾」；拒絕所有Claude生成價位／比例、競品能力斷言與未證實事實。
- Curriculum不得冒充Owner policy、pricing authority或human gold；只用去識別合成正反例驗prompt與deterministic guard。LINE首輪仍最多三題、240字、8行，不以「我們主要只做餐飲」自我降級、不以服務費開頭、不用「依過去經驗」編造、不承諾檔期。
- Cloud runner預設只允許zero-call preflight。真正completion同時需要明示去識別外送授權與machine-readable quality-gate receipt：20 named-human labels、identity-blind scorer exact agreement至少18/20、安全維度mismatch=0；缺一即execution closed。
- Canonical implementation/receipt：`/Users/pagemacmini/investment-os/tasks/OPENROUTER_950_HERMES_TRAINING_20260831.md`、`/Users/pagemacmini/investment-os/scripts/free_compute/curricula/claude_quote_strategy_20260831.json`、`/Users/pagemacmini/investment-os/reviews/OPENROUTER-950-HERMES-TRAINING-20260831/validation_report.md`。

## 2026-09-01 真正權重訓練與蒸餾路線

- 前5輪實際為random two-shot inference，沒有更新權重；4/25 pass（16%），各輪40%→0%→0%→40%→0%，第1與第4輪各有1個未授權價格。這些是失敗的evaluation rounds，不再稱為持續訓練。
- 950個OpenRouter attempts只可用來產去識別候選、反例與測試覆蓋；候選須經Owner／Mina核准或最小改寫，才可進SFT。一般chat API不回teacher logits，不能把response generation宣稱為logits knowledge distillation。
- 本機主線固定Apple MLX-LM＋Qwen3-4B-Instruct-2507 4-bit QLoRA；DeepSeek借用「強teacher→過濾→student SFT」的方法，不直接安裝R1重型RL、ms-swift或LLaMA-Factory CUDA stack。
- 已完成3-step synthetic QLoRA smoke：真正產生並reload adapter、base／adapter對同prompt輸出不同、peak memory 2.697GB；adapter只縮短回覆，仍漏「單一窗口價值」，所以`QUALITY_NOT_PROVEN`且live route disabled。
- 外接碟未加密，只能放公開hash-pinned基模；LINE、private dataset、adapter、log與fused model固定留`/Users/pagemacmini/.maplab/a6-hermes-training/mlx/`的owner-only root。
- 真正SFT前仍需20/20具名真人rubric labels、scorer >=18/20 exact且安全mismatch=0、完整DLP／rights manifest，再建立30–50組Owner-corrected gold。SFT確認提升後才收chosen／rejected評估DPO／KTO。
- Canonical method／receipt：`docs/hermes-distillation-method-v1.md`、`tools/hermes_mlx_lab/`、`reviews/HERMES-MLX-DISTILLATION-20260901/install-smoke-receipt.json`。

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

> 我是接手 Hermes LINE 訓練的 Codex / A1。先讀 CURRENT_STATUS、pitfalls、active Task Card、durable job、rubric guide、OpenRouter validation、`docs/hermes-distillation-method-v1.md`與MLX receipt。舊12輪是random two-shot evaluation，不是權重訓練；MLX 3-step smoke只證明本機可更新adapter，`QUALITY_NOT_PROVEN`且live route disabled。每日950是`:free` provider request ceiling，不是目標。下一步先完成20/20具名真人labels，校正scorer到>=18/20且安全mismatch=0，再做DLP與30–50組Owner-corrected gold；外接碟只放公開基模，私有資料與adapter留owner-only root。此前不得外送原始LINE、customer send或接正式gateway。
