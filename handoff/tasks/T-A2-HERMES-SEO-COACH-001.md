# Task Card: T-A2-HERMES-SEO-COACH-001

- State: `RUNNING`
- Priority: `P1`
- Created: `2026-09-01`
- Coach: A0 / Codex
- Intake: Hermes durable-job gateway
- Executor: A2/Codex local SEO domain worker
- Checker: A0/A2 coach
- Data class: `public`
- Parent: `handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
- Durable job: `MAPJOB-20260901-120729-7b2afc`
- Canonical receipt: `workbook/reviews/MAPLAB-DURABLE-JOBS/MAPJOB-20260901-120729-7b2afc/job.json`

## Owner outcome

把定時喚醒改成有證據差異才做事；由教練判斷要修細節或先寫計畫，建立正確 SOP、資料契約與可搜尋 Skill，再把一個可重跑、可驗證的 SEO 任務交給 Hermes。

## Authorization

本任務已授權：公開網站 GET、公開 WordPress REST、repo/local readback、建立 Skill/SOP/Task Card/review receipt、停用可逆的無效本機排程，以及建立零客訊的 Hermes durable job。

仍需 Owner 明確批准：任何 live WordPress 寫入或發布、Google/Meta Ads 或 Rank Math 設定變更、對客 LINE/Telegram 發送、新花費、私密資料送新第三方、不可逆操作或實質商務/創意選擇。

## Verified baseline

- `robots.txt` 與 sitemap index 為 200。
- WordPress 公開 REST：58 published posts、6 published pages。
- post/page sitemap 共 64 URLs，本輪公開 crawl 全部 200。
- 九個高價值 URL 均為 200、index/follow、自指 canonical、單一 H1、title/meta 存在。
- `/press-conference-catering/` 的 FAQ JSON-LD 3 blocks 中只有 2 blocks 可解析；block 2 在 position 441 有 literal control character。
- 同頁在 64 頁 sitemap corpus 中站內 inbound source 為 0；這是結構機會，但不等於已證排名損失。
- GSC/Google URL Inspection、CTR、query/page ranking 與 CWV 本輪皆 `MISSING`。

Evidence:

- `workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_baseline.json`
- `workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_no_delta_receipt.json`
- `workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_corpus_audit.json`

## Current phase

`post-879-jsonld-preview-proposal / dispatched-to-Hermes`

## Hypothesis

只把 post 879 FAQ JSON-LD 的 raw newline 改為合法 JSON 字元或空格，即可在不改 visible copy 的前提下，把 JSON-LD parse 從 2/3 提升為 3/3。

## Changed variable

`press-conference-catering` 內嵌 FAQ JSON-LD `acceptedAnswer.text` 中的一個 raw newline；其他欄位全部固定。

## Fixed holdout

- public URL、post ID 879、slug、title、meta description、canonical、robots、H1、visible body、internal links、其餘 JSON-LD blocks。
- Public REST rendered source modified timestamp: `2026-06-15T21:03:12`。
- Public REST rendered source SHA-256: `3858ec65e694c2cc029db42abcfcece0c4f9bb370e70459ec57ab8e629b6bc5f`。

## Expected delta

- Preview/parser acceptance: JSON-LD valid blocks `2/3 -> 3/3`。
- HTTP 200、index/follow、自指 canonical、單一 H1 與 visible text保持不變。
- 本 action external writes=0、customer sends=0、private third-party egress=0。

## Stop loss

- 只產 approval-ready patch proposal 與本機 preview/parser receipt，不改 live post。
- 若單一字元正規化後仍 parse fail，停止此 branch；不得順便重寫整篇或增加新內容。
- 連續兩個 receipt 沒有 verified acceptance delta 時，禁止第三次同方法，先做 failure bucket 與第一性原理 review。

## Next Bounded Action

Hermes 接單後由 A2/Codex local domain worker 產出 `press_conference_faq_jsonld_patch_proposal.md`：精確定位失敗 block、提供最小 before/after、在本機 parser 證明 3/3 valid，並留下 live write 仍為 `OWNER_REVIEW` 的 rollback/驗收卡。

## Acceptance

1. 精確輸出 `workbook/reviews/JOB-A2-SEO-COACH-20260901/press_conference_faq_jsonld_patch_proposal.md` 與 `hermes_action_receipt.json`。
2. Proposal 只正規化一個 raw newline；沒有 WordPress/Ads/Rank Math write，且 visible copy、post ID/slug、title/meta、canonical/robots/H1、links 與其他 schema blocks 不變。
3. Parser receipt 證明 candidate JSON-LD `2/3 -> 3/3` valid；固定 holdout 全部逐欄 readback 相同。
4. Counters 明列 `external_writes=0`, `customer_send=0`, `private_third_party_egress=0`。
5. Coach 驗 artifact 後才可轉 `OWNER_REVIEW`；沒有授權後的 live write 與公開 readback 不得稱 live 修復完成。

## Resume Prompt

我是 MAPLAB SEO 教練接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`.agents/skills/maplab-seo-coach-patrol/SKILL.md` 與 `workbook/reviews/JOB-A2-SEO-COACH-20260901/`。先 readback canonical durable job 並做 plateau review，再執行唯一 next action：為 post 879 的 FAQ JSON-LD raw newline 產最小 preview-only patch proposal與3/3 parser receipt。不得寫 live WordPress、Ads、Rank Math，不得對客發訊，不得外送私密資料。完成後原子更新 job、Task Card、Active Task、Next Bounded Action 與 Resume Prompt。
