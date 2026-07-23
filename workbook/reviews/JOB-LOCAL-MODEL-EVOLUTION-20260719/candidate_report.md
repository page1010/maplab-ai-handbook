# Candidate Report — JOB-LOCAL-MODEL-EVOLUTION-20260719

## 狀態：無候選

第一輪沒有建立任何模型/adapter/prompt 候選版本。原因：`models/registry.json`
明文要求「沒有 baseline、固定 eval、資料權利與 rollback 前，不得開始 LoRA」，
而本輪連 Level A（prompt/skill）候選都還沒有——因為沒有真實地端模型可以
在此沙盒測試任何候選是否比 baseline 好。

下一輪在 Mac mini 取得真實 baseline 後，才會在這裡記錄第一個 Level A 候選
（預期形式：prompt template 或 metadata hard filter，見
`local_model_evolution/reports/latest.md` §第一版改善方案）。
