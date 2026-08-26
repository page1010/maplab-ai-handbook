---
name: maplab-video-evidence-readback
description: Inspect a local or public video for MAPLAB when the user asks what happens, what is said, which frames prove a claim, or whether an A8 render has visual evidence. Routes to the installed watch skill with private-first egress limits and produces a bounded evidence report. Do not use for video generation, editing, publishing, rights approval, or final A8 acceptance.
---

# MAPLAB video evidence readback

Use this as an evidence layer, not as an editor or acceptance shortcut.

## Required reads

1. Read `CURRENT_STATUS.md` and the active Task Card.
2. For A8 work, read `skills/a8-produce-to-publish-sop.md` and the relevant section of `skills/a8-video-pipeline-skills.md`.
3. Read [references/evidence-contract.md](references/evidence-contract.md) before creating a receipt or making a pass/fail claim.

If no active Task Card exists, a read-only classification may continue while reporting that gap. Create a task-scoped card before any download, external call, config write, or durable artifact mutation.

## Route

1. Classify the source as `public`, `user_supplied`, `maplab_private`, or `unknown`.
2. Record the question, requested time range, and smallest useful frame budget. Prefer a focused range for videos longer than 10 minutes.
3. Choose the narrowest path:
   - Metadata only: use `ffprobe`; do not extract frames.
   - Visual question: invoke the installed `$watch` skill with `--no-whisper`, `--detail efficient|balanced`, and an explicit `--max-frames` no higher than 100.
   - Public URL with native captions: native captions may be used; do not add cloud Whisper merely for convenience.
   - Private or customer footage without captions: if the user specifically requested a transcript, return `BLOCKED_EGRESS`; offer a separate frames-only visual pass, but do not present it as fulfillment of the transcript request. If the question is visual, proceed frames-only unless the active Task Card explicitly authorizes a named transcription provider for that run.
4. Read the selected frames and align claims to timestamps. Distinguish what is visible, what is spoken, and what is inferred.
5. Return the evidence contract. Preserve the exact working directory for bounded follow-up or reviewed cleanup.

## Hard gates

- Never use `token-burner` by default.
- Never put customer, child, Owner, unreleased campaign, or other private audio into Groq/OpenAI transcription without explicit per-run authorization.
- Never auto-install packages, write API keys, use browser cookies, or delete a work directory as a side effect.
- A sampled frame report cannot prove full playback, sync across every line, target-device appearance, source rights, or privacy clearance.
- For A8 acceptance, the existing acceptance receipt, full 1x/0.5x playback, target-device visual readback, rights/privacy checks, and Owner gate still apply.

## Output statuses

Start with exactly one:

- `EVIDENCE_READY` — requested visual/spoken evidence is supported within the declared range.
- `PARTIAL_EVIDENCE` — one evidence stream or part of the range is missing.
- `BLOCKED_EGRESS` — answering would require an unapproved external transcription or download route.
- `NOT_A_VIDEO_READBACK_TASK` — route to A8 editing, generation, publishing, or another owner.
