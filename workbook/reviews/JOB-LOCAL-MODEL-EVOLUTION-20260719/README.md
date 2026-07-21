# JOB-LOCAL-MODEL-EVOLUTION-20260719

Local Model Evolution Orchestrator 第一輪執行紀錄。依據 Draft PR #20
`LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`，在分支
`claude/local-model-evolution-orchestrator-puvj7d` 執行。

**一句話結論**：骨架、Quota Sentinel、兩個 P0 curriculum、eval harness 全部
建立並可執行驗證；真實地端模型 baseline 因這個 remote 沙盒沒有 Ollama/Mac mini
runtime 而 blocked——沒有假造任何 baseline 數字。

## 檔案索引

| 檔案 | 內容 |
|---|---|
| `runtime_capability_check.md` | 環境盤點摘要（指回 canonical report） |
| `quota_source_matrix.md` | Quota Sentinel 資料來源優先序 + 治理衝突發現 |
| `provider_status.json` | quota_sentinel.py 執行結果快照 |
| `RUN_PLAN.md` / `STATE.md` | 指回 canonical 檔案（避免平行真相源） |
| `curriculum_inventory.md` | 兩個 curriculum 盤點表 |
| `dataset_manifest.json` / `eval_manifest.json` | 資料集與 eval set 清單 |
| `baseline_report.md` | 指回 canonical baseline 報告（blocked 狀態） |
| `candidate_report.md` | 無候選（尚未有 baseline 可比較） |
| `shadow_report.md` | 未進入 shadow（無候選） |
| `model_registry.json` | registry 快照，candidates 為空 |
| `security_review.md` | 安全紅線逐項自查 |
| `weekly_governance_review.md` | B2/B3/B4 視角治理回顧 |

## Canonical 工作目錄

`local_model_evolution/`（本檔案只作 job-time receipt 快照，正式維護入口見
`local_model_evolution/RUN_PLAN.md` + `local_model_evolution/state/STATE.md`）。

## Next exact cycle

在 Mac mini Remote Codex 上重跑，見
`local_model_evolution/evals/baseline_report.md` 第 3 節的具體指令。
