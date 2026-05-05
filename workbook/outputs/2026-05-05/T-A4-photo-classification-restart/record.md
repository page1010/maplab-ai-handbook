# T-A4 Photo Classification Restart — Record

Date: 2026-05-05  
Role: A1

## What We Found
- Existing system records confirm A4 photo classification has historical blockers and cost issues:
  - `data/MAPLAB_Dashboard.html` shows `T-A4-001` blocked note.
  - `docs/system-evolution-stories/2026-03-23-gemini-api-selection.md` documents model selection pitfalls.
  - `docs/system-evolution-stories/2026-04-18-gcp-billing-gemini-api.md` documents billing overrun.
  - `projects/slides-quotation-system.md` still depends on A4 Phase 4 classification output.

## Actions Started
1. Added `tools/ai_workbook/photo_pipeline.py`
2. Generated `classification_plan.json` (proposal-only)
3. Enforced rule: no automatic file moves before human approval

## Next Step
- Add optional LLM assist pass:
  - default local `ollama` for low-risk tag suggestions
  - escalate to `gemini-2.5-flash-lite` only for low-confidence items
- After approval, run move executor in dry-run first, then apply mode.

