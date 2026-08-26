---
name: maplab-project-knowledge-router
description: Locate MAPLAB code, SOPs, owners, handoffs, gates, dependencies, and evidence when a user asks where something lives, how a workflow connects, or what could be affected. Routes code topology to local Graphify, governance navigation to the sanitized NotebookLM project brain, and current facts to live readback. Do not use either index as proof that runtime, publication, or approval changed.
---

# MAPLAB project knowledge router

This modern skill wraps the existing Graphify graph and NotebookLM pack. It does not install a second control plane.

## Cold start and preflight

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, `SYSTEM_DIRECTORY_INDEX.md`, and the active Task Card before querying an index.
2. Run:

```bash
python3 .agents/skills/maplab-project-knowledge-router/scripts/preflight.py --repo-root . --json
```

3. Read `routes.graphify` and `routes.notebooklm` separately. A stale graph does not block NotebookLM navigation, but any Graphify-derived answer must start `NEEDS_LIVE_REFRESH` until the graph is rebuilt. Rebuild only through the canonical command reported for that route; do not patch generated packs or graph files by hand.

If no active Task Card exists, read-only navigation may continue while reporting the missing assignment boundary. Create a task-scoped card before any rebuild or durable mutation.

## Routing rules

| Question | Route | Truth boundary |
|---|---|---|
| symbol, caller, dependency, code path, blast radius | local Graphify | code topology only |
| SOP, role, required reads, input, handoff, gate, receipt path | sanitized NotebookLM pack or its local Markdown fallback | navigation only |
| current task state, daemon/runtime, public page, authenticated UI, approval, publish result | canonical file plus live/API/UI readback | current evidence |
| mixed question | query each relevant route and label each result | never merge inference into verified fact |

For Graphify, start with `graphify query`, `graphify path`, or `graphify explain`. Keep the existing `.graphifyignore` and AST-only corpus. Do not enable semantic/media indexing, HTTP MCP, hooks, watch mode, or graph updates without a separately reviewed task.

For NotebookLM, use `config/notebooklm/maplab-project-brain-router.json`. Query the canonical notebook only after cold-start files and local search cannot locate the answer. If no authenticated browser operator is available, read `workbook/notebooklm/maplab-project-brain/maplab-sop-router.md`. Never install or use `notebooklm-py`, import Google cookies, or expose bearer tokens for this route.

## Response contract

Start with `FOUND`, `NEEDS_LIVE_REFRESH`, or `NOT_IN_PACK`, then return. A valid hash only proves that a configured pack matches the router; use `FOUND` only after the requested content is actually located.

1. exact repo path or symbol;
2. why it applies;
3. required reads and inputs;
4. output or handoff owner;
5. approval gate;
6. evidence path;
7. next bounded action;
8. citations or commands used.

Read [references/truth-boundaries.md](references/truth-boundaries.md) when a result crosses more than one route or will be used in a governance decision.
