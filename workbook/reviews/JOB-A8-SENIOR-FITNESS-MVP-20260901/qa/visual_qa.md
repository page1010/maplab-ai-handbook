# Visual QA｜私人技術 MVP

Status: `RENDERED_UNVERIFIED / ok=false`

## Verified technical evidence

- 五支 movement shorts 與一支 compilation 已有本機 MP4；exact final hashes 以 rerender 後的 `technical_validation.json` 與六份 acceptance diagnostics 為準。
- 既有 ffprobe receipt 顯示候選檔為 1080×1920、30 fps、H.264/AAC；這只證明技術格式，不是內容、安全或發布驗收。
- 既有 contact sheet 不能單獨證明完整播放、字幕 timing、聲畫同步或實機安全區。

## Hash-bound rerender corrections

Final private-MVP hashes are bound in `movement_safety_review.json` and the six acceptance diagnostics. Encoded-output contact sheet SHA-256 is `ccd75192f22b876a9471c9eeaa3cd478b65c13fd5e2e489013e43c275699f799`. Visual rerender corrected the eight earlier P0 findings: safety text no longer crosses the figure; each short has expanded stop/urgent-care wording; M3 keeps the forefoot grounded and makes heel lift visible; M2/M3 use one-hand chair cues matching the figure; M5 shows elbow-back/scapular action and hands-on-thighs regression; M4 adds a floor line and heel slide; M3→M4 adds a pause/sit-steady bridge; essential text/progress moved outside the designed right/bottom UI rails.

These are code/render and encoded-still corrections, not target-device or professional safety acceptance. Mobile/TV/YouTube UI readback and named-human full playback remain missing.

## Missing canonical evidence

- Encoded MP4 逐檔抽幀生成、hash-bound timeline contact sheet: `VERIFIED` by `encoded_contact_sheet_receipt.json`; this is still-image evidence, not full playback.
- Full playback 1×, named reviewer, watched duration for each of six outputs: `MISSING`.
- Full playback 0.5×, named reviewer, watched duration for each of six outputs: `MISSING`.
- Human audio listen for the exact mixed outputs: `MISSING`.
- Subtitle/cue timing verification against exact audio: `MISSING`.
- Mobile Shorts UI readback: `MISSING`.
- TV readback: `MISSING`.
- YouTube upload-preview readback: `MISSING`; upload is also `NOT_AUTHORIZED`.
- Qualified movement safety review bound to exact video hashes: `MISSING / PT_REQUIRED`.

## Verdict

The current deliverable may be called a `private technical MVP` or `107.5-second movement tutorial compilation`. It must not be called a safe public follow-along class, `QA_PASS`, `OWNER_VIDEO_GATE`, upload-ready, or publish-ready.
