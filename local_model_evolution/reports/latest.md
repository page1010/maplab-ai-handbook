# Local Model Evolution — latest

Cycle: `2026-07-19-first-cycle`
Status: first cycle complete; shadow not started

## What

- Runtime capability inventory complete.
- Quota Sentinel dry-run: 8 providers/runtimes, usage APIs 0, teacher jobs 0.
- Two P0 curricula frozen at 20 cases each.
- `qwen2.5:14b` baseline: 284/320 (`88.75%`); safety 206/240 (`85.83%`).
- Candidate wrapper: 320/320 (`100%`); inference calls 0.

## So What

The top failures are provenance, forbidden-fact exclusion, and missing-data
honesty. A deterministic wrapper fixes the first-cycle safety contract more
reliably and cheaply than LoRA, but it does not improve model semantics.

## Now What

Allow only a de-identified file-only shadow of the wrapper. Keep quota-based
teacher jobs, model promotion, production scheduling, and LoRA blocked.

## Loop Back

Add a versioned semantic rubric and two shadow reports, then route only the
narrative field through the local model if safety invariants remain deterministic.

Receipt: `workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260719/validation_receipt.md`
