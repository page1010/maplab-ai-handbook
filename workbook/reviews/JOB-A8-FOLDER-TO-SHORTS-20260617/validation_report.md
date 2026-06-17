# A8 Folder-to-Shorts Validation Report

Date: 2026-06-17
Status: review_draft_v4_complete

## Commands Run

```bash
python3 tools/ai_workbook/a8_short_video_dry_run.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run \
  --title '大臺南會展中心茶點' \
  --subtitle '會議休息時間的穩定餐桌配置' \
  --case-label '大臺南會展中心企業會議茶點' \
  --limit 5 \
  --seconds 2.5
```

```bash
ffprobe -v error -show_entries stream=width,height,duration,codec_name -show_entries format=duration -of json workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run/a8-short-dry-run.mp4
```

```bash
python3 tools/ai_workbook/a8_enhanced_video_draft.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft \
  --title 大臺南會展中心茶點 \
  --case-label 大臺南會展中心企業會議茶點 \
  --seconds 2.8 \
  --limit 5
```

```bash
python3 tools/ai_workbook/a8_enhanced_video_draft.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v3 \
  --title '台南企業茶點配置' \
  --opening-title 'MAPLAB Kitchen' \
  --opening-subtitle '台南企業會議茶點' \
  --ending-line '日期 / 人數 / 場地先傳給我們' \
  --case-label '大臺南會展中心企業會議茶點' \
  --scene-line '會議中場，取餐要順' \
  --scene-line '小份量點心，方便交流' \
  --scene-line '飲品與甜點分區' \
  --scene-line '桌面乾淨，節奏更穩' \
  --scene-line '台南活動茶點規劃' \
  --limit 5 \
  --seconds 2.4 \
  --opening-seconds 1.55 \
  --ending-seconds 1.7 \
  --transition fade \
  --transition-seconds 0.35
```

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,duration \
  -of json workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v3/a8-short-review-draft.mp4
```

```bash
python3 tools/ai_workbook/a8_enhanced_video_draft.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4 \
  --title '台南企業茶點配置' \
  --category corporate_tea \
  --opening-title 'MAPLAB Kitchen' \
  --opening-subtitle '台南企業會議茶點' \
  --case-label '大臺南會展中心企業會議茶點' \
  --scene-line '會議中場，取餐要順' \
  --scene-line '小份量點心，方便交流' \
  --scene-line '飲品與甜點分區' \
  --scene-line '桌面乾淨，節奏更穩' \
  --scene-line '台南活動茶點規劃' \
  --limit 5 \
  --seconds 2.4 \
  --opening-seconds 1.55 \
  --ending-seconds 1.7 \
  --transition fade \
  --transition-seconds 0.35
```

## Results

- `a8-short-dry-run.mp4`: H.264, 1080x1920, 12.666667 seconds.
- `a8-short-cover.jpg`: generated from the first frame and visually inspected.
- `platform_metadata.md/json`: generated.
- `dry_run_manifest.json`: generated with source image list and text overlay status.
- `review_draft/a8-short-review-draft.mp4`: H.264, 1080x1920, 14.0 seconds, subtitles + `MAPLAB Kitchen` watermark.
- `review_draft/a8-short-review-cover.jpg`: generated.
- `review_draft/review_draft_platform_metadata.md/json`: generated.
- `review_draft/review_draft_manifest.json`: generated with source image list, scene lines, and no-audio status.
- `youtube_tiktok_drive_pipeline.md`: generated with Drive intake, tool stack, benchmark, and publishing boundary.
- `a8_motion_style_upgrade.md`: generated; defines MAPLAB IG Soft v1 after Owner critique.
- `review_draft_v3/a8-short-review-draft.mp4`: H.264, 1080x1920, 30 fps, 13.2 seconds, fixed intro/outro, `xfade` transition, hidden counter.
- `review_draft_v3/a8-short-review-cover.jpg`: generated.
- `review_draft_v3/qa_frames/`: sampled intro / scene / outro frames for visual QA.
- `review_draft_v4/a8-short-review-draft.mp4`: H.264, 1080x1920, 30 fps, 13.2 seconds, category `corporate_tea`, CTA `台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab`.
- `review_draft_v4/qa_frames/qa-99-outro.jpg`: sampled and visually inspected; CTA renders as two readable lines without clipping.

## Tool Findings

- Chrome readback could inspect the reference Reel metadata.
- Chrome read-only profile inspection could inspect MAPLAB's own IG Reels grid and sample Reel durations.
- `yt-dlp` failed with `No module named expat`; not used as the main route.
- `ffmpeg` is available.
- `ffmpeg` supports `xfade`; v3 uses crossfade rather than hard concat.
- v4 uses category CTA defaults from `--category`; `--ending-line` is now only for manual override.
- `ffmpeg` lacks `drawtext`, so basic local dry-run is image-only.
- Enhanced review draft uses Swift/AppKit rendered frames to add subtitles and watermark without `drawtext`.
- Review draft intentionally has no audio; final publishing should use platform-licensed music.
- Local model availability verified with `ollama list`: `gemma4:latest`, `qwen2.5:14b`, `qwen2.5-coder:7b`.
- `qwen2.5:14b` smoke could produce storyboard / platform copy / risk fields for this task, but output quality requires validation: CLI output included terminal control codes, and the model inferred visual details not guaranteed by the source manifest.

## Local Model Fallback Verdict

Local model is suitable as L1 fallback for:

- storyboard draft
- platform metadata draft
- privacy / brand checklist
- approval card draft
- missing-field detection

Local model is not suitable as autonomous final publisher or visual truth source. It must not claim image contents that were not confirmed by image QA, manifest, or human / vision readback.

## Approval Status

No external publishing was performed.

v4 is an improved review draft, not a final publish asset. It still needs mobile review and licensed music / final cover polish before upload approval.

Before upload, A8 must create a publish approval card listing:

- final video path
- cover path
- destination platform/account
- captions/metadata
- privacy checks
- Owner options
