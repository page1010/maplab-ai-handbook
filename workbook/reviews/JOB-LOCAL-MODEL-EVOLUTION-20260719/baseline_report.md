# Baseline report — qwen2.5:14b

## What

The current local model ran all 40 fixed cases through the existing prompt-only
path.

| Metric | Result |
|---|---:|
| Total | 284 / 320 (`88.75%`) |
| Safety checks | 206 / 240 (`85.83%`) |
| Investment curriculum | 140 / 160 (`87.50%`) |
| SEO curriculum | 144 / 160 (`90.00%`) |
| Median latency | 14,491 ms/case |
| Maximum latency | 164,853 ms (`INV-017`, no evidence) |
| Total inference latency | 1,159,860 ms (~19m20s) |
| Parse failures | 1 |
| Action-boundary failures | 1 |

## So What

The model is not promotable. Its prose ability hides unsafe truth handling, and
an empty-evidence case can consume almost three minutes before failing.

### Top three error types

1. `fact_provenance`: 12 failures — the output used facts that did not satisfy
   the allowed entity/date/source set.
2. `forbidden_fact_exclusion`: 12 failures — stale, simulated, wrong-entity,
   private, or unsupported material leaked into the answer.
3. `missing_data_honesty`: 6 failures — evidence gaps were not represented by
   the required `insufficient_data` state.

The baseline also had two subject-identity failures, one date-integrity failure,
one action-boundary failure, and one full 0/8 case.

## Now What

Do not tune prose. First place entity/date/rights/source filters before inference,
render invariant control fields deterministically, and make missing-data a fast
failure. Compare that wrapper on the identical 40 cases.

## Loop Back

After the wrapper reaches shadow, measure residual semantic usefulness separately.
Only those residual errors can justify prompt, skill, RAG, or adapter work.
