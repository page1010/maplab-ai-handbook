# Hash Verification Receipt — 2026-09-02

## VERIFIED
- 01-chair-march.mp4 — f1c5bbe8c34a0e5cd972f231b4dabb610550d15fc358e992c8291ebccb275bd8 — **MATCH**
- 02-chair-side-tap.mp4 — 68bee59e8f60bfad2a0adb68d95913df7d4fc9007b3995d101c40a8257409911 — **MATCH**
- 03-chair-heel-raise.mp4 — 8b30441b6ddf117b8d6044c896098d0e2a5a0f9a4c6a768f9e80e7dfafd1a6f8 — **MATCH**
- 04-seated-knee-extension.mp4 — 564af61c790f2bfc67bcc2caeeef76509ec37a3e53e5d837707e8f126554364c — **MATCH**
- 05-seated-chest-open.mp4 — 33defeed5a4c3f7e8da2c2ac5988036f7f0e50f243918fd647ad7fb19d7fea7c — **MATCH**
- a8-fitness-mvp-compilation-107.5s.mp4 — 31027675a7b16891df4e1621c9bedd41ff3322d64338ba0d812f5b1e68faf5b1 — **MATCH**

All six final MP4 SHA-256 hashes recomputed via `shasum -a 256` and match the Verified Starting Point in `handoff/tasks/T-A8-FITNESS-HERMES-CONTINUATION.md` exactly.

## DRIFT
none

## MISSING
- PT review: `movement_safety_review.json` reviewer.name/qualification/credential_or_organization = MISSING, all movement.verdict = MISSING, compilation.verdict = MISSING
- Human audio listen: `actual_audio_human_listen` gate not completed (no named person, no date, no per-video confirmation)
- Target-device readback: no 3–5 target-age usability tests, no phone/TV/desktop playback verification
- Canonical one-pass compilation acceptance: `maplab.a8.video-acceptance/v2` diagnostic receipts not produced
- Owner gate for YouTube channel Create: action-time confirmation not obtained

## NEXT
Produce six `maplab.a8.video-acceptance/v2` diagnostic receipts under `receipts/acceptance/` and six validator results (Phase 1 step 3), keeping every result `ok=false` due to missing PT, human listen, device readback, and Owner gate.