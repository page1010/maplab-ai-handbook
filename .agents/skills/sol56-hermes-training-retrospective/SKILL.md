---
name: sol56-hermes-training-retrospective
description: Turn Hermes training failures into a repeatable What / So What / Now What learning loop with evidence, method selection, success contracts, and durable prevention. Use for Sol 5.6 訓練 Hermes 經驗談, Hermes 訓練檢討, 企業學習蛛網／經驗學習圈, poor results, misleading round counts, plan-versus-actual drift, new-data decisions, or deciding whether prompt, retrieval, SFT, DPO, or system controls should change; not for routine inference.
---

# Sol 5.6 訓練 Hermes 經驗談

把一次訓練的成功或失敗接回 MAPLAB 的企業學習蛛網，讓事實、方法、根治、驗收與下一次冷啟動彼此相連。

## 先建立真相

開始前先讀 repo 的 `CURRENT_STATUS.md`、`pitfalls.md`、Hermes active Task Card、最新 receipt 與 Resume Prompt。聊天中的「跑了幾輪」「訓練過」「已改善」都只當待驗證說法。

若任務在檢討目前 Hermes 訓練或沿用這次案例，另讀 [Hermes case study](references/hermes-case-study.md)。不要把該案例的數字當成其他模型或任務的通用門檻。

## 建立學習蛛網

每個問題至少要形成這條可追溯鏈：

```text
事實 → 偏差 → 根因 → 方法 → 實驗 → 結果 → 防復發規則 → 測試／收據 → Task／Resume
```

若結論只留在聊天、沒有連到檔案、測試、gate 或下一次冷啟動入口，就還沒形成組織學習。

## What：先發現事實

先區分下列單位，不能互相代稱：

| 單位 | 證明什麼 | 不證明什麼 |
|---|---|---|
| Provider request attempt | 外部 API 被呼叫一次 | 模型學會、案例完成 |
| Example | 一個輸入案例被處理 | 只消耗一次 request |
| Inference／evaluation round | 固定或抽樣案例被產生與評分 | 權重有更新 |
| Optimizer step | 梯度被套用一次 | 業務品質有改善 |
| Training run | 有可保存、可 reload 的權重或 adapter delta | 可上線 |
| Qualification panel | 固定盲測的可比較結果 | 真實使用者會採用 |
| Shadow case | 人工審核下的真實工作表現 | 已授權自動發送 |

只有同時具備 optimizer／gradient 證據、可保存權重 delta、reload proof，才能稱為權重訓練。只有回答變了，不能稱為變好。

建立 `VERIFIED / INFERENCE / MISSING` ledger，至少回答：

1. 原定的成功定義、baseline、固定 holdout 與停止條件是什麼？
2. 實際執行的 command、資料、模型、prompt、seed、evaluator 與 route 是什麼？
3. 哪些權重、資料、規則或程式真的改變？留下 SHA 或 immutable receipt。
4. 結果是整體、各 stage、硬性安全錯誤與人工採用率多少？
5. 計畫與實際從哪一步開始分岔？分岔是誰或哪個 side door 造成？

正式檢討另須列出這條活動量對照，不得混算：

```text
provider_attempt_id → response_id／outcome → example_id → evaluation_round_id
```

retry 與 fallback 各自算一個 provider attempt；同一 example 可以消耗多個 attempts，但只能算一個 example。逐欄回報 attempts、responses、examples、evaluation rounds、optimizer steps、training runs、qualification cases 與 shadow cases；缺 mapping receipt 就標 `MISSING`。

若 rubric、evaluator 或 hard gate 曾改版，必須用同一份凍結 rubric 重評要比較的歷史輸出；沒有重評就把跨版趨勢標成 `INCOMPARABLE`，不得串成進步曲線。

不要用呼叫次數、回答率、單次漂亮輸出、loss 下降或腳本 exit 0 代替業務品質。

## So What：按機制找方法

先畫出原本預期的因果鏈，再標出實際斷點。用以下五問做第一性原理檢查：

1. 真正要改變的使用者行為或業務結果是什麼？
2. 哪個可觀測機制能造成這個改變？
3. 本次實際改變的是那個機制，還是只增加活動量？
4. 若結果偏離，是資料、評分、模型、系統 authority、執行 route 還是治理失效？
5. 下一個實驗要看到什麼結果，才會推翻目前假設？

依失敗機制選方法，不依 GitHub 熱度選工具：

| 失敗訊號 | 優先處理 | 不要先做 |
|---|---|---|
| 捏造價格、政策、檔期、付款 | Runtime authority、retrieval、deterministic guard、轉人工 | 把易變事實背進權重 |
| 重問已知欄位、忘記上下文 | State／slot tracking、prompt contract、context assembly | 盲目擴大模型 |
| 回覆過長、語氣不合、價值順序錯 | 高品質 gold、completion-only SFT；之後才偏好學習 | 只調字數 heuristic |
| Prompt 已清楚但模式仍不穩 | 小型 SFT／QLoRA，固定 base 與 adapter | 重抽 few-shot 當訓練 |
| 有同題 chosen／rejected | DPO；只有獨立好／壞標籤時評估 KTO | 在 SFT 未證明前直接做偏好學習 |
| Reward 可精確驗證的推理任務 | 才考慮 RL／GRPO | 對主觀客服 reward 硬套 RL |
| 工具、權限、路由失效 | 修 system contract 與 regression | 指望蒸餾修好控制面 |

要研究外部論文或 GitHub 時，先完成上述分類，再比較：目標任務、硬體、隱私、資料格式、授權、可回滾性與本機驗證成本。外部方案只是 candidate，沒有本地固定盲測前不能叫解法。

## Now What：判斷是否會再發生，並根治

對每個根因逐一問：相同觸發條件明天再出現時，系統會在造成成本前自動發現、阻擋並指出修復入口嗎？如果答案是否定，還沒根治。

至少建立四層防線：

1. **Detect**：固定 metric、holdout、schema 或 regression 能發現同類錯誤。
2. **Contain**：安全錯誤、資料漂移、manifest 漂移或無改善時 fail closed／停止消耗。
3. **Correct**：改正真正機制；每次實驗只有一個主要變因。
4. **Institutionalize**：更新 `pitfalls.md`、Task Card、receipt、Resume Prompt；只有跨任務可重用的判斷才更新 Skill。

若本次任務是唯讀審查，第四層只輸出 `PROPOSED_WRITEBACKS / NOT_APPLIED`；未獲寫入授權不得把建議冒充已回灌。

下一個 bounded experiment 必須預先寫清楚：

- 假設與唯一主要變因。
- 固定 baseline、holdout 與不可進訓練的案例。
- 需要的最小新資料與資料使用權。
- Outcome metrics、process metrics、硬性違規與停止條件。
- 執行上限、回滾方式、預期 artifact 與接手入口。

連續兩個 qualification experiments 沒有 verified improvement，就停止同方法；不得只換 seed、sample、模型名稱或版號繼續消耗。

## 定義「訓練成功」

成功契約必須同時含成果與過程。

成果面至少包括：

- 相對固定 baseline 的盲測提升，而非單一範例。
- 各重要 stage 不退步。
- 未授權商業事實、隱私洩漏與自動客戶發送為 0。
- 回答當前問題、下一問正確、不重問、長度與語氣符合人工標準。
- 私有 shadow 中 direct-use／minor-edit 採用率達 Task Card 門檻。

過程面至少包括：

- 資料來源、DLP、使用權、conversation-level split 與 holdout 汙染檢查可重建。
- Base、adapter、prompt、evaluator、rubric、seed 與資料 manifest 有版本或 SHA。
- Scorer 先與具名真人校正，安全維度零 mismatch。
- Base／candidate 使用相同輸入做 identity-blind 比較。
- 底層模型降規時，工具、route、authority、權限與 system contract 另做 parity test；語言品質好不能代替系統使用正確。

Task Card 必須在看結果前登記 panel size、paired comparison、最小有意義改善幅度、判定方式與時間窗；樣本不足只回 `INCONCLUSIVE`。可依任務用 paired bootstrap、exact sign test 或逐案 exact agreement，但不得事後挑選最有利算法。

Shadow adoption 的操作定義固定為：

- `direct-use`：在登記時間窗內直接採用，沒有語意、事實、問題或動作修改。
- `minor-edit`：只改錯字、標點、格式或不改變承諾與下一步的語氣；任何事實、必要補問、承諾、CTA 或安全處置改動都算 `major-edit`。
- 分母是所有預先定義的 eligible shadow cases；排除理由與時間窗須事先登記。
- 兩位 reviewer 不一致時依 Task Card 的 adjudicator 規則裁決，不能由模型自行選有利標籤。

## 分開三種 Learning Verdict

每份回報先給一行總判定，分開：

1. `WEIGHT_LEARNING = PROVEN / NOT_PROVEN / FAILED`：只看 optimizer、delta、reload 與固定盲測。
2. `SYSTEM_QUALITY = IMPROVED / NOT_PROVEN / REGRESSED`：看完整 route、authority、安全與人工採用。
3. `ORGANIZATIONAL_LEARNING = INSTITUTIONALIZED / PROPOSED / MISSING`：看 pitfall、gate、receipt、Task／Resume 是否已回灌。

另附 `SAFETY = PASS / FAIL / MISSING` 與 `PROMOTION = ELIGIBLE / BLOCKED`。例如：

```text
WEIGHT_LEARNING_NOT_PROVEN / SYSTEM_QUALITY_NOT_PROVEN / ORGANIZATIONAL_LEARNING_PROPOSED / SAFETY_FAIL / PROMOTION_BLOCKED
```

正式收據依 [machine-readable report schema](references/training-retrospective-report.schema.json) 輸出，並用 `scripts/validate_report.py <report.json>` 驗證 schema 與跨欄位一致性；聊天摘要不能取代該 artifact。驗證失敗時不得發布成功 verdict。

## 只索取最小必要資料

不要先向 Owner 要更多 raw logs。先說明哪個不確定性需要人工資料，優先索取：

1. 固定 holdout 的具名真人 rubric labels。
2. 代表主要失敗類別的「舊答案 → 人工最小修正版 → 原因代碼」。
3. 當期價格／政策／檔期 authority snapshot，或逐欄明示 unknown。
4. 完全不進訓練的 hard negatives 與轉人工案例。

私有資料預設留本機；外送或 teacher 生成前必須有明確授權與 DLP receipt。

## 回報格式

先用一段話講核心經驗，再依序交付：

1. `VERDICT — 三種 learning／safety／promotion`
2. `WHAT — VERIFIED / INFERENCE / MISSING + ACTIVITY MAP`
3. `SO WHAT — 因果斷點與方法選擇`
4. `NOW WHAT — 復發判斷與根治防線`
5. `SUCCESS CONTRACT — 成果、過程與 sample plan`
6. `MINIMUM NEW DATA`
7. `NEXT BOUNDED EXPERIMENT`
8. `RECEIPTS / PITFALL / RESUME / PROPOSED WRITEBACKS`

明確區分：已改善、只完成基礎建設、尚未證明。不要為了讓進度好看，把後兩者改寫成訓練成功。
