# A8 Folder-to-Shorts Validation Report

Date: 2026-06-17
Status: review_draft_complete

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

## Tool Findings

- Chrome readback could inspect the reference Reel metadata.
- `yt-dlp` failed with `No module named expat`; not used as the main route.
- `ffmpeg` is available.
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

Before upload, A8 must create a publish approval card listing:

- final video path
- cover path
- destination platform/account
- captions/metadata
- privacy checks
- Owner options
