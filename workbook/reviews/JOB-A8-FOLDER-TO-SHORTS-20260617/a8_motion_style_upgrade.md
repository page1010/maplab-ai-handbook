# A8 Motion Style Upgrade - MAPLAB IG Soft v1

Date: 2026-06-17
Owner: A8 video pipeline
Status: applied to `review_draft_v3`

## Why v2 Was Not Good Enough

v2 proved the engineering path: A8 can read a case folder, render 1080x1920 H.264, add subtitles, add a watermark, and produce platform metadata.

The visual standard was still too low:

- It used a heavy black subtitle band that does not match MAPLAB's IG grid.
- It exposed a left-bottom `01/05` scene counter. This is useful for internal QA but should not be visible in public drafts.
- It had no fixed opening or ending system, so each run could drift.
- It did not turn MAPLAB's existing Reels into a repeatable style template.
- It solved output, not taste.

## Internal Reference Readback

Sources used:

- Owner-provided IG profile screenshots, 2026-06-17.
- Chrome read-only inspection of `https://www.instagram.com/maplabkitchen/reels/`, 2026-06-17.

Profile signals:

- Account: `@maplabkitchen`
- Public position: `MAPLAB KITCHEN-外燴設計顧問`
- Service fields: `西式派對 / 品牌活動 / 婚禮茶會`
- Brand promise visible in bio: `美感 x 節奏`
- Since marker: `SINCE 2016`
- Highlight categories include business/meeting catering, opening catering, art/wine events, seasonal dining, custom boxes.

Visible Reels grid / live link matrix:

| Rank | Reel | Live signal | Style observation |
|---|---|---:|---|
| 1 | `/maplabkitchen/reel/DTpw3nKjy4g/` | 41.7萬 views | high-performing party/celebration reference; 28.5s sample duration; warm, memory-led captioning. |
| 2 | `/maplabkitchen/reel/C5Y0eoLvGpF/` | 3,944 views | pinned; soft table scene, shallow depth, light overlay; 16.7s sample duration. |
| 3 | `/maplabkitchen/reel/C4w2kDkvMmk/` | 2,947 views | pinned; dessert closeup with stronger floral color; 13.6s sample duration. |
| 4 | `/maplabkitchen/reel/C0t_v8KPOhd/` | 2,811 views | pinned; birthday/event table, white fabric, light decor. |
| 5 | `/maplabkitchen/reel/DY93iaAvcJK/` | 2,778 views | text wall / floral scene; stronger typography moment but still minimal. |
| 6 | `/maplabkitchen/reel/DWqC8V-j74M/` | 1,991 views | dessert/table rhythm reference. |
| 7 | `/maplabkitchen/reel/DV3g4spD0m5/` | 1,996 views | dessert/table rhythm reference. |
| 8 | `/maplabkitchen/reel/DT98eBKDzXc/` | 1,521 views | event-table reference. |
| 9 | `/maplabkitchen/reel/DXmJ_w2D-Fq/` | 1,425 views | soft food closeup reference. |
| 10 | `/maplabkitchen/reel/DZg0DrVvjiM/` | 962 views | bottle / drink station reference; lower text weight. |

Grid-level pattern:

- Warm cream / sand / blush / low-saturation green.
- Shallow depth, close food details, table rhythm, floral or venue hints.
- Text is sparse and low-pressure. It usually describes the scene, not a hard sale.
- Watermark is subtle. It should never compete with food, flowers, or client environment.
- Public draft should not show production counters, file labels, or debug marks.

## External Tool Benchmark

The tool choice should follow the production level:

| Tool | Useful for A8 | Why not switch immediately |
|---|---|---|
| ffmpeg `xfade` + Swift/AppKit renderer | Fast local review draft, deterministic, no upload required. | Lower ceiling for complex motion graphics. |
| Remotion | Best next upgrade for template-based branded videos driven by data, React components, CSS, and reusable logic. | Commercial license rules may matter; introduce only when A8 has stable style requirements. |
| Motion Canvas | Good for coded motion graphics, explainers, and voice-over synchronized animations. | Better for motion explainer scenes than food/event recap drafts. |
| MoviePy | Python-friendly nonlinear editing, compositing, effects, and prototyping. | Slower than direct ffmpeg; less aligned with existing Swift renderer path. |
| Canva / CapCut / Google Vids | Final polish, licensed music, manual visual taste. | Upload or third-party processing needs approval for private client material. |

Decision:

- Keep the current local pipeline for A8 review drafts.
- Add fixed opening, ending, crossfade, warm filter, and hidden counters now.
- Upgrade to Remotion only after the MAPLAB IG Soft template is accepted, because Remotion is best when the design system is already defined.

## MAPLAB IG Soft v1 Template

Opening, 1.4-1.8s:

- Warm cream veil over the first image.
- `MAPLAB Kitchen` as the brand mark.
- Case/service line below, e.g. `大臺南會展中心企業會議茶點`.
- Thin warm-gold rule.
- `SINCE 2016` small, not decorative-heavy.

Scene cards, 2.2-2.8s each:

- Full-bleed image crop.
- Small top subtitle zone, no heavy black band.
- One short line per scene, 6-14 Chinese characters if possible.
- `MAPLAB Kitchen` watermark low-right, subtle.
- Optional small English/service note, not necessary in every scene.
- No `01/05` counter unless `--show-counter` is explicitly used for internal QA.

Transition:

- Default `xfade=fade`, 0.35s.
- Acceptable alternatives for later tests: `smoothleft`, `dissolve`.
- Avoid flashy transitions for corporate / meeting catering. The food and spatial rhythm should carry the video.

Filter:

- Warm, soft, low-contrast. Current local preset:
  - `brightness=0.012`
  - `contrast=0.94`
  - `saturation=1.035`
  - `gamma=1.015`
  - `unsharp=3:3:0.22`
- Do not push yellow flowers or warm wood into orange-heavy tones.

Ending, 1.5-2.0s:

- Warm cream veil.
- CTA should ask for event basics, not pressure:
  - `日期 / 人數 / 場地先傳給我們`
  - `台南外燴設計顧問｜MAPLAB Kitchen`

Caption voice:

- Start with location + scene + service.
- Use warm observation language: table rhythm, movement, guests can take food smoothly.
- Avoid generic hard-sell claims like "best", "must book", "limited time", or price-first copy.

## A8 Acceptance Gate

A8 can mark a local review draft as pass only if:

- 1080x1920 H.264.
- Has fixed MAPLAB opening and ending unless the task explicitly disables them.
- Uses a soft transition between scenes.
- No visible debug counter in public draft.
- Text does not cover the food subject.
- Brand voice follows A2: warm, concrete, scene-first, not pushy.
- Metadata has YouTube Shorts, TikTok, and Pinterest drafts.
- Music is not embedded locally unless license is verified.
- Upload/publish still waits for Owner/A1 approval.

