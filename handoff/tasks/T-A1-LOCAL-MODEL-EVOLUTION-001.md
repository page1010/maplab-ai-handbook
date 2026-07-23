# T-A1-LOCAL-MODEL-EVOLUTION-001 — Narrow-domain evolution loop

## 接續狀態

- **狀態**: 🔄 進行中（第一輪重驗完成；file-only shadow 尚未開始）
- **最後活動**: 2026-07-23 gold-label leakage repaired; live baseline and receipt complete
- **接續點**: 版本化 semantic rubric，產兩份去識別化 shadow report。
- **阻塞**: 非地端 provider remaining quota 全為 `unknown`；只阻塞 teacher jobs，不阻塞 local shadow。
- **assigned_session**: 2026-07-23 / Local Model Evolution Orchestrator
- **last_committed_by**: Codex（scoped Draft PR branch commit）

## Owner 目標

把模型分層、Learning Loop、B5 蒸餾、全局索引、Remote Role Launcher、
Investment OS 與 Google Drive data domains 接成可信的窄域演進管線。優先
Investment current state 與 SEO ranking/keyword，不盲目清空額度，不先做 LoRA。

## 第一輪完成

- [x] Runtime/Drive/SQLite/launchd/training-framework inventory。
- [x] Quota Sentinel dry-run；8 providers/runtimes；0 API、0 teacher jobs。
- [x] 指定 9 個 Drive domains metadata-only 盤點；0 content fetch。
- [x] 兩個 P0 Curriculum，各 20 個 synthetic de-identified cases。
- [x] `qwen2.5:14b` baseline：284/320；safety 206/240。
- [x] top 3：provenance 11、forbidden fact 11、missing honesty 8。
- [x] 2026-07-19 candidate gold-label leakage 已撤回並封坑。
- [x] 重驗 candidate：input-only metadata hard filter + deterministic renderer，320/320。
- [x] 決策：wrapper 可進 file-only shadow；模型不升格；LoRA gate closed。

## Progress Log

| Done | Result | Next | Blocker |
|---|---|---|---|
| First-cycle eval | Fixed baseline/candidate receipts | Add semantic rubric | none |
| Quota truth | Nonlocal remaining = unknown | Await trusted source | teacher jobs only |
| Safety wrapper | 100% fixed safety checks; gold-label mutation test passes | Two shadow reports | none |

## Root-cause fast path

- `trigger_condition`: wrong/stale/private/simulated fact, invented missing data, or empty-evidence timeout.
- `shortest_probe`: rerun one fixed case id and inspect failed checks.
- `known_bad_path`: unfiltered facts -> prompt-only model -> free-form report.
- `fix_entrypoint`: `local_model_evolution/bin/run_eval.py`.
- `proof_gate`: frozen eval + no safety regression.
- `routing`: A1 integration; B5 eval/data QA; B2 privacy; B4 quota/cost.

## Approval gates

Owner approval before paid API calls, teacher execution, unclear-rights dataset
admission, LoRA, schedule install, production writes, publish/Ads/customer/quote
actions, or model promotion.

## Resume Prompt

我是 Local Model Evolution Orchestrator，環境 Mac mini Remote Codex。
先讀 `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、
`LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`、本卡、
`local_model_evolution/state/STATE.md`、`local_model_evolution/reports/latest.md`、
`workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260723/validation_receipt.md`。
第一輪已完成：40-case baseline 284/320，wrapper 320/320；這不是模型升格。
舊版 wrapper 曾讀 expected gold labels，已於 2026-07-23 改為 input-only
metadata/policy gate，並以 gold-label mutation test 封坑。
下一步建立 versioned semantic rubric，產 Investment/SEO 各一份 synthetic
file-only shadow report；不可讀 secrets、不可真實下單/發布/改 Ads/回客戶、
不可執行 teacher jobs 或 LoRA。重跑固定 safety eval，任一 regression 即 rollback。
