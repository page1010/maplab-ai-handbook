# Validation receipt — JOB-LOCAL-MODEL-EVOLUTION-20260723

## Outcome

The first local evolution cycle is now independently revalidated: live runtime
and named Drive-domain inventories are recorded, Quota Sentinel fails closed,
two 20-case P0 curricula are frozen, the real local baseline is complete, the
top three errors are measured, and the smallest reversible improvement no
longer reads gold labels.

## Commands and results

| Check | Result |
|---|---|
| `rtk python3 local_model_evolution/bin/quota_sentinel.py --dry-run` | PASS; 8 providers/runtimes, 0 usage APIs, 0 teacher jobs, global blocked |
| Drive connector searches with `best_effort_fetch=false` | PASS; all 9 required domains matched; metadata only |
| `rtk python3 -m py_compile ...` | PASS |
| `rtk python3 -m unittest discover -s local_model_evolution/tests -v` | PASS; 7/7 |
| `rtk python3 local_model_evolution/bin/build_eval_cases.py` | PASS; schema 1.1; 20 Investment + 20 SEO |
| `rtk python3 local_model_evolution/bin/run_eval.py --mode baseline --model qwen2.5:14b --run-id 20260723` | Harness complete; 284/320, safety 206/240; one recorded timeout |
| `rtk python3 local_model_evolution/bin/run_eval.py --mode candidate --model qwen2.5:14b --run-id 20260723` | PASS; 320/320, safety 240/240; no model inference |

## Evidence paths

- Runtime: `runtime_capability_report.md`
- Drive scope: `drive_metadata_inventory.md`
- Quota: `quota_sentinel_dry_run.md`
- Eval and improvement: `baseline_and_candidate_report.md`
- Security: `security_review.md`
- Baseline rows: `local_model_evolution/evals/results/baseline_qwen2.5_14b_20260723.jsonl`
- Candidate rows: `local_model_evolution/evals/results/candidate_qwen2.5_14b_20260723.jsonl`

## Decision

- Wrapper: `file_only_shadow_candidate`.
- Model: `no_promotion`.
- Teacher jobs: 0 created, 0 executed.
- LoRA: closed.
- Runtime/production/main branch: unchanged.

## GitHub delivery state

- Remote branch:
  `codex/system-directory-index-v0-1-20260718`.
- PR #20 was closed without merge on 2026-07-21 and remains closed.
- PR #21 was merged on 2026-07-21 from a separate implementation branch.
- This cycle pushed the scoped revalidation commits to the requested remote
  branch. It did not reopen PR #20, create a duplicate PR, merge `main`, or
  resolve the branch's pre-existing merge conflicts.
- A future integration decision should start from current `main` and carry only
  the scoped revalidation diff; do not assume reopening PR #20 is safe.

## One-week MVP

1. Day 1: keep the 40-case v1.1 eval frozen; investigate the Ollama timeout
   without rewriting the failed result.
2. Day 2: add a versioned semantic-quality rubric for usefulness and faithful
   synthesis.
3. Day 3: generate one synthetic Investment and one synthetic SEO file-only
   shadow report.
4. Day 4: B5 reviews provenance, false confidence, and dataset rights.
5. Day 5: rerun all 40 fixed cases plus the semantic rubric; drill rollback.
6. Day 6: measure Owner correction burden on the two shadow reports.
7. Day 7: Owner-facing promote/hold/rollback decision. No automatic promotion.

## Resume Prompt

我是 Local Model Evolution Orchestrator，環境是 Mac mini Remote Codex，
工作分支 `codex/system-directory-index-v0-1-20260718`（原 Draft PR #20 分支）。

冷啟動先讀：
1. `CURRENT_STATUS.md`
2. `pitfalls.md`
3. `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`
4. `handoff/tasks/T-A1-LOCAL-MODEL-EVOLUTION-001.md`
5. `local_model_evolution/state/STATE.md`
6. `local_model_evolution/reports/latest.md`
7. `workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260723/validation_receipt.md`

已完成：Quota Sentinel dry-run（8 providers、0 API、0 teacher jobs）；
Drive 9 個指定域 metadata-only 盤點；40-case v1.1 固定評測；
`qwen2.5:14b` baseline 284/320、安全 206/240；Top 3 =
provenance 11 / forbidden exclusion 11 / missing honesty 8。

重要修正：舊 candidate 讀取 `expected` gold labels，320/320 不可信；
已改成只讀 input metadata + required metrics + action policy，
並新增 gold-label mutation test。新 candidate 320/320，
但它是 deterministic wrapper，不是模型升格。

下一步只做：版本化 semantic rubric；產 Investment 與 SEO 各一份
synthetic/de-identified file-only shadow report；跑完整固定回歸。

GitHub 現況：PR #20 已於 2026-07-21 closed without merge；PR #21 已由
另一分支 merged。不得直接 reopen #20、另開重複 PR 或 merge main；
若要整合，先從 current main 建立乾淨 scoped branch，只帶本次 revalidation diff。

禁止：付費 API、teacher jobs、LoRA、模型自動升格、live order、
外部發布/Ads/GSC 寫入、客戶回覆、正式報價、scheduler install、merge main。
任一 safety regression、權利不明、來源過期或真相混用，立即 rollback。
