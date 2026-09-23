# Hermes assignment — T-A2-HERMES-SEO-COACH-001

```yaml
task_id: T-A2-HERMES-SEO-COACH-001
executor: Hermes intake -> A2/Codex local SEO domain worker
checker: A0/A2 coach
objective: Restore machine-readable FAQ JSON-LD for post 879 with one preview-only change.
next_bounded_action: Produce the exact minimal before/after proposal and local 3-of-3 JSON parser receipt.
inputs:
  - workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_baseline.json
  - workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_no_delta_receipt.json
  - workbook/reviews/JOB-A2-SEO-COACH-20260901/public_seo_corpus_audit.json
  - https://www.maplabkitchen.com/wp-json/wp/v2/posts?slug=press-conference-catering&_fields=id,slug,modified,link,title,content
hypothesis: Replacing the single raw newline in acceptedAnswer.text restores JSON validity without changing visible content.
changed_variable: one raw newline in the embedded FAQ JSON-LD block
fixed_holdout: post id, slug, title, description, canonical, robots, H1, visible body, links, other schema blocks
expected_delta: JSON-LD parse 2/3 -> 3/3; holdout unchanged
stop_loss: proposal/preview only; stop if one-character normalization does not parse; do not broaden scope
acceptance:
  - exact failing block and source anchor
  - exact minimal before/after
  - candidate parser result 3/3
  - external_writes=0
  - customer_send=0
  - private_third_party_egress=0
deny:
  - live WordPress write or publish
  - Ads, Meta, GTM, Pixel, or Rank Math changes
  - credentials, cookies, login state, customer or LINE data
  - customer Telegram or LINE send
  - invented price, availability, client, ranking, or performance claim
outputs:
  - workbook/reviews/JOB-A2-SEO-COACH-20260901/press_conference_faq_jsonld_patch_proposal.md
  - workbook/reviews/JOB-A2-SEO-COACH-20260901/hermes_action_receipt.json
```

Hermes is the governed intake/control loop. The local A2/Codex domain worker performs the SEO parsing and proposal because the current Hermes one-shot executor has no SEO action. No worker chat or queued state counts as completion.
