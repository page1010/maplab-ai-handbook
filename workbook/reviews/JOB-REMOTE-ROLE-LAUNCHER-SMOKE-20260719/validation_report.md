# Remote Role Launcher Validation Report

Date: 2026-07-19

Role: A1 System Orchestrator

Runtime: Codex / Remote Codex

Branch: `codex/system-directory-index-v0-1-20260718`

Result: **PASS_WITH_FOLLOW_UP**

## What

Draft PR #20 的 Remote Role Launcher 能產生 Extension-style handoff，四個手冊 smoke cases 都選到合理角色並帶入必要關聯。

在真正用 launcher 驗證 launcher 自己時，基線曾錯選 B1：`B1:2, B2:2, A1:1`。根因是泛用詞「驗證／實作／runtime」比「Role Launcher／Remote Codex／branch freshness」更容易命中 B-role。

另有一項 freshness 缺口：module 內有 `source_sha256`，但 builder 原本只檢查檔案是否存在，所以過期來源仍標成 `[ok]`。

## So What

- 錯誤角色會讓 Owner 再次負責解釋任務是治理驗證，不是 Investment OS 功能開發。
- 假 `[ok]` 會把「有檔案」誤認成「module 仍新鮮」，違反 generated index 不可取代 live source 的原則。
- 對 Investment OS 而言，錯誤路由可能把本應走 entity／period／freshness hard filter 與 deterministic query 的問題，誤派成泛用模型研究；這會增加張冠李戴與期間錯配風險。

## Now What

本輪採最小修補：

1. A1 增加明確 launcher 治理詞，不改角色架構或通用 tie-breaker。
2. read-first source hash 不一致時標 `stale_hash`；仍讀 linked live source，不自動重建 module。
3. 新增六個 deterministic regression tests，涵蓋四個官方 smoke、launcher 自我驗證與 hash drift。
4. 用 non-force merge 把 feature branch 追上最新 `origin/main`。

## Branch Readback

- Remote feature head before update: `96b412a8715f87240d071ffdf83d39a366afe199`
- `origin/main` used for update: `ee1f854ed9ad0097969f8a3ec5ab2979974d2509`
- Before update: behind 19 / ahead 8
- Merge commit: `a3cfd0c4f90125595502661509c112da27b86b80`
- After update, before validation commit: behind 0 / ahead 9
- Update method: merge `origin/main` into feature branch; no force push and no main merge
- Original dirty main worktree: preserved and not modified
- Validation worktree: `/private/tmp/maplab-system-directory-index-pr20`

## Four Official Smoke Tests

| Test | Task | Selected role | Required evidence | Result |
|---|---|---|---|---|
| A | A6 quote did not write `REVISION_LOG` | A5 | `DRIVE-MAPLAB-SHEET`; A5/A6/A7 relation | PASS |
| B | Drive enterprise-opening assets for SEO/social | A2 | `DRIVE-CASE-ASSETS`; A4 relation | PASS |
| C | IOS-LEFT/IOS-RIGHT freshness and downstream | B2 | `GOV-INVEST-STATE`; `CURRENT_STATE.md`; Investment Decision Loop | PASS |
| D | Global cold-start index for Extension/Remote Codex | A1 | directory, relation, module index, startup protocol | PASS |

Post-fix route candidates:

- A: `A5:1, B2:1`
- B: `A2:1, A3:1, A4:1`
- C: `B2:1`
- D: `A1:4, A0:1`
- Real launcher validation: `A1:5, B1:2, B2:2`

## Freshness Readback

After merging current main, hash comparison found:

| Module | Checked sources | `stale_hash` | Missing |
|---|---:|---:|---:|
| A1 | 26 | 9 | 0 |
| A5 | 27 | 7 | 0 |
| A2 | 32 | 12 | 0 |
| B2 | 22 | 8 | 0 |

This is not silently repaired. The handoff now exposes the drift so A1 can run module regeneration as a separate reviewed task.

## Tests Run

1. `python3 -m py_compile tools/ai_workbook/build_remote_role_handoff.py tools/ai_workbook/test_build_remote_role_handoff.py` — PASS.
2. `python3 tools/ai_workbook/test_build_remote_role_handoff.py -v` — 6/6 PASS.
3. Four exact commands from `docs/remote-role-cold-start-launcher.md` — 4/4 PASS.
4. Required-content assertions over all four generated handoffs — 4/4 PASS.
5. Real launcher validation task reroute — A1 PASS.
6. A1 source hash readback — `stale_hash` visibly emitted PASS.
7. `git diff --check` — PASS after removing one pre-existing trailing space in the PR files.

## Files Actually Read

- `SYSTEM_DIRECTORY_INDEX.md`
- `workbook/system_index/system_relation_index.csv`
- `skills/system-directory-index/SKILL.md`
- `CURRENT_STATUS.md` before and after branch update
- `AGENT_RULES.md`
- `AGENT_STARTUP_PROTOCOL.md`
- `chrome-extension/task-modules/A1.json`
- `recalls/A1_recall.md`
- `skills/task-progress-guide.md`
- `skills/session-lifecycle/SKILL.md`
- `skills/superpowers-guide.md`
- `skills/extension-agent-summon-guide.md`
- `skills/verification-checklist-guide.md`
- `skills/github-api-workflow-guide.md`
- `docs/agent-behavior-framework.md`
- `docs/remote-role-cold-start-launcher.md`
- `REMOTE_CODEX_ROLE_LAUNCHER_PROMPT.md`
- `tools/ai_workbook/build_remote_role_handoff.py`

## Changes in This Validation

- `tools/ai_workbook/build_remote_role_handoff.py`
  - keep launcher/governance validation with A1;
  - report `stale_hash` for drifted module sources.
- `tools/ai_workbook/test_build_remote_role_handoff.py`
  - add deterministic route/relation/freshness regression tests.
- `docs/remote-role-cold-start-launcher.md`
  - remove trailing whitespace;
  - document `stale_hash` handling.
- This review bundle.

## Owner Direction Applied as a Boundary

The Owner clarified that Investment OS is not being built to collect RL／AutoML／RAG résumé terms. Future Investment OS routing must first protect entity, ticker, market, reporting period, document type, freshness, lineage, unit and trust boundary; exact numbers should use deterministic SQLite/API/calculation paths, while narrative research uses hard-filtered documents. Missing verified evidence should return `insufficient_verified_data`.

No financial evidence contract, router, AutoML or RL component was implemented in this launcher-validation task. Hybrid search/reranking remain deferred; production policy remains human-approved.

## Known Follow-ups / Stop Conditions

1. `chrome-extension/task-modules/B5.json` is missing and B5 is absent from the module index although `recalls/B5_recall.md` exists. This remains a declared gap, not a fake B5 launch.
2. Module hashes are stale after current main changes. Run the existing module builder only as a separate scoped task and review its diff; do not hide drift by silently regenerating during launch.
3. Chrome Extension GUI parity was not visually tested; this task validated the file-backed Remote Codex path only.
4. If regenerated modules or relation rows change, rerun all six regression tests and the four full handoff assertions.

## Index Loop Back

- Next agent can find this result without Owner help: yes, via this review bundle and the branch/PR.
- New source discovered: no new truth source.
- New department/role consumers: no; existing A1/Extension/Remote Codex consumers confirmed.
- New upstream/downstream relation: no relation CSV mutation required.
- Incident/prevention added: launcher self-validation misroute now has a regression test; module hash drift is visible.
- Owner burden reduced: Owner no longer needs to correct this launcher-governance task from B1 to A1 or detect stale module hashes manually.
- Index update required: no relation update; module regeneration remains follow-up.
- Automatic rebuild candidate: role module builder, but never silently inside launcher.
- Same problem recurrence risk: low for tested route; medium for unweighted keyword ties outside the regression set.

## Handoff Checkpoint

- Read: files listed above.
- Changed: launcher routing/freshness reporting, tests, manual, this review bundle.
- Tests run: 6/6 regression tests, 4/4 official smoke handoffs, compile, content assertions, diff check.
- Receipt: this file.
- Confirmed: Remote file-backed launcher works for the four documented roles and real A1 validation after the fix.
- Next: review/push feature branch; separately decide whether to regenerate all role modules and add B5.
- Blockers: none for Remote launcher validation.
- Shortest Path: isolate worktree → merge main non-force → run four smoke → fix only proven gap → rerun deterministic tests → save receipt → push feature branch.
- Tool Choices: local Python/CSV/Git readback; no Drive, secret, browser, production API or runtime mutation.

## Resume Prompt

```text
你是 MAPLAB A1 System Orchestrator。
在 branch codex/system-directory-index-v0-1-20260718 接手 Remote Role Launcher。
先讀 workbook/reviews/JOB-REMOTE-ROLE-LAUNCHER-SMOKE-20260719/validation_report.md。
四個官方 smoke 與六個 regression tests 已通過；launcher 自我驗證誤選 B1 與 source hash 假 ok 已修。
下一步只在 Owner/A1另開 scope 後做 module regeneration、B5 module/index 或 Chrome Extension GUI parity readback。
禁止讀 secrets、修改 production、force push 或合併 main。
```
