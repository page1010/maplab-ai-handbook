# Ads / Landing Alignment (Read-only)

Date: 2026-06-01

## VERIFIED

- Google Ads authenticated read-only evidence exists in latest A2 bundle (`google_ads_chrome_round_001.md`):
  - Account `844-336-3178` accessible.
  - Visible keywords concentrated in one campaign/ad group (`Campaign 4：高意圖搜尋_南台灣外燴` / `廣告群組 1`).
  - Keyword rows showed `Final URL = —` at row level.
- Meta Ads authenticated read-only detail evidence exists (`meta_ads_owner_chrome_detail_visual_bridge_round_006.md`):
  - Account `318634712` / business scope `215690449213844` confirmed.
  - Active ad sets are engagement-oriented seeds (`互動廣告組合 A/B`), not yet proven as WordPress landing traffic paths.
- Existing recommended landing map to 7 live To-B URLs exists in `review_request.md` and remains structurally valid.

## REASONABLE INFERENCE

- Ads intent mixing in one Google ad group likely weakens landing relevance and quality signals.
- Meta current objective behaves more like engagement/follow growth; a separate proposal-only traffic path to WordPress is still needed.

## MISSING DATA

- No new 2026-06-01 UI capture for Google Ads ad-level final URL / URL expansion.
- No new 2026-06-01 UI capture for Meta B ad set detail pane fields.
- No 2026-06-01 confirmation of conversion event drift/state changes.

## Safe Proposal (No external edits)

- Keep active engagement ads unchanged.
- Prepare proposal-only split for Google intents:
  - 企業外燴
  - 會議茶點
  - 開幕茶會
  - 品牌/公關
- Maintain URL mapping only to verified live URLs (not planned slugs).

## Next Concrete Command

```bash
cd /Users/pagemacmini/maplab-ai-handbook
rg -n "Final URL|最終到達網址|Campaign 4|互動廣告組合|Needs UI Detail" workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/*.md
```
