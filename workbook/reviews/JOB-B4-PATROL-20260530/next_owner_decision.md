# Next Owner Decision — JOB-B4-PATROL-20260530

## Recommended Decision

1. **Freeze experimental expansion for now.**
   - Keep the core owner-facing surfaces.
   - Do not open new lanes until the stalled critical work is healthier.

2. **Keep only bounded OpenClaw / Hermes use.**
   - They may continue as read-only evidence / cold-path helpers.
   - Do not promote them into hot-path authority surfaces yet.

3. **Keep the legacy broker-simulation path archived.**
   - Do not revive `proposed_orders` / `execute_open_orders.py` / `simulation=True` as if it were the local ledger.

4. **Park the research_method_layer schema as draft-only.**
   - It can stay in the repo as a design artifact.
   - It should not become runtime truth without a current owner task that needs it.

## If Owner Wants One Experiment Lane Alive

Pick exactly one:

- OpenClaw bounded evidence pipeline
- Hermes cold-path research prep
- research_method_layer schema work

Do not keep all three moving at full speed. That would recreate the overbuild pattern this patrol is trying to prevent.

## 5-Minute Decision Package

- What is the smallest set of lanes that still improves Owner value this week?
- Which lane should be frozen first if time or attention gets tight?
- Which legacy route should be considered permanently retired?
