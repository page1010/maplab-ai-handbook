# Validation receipt — JOB-LOCAL-MODEL-EVOLUTION-20260719

## What

First-cycle quota truth, two curricula, fixed eval, real local-model baseline,
smallest reversible candidate, and promotion decision are complete.

## Commands and results

| Check | Result |
|---|---|
| `python3 -m py_compile ...` | PASS |
| `python3 local_model_evolution/bin/build_eval_cases.py` | PASS; 20 + 20 cases |
| `python3 local_model_evolution/bin/quota_sentinel.py --dry-run` | PASS; 8 providers, 0 APIs, 0 teacher jobs, blocked |
| `python3 local_model_evolution/bin/run_eval.py --mode baseline --model qwen2.5:14b` | PASS harness; model score 284/320 |
| `python3 local_model_evolution/bin/run_eval.py --mode candidate --model qwen2.5:14b` | PASS; wrapper score 320/320 |
| `python3 -m unittest discover -s local_model_evolution/tests -v` | PASS; 5/5 |
| JSON parse for configs/status/manifests/summaries | PASS |
| relation CSV schema | PASS; 26 rows, 14 columns, one evolution row |
| scoped `git diff --check` | PASS |

## Promotion decision

- Wrapper: `shadow_candidate` for de-identified, file-only reports.
- Local model: no tier promotion.
- LoRA/adapter: blocked.
- Teacher jobs: created 0; executed 0.
- Runtime/scheduler: no production change.

## Root-cause fast path

- `trigger_condition`: report cites a stale/wrong/private/simulated fact, invents
  missing data, or an empty-evidence case is slow.
- `shortest_probe`: rerun the relevant fixed case id and inspect failed checks.
- `known_bad_path`: raw facts -> prompt-only local model -> free-form report.
- `fix_entrypoint`: metadata filter and deterministic contract in
  `local_model_evolution/bin/run_eval.py`.
- `proof_gate`: identical frozen eval, 100% safety checks, no regression.
- `routing`: A1 integrates; B5 reviews data/eval; B2 privacy and B4 quota policy
  gate any expansion.

## Loop Back

Next exact cycle: add a versioned semantic-quality rubric, create two
de-identified file-only shadow reports, review false confidence and usefulness,
then decide whether only the narrative field should route through a local model.
