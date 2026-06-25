# A8 Publish Approval Card v6 — 2026-06-24

Role: A8-APPROVAL worker
Environment: `/Users/pagemacmini/maplab-ai-handbook`
Scope: package the existing local v6 video, cover, metadata, and reports for Owner/A1 review.

Boundaries honored in this card:

- No upload.
- No publish.
- No social account access.
- No commit or push.
- Write target limited to this file.

## Verdict

Status: `approval_ready_for_owner_review`, not publish-ready.

The v6 local-motion package is coherent enough for Owner/A1 to review and decide the next safe action. It should not be called publish-ready because there is no mobile proof, no platform preview proof, no licensed music selection, no final cover approval, and no upload receipt.

Recommended decision: approve v6 for mobile/platform preview only, with no posting. The preview should verify phone-safe text placement, cover crop, outro CTA visibility, and platform licensed music choice before any publish approval.

## Evidence Read

- `CURRENT_STATUS.md`
- `TASK_QUEUE.md`
- `pitfalls.md`
- `handoff/tasks/T-A8-001-folder-to-video-distribution.md`
- `workbook/reviews/JOB-DISPATCH-HUMAN-EYE-AUDIT-20260624/completion_human_eye_audit.md`
- `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/routing.md`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/publish_readiness_20260624.md`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/pipeline_report.md`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.md`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/parsed_output.json`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/validation.json`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.json`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_manifest.json`

## Candidate Assets

| Asset | Path | Status |
|---|---|---|
| v6 MP4 | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4` | Current local review candidate |
| v6 cover | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-cover.jpg` | Local cover draft |
| Pipeline report | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/pipeline_report.md` | Evidence source |
| Parsed local model output | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/parsed_output.json` | Validator-clean source copy |
| Validation JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/validation.json` | `valid=true` |
| Render metadata MD | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.md` | Platform metadata draft; has one copy issue |
| Render metadata JSON | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_platform_metadata.json` | Platform metadata draft; has one copy issue |
| Render manifest | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_manifest.json` | Visual template and source image list |
| Intro QA frame | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-intro.jpg` | Viewed locally |
| Middle QA frame | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-middle.jpg` | Viewed locally |
| Outro QA frame | `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-outro.jpg` | Viewed locally |

Source images listed by render manifest:

- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-business-meeting-catering-14.webp`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-closeup-07.webp`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-table-overview-01.webp`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-table-overview-02.webp`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-corporate-catering-display-11.webp`

## ffprobe Summary

Current ffprobe result for the candidate MP4:

```json
{
  "streams": [
    {
      "index": 0,
      "codec_name": "h264",
      "codec_type": "video",
      "width": 1080,
      "height": 1920,
      "r_frame_rate": "30/1",
      "avg_frame_rate": "30/1",
      "duration": "13.166667"
    }
  ],
  "format": {
    "duration": "13.166667"
  }
}
```

Interpretation:

- Format is correct for short vertical review: H.264, 1080x1920, 30 fps, 13.166667 seconds.
- Only a video stream was found. No audio stream is present in the local MP4.
- This supports local review, not final publish approval.

## Visual Package

Render manifest status:

- Case label: `大臺南會展中心企業會議茶點`
- Category: `corporate_tea`
- Visual template: `MAPLAB IG Soft v1`
- Opening: fixed intro card
- Ending: fixed CTA card
- Counter: hidden
- Transition: `xfade`, fade, 0.35 seconds
- Subtitle overlay: Swift/AppKit rendered
- Watermark: `MAPLAB Kitchen`
- Audio: `none_local_draft_add_platform_licensed_music_before_publish`
- Render status: `review_draft_rendered`

Human-eye notes from local image review:

- Cover and intro: readable, brand-safe, no visible debug counter. The food image is softened by a pale overlay, so it feels reviewable but not the strongest platform thumbnail.
- Middle frame: stronger food visibility and clear text. It may be a better thumbnail candidate than the current intro-style cover.
- Outro: CTA is readable and not clipped in the local frame. Bottom watermark and platform UI safety still need phone/platform proof.
- No obvious faces, QR codes, phone numbers, meeting slides, or private labels were visible in the cover/intro/middle/outro frames inspected locally. This is not a full moving-video privacy pass.

## Platform Copy Draft

Validator-clean source from `parsed_output.json`:

### YouTube Shorts

- Title: `大臺南會展中心企業會議茶點 | 台南企業外燴茶點 #Shorts`
- Description:

```text
大臺南會展中心企業會議茶點紀錄。以好拿取、畫面乾淨、休息時間不打斷交流為主。

台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab
```

- Hashtags: `#台南外燴 #企業外燴 #會議茶點 #MAPLAB #Shorts`

### TikTok

Clean candidate caption from `parsed_output.json`:

```text
大臺南會展中心企業會議茶點。會議休息時間的茶點配置，重點是好拿取、桌面留白乾淨。台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab
```

Important issue: `rendered_video/review_draft_platform_metadata.md` and `.json` still contain this stale TikTok phrase:

```text
重點是好拿取、動線穩
```

This should be replaced before platform preview because `動線穩` is an internal/process-style phrase previously flagged by A8 wording rules.

### Pinterest

- Board draft: `MAPLAB Catering / Corporate Refreshments`
- Pin title: `大臺南會展中心企業會議茶點｜台南企業外燴茶點`
- Pin description: `大臺南會展中心企業會議茶點與飲品桌面配置參考。`

### CTA

```text
台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab
```

CTA human verdict: can be reviewed. It is clear, category-specific, and aligned with the existing corporate tea default. It still needs platform-safe crop/readback.

## Privacy Checklist

| Check | Current status | Evidence / gap |
|---|---|---|
| Public-safe case label | Pass for review | Uses `大臺南會展中心企業會議茶點`; source case was already selected as public-safe in the A8 task card. |
| Faces | No issue observed in sampled frames | Cover, intro, middle, and outro frames inspected locally. Full moving-video pass still needed. |
| QR codes / phone numbers | No issue observed in sampled frames | No QR or phone number visible in sampled frames. Full video and platform UI proof still needed. |
| Meeting slides / client documents | No issue observed in sampled frames | No private slide/document visible in sampled frames. Full video pass still needed. |
| Internal local paths in public copy | Pass for draft copy | Platform copy fields do not expose local paths. This approval card itself contains internal paths for review evidence. |
| Internal/process wording | Needs edit before preview | Rendered TikTok metadata still says `動線穩`; use validator-clean caption instead. |
| Platform safe zones | Missing | No phone/platform preview screenshots or readback. |
| Final Owner/A1 approval | Missing | No approval receipt found. |

## Audio / Licensed Music Status

Status: not ready for publishing.

- ffprobe found no audio stream in the MP4.
- Pipeline report explicitly marks audio as none in the local draft.
- Metadata recommends using platform licensed music after upload/draft setup.
- No licensed music title, source, platform sound ID, or usage proof exists yet.

Decision needed before publish approval:

- Use platform-native licensed music in YouTube/TikTok/IG, or keep no-audio only if Owner/A1 explicitly accepts it for this piece.
- Record the selected music source or platform sound ID in the next receipt before posting.

## Mobile / Platform Preview Status

Status: missing.

Current evidence:

- Local cover opened and inspected.
- Local QA frames opened and inspected.
- ffprobe passed for local MP4.

Missing before any publish-ready claim:

- Phone preview or platform draft preview for YouTube Shorts.
- Phone preview or platform draft preview for TikTok.
- IG Reels cover crop / safe-zone preview if IG is in scope.
- Pinterest pin cover preview if Pinterest is in scope.
- Screenshot/readback showing first screen, middle frame or selected cover, and outro CTA after platform UI overlays.

## Human Approval Notes

Cover:

- Reviewable, but not final-thumbnail strong yet. The pale overlay makes the brand text readable, but the food impact is muted. Consider using the middle food-forward frame as a cover candidate or increasing visual contrast for the current cover.

CTA:

- Reviewable. The line is direct and appropriate for corporate tea/event inquiries.
- Still needs phone/platform safe-zone proof because social UI can cover lower or side text.

Copy:

- YouTube and Pinterest drafts are reviewable.
- TikTok must be synced to the validator-clean caption before preview; the rendered metadata still contains `動線穩`.
- Copy should not be approved for posting until Owner/A1 confirms the final wording and platform hashtags.

## Owner / A1 Decision Options

### Option 1 — Approve for mobile preview

Approve v6 only for phone/platform draft preview, not posting.

Required preview evidence:

- First-screen screenshot or readback.
- Cover/thumbnail crop screenshot or readback.
- Outro CTA screenshot or readback.
- Licensed music decision or no-audio decision.
- Confirmation that TikTok caption uses the clean text, not the stale `動線穩` metadata.

### Option 2 — Request edits

Suggested minimal edits:

- Replace stale TikTok metadata phrase `動線穩` with the validator-clean phrase `桌面留白乾淨`.
- Compare current cover with the middle food-forward frame as thumbnail candidate.
- Confirm or choose platform licensed music.
- Run a full moving-video privacy pass before platform preview.

### Option 3 — Reject / remake

Use this if Owner/A1 wants a stronger public-facing piece instead of approving this as a local draft.

Remake direction:

- Re-run A8 local video pipeline from selected A-class frames.
- Use a food-forward first screen rather than a pale brand intro as the cover.
- Keep fixed CTA and hidden counter.
- Keep the output local until Owner/A1 re-approves preview.

## Next Smallest Recheck

Smallest safe next step: Owner/A1 chooses Option 1 or Option 2.

If Option 1 is chosen, run a no-post mobile/platform preview and save proof:

1. Open the v6 MP4 and cover on a phone or platform draft surface.
2. Verify first screen, selected cover, and outro CTA under platform UI overlays.
3. Confirm the platform caption uses the validator-clean copy.
4. Choose licensed platform music or explicitly approve no-audio.
5. Save screenshots/readback in the next review receipt before any upload/publish decision.

Until that proof exists, this package remains `approval_ready_for_owner_review`, not publish-ready.
