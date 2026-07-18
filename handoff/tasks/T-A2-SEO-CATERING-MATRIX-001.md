# T-A2-SEO-CATERING-MATRIX-001 - Foreign Catering SEO Benchmark -> MAPLAB Article Matrix

## 接續狀態
- **狀態**: 🟡 STALLED（since 2026-07-19，48h 無 commit，Owner 可更新最後活動解除）
- **最後活動**: 2026-06-17
- **接續點**: 競品分析工作包已建立於 `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/`；文章矩陣撰寫尚未開始。
- **阻塞**: WP 寫入憑證需 Owner 確認（路徑：`skills/credentials/wordpress-api.md`）

**Status**: 🔄 進行中
**Owner**: A2 / Claude
**Created**: 2026-06-17
**Source request**: Owner asked A0 to search foreign catering websites with SEO keyword matrix layouts, benchmark strong performers, and dispatch the article/SEO work to Claude.

## Cold Start Required

Read before action:

1. `CURRENT_STATUS.md`
2. `pitfalls.md`
3. `handoff/tasks/T-A2-005-local-seo-factory.md`
4. `handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
5. `handoff/tasks/T-A2A3-001-B.md`
6. `projects/seo-ads-agent.md`
7. `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/`

## Goal

Turn the competitor SEO benchmark into MAPLAB's first durable catering SEO keyword matrix and 3 publishable draft articles, while preserving A2 boundaries:

- no external publishing without approval
- no Google Ads edits
- no credentialed WordPress edits unless explicitly approved
- no fabricated live URLs or unverified case claims

## Current Research Packet

Primary packet:

- `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/competitor_seo_matrix_benchmark.md`
- `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/article_matrix_seed.md`
- `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_task_prompt.md`

Benchmarks used:

- Social Pantry: service/location/venue/case/blog matrix
- ZeroCater: large-scale taxonomy matrix
- Fooditude: B2B office/corporate catering cluster
- Rocket Food: premium case-study and venue proof layer

## Next Claude Action

Use `claude_task_prompt.md` as the exact dispatch prompt.

Expected outputs:

- `claude_outputs/keyword_matrix_v1.md`
- `claude_outputs/article_briefs_v1.md`
- `claude_outputs/draft_01_icc_tainan_expansion.md`
- `claude_outputs/draft_02_tainan_corporate_catering_admin_guide.md`
- `claude_outputs/draft_03_opening_tea_party.md`
- `claude_outputs/publication_risk_checklist.md`
- `claude_outputs/README.md`

## Acceptance Criteria

- Matrix covers location, venue, event type, buyer role, menu type, proof, and FAQ axes.
- Drafts label evidence status: `verified_public`, `verified_internal`, `reasonable_inference`, `needs_owner_evidence`.
- Drafts include SEO title, slug, meta description, H1/H2 outline, FAQ, CTA, asset needs, and internal-link checks.
- Drafts do not claim Instagram Reel content unless transcript/screenshots are supplied.
- Drafts do not treat planned slugs as live URLs.

## Resume Prompt

你是 MAPLAB A2 SEO Writer / Claude。請冷啟動讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A2-005-local-seo-factory.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`handoff/tasks/T-A2A3-001-B.md`、`projects/seo-ads-agent.md`，然後讀 `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_task_prompt.md`。不要發布 WordPress 或修改 Ads。請只在 `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_outputs/` 產出 keyword matrix、10 篇 brief、3 篇草稿、發布風險清單與 30 行內 Resume Prompt。
