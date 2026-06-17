# A8 Reel Research Notes

Date: 2026-06-17
Reference: `https://www.instagram.com/reel/DZp4BxgguqC/?igsh=c3k0NGM1YTB3N2Fz`

## Chrome Readback

Chrome logged-in, read-only inspection returned:

- Creator: `michelletech2026`
- Caption: `Using Higgsfield MCP to make a bag`
- Metadata date: 2026-06-16
- Public metrics at readback: 25 likes, 5 comments
- Main observed video duration: about 29.6 seconds
- Keywords from page metadata include: `higgsfield mcp`, `create content`, `side hustle`, `content marketing`, `make money online`, `business`.

## What To Copy

Do not copy the Reel's content, visuals, or money-making framing. Copy the production architecture:

1. One clear tool workflow.
2. One concrete outcome.
3. Short vertical proof.
4. Platform-native caption and hashtags.
5. A repeatable loop that can be run again with a new source folder.

## A8 Translation

MAPLAB version:

```text
Folder case evidence
→ public-safe case label
→ storyboard and subtitle plan
→ local dry-run mp4 + cover
→ Google Vids / Canva / CapCut final assembly
→ YouTube Shorts / TikTok / IG Reels / Pinterest metadata
→ Owner approval
→ upload receipts
→ learning-loop writeback
```

## External Tool Notes

Search results and current news describe Higgsfield as a generative media workflow layer used for short-form social media and marketing. Recent reporting also emphasizes prompt/detail consistency, iteration, and orchestration over just choosing one model.

Implication for MAPLAB:

- Treat AI video tools as orchestration surfaces, not magic final editors.
- Preserve prompt, source folder, generated assets, final metadata, and upload receipts.
- Use real MAPLAB cases as the differentiator; generated motion is optional.

## First Dry-Run Case

Seed case: `大臺南會展中心企業會議茶點`

Reason:

- Recent real case.
- Source bundle already has public-safe labels and visual QA notes.
- WordPress page is live, so A8 can connect video metadata back to a valid landing page.

Dry-run output:

- `dry_run/a8-short-dry-run.mp4`
- `dry_run/a8-short-cover.jpg`
- `dry_run/platform_metadata.md`

## Constraints Found

- `yt-dlp` failed on this host because the runtime reported `No module named expat`; Chrome readback was the usable route.
- Local `ffmpeg` exists and can render 9:16 H.264, but lacks `drawtext`; text overlay should be done in Google Vids / Canva / CapCut.
- Publishing and external AI upload remain approval-required.
