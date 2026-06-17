# A8 YouTube/TikTok + Drive Production Plan

Status: draft_ready_for_owner_review
Updated: 2026-06-17

## Answer

可以實際結合 YouTube Studio、Google Drive 素材與半 AI 生成跑影片，但要拆成三層：

1. **Drive intake**：A8 讀 Google Drive / ASSET_LOG / TimeTree 對應場次，不直接猜活動名稱。
2. **Video production**：本機先產 review draft；正式版再用 Google Vids / Canva / CapCut 加字幕、授權音樂、封面與細修。
3. **Publishing**：YouTube / TikTok / Pinterest 只能在 Owner/A1 approval 後上傳；上傳後必須回寫 receipts。

本輪已補出比 dry-run 更接近可審核的版本：

- Review draft video: `review_draft/a8-short-review-draft.mp4`
- Review draft cover: `review_draft/a8-short-review-cover.jpg`
- Metadata: `review_draft/review_draft_platform_metadata.md`
- Spec: H.264, 1080x1920, 14.0s, subtitles + `MAPLAB Kitchen` watermark, no audio.

這支仍不是最終發布版，因為缺授權配樂、動態剪輯、封面細修與平台上傳回讀。

## How A8 Gets Drive Assets

Current local truth:

- Drive credential guide: `skills/credentials/google-drive-api.md`
- Active MAPLAB asset folder: `MAPLAB_ASSETS = 1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`
- Asset log: `MAPLAB_ASSET_LOG = 1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`, tab `工作表1`
- Event calendar source: `data/timetree_events_2022_2026.json`
- Rule: Drive tree is source archive; Sheet is index.

New coworker/A8 must receive this in the task card:

```text
Source:
- Drive folder ID or local review bundle path
- Internal folder/event title
- Expected public-safe case label if known

Required readbacks:
- folder id/name/parent/trashed
- source image list
- ASSET_LOG rows if available
- TimeTree event match candidates
- public-safe label
- excluded assets and exclusion reason
```

If event matching is ambiguous, A8 marks `needs_owner_label` and must not publish the internal folder name.

## Recommended Tool Stack

| Layer | Tool | Reason |
|---|---|---|
| Intake | Google Drive connector/API + ASSET_LOG + TimeTree JSON | Keeps event/source truth file-backed. |
| Local proof | `tools/ai_workbook/a8_short_video_dry_run.py` | Fast 9:16 smoke test. |
| Review draft | `tools/ai_workbook/a8_enhanced_video_draft.py` | Adds subtitles + watermark even when ffmpeg lacks drawtext. |
| First AI edit | Google Vids | Prompt + Drive file to suggested storyboard/scenes/media/music. |
| Final polish | Canva / CapCut | Better subtitle placement, music, cover, mobile-first review. |
| YouTube | YouTube Studio first; Data API only after scope/audit | API upload requires `youtube.upload`; unverified projects may be private-only. |
| TikTok | Web/Studio first; Content Posting API after app/scope/audit | Direct Post requires app + `video.publish`; unaudited clients are private-only. |
| Pinterest | Cover-first Pin workflow | Pinterest wants strong vertical visual, clear branding, concise copy. |

## Quality Verdict

Current dry-run:

- Good: source folder can become a valid 9:16 MP4.
- Not good enough: no subtitles, no music, no watermark, no cover copy, no upload readback, no final privacy check.

Review draft:

- Better: readable subtitle overlay, watermark, platform metadata, 14s structure.
- Still missing: gentle motion, licensed music, mobile cover optimization, final brand QA, YouTube/TikTok preview.

Final publish-quality target:

- 12-25 seconds.
- 5 scenes max.
- 6-12 Chinese characters per subtitle line.
- One calm licensed music bed at low volume.
- Subtle MAPLAB watermark on every scene.
- Cover text: `台南企業會議茶點` or `大臺南會展中心茶點`.
- No price, internal date, local path, private meeting material, QR code, phone number, slides, or face close-ups.

## Benchmark

Primary business/style benchmark:

- **24 Carrots Catering & Events**: high-end event/catering positioning, strong corporate/wedding/event service framing. Useful for MAPLAB's trust and event-service narrative.

Editing/pacing references:

- **Tasty**: simple food-forward frames, quick cuts, text overlay; useful for making food instantly readable on mobile.
- **Food52**: calmer food/editorial tone; useful for MAPLAB's restrained, less salesy brand voice.

MAPLAB should not copy viral recipe energy directly. For B2B cases, the better formula is:

```text
clean event table -> operational observation -> food detail -> venue/context -> soft CTA
```

## Was The Previous Tutorial Too Coarse?

Yes. The previous handoff was enough to prove the pipeline, but not enough to make a good video. It missed:

- exact shot order and duration
- subtitle copy per scene
- text-safe zones
- cover spec
- music choice boundary
- watermark rule
- upload privacy setting
- platform preview/readback
- post-publish receipt
- failure feedback loop

Future A8 task cards must require:

```text
source_manifest -> storyboard -> review draft -> final edit -> approval card -> upload receipts -> performance notes
```

## Sources Checked

- YouTube Shorts upload help: https://support.google.com/youtube/answer/12779649
- YouTube Studio upload help: https://support.google.com/youtube/answer/57407
- YouTube Data API `videos.insert`: https://developers.google.com/youtube/v3/docs/videos/insert
- TikTok Content Posting API: https://developers.tiktok.com/doc/content-posting-api-get-started
- Google Vids product page: https://workspace.google.com/products/vids/
- Pinterest creative best practices: https://business.pinterest.com/creative-best-practices/
- 24 Carrots official site: https://24carrots.com/
