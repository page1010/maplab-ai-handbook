# T-A8-001 — Folder Case to Short Video Distribution

Owner: A8 影音內容產線
Status: 🔄 ACTIVE
Created: 2026-06-17
Risk: medium

## Owner Request

Owner wants A8 to stop being idle and run a real content production loop:

> 拿我的資料夾實例，取用 AI 工具做成影片，上傳到 TikTok / YouTube，整理封面到 Pinterest。先研究 IG Reel 的底層邏輯，跑看看，再把流程技能寫好。

Reference Reel:

- `https://www.instagram.com/reel/DZp4BxgguqC/?igsh=c3k0NGM1YTB3N2Fz`

## Current Readback

Chrome logged-in read-only inspection could access the Reel metadata:

- Creator: `michelletech2026`
- Caption/topic: `Using Higgsfield MCP to make a bag`
- Date shown in metadata: 2026-06-16
- Public metrics at readback: 25 likes, 5 comments
- Observed media duration: about 29.6 seconds for the main video

Interpretation:

- The useful pattern is not the exact content; it is a tool-led workflow Reel: show a repeatable AI tool path, package it as a clear outcome, then distribute it with platform-specific metadata.
- MAPLAB should adapt this into: case folder evidence → public-safe label → storyboard → AI/video assembly → YouTube/TikTok/IG/Pinterest package → approval → publish receipts.

2026-06-17 MAPLAB IG readback:

- Owner screenshots and Chrome read-only profile inspection confirm MAPLAB's own Reels style is the better primary benchmark than generic catering reels.
- Live grid readback found 12 visible Reel links and view labels; top visible high-performance sample: `/maplabkitchen/reel/DTpw3nKjy4g/` with 41.7萬 views.
- Three sample Reel pages exposed playable media durations around 13.6s, 16.7s, and 28.5s.
- Brand profile terms to preserve in A8 copy: `外燴設計顧問`, `西式派對 / 品牌活動 / 婚禮茶會`, `美感 x 節奏`, `SINCE 2016`.
- Visual conclusion: warm soft light, low-saturation table scenes, shallow depth, sparse scene-first text, subtle watermark, no public debug counters.

Reference matrix and new visual rules:

- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md`

## Seed Case Used for Dry Run

Use this already-reviewed MAPLAB case bundle as the first A8 sample:

- Source bundle: `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/`
- Asset dir: `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/`
- Public-safe case label: `大臺南會展中心企業會議茶點`
- Related live page: `https://www.maplabkitchen.com/icc-tainan-catering/`

Reason:

- It is a real recent case.
- Images are already converted and partially used on WordPress.
- A4 manifest already separates public-safe label from internal folder name.

## Work Completed

- Created dry-run script: `tools/ai_workbook/a8_short_video_dry_run.py`
- Rendered proof video: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/a8-short-dry-run.mp4`
- Rendered cover draft: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/a8-short-cover.jpg`
- Generated platform metadata: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/platform_metadata.md`
- Created enhanced review-draft renderer: `tools/ai_workbook/a8_enhanced_video_draft.py` + `tools/ai_workbook/a8_render_story_frame.swift`
- Rendered subtitled review draft: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft/a8-short-review-draft.mp4`
- Rendered review cover: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft/a8-short-review-cover.jpg`
- Rendered v2 review draft: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v2/a8-short-review-draft.mp4`
- Owner review found v2 still below standard: visible left-bottom scene counter, no fixed opening/transition system, too little style difference after research.
- Added MAPLAB IG Soft v1 motion style spec: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md`
- Upgraded review-draft renderer to support fixed intro/outro, hidden counters by default, warm visual preset, and `xfade` transitions.
- Owner approved the corporate/tea CTA pattern: `台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab`.
- Added category-based CTA defaults to `tools/ai_workbook/a8_enhanced_video_draft.py`; `--ending-line` is now manual override only.
- Rendered v4 review draft with `--category corporate_tea`: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/a8-short-review-draft.mp4`.
- Added validator-gated local fallback runner: `tools/ai_workbook/a8_local_model_fallback.py`.
- Ran staged local-model prompt training with `qwen2.5:14b`; v2-v5 exposed failure modes, v6 passed.
- Saved valid local fallback output: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/parsed_output.json`.
- Wrote platform/Drive publishing plan: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/youtube_tiktok_drive_pipeline.md`
- Updated A8 skill: `skills/a8-video-pipeline-skills.md`

Validation:

- Video: H.264, 1080x1920, 12.666667 seconds.
- Review draft video: H.264, 1080x1920, 14.0 seconds, subtitles + `MAPLAB Kitchen` watermark, no audio.
- v2 review draft video: H.264, 1080x1920, 13.0 seconds, subtitles + watermark, no audio; rejected for style gate because public draft showed `01/05` counter and lacked fixed opening/transition template.
- `ffmpeg` exists.
- This host's `ffmpeg` lacks `drawtext`; enhanced review draft uses Swift/AppKit rendered frames as fallback.
- `ffmpeg` supports `xfade`; v3 should use crossfade transitions rather than hard concat.
- v4: H.264, 1080x1920, 30fps, 13.2 seconds; CTA category `corporate_tea`; outro QA frame checked and not clipped.
- Local model fallback smoke: `ollama list` confirms `gemma4:latest`, `qwen2.5:14b`, `qwen2.5-coder:7b`. `qwen2.5:14b` can draft storyboard / platform copy / risks, but must be validator-gated because it may invent visual details and CLI output may include terminal control codes.
- Local model fallback v6: `qwen2.5:14b` returned valid JSON; validator result `valid=true`, `errors=[]`, `warnings=[]`. Output is usable as A8 draft only, not final public copy.

## A8 Next Actions

1. Read `skills/a8-video-pipeline-skills.md`.
2. Review `a8_motion_style_upgrade.md` before rendering.
3. Review `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/`, `review_draft/`, `review_draft_v2/`, `review_draft_v3/`, and latest `review_draft_v4/`.
4. Review `youtube_tiktok_drive_pipeline.md` and confirm A8 Drive intake / platform approval route.
5. Use Google Vids / Canva / CapCut or approved AI video tool to add licensed music, motion polish, and final cover text.
6. Produce final 9:16 mp4 and cover from the accepted review draft.
7. Ask Owner/A1 for upload approval.
8. After approval, upload / schedule to YouTube Shorts and TikTok, create Pinterest pin/cover, then write `platform_receipts.md`.

Optional fallback route:

- If GPT/Gemini quota is unavailable, run `tools/ai_workbook/a8_local_model_fallback.py` with `qwen2.5:14b` for draft storyboard / platform metadata / approval checklist.
- Do not let local model publish, upload, or make final visual claims.
- Run cleanup / validation before using local output in public copy.
- Latest accepted example: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/run_report.md`.

## Approval Boundaries

A8 may directly do:

- Research.
- Source-folder readback.
- Local dry-run.
- Storyboard, metadata, and approval-ready package.
- Draft work inside Google Vids / Canva / CapCut if no external publishing occurs.

A8 must ask Owner/A1 before:

- Uploading or publishing to YouTube / TikTok / Instagram / Pinterest.
- Using private photos with clear faces, QR codes, phone numbers, meeting slides, client documents, or internal project labels.
- Sending files to a third-party AI tool when the file contains private client material.

## Resume Prompt

```text
你是 MAPLAB A8 影音內容產線。請先讀 CURRENT_STATUS.md、recalls/A8_recall.md、skills/a8-video-pipeline-skills.md、handoff/tasks/T-A8-001-folder-to-video-distribution.md。

本任務是把 MAPLAB 真實資料夾案例轉成可審核短影音產線。第一個 seed case 是 ICC Tainan bundle：
workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/

已完成 dry-run：
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/a8-short-dry-run.mp4
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/a8-short-cover.jpg
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/platform_metadata.md

已完成審核版 v1/v2：
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft/a8-short-review-draft.mp4
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft/a8-short-review-cover.jpg
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v2/a8-short-review-draft.mp4

Owner 指出 v2 不合格：左下角 `01/05` 不該顯示、缺固定開場/轉場系統、沒有把 MAPLAB 既有 IG 影片風格吸收成模板。已新增 MAPLAB IG Soft v1：
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md

最新產線應使用：
tools/ai_workbook/a8_enhanced_video_draft.py
tools/ai_workbook/a8_render_story_frame.swift

要求：預設不顯示 counter；要固定 intro/outro；轉場用 `xfade`；字幕語氣依 A2 品牌語氣；不得未核准上傳。
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/youtube_tiktok_drive_pipeline.md

Owner 已校正企業茶會 CTA，最新 v4 使用 category CTA 預設：
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/a8-short-review-draft.mp4
CTA: 台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab

地端備援已接好並跑過一次：
tools/ai_workbook/a8_local_model_fallback.py
workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/parsed_output.json
validator: valid=true, errors=[], warnings=[]

下一步：先確認最新 `review_draft_v4/` 是否通過手機預覽；如 GPT/Gemini 不可用，可先跑地端 fallback 產 storyboard / metadata 草稿，但仍需人工/雲端工具 polish。再用 Google Vids / Canva / CapCut 加授權配樂、動態細修與最終封面，產 final 9:16 mp4 + cover；再產 publish approval card。未經 Owner/A1 approval，不得上傳 YouTube / TikTok / Instagram / Pinterest。
```
