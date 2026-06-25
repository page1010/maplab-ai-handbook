# Dispatch Packages — 2026-06-24

Purpose: turn the 2026-06-24 human-eye audit gaps into bounded worker packages and recheckable evidence.

Boundaries for all packages:

- No publish, upload, social posting, Telegram live send, broker/order action, runtime DB write, LaunchAgent change, secret read, push, or broad cleanup.
- Do not revert unrelated dirty files.
- Write only the package's assigned output files.
- Every OK needs file/live evidence. Every not-OK needs the next smallest recheck.

## Shared Completion States

- `code_candidate`: code/tests pass in an isolated workspace, no runtime proof.
- `approval_ready`: Owner can decide the next safe action from evidence.
- `runtime_verified`: runtime or production evidence exists.
- `owner_visible_done`: human-facing surface has eye proof or receipt.

## Packages

| Package | Role | Scope | Write target | Done condition |
|---|---|---|---|---|
| A2-EYE-GATE | A2 SEO public/auth gate reviewer | Verify public ICC/pillar visibility, sitemap drift, and authenticated gates that remain. | `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/a2_eye_gate.md` | Clear approval-ready plan for authenticated duplicate, Rank Math, GSC, sitemap/indexing gates. |
| A8-APPROVAL | A8 short-video approval packager | Prepare v6 publish approval card from existing local draft, with human-eye gaps explicit. | `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/publish_approval_card_v6_20260624.md` | Local review package is ready for Owner/A1, without claiming publish-ready. |
| KOL-LIVE-RSS | KOL source-quality verifier | Run no-write live RSS/fulltext preview in `/tmp/wt_kol` and verify deprecated sources stay out. | `/tmp/wt_kol/workbook/reviews/JOB-KOL-LIVE-RSS-20260624/live_rss_preview.md` | At least one real-source row proves `rss_fulltext_summary` or fallback label with diagnostic evidence. |
| BS-VIX-PHASE1 | Black swan realtime Phase 1 worker | Implement or run no-write `^VIX` intraday quote smoke in `/tmp/wt_blackswan`. | `/tmp/wt_blackswan/reports/blackswan/realtime_vix_quote_smoke_20260624.md` plus safe code/tests if needed | Quote JSON shows source, observed_at, current, previous_close/lookback, and decision, or a precise missing-data verdict. |
| FIX6-COMMIT-READINESS | Pipeline closure reviewer | Review `/tmp/ios_fix6_wt` diffs and tests for scoped commit readiness. | `/tmp/ios_fix6_wt/workbook/reviews/JOB-PIPELINE-FIX6-20260624/commit_readiness.md` | File list, tests, residual runtime gates, and recommended commit plan are explicit. |
| LINE-ANSWER-GATE | A6 LINE answer-side gate designer | Turn missing answer-side data into exact import/labeling checklist. | `workbook/a6-training/line_answer_side_data_gate_20260624.md` | Owner can provide the minimum Account-row/archive/manual labels without ambiguity. |

## Main-Agent Integration

Main Codex will:

1. Spawn package workers with disjoint write targets.
2. Run independent safe checks while workers run.
3. Read worker outputs.
4. Update `completion_human_eye_audit.md` with improved states if evidence upgrades any item.
5. Stop only where a gate genuinely needs login, publishing approval, runtime mutation, or source data that is not locally available.
