# Validation Receipt — JOB-A1-NOTEBOOKLM-ROUTER-20260825

- Date: 2026-08-25 Asia/Taipei
- Role: A1 / Codex
- Base commit: `e5d931d46f72`
- Scope: MAPLAB non-investment governance, SOP/path/handoff navigation, local-model fallback
- Canonical notebook: `https://notebook.google.com/notebook/68114d21-ebc9-4116-a88a-52cc31cbe9a7`
- Notebook title: `MAPLAB Project Brain｜SOP・路徑・角色・產物（非投資域）`

## What was connected

The notebook is a navigation layer, not a repository dump or runtime authority. The reproducible local bundle has two upload files:

1. `workbook/notebooklm/maplab-project-brain/maplab-project-brain.md` — governance core
2. `workbook/notebooklm/maplab-project-brain/maplab-sop-router.md` — full SOP corpus plus canonical A2–A8 workflow route cards

`workbook/notebooklm/maplab-project-brain/source-manifest.json` remains local audit evidence because the current Gemini Notebook upload UI does not accept JSON. It is not an upload source.

Machine-readable route for agents and local models:

- `config/notebooklm/maplab-project-brain-router.json`
- Browser-capable operator: open the canonical notebook and apply its prompt template.
- Browserless Hermes/local model: read the local SOP router and use the same answer contract.

## Source boundary

- Underlying curated sources: 28 total; governance 8, SOP router 20.
- Upload files: 2 Markdown files.
- Generator-recorded redactions: 1.
- Final secret-value rescan: 0 matches across both upload packs and the machine router.
- Excluded: credentials, secrets, cookies/session data, customer raw conversations, runtime logs, SQLite/DB dumps, investment data, media binaries and generated noise.
- Full repo upload: not performed.

Final local artifacts uploaded to the canonical notebook:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `maplab-project-brain.md` | 196027 | `1b4384878875151439aca4f92433691639213233f78ba13b2677f9d060367b7a` |
| `maplab-sop-router.md` | 185142 | `b21270aba451f70f70128962ddb726de5a924b631967f3e57b87c97b7f395132` |
| `maplab-project-brain-router.json` | 2045 | `5b6783c066c66500206c450b9be513e1facb7b2747256ad3e2c4b0813d839c3e` |

## Browser readback and retrieval tests

### Notebook creation and compatibility

- Gemini Notebook was created in the signed-in in-app Browser session.
- The notebook URL and title above were read back from the live UI.
- The first notebook was retained and renamed `MAPLAB Project Brain｜DRAFT 2026-08-25（保留，不作 agent 路由）`; no cloud source or notebook was deleted. The clean notebook above is the only canonical route.
- JSON upload was rejected by the current UI; the source contract was corrected to supported Markdown uploads only.
- Ingestion readback showed both named sources and zero progress bars after completion.

### Smoke 1 — governance-only weakness found

The first question asked for cold-start order, A2→A8 routing and the missing-answer rule. The answer cited the governance pack and correctly separated static truth from `NEEDS_LIVE_REFRESH`, but it could not return the concrete A8 SOP/body because only the governance pack was present. This was treated as a failed coverage test, not a completion claim.

### Smoke 2 — exact paths found, retrieval weakness found

After adding the full SOP pack, an A8 question returned these exact paths with citations:

- `skills/a8-produce-to-publish-sop.md`
- `skills/a8-video-pipeline-skills.md`

It still misclassified the embedded SOP body as unhydrated and returned `NOT_IN_PACK` for several static details. The source actually contained the full documents. Root cause: retrieval favored metadata near the top of the large bundle.

Fix: the generator now prepends `Authoritative A2-A8 workflow route cards`, derived directly from the canonical manifest, with exact SOP paths and every stage's inputs, actions, outputs, acceptance, handoff, approval gate and evidence. Unit coverage requires the A8 video SOP, produce-to-publish SOP, songwriter skill, lyrics gate and licensed audio handoff to appear in the pack.

### Smoke 3 — final clean notebook PASS

To avoid destructive cloud deletion, the original notebook was retained as a labeled draft and a clean canonical notebook was created. Live readback confirmed exactly two checked sources, both final Markdown packs, zero ingestion progress bars and zero Browser console errors.

The final A8 question started with `FOUND` and cited `maplab-sop-router.md`. It returned all three exact SOP paths:

- `skills/a8-video-pipeline-skills.md`
- `skills/a8-produce-to-publish-sop.md`
- `skills/maplab-hiphop-songwriter/SKILL.md`

It then returned A8-01 through A8-04 with each stage's required inputs, actions/reads, outputs, handoff, approval gate, evidence and next bounded action. It correctly included `licensed audio track`, `Owner lyrics approval before paid/external generation`, `Owner approves public publishing`, media probe evidence and per-platform UI/API receipts. Current task approval and runtime/UI state remained a separate verification requirement rather than being inferred from the static route.

## Local verification

- `python3 -m unittest tools.ai_workbook.test_build_directional_system_map -v`: 7/7 PASS.
- `python3 tools/ai_workbook/build_directional_system_map.py --check`: manifest valid; generated outputs fresh.
- JSON Schema validation: PASS.
- `node --check chrome-extension/popup.js`: PASS.
- docs/Extension HTML byte comparison: PASS.
- `git diff --check`: PASS.
- Graphify final topology: 1820 nodes／3262 edges／147 communities.
- Graphify multigraph diagnostics: 0 missing endpoints, dangling endpoints, self-loops, collapsed edges and duplicates.
- Repeated `graphify update .`: `No code-graph topology changes detected`.
- Graphify token benchmark: 121333 naive corpus tokens versus about 3404 average query tokens, `35.6x` reduction.

## Truth and operating contract

Notebook answers must start with exactly one status:

- `FOUND`: static path/SOP/handoff is present in the pack.
- `NEEDS_LIVE_REFRESH`: current task, approval, runtime/UI, platform, publication or receipt state must be read back live.
- `NOT_IN_PACK`: the static subject is outside the curated pack.

Every answer must include exact path, reason, required reads, inputs, output/handoff, gate, evidence, next bounded action and citations. NotebookLM/Gemini Notebook is a navigation oracle, not execution evidence.

## NEXT

Regenerate and replace the two canonical notebook sources only when their hashes change; do not upload JSON or the repository wholesale. The separate Extension reload remains an Owner-only Chrome action from the parent directional-map task.

## Resume Prompt

我是 A1 NotebookLM 導航層接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-DIRECTIONAL-MAP-001.md`、`config/notebooklm/maplab-project-brain-router.json` 與本 receipt。重跑 generator、7 個 unit tests、`--check`、secret rescan 與 Graphify stable update。若兩個 upload pack 的 hash 改變，只替換 canonical notebook 的兩個 Markdown source，不上傳 JSON 或整庫。用 A8 approved brief 情境確認回答列出三個 exact SOP paths、A8-01 至 A8-04 inputs／outputs／gates／evidence，靜態內容為 `FOUND`，實際核准與 runtime 狀態為 `NEEDS_LIVE_REFRESH`。只 stage 本任務檔案，不碰 unrelated dirty state。
