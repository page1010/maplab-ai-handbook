# T-A8-FITNESS-HERMES-CONTINUATION — Hermes 接續計畫案

Owner: pagewu1010  
Assignee: Hermes `default` profile  
Workspace: `/Users/pagemacmini/maplab-ai-handbook`  
Parent: `handoff/tasks/T-A8-FITNESS-MVP-001.md`  
Status: `READY_FOR_HERMES / PRIVATE_MVP_RENDERED_UNVERIFIED / PT_REQUIRED`  
Created: 2026-09-01  

## Objective

接手「跟著動｜華語樂齡節拍」MVP 的剩餘工作，先完成可重跑、可審核的本機收據與 Extension live readback，再停在真正 Owner／PT gate。不得把私人技術 MVP 說成可發布健身課。

## Cold Start

第一句必須說：

> 我是 Hermes A8-FITNESS 接續執行者，環境 `/Users/pagemacmini/maplab-ai-handbook`，本輪任務是完成一個有檔案收據的 bounded action。

依序完整讀：

1. `AGENT_CORE.md`
2. `CURRENT_STATUS.md`
3. `pitfalls.md`
4. `handoff/tasks/T-A8-FITNESS-MVP-001.md`
5. 本計畫案
6. `recalls/A8-FITNESS_recall.md`
7. `skills/a8-senior-fitness-video-sop.md`
8. `skills/a8-produce-to-publish-sop.md`

## Verified Starting Point

- DeerFlow public research completed：`DFR-20260901-122529-0f23b8`，artifact SHA-256 `6343d3707636efb95925ef8f4d58b565dc4d93f30d51686453f263f5376264f3`。
- A8-FITNESS role／SOP／Task Card／Extension module 已建立；AUTO route、relation rows、fail-closed PT/receipt gates 的 repo tests 通過。
- Chrome 已重新載入 `MAPLAB Agent Commander`，live role menu 已看見 `A8-FITNESS｜華語樂齡節拍導演（A8 子角色）`；仍需選中後保存完整 module/handoff readback。
- Suno variant A 已用可視 Chrome＋macOS native Save 下載：`audio/suno-variant-a-32s.wav`，32.280 秒，48 kHz stereo PCM，SHA-256 `7245ce245774c6b52fb40a56cb2cea218dfc82e6e8f6e58e34b678348144cc9f`。
- 安全修正版已把 Suno A 以 0.11 音量混入；五支短片各 17.500 秒，合輯 107.521333 秒；plain full decode 5+1 PASS、`setpts=false`。
- Final candidate hashes：
  - `01-chair-march.mp4` — `f1c5bbe8c34a0e5cd972f231b4dabb610550d15fc358e992c8291ebccb275bd8`
  - `02-chair-side-tap.mp4` — `68bee59e8f60bfad2a0adb68d95913df7d4fc9007b3995d101c40a8257409911`
  - `03-chair-heel-raise.mp4` — `8b30441b6ddf117b8d6044c896098d0e2a5a0f9a4c6a768f9e80e7dfafd1a6f8`
  - `04-seated-knee-extension.mp4` — `564af61c790f2bfc67bcc2caeeef76509ec37a3e53e5d837707e8f126554364c`
  - `05-seated-chest-open.mp4` — `33defeed5a4c3f7e8da2c2ac5988036f7f0e50f243918fd647ad7fb19d7fea7c`
  - `a8-fitness-mvp-compilation-107.5s.mp4` — `31027675a7b16891df4e1621c9bedd41ff3322d64338ba0d812f5b1e68faf5b1`
- Encoded-output contact sheet SHA-256 `ccd75192f22b876a9471c9eeaa3cd478b65c13fd5e2e489013e43c275699f799`。
- YouTube form is ready but not submitted：name `跟著動｜華語樂齡節拍`、handle `@跟著動樂齡節拍`、green availability check、final Create enabled。

## Execution Plan

### Phase 1 — Freeze receipts and repo truth

1. Recompute the six final MP4 hashes; if any differs, stop and label `HASH_DRIFT`.
2. Ensure `qa/movement_safety_review.json` binds the exact six hashes while reviewer/verdict remain `MISSING`.
3. Produce six `maplab.a8.video-acceptance/v2` diagnostic receipts under `receipts/acceptance/` and six validator results. Missing PT, human listen, device readback, canonical one-pass compilation or Owner gate must keep every result `ok=false`.
4. Confirm `receipts/audio_rights_receipt.json` still contains the Suno WAV hash, visible-download receipt and public-rights boundary after rerender.
5. Run focused Extension/A8 tests, JSON validation, `node --check`, `py_compile`, plain full decode and `git diff --check`.

### Phase 2 — Chrome Extension live readback

1. In the already installed `MAPLAB Agent Commander`, select A8-FITNESS.
2. Save a screenshot and machine-readable receipt proving role name, Task Card path, review bundle path, Output Contract, PT gate and six-receipt rule.
3. Run AUTO on the senior-fitness task text and prove the live UI selects A8-FITNESS.
4. Do not expose or copy the GitHub token field.

### Phase 3 — Owner review package

1. Present the compilation, one representative short, encoded contact sheet and Suno WAV for human review.
2. Keep `actual_audio_human_listen`, target-device readback, 3–5 target-age usability tests and PT review as `MISSING` until named people actually complete them.
3. Describe this version as a `107.5 秒動作教學合輯`, not a complete workout class.

### Phase 4 — YouTube channel gate

1. Re-read the form immediately before action.
2. Ask Owner for action-time confirmation using the exact name and handle above.
3. Only after a fresh explicit confirmation, click final Create once and save channel URL, channel ID and signed-in name readback.
4. Do not upload any video. Private, unlisted and public uploads are all `NOT_AUTHORIZED`.

### Phase 5 — Commit and rolling state

1. Preserve unrelated dirty work. Stage only A8-FITNESS source, generated contract files, task-scoped review artifacts, and exact hunks in `CURRENT_STATUS.md`／`pitfalls.md`.
2. Commit locally with a task-scoped message; do not push unless separately authorized.
3. Update parent Task Card, durable job and Resume Prompt with `VERIFIED / DRIFT / MISSING / NEXT`.
4. One bounded action per heartbeat. If the next step is PT, Owner confirmation, human listening or target-device testing, mark the card `BLOCKED_OWNER_REVIEW` with the exact missing proof; do not loop or manufacture evidence.

## Non-negotiable Boundaries

- No additional Suno Create, purchase, subscription or plan change.
- No lyrics generation until `OWNER_LYRICS_GATE` passes.
- No upload, publication, customer send, WordPress write or private third-party egress.
- No medical, rehabilitation, treatment, fall-prevention, weight-loss or body-part fat-loss claim.
- No `PT_PASS` without a named qualified reviewer, qualification, date, per-movement verdict and exact video hashes.
- No `QA_PASS` from ffprobe, tests, source previews or enabled buttons alone.

## Completion Receipt

Hermes must leave one final file receipt summarizing:

- `VERIFIED`: exact hashes, tests, encoded frames, Extension live readback and any channel readback actually completed.
- `DRIFT`: changed paths/hashes or contract mismatch.
- `MISSING`: PT, human listen, target-age/device tests, rights/legal review and Owner gates.
- `NEXT`: exactly one bounded action.

## Resume Prompt

```text
我是 Hermes A8-FITNESS 接續執行者，環境 /Users/pagemacmini/maplab-ai-handbook。依計畫 handoff/tasks/T-A8-FITNESS-HERMES-CONTINUATION.md，只執行下一個 bounded action。現在是 PRIVATE_MVP_RENDERED_UNVERIFIED / PT_REQUIRED。先重算 final hashes；缺 PT、human listen、device/target-age readback、Owner gate 或 canonical acceptance 任一項時，收據必須 ok=false。YouTube final Create 需要 action-time confirmation；所有影片上傳與公開未授權。保留 unrelated dirty work，留下 VERIFIED / DRIFT / MISSING / NEXT 與 Resume Prompt。
```
