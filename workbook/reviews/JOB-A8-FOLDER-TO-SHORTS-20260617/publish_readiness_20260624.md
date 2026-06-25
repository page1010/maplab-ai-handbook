# A8 Publish Readiness Review — 2026-06-24

Scope: A8 folder-to-shorts readiness check for `JOB-A8-FOLDER-TO-SHORTS-20260617`.

Boundaries honored: no upload, no publishing, no social account access, no secrets, no push, no commit. This file is the only repo file updated in this run.

## Verdict

A8 is usable for **local review draft / approval package production**, but **not usable for automatic publishing**.

More precise judgment:

- The pipeline has already produced multiple 9:16 H.264 MP4 review assets from the ICC Tainan case.
- `local_model_video_v6` is the newest verified local-motion review draft found in this check.
- `local_model_video_v5` remains a valid earlier accepted local-model MP4 proof.
- `review_draft_v4` is historically important and ffprobe-valid, but it should not be treated as the current publish candidate because its scene/platform copy still contains internal/process wording later rejected by Owner and validator, including `取餐要順`, `方便交流`, `動線穩`, and `節奏更穩`.
- No external publish receipt exists. No Owner/A1 approval for upload was found. Therefore A8 is not publish-ready for TikTok / YouTube Shorts / IG Reels / Pinterest.

Current best candidate for local review: `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4`.

## Produced Assets

### v4 Review Draft

Status: produced; specs pass; superseded for publish consideration due to rejected wording in metadata/scene lines.

| Type | Absolute path |
|---|---|
| MP4 | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/a8-short-review-draft.mp4` |
| Cover | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/a8-short-review-cover.jpg` |
| Metadata MD | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.md` |
| Metadata JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.json` |
| Manifest | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_manifest.json` |
| QA frame | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/qa_frames/qa-99-outro.jpg` |
| Report source | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/validation_report.md` |

ffprobe summary:

```json
{
  "codec": "h264",
  "resolution": "1080x1920",
  "fps": "30/1",
  "duration": "13.200000"
}
```

Notes:

- Counter is hidden; fixed intro/outro and CTA are present.
- Audio is absent by design.
- This version is not the recommended publish candidate because later A8 rules reject its internal/process language.

### v5 Local Model Video

Status: produced; validator pass; accepted local-model MP4 proof from 2026-06-17.

| Type | Absolute path |
|---|---|
| MP4 | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-video.mp4` |
| Cover | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-cover.jpg` |
| Pipeline report | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/pipeline_report.md` |
| Local model run report | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/local_model/run_report.md` |
| Parsed JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/local_model/parsed_output.json` |
| Validation JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/local_model/validation.json` |
| Rendered metadata MD | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/rendered_video/review_draft_platform_metadata.md` |
| Rendered metadata JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/rendered_video/review_draft_platform_metadata.json` |
| Render manifest | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/rendered_video/review_draft_manifest.json` |
| QA frames | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/qa_frames/` |

ffprobe summary:

```json
{
  "codec": "h264",
  "resolution": "1080x1920",
  "fps": "30/1",
  "duration": "13.200000"
}
```

Validation:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

Scene lines:

- `茶點動線清楚`
- `交流節奏不被打斷`
- `飲品甜點分區`
- `桌面留白乾淨`
- `台南企業茶會`

### v6 Local Motion Video

Status: produced; validator pass; newest local-motion review draft found in this check.

| Type | Absolute path |
|---|---|
| MP4 | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4` |
| Cover | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-cover.jpg` |
| Pipeline report | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/pipeline_report.md` |
| Local model run report | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/run_report.md` |
| Parsed JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/parsed_output.json` |
| Validation JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/validation.json` |
| Rendered metadata MD | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.md` |
| Rendered metadata JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.json` |
| Render manifest | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_manifest.json` |
| QA frames | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/` |

ffprobe summary:

```json
{
  "codec": "h264",
  "resolution": "1080x1920",
  "fps": "30/1",
  "duration": "13.166667"
}
```

Validation:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

Scene motions from report:

- `pan_right`
- `dolly_in`
- `static`
- `dolly_out`
- `pan_left`

Observed local QA from this run:

- v6 cover opens and is readable on desktop preview.
- v6 outro CTA opens and text is not clipped on desktop preview.
- This is not mobile eye proof and not platform preview proof.

## Publish Gap

Common gap for all platforms:

- No mobile eye proof on phone / platform preview surface.
- No licensed music selected or attached; all local drafts are no-audio review drafts.
- No final cover polish approved for platform thumbnails.
- No final platform copy approval; v6 copy is draft-level and needs Owner/A1 brand approval.
- No final privacy check on full moving video for faces, QR codes, phone numbers, meeting slides, client documents, or private labels.
- No current v6 Publish Approval Card. Existing `publish_approval_card_draft.md` is v4-era and stale.
- No Owner/A1 upload approval.
- No upload receipts or platform URLs.

Platform-specific gaps:

| Platform | Missing before publish |
|---|---|
| YouTube Shorts | YouTube Studio preview, title/description/#Shorts final review, licensed music decision, thumbnail/cover readback, Owner/A1 upload approval. |
| TikTok | TikTok app/Studio mobile preview, caption/hashtag final review, licensed TikTok sound selection, cover frame check, Owner/A1 upload approval. |
| IG Reels | A3 handoff or IG operator readback, Reel cover crop check, caption/hashtag final review, licensed audio choice, Owner/A1 approval. |
| Pinterest | Final static cover/pin image polish, board selection, pin title/description approval, no local path/internal label in public copy, Owner/A1 approval. |

## Next Commands

Only local validation and approval-card preparation are listed. No upload or publishing command is included.

Re-run the latest candidate ffprobe:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate,duration \
  -show_entries format=duration \
  -of json \
  /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4
```

Open local video and cover for human review:

```bash
open /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4
open /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-cover.jpg
```

Read current v6 evidence before making any approval card:

```bash
sed -n '1,220p' /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/pipeline_report.md
sed -n '1,220p' /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/run_report.md
sed -n '1,220p' /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/validation.json
```

Prepare the next approval card locally:

```bash
sed -n '368,388p' /Users/pagemacmini/maplab-ai-handbook/skills/a8-video-pipeline-skills.md
sed -n '1,180p' /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/publish_approval_card_draft.md
```

Then update `publish_approval_card_draft.md` to v6 with `apply_patch` or the next session's approved edit path. Minimum card fields: v6 video, v6 cover, platform copy, privacy checks, mobile proof status, licensed music status, Owner options. Do not upload.

## Resume Prompt

```text
你是 MAPLAB A8 影音內容產線 worker，環境 /Users/pagemacmini/maplab-ai-handbook。
任務：接續 A8 folder-to-shorts publish readiness，不上傳、不發布、不讀 secrets。
先讀 CURRENT_STATUS.md、TASK_QUEUE.md、pitfalls.md、handoff/tasks/T-A8-001-folder-to-video-distribution.md。
再讀 recalls/A8_recall.md、skills/a8-video-pipeline-skills.md、skills/a8-local-motion-integration.md。
本次 readiness 檔：workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/publish_readiness_20260624.md。
核心 verdict：A8 可做本地 review draft / approval package，不可自動發布。
v4 影片規格合格但含被淘汰內部流程語，不當最新 publish candidate。
v5 有 accepted local-model MP4，validator valid=true。
v6 是最新 local-motion review draft candidate。
v6 video: workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4
v6 cover: workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-cover.jpg
v6 report: workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/pipeline_report.md
v6 ffprobe: h264, 1080x1920, 30fps, 13.166667s。
下一步只做本地驗證與 approval card：手機/平台預覽、授權音樂、封面 polish、平台 copy、privacy check、Owner/A1 approval。
不得上傳 YouTube/TikTok/IG/Pinterest，不得碰社群帳號。
若要產 approval card，先把 publish_approval_card_draft.md 從 v4 更新到 v6，列出 Owner options。
```
