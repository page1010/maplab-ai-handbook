---
name: maplab-creative-prototype-router
description: Choose and govern Impeccable, Google Stitch, Pomelli, Opal, Antigravity, or Mixboard when a MAPLAB task asks for UI design, a campaign concept, a no-code prototype, a moodboard, or design critique. Produces the safest useful route and prototype artifact without treating experimental tools as brand truth or authorizing external publication.
---

# MAPLAB creative prototype router

Use one primary tool per deliverable. Read [references/tool-matrix.md](references/tool-matrix.md) before selecting a Google Labs route.

## Required truth

1. Read `CURRENT_STATUS.md`, the active Task Card, `skills/maplab-visual-spec.md`, and `skills/brand-voice-guide.md`.
2. Treat the supplied brief and approved MAPLAB artifacts as authoritative. Tool-generated brand DNA, palettes, copy, or imagery are proposals.
3. Classify all inputs as `public`, `approved_brand`, `synthetic`, or `private`. Only the first three may enter external experimental tools, and `approved_brand` still requires the task's outbound-use gate.

If no active Task Card exists, local/read-only routing may continue while reporting the gap. Create a task-scoped card before any external draft, upload, authenticated write, sharing, or repo mutation.

## Choose the route

- Existing frontend code, UI review, accessibility, responsive behavior, hierarchy, or visual refinement: use the installed `$impeccable` skill. Do not install or approve its hooks as a side effect.
- New UI canvas or high-fidelity interface prototype: use Stitch only when the authenticated service or official MCP/SDK is actually available. Keep the result `PROTOTYPE_ONLY` until code export, tests, visual QA, and a receipt exist.
- Campaign directions derived from a public or explicitly approved brand site: use Pomelli for draft concepts. Compare every result with MAPLAB's local visual and voice specs.
- No-code mini-app or workflow experiment: keep Opal on `HOLD` until account, region, storage, sharing, and data routes are live-verified. Private/customer input is `PROHIBITED_PRIVATE_INPUT` and cannot be overridden by an Owner gate; when the service route is cleared, use synthetic data first.
- Moodboard or visual exploration: use Mixboard with public, approved, or synthetic assets only. A board is not a final asset, rights receipt, or publish proof.
- Google ecosystem/browser second opinion: use Antigravity only within its current read-only/browser-artifact boundary. Do not grant a write lease or expand its role through this skill.

## Produce a route card

Return:

```text
ROUTE: <tool or LOCAL_FALLBACK>
ROUTE_STATUS: <READY|CONDITIONAL|HOLD|PROHIBITED_PRIVATE_INPUT>
DELIVERABLE: <exact prototype or critique>
DATA_CLASS: <public|approved_brand|synthetic|private>
CAN_PREPARE_BRIEF_NOW: <yes|no>
CAN_CREATE_EXTERNAL_NOW: <yes|no>
OWNER_GATE: <none|outbound_use|authenticated_write|publish>
CANONICAL_INPUTS: <paths>
PROTOTYPE_ARTIFACT: <path or external draft id>
REQUIRED_RECEIPT: <what proves export/readback>
FALLBACK: <local Impeccable or manual brief path>
```

External creation, upload, sharing, authenticated writes, and publishing remain proposal-only until the matching gate is explicit. Never claim a tool is free, available in Taiwan, API-accessible, or integrated merely because it appears in a social post.
