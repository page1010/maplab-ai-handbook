# Dispatch Completion Human-Eye Audit — 2026-06-24

Scope: 2026-06-23 night MAPLAB dispatch completion review, plus A2/A8 follow-up checks.

Boundaries: no WordPress login, no publish, no social upload, no runtime DB write, no LaunchAgent change, no secrets, no push, no commit.

## Culture Lens

MAPLAB completion should mean a human can trust the next step, not only that a script or test passed.

Working standard for this audit:

- Truth lives in files and live surfaces, not chat memory.
- Public/live evidence outranks stale planning notes.
- Owner-facing or customer-facing work is not done until it has eye proof on the real surface or is clearly labeled as pending readback.
- Engineering completion, runtime completion, and business completion are separate states.
- A useful "not OK" must name the fix and the next smallest recheck.

## Recheck Evidence

Commands and checks performed in this review:

- KOL tests: `54 passed, 2 warnings`
- KOL live RSS package: BlockTempo live sample `3/3` `rss_fulltext_summary`; SoundOn live sample `3/3` `rss_summary_fallback`; deprecated Twitter/Congress gate confirmed.
- Black swan tests: `15 passed`
- Black swan Phase 1 package: no-write Yahoo `^VIX` 1m quote smoke succeeded; `observed_at=2026-06-24T15:18:46Z`, age `921.439s`, decision `normal/no_realtime_alert`; scoped fetcher tests `11 passed`.
- LINE scaffold tests: `2 tests OK`
- LINE answer-side package: minimum `Account` rows / sent archive / manual labels gate written.
- Pipeline loop closure tests with shared `.venv`: `46 passed, 1 warning`
- Pipeline FIX6 commit-readiness package: targeted tests `46 passed`, `git diff --check` pass, two generated rumour reports marked do-not-stage.
- A2 live ICC front-end title: `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB`
- A2 browser proof: public ICC page H1/H2/CTA visible; screenshot saved at `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/evidence/a2_icc_browser_view.png`.
- A2 `post-sitemap.xml` ICC check: `0`
- A8 v6 ffprobe: `h264`, `1080x1920`, `30/1`, `13.166667`
- A8 visual spot check: v6 contact sheet, cover, and outro frame opened locally.
- A8 approval package: v6 approval card written; status `approval_ready_for_owner_review`; found stale TikTok metadata phrase `動線穩`, weak cover contrast, no audio stream, and no mobile/platform preview proof.

## Completion Verdicts

| Workstream | User-facing verdict | Evidence seen | Not OK / Gap | Optimization and recheck |
|---|---|---|---|---|
| A2 SEO REST plan | Upgraded to `approval_ready`; not WP/GSC done. | `docs/a2a3/a2-rest-inventory-20260624.md`; `docs/a2a3/a2-seo-plan-refresh-20260623.md`; `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/a2_eye_gate.md`; browser screenshot; live ICC title; sitemap count `0`. | Authenticated gates remain: drafts, scheduled/trash, Rank Math, GSC, duplicate drafts. ICC live post is still absent from sitemap. Public page first viewport has a large blank lower area; usable but not polished. | Next: approve authenticated read-only duplicate + Rank Math + GSC + sitemap/indexing gate. Recheck: screenshot/readback, REST ID 1829, sitemap contains ICC, GSC indexed state. |
| A8 folder-to-shorts | Upgraded to `approval_ready_for_owner_review`; not publish-ready. | `publish_readiness_20260624.md`; `publish_approval_card_v6_20260624.md`; local visual frame checks; ffprobe pass. | No mobile/platform preview, no licensed audio, no full moving-video privacy pass, no upload receipt. New issue: TikTok metadata still contains `動線穩`; cover is readable but visually weak. | Next: edit metadata to validator-clean caption, test stronger cover candidate, run mobile/platform preview with no posting. Recheck: phone/platform screenshot or readback before publish claim. |
| KOL RSS source upgrade | Upgraded to live-source `approval_ready`; not production owner-visible. | `/tmp/kol_out.txt`; `live_rss_preview.md`; live BlockTempo 3/3 `rss_fulltext_summary`; SoundOn 3/3 honest fallback; tests `54 passed`. | New issues: BlockTempo extraction includes boilerplate; `$1650` leaked as false ticker-like seed. No Dashboard eye proof, no runtime DB preview, no Telegram/readback. | Next: add boilerplate removal and crypto price-number false ticker suppression tests/fixes; then no-write live preview again. Recheck Dashboard hides deprecated sources in browser before runtime. |
| Realtime black swan | Upgraded to `approval_ready_plus_live_data_smoke`; not realtime alert system. | `/tmp/bs_out.txt`; design doc; `fetch_realtime_vix_quote.py`; `realtime_vix_quote_smoke_20260624.md`; scoped tests `11 passed`. | No `risk_alerts`, no Telegram preview/readback, no LaunchAgent/runtime wiring. Yahoo source still needs repeated freshness/second-source thinking before production. | Next: if approved, design Phase 2 `realtime-alert-json` / `risk-alerts-only`; otherwise only rerun no-write smoke. |
| LINE reply training | Upgraded to `approval_ready / answer_source_identified`; not training-ready. | `/tmp/line_out.txt`; `workbook/a6-training/*`; `line_answer_side_data_gate_20260624.md`; unittest OK. | Need real `Account` rows, sent archive, or 50+ approved manual gold labels. No answer-side data imported. | Next: Owner provides minimum answer-side CSV/archive; recheck schema, pairing, masking, approved labels before training. |
| 6 pipeline loop closures | Upgraded to `commit_ready`; not runtime closure. | `/tmp/ios_fix6_out.txt`; `commit_readiness.md`; targeted pytest `46 passed`; `git diff --check` pass. | Runtime gates remain. Two untracked report artifacts must not be staged: `reports/rumour_heatmap/rumour_heatmap_2026-05-18.md`, `reports/rumour_heatmap/rumour_heatmap_2026-05-20.md`. | Next: scoped commits excluding generated reports; then runtime-safe no-send checks per gate. |
| B2-B4 RSI patrol | OK as read-only diagnostic; not OK as B2/B3/B4 closure. | `/tmp/b2b4_patrol_out.txt`. | It did not write archive/review bundles or fix red gates; it only produced B1 todo. | Next: B1 repairs highest-leverage failures, then B3 archive bundle. Recheck RSI score and file-backed receipts. |
| Codex SSD / memory-watch notes | OK as operational note; not enough evidence here to relabel as completed business task. | Dispatch handoff only. | No current launchd/scheduler readback in this audit. | Next: inspect automation status only if Owner wants system health audit. Recheck should be separate from content/pipeline completion. |

## Problems To Optimize

### 1. Stop using one word for three completion states

Current language says "completed" for worktree patches, design docs, and user-visible outcomes. That hides risk.

Use this state model instead:

- `code_candidate`: tests pass, isolated worktree, no runtime.
- `approval_ready`: Owner can decide the next safe step.
- `runtime_verified`: production/runtime evidence exists.
- `owner_visible_done`: human-facing surface has eye proof or receipt.

### 2. Put eye proof in the task card, not only in chat

For every owner-facing task, add fields:

- `human_surface`
- `eye_proof_path`
- `last_seen_text`
- `pending_visual_readback`
- `next_5_minute_recheck`

### 3. Separate public proof from authenticated proof

A2 is the clean example. Public REST can prove live posts and slug collision. It cannot prove drafts, Rank Math, or GSC. Keep those as separate gates instead of one vague blocker.

### 4. Convert not-OK into the next smallest command

Each incomplete item above has a next small check. This prevents "waiting for Owner" from becoming a parking lot.

## Next Review Order

1. Commit-ready technical candidates after scoped diff review: KOL, black swan scaffold, pipeline fix6.
2. Business-facing proof next: A2 authenticated sitemap/GSC gate, A8 mobile/platform preview.
3. Data-dependent work last: LINE answer-side import, KOL live source preview, black swan intraday quote fetcher.

## Resume Prompt

```text
你是 MAPLAB dispatch human-eye auditor，環境 /Users/pagemacmini/maplab-ai-handbook。
先讀 TASK_QUEUE.md、CURRENT_STATUS.md、pitfalls.md（若存在），再讀 workbook/reviews/JOB-DISPATCH-HUMAN-EYE-AUDIT-20260624/completion_human_eye_audit.md。
任務：把已完成任務分成 code_candidate / approval_ready / runtime_verified / owner_visible_done。
不要發布、不要 push、不要讀 secrets、不要碰 runtime，除非 Owner 明確批准。
優先驗收：A2 authenticated gates、A8 mobile/platform preview、KOL live RSS preview、pipeline fix6 scoped commit readiness。
每個 OK 都要有檔案或 live surface 證據；每個不 OK 都要有下一個最小 recheck。
```
