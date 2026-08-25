---
name: maplab-case-to-content-pipeline
description: Run one MAPLAB event case from verified Drive facts through A2 WordPress/SEO copy, Owner lyric approval, subscribed music generation, and A8 long/short video review. Use when the Owner asks to turn one activity folder into an article, song, and platform-ready video package.
---

# MAPLAB Case to Content Pipeline

Turn one real event into one reviewable content package. Each specialist receives a clean handoff, and the Owner sees the customer-facing result before the next creative stage begins.

## Cold start

Read `CURRENT_STATUS.md`, `pitfalls.md`, the Active Task Card, `skills/wp-article-standard.md`, `skills/brand-voice-guide.md`, `skills/maplab-hiphop-songwriter/SKILL.md`, and `skills/a8-produce-to-publish-sop.md`.

State the case, current gate, source folder, and the single deliverable for this session. Keep one case active at a time.

## Stage 1 — A2 article and SEO

1. Summon A2 with `skills/summon-role/SKILL.md` and the exact `recalls/A2_recall.md` prompt. Use A2 as an independent checker while the main session owns delivery.
2. Read live WordPress REST/front-end evidence and the canonical keyword map. Classify the case as a pillar, child case, or content gap before choosing the focus keyword.
3. Inspect the event folder and the narrowest matching client record. Use private records only to verify facts. The public article receives confirmed event facts and approved naming only.
4. Deliver:
   - customer-ready `wp_draft.md`;
   - internal `wp_internal_notes.md` with slug, metadata, schema, links, media plan, and missing evidence;
   - public-safe body images plus 1200x630 OG candidate;
   - an A2 checker receipt.
5. Create one mobile-readable review surface and read it back. WordPress creation or publication begins only after the Owner approves the article.

## Stage 2 — songwriter and lyric gate

1. Give the songwriter only the approved public article or event brief plus the Owner's music direction.
2. Produce a short complete song and a distinct exact 15-second hook. Run `tools/ai_workbook/a8_lyrics_engine.py review`.
3. Put lyrics in the same review surface and set `OWNER_LYRICS_GATE`.
4. Owner approval can select the public-safe version, an explicitly approved named version, or line edits. Line edits return to the lyric review before any credit is consumed.

## Stage 3 — subscribed music generation

Generate a fresh track only from the approved lyric version while the selected service subscription is active. Record service, model/version, generation time, subscription/commercial-rights boundary, duration, pronunciation, and selected master. Earlier free-tier tracks may guide style but are not silently promoted to a commercial master.

## Stage 4 — A8 review package

Give A8 the selected audio master and approved A-grade media only. Produce:

- 16:9, 1920x1080 long version for the complete approved song;
- 9:16, 1080x1920, exact 15.0-second vertical version using the complete hook;
- subtitles, platform-specific title/description, 16:9 thumbnail, vertical cover, and an approval card;
- ffprobe, frame, privacy, spelling, and duration evidence.

When moving-image coverage is short, extend the approved atmosphere with a safe still, lyric subtitles, and slow zoom-out or restrained pan. The review package ends with private links. Publishing is a later Owner gate.

## Hermes role

Hermes may receive only public or sanitized text for disposable first-pass QA, source clustering, or formatting. A2 and the main session remain responsible for client facts, WordPress truth, and final judgment. A failed Hermes capability probe records `QA_NOT_ACCEPTED` and the delivery continues through the verified path.

## Checkpoint

Update the Task Card, `CURRENT_STATUS.md`, a durable review receipt, and the Resume Prompt. Record the current stage, verified artifacts, one Owner action, and the single next bounded action. Commit only the case-scoped files.
