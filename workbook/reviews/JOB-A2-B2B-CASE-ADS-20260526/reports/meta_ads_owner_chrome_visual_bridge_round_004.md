# Meta Ads Owner Chrome Visual Bridge — Round 004

日期：2026-05-26
執行者：A2
方式：Computer Use + Owner Chrome UI，只讀檢查。

## Purpose

Antigravity 看不到 A2 正在看的 Owner Chrome 畫面，所以 A2 將 live UI 轉成「視覺證據包」：

1. A2 用 Computer Use 讀取正確 Owner Chrome 視窗。
2. A2 只截取 Meta Ads Manager 視窗，不包含旁邊 Telegram / agent FB / Antigravity 對話。
3. A2 將畫面事實萃取成本文報告。
4. Antigravity 只能讀本報告與截圖，再產分析；不能自行假設 Chrome UI。
5. A2 回頭驗收 Antigravity 是否忠於證據。

## Correct Window

- 正確 app：`/Users/pagemacmini/Desktop/Google Chrome.app/`
- 正確視窗標題：`(1) 廣告管理員 - 管理廣告 - 行銷活動`
- 正確 URL context：
  - `adsmanager.facebook.com/adsmanager/manage/campaigns`
  - `global_scope_id=215690449213844`
  - `business_id=215690449213844`
  - `act=318634712`
- 錯誤路徑：`/Applications/Google Chrome.app` 裡 agent 使用中的 Facebook / 財經網紅視窗。該視窗不可再作 MAPLAB Meta Ads 證據。

## Screenshot Evidence

- Cropped evidence：`visual_evidence_round_004/meta_ads_owner_chrome_campaigns_round_004_cropped.png`
- Full-screen raw capture：已排除，不進 repo 證據鏈，避免混入旁邊私人聊天或其他 agent 視窗。

## Verified Facts From Owner Chrome UI

- Meta ad account shown：`318634712 (318634712)`
- Business / global scope：`215690449213844`
- Date range：`過去 30 天：2026年4月26日 – 2026年5月25日`
- A2 did not click:
  - `檢查並發佈 (4)`
  - `捨棄草稿`
  - policy acceptance dialogs
  - campaign / ad set / ad edit controls
- UI shows an active draft state:
  - `檢查並發佈 (4)`
  - `捨棄草稿`
- Visible layers:
  - `行銷活動`
  - `廣告組合`
  - `廣告`
- Visible tool group:
  - `所有廣告`
  - `動作`
  - `刊登中的廣告`
  - `另外 1 個瀏覽畫面`

## Visible Campaign Rows

13 campaign rows are visible in the campaign table.

| Row | Campaign name visible in UI | Delivery status | Toggle state | Notes |
|---:|---|---|---|---|
| 1 | `2026 品牌知名度廣告 A組 周歲與廣泛 -高收入媽媽族群 - 複本` | `進行中` | on | UI shows `1 項建議` |
| 2 | `2026 策略一｜頂層品牌認知 週歲/家庭冷受眾 - 複本` | `進行中` | on | no recommendation badge visible |
| 3 | `2026 B組"互動"行銷活動-cta` | `進行中` | on | UI shows `1 項建議` |
| 4 | `2026 策略一｜頂層品牌認知 週歲/家庭冷受眾` | `已關閉` | off | To C / family-cold audience |
| 5 | `2026 品牌知名度廣告 A組 周歲與廣泛 -高收入媽媽族群` | `已關閉` | off | To C / family audience |
| 6 | `開發潛在客戶2026` | `已關閉` | off | lead-gen surface candidate |
| 7 | `Instagram post: #派對實拍場景 | Wedding Party | 點心Bar...` | `已關閉` | off | social / party post |
| 8 | `Instagram 貼文：#外燴紀錄 今年夏天，我們又來到麻豆區的邦尼托嬰...` | `已關閉` | off | childcare / center post |
| 9 | `Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜在...` | `已關閉` | off | ESG / corporate seed |
| 10 | `新的品牌認知行銷活動` | `已關閉` | off | generic |
| 11 | `新的開發潛在顧客行銷活動` | `已關閉` | off | generic lead-gen |
| 12 | `竹南加盟廣告A` | `已關閉` | off | franchise / location-specific |
| 13 | `新的品牌認知行銷活動` | `已關閉` | off | generic |

## B2B Relevance From Current Screen

Verified B2B / near-B2B seeds visible at campaign layer:

- `開發潛在客戶2026`
- `Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜在...`
- generic `新的開發潛在顧客行銷活動`

Visible but mostly To C / party-family oriented:

- 周歲 / 家庭冷受眾 campaigns
- Wedding Party post
- childcare / maternity-center adjacent campaign

## Missing Data

This screen is campaign-level only. It does not yet verify:

- Ad set detailed targeting / interest tags.
- Custom audience / retargeting audience availability.
- Pixel / conversion event settings.
- Ad-level destination URL.
- Creative asset mapping.
- Whether any current drafts are related to B2B case articles.

## Next Read-Only UI Packet Needed

A2 should use Computer Use to open the `廣告組合` layer for selected B2B candidate campaigns and produce the next visual bridge packet.

Priority order:

1. `開發潛在客戶2026`
2. `Instagram 貼文：#外燴紀錄 | 中華賓士-愛心慈善捐贈活動｜ESG｜在...`
3. `新的開發潛在顧客行銷活動`

Do not publish, discard, save, duplicate, edit, accept dialogs, or change toggles.
