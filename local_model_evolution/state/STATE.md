# Local Model Evolution state

- cycle: `2026-07-23-first-cycle-revalidated`
- status: `first_cycle_revalidated_shadow_not_started`
- model tier target: `G1 -> G2 foundation`
- baseline model: `qwen2.5:14b`
- fixed eval cases: `40` (`20 investment`, `20 SEO`)
- quota sentinel: `dry-run only`
- nonlocal usage confidence: `unknown`
- safe reserve: `15%`
- teacher jobs created: `0`
- teacher jobs executed: `0`
- LoRA gate: `closed`
- production changes: `none`
- baseline: `284/320 (88.75%)`; safety `206/240 (85.83%)`; one recorded timeout
- candidate wrapper: `320/320 (100%)`; local model inference calls `0`
- candidate independence: `expected` gold labels are scorer-only; mutation regression test passes
- top errors: provenance `11`; forbidden-fact exclusion `11`; missing-data honesty `8`
- promotion: `wrapper_shadow_candidate`; model `no_promotion`
- next: two de-identified file-only shadow reports plus semantic-quality rubric
