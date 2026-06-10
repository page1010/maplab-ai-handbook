# Ads / Landing Alignment

Date: 2026-06-08
Mode: read-only evidence patrol

## VERIFIED

- Google Ads verified account context remains `844-336-3178`.
- Latest authenticated Google Ads evidence still shows 13 visible keywords concentrated in:
  - `Campaign 4：高意圖搜尋_南台灣外燴`
  - `廣告群組 1`
- Keyword-row `最終到達網址` showed `—` in the last verified UI packet; this means row-level URL is not proven.
- Latest verified Meta account context remains:
  - account `318634712`
  - business/global scope `215690449213844`
- `互動廣告組合 A 企業窗口` is verified as engagement/follow-oriented, not a confirmed WordPress traffic ad.
- `互動廣告組合 B 公關公司窗口` remains a valid B2B seed, but detailed targeting and destination remain incomplete.
- Proposal-only alignment documents already exist and remain internally consistent:
  - `google_ads_change_plan.md`
  - `ads_landing_settings_round_008.md`
  - `meta_landing_page_proposal_round_007.md`

## Current Shared Landing Map

| Intent cluster | Landing URL | Google proposal state | Meta proposal state |
|---|---|---|---|
| 開幕茶會 / 辦公室 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | P1 split proposed | landing-page traffic path proposed |
| 會議茶點 / 研討會 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | P1 split proposed | landing-page traffic path proposed |
| 企業 / 品牌 / 公關 | `https://www.maplabkitchen.com/corporate-catering-tainan/` / `https://www.maplabkitchen.com/brand-esg-catering-service/` / `https://www.maplabkitchen.com/press-conference-catering/` | P1/P2 proposal only | A seed validated, B still needs UI detail |
| VIP / 展覽 / 商務接待 | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | proposal-only | landing-page traffic path proposed |
| 文化場館 / 特展 | `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` | lower-priority support route | proposal-only retargeting / authority route |

## REASONABLE INFERENCE

- Google and Meta planning are converging on the same live URL set, which is the right structure.
- The weak point is freshness and implementation proof, not planning coherence.
- The safest next move remains proposal review plus refreshed UI capture before any ad change approval.

## MISSING DATA

- No fresh proof of ad-level final URL or URL expansion.
- No fresh proof of Meta destination URLs or CTA destination state.
- No fresh proof of pixel/custom audience readiness.

## Guardrail Reminder

- Do not treat proposal routing as live ad state.
- Do not infer that current Meta engagement campaigns already send traffic to WordPress.
- Do not infer final URL coverage from repo plans alone.

## Next Concrete Command

```bash
cd /Users/pagemacmini/maplab-ai-handbook
rtk rg -n "Final URL|landing-page traffic|Needs UI Detail|A 企業窗口|B 公關公司窗口" \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/google_ads_change_plan.md \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/meta_landing_page_proposal_round_007.md \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/google_ads_chrome_round_001.md \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_owner_chrome_detail_visual_bridge_round_006.md
```
