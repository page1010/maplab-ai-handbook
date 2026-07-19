# datasets/ — 訓練樣本存放區

> 狀態（2026-07-19）：**空**。第一輪刻意不建大量 training case，只建 eval cases
> （見 `../curricula/*/evals/`）。這是 `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`
> §十六 第 5 條的明文要求：「每個 curriculum 建立 20–50 個去識別化 eval cases，
> 而非先建大量 training cases」。

## 何時才會有檔案進來

只有在下列條件**全部**成立後，才會開始收集 training/preference sample：

1. 對應 curriculum 已有 Mac mini 上跑出的真實 baseline（非本沙盒的 harness 自我測試）。
2. baseline 的前三大錯誤類型已確認，且 Level A（prompt/skill/routing/validator）
   已先嘗試過一輪。
3. 資料權利邊界清楚：來源是否可合法用於教師蒸餾、是否需要去識別化、是否有客戶個資。
4. 有明確 rollback 與 model registry 機制接住候選版本（見 `../models/registry.json`）。

## 樣本 schema（進資料時必須遵守）

見 `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md` §十：每筆樣本至少含
`sample_id / department / task_type / input / context_refs / expected_output /
teacher_provider / teacher_model / reviewer / created_at / as_of /
source_lineage / freshness_status / sensitivity / usage_rights / label_type /
verification / outcome`。

## 紅線（不得違反）

- 不將客戶姓名、電話、LINE 原文、地址、家庭資料或金融帳戶秘密送進教師模型。
- 送進教師模型前必須去識別化，除非該來源與用途已明確核准。
- `usage_rights` 標 `unknown` 或 `restricted` 的輸出不得加入訓練集。
- 測試集必須時間隔離，不能讓未來資訊洩漏到過去情境。
