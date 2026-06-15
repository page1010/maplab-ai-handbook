# A3 Ads Strategy Plan

Date: 2026-06-15
Status: approval_ready

## Strategy Summary

Use Google Search Ads for venue-intent capture and Meta for memory, visual proof, and retargeting. Do not spend heavily on broad `台南外燴` terms until the venue page has proof and conversion readback.

## Google Ads Plan

No Google Ads settings were changed. This is an approval-ready structure.

### Campaign / Ad Group Option

Preferred implementation after approval:

- Create a small dedicated Search campaign or tightly separated ad group: `Search_ICC_Tainan_大臺南會展中心`
- Daily test cap: NT$100-200
- Match type: exact and phrase only for first 14 days
- Landing page: `https://www.maplabkitchen.com/icc-tainan-catering/` after draft publish approval
- Interim landing if page is not published: do not launch venue-specific ads yet

### P1 Venue Keywords

Use exact match first:

```text
[大臺南會展中心外燴]
[大台南會展中心外燴]
[大臺南會展中心茶點]
[大台南會展中心茶點]
[大臺南會展中心活動餐點]
[大台南會展中心活動餐點]
[大臺南會展中心展覽茶點]
[大台南會展中心展覽茶點]
[大臺南會展中心會議茶點]
[大台南會展中心會議茶點]
[大臺南會展中心貴賓接待]
[大台南會展中心貴賓接待]
[大臺南會展中心開幕茶會]
[大台南會展中心開幕茶會]
```

Use phrase match only for English / mixed-language variants:

```text
"ICC Tainan catering"
"ICC Tainan 外燴"
"ICC Tainan 茶點"
"Tainan convention center catering"
```

### P2 Event Scenario Keywords

Use only after page is published or route to existing live pages:

```text
"台南展覽茶點"
"台南展覽外燴"
"台南企業茶會"
"台南開幕茶會"
"台南品牌發表會外燴"
"台南記者會茶點"
"台南招商說明會茶點"
"台南貴賓接待茶點"
"台南研討會茶點"
```

Landing split:

- Meeting / seminar: `corporate-tea-party-desserts`
- Opening: `tainan-corporate-opening-tea-catering`
- Expo / VIP: `vip-expo-catering-business-meeting`
- Corporate umbrella: `corporate-catering-tainan`
- Venue-specific: `icc-tainan-catering` after publish

### P3 Style / High-Value Keywords

Small test only:

```text
"台南西式外燴"
"台南精緻外燴"
"台南精緻茶點"
"台南活動茶點佈置"
"台南外燴擺設"
"台南甜點外燴"
"台南 Finger Food"
"台南 Canapé"
"台南品牌活動外燴"
```

### Negative Keyword Plan

Hard negatives from day 1:

```text
便當
會議便當
團體便當
便當外送
團膳
團購
便宜
低價
最便宜
50元
100元
吃到飽
自助餐吃到飽
餐盒
便當店
徵才
工作
職缺
停車
交通
地址
門票
展覽門票
活動資訊
攤位租借
場地租借
```

Watch-list negatives, add only if search terms prove low fit:

```text
自助餐
buffet
午餐
晚餐
喜宴
辦桌
流水席
總鋪師
學校營養午餐
餐廳
美食節
伴手禮
```

Rationale:

- `便當 / 團膳 / 便宜` terms pull MAPLAB into the wrong market.
- `停車 / 交通 / 地址 / 門票 / 場租` terms are venue-service intent, not catering intent.
- `自助餐 / buffet` can overlap with MAPLAB service, so keep them as watch-list terms instead of immediate broad negatives.

### Example Search Ad Copy

Headlines:

```text
大臺南會展中心活動外燴
台南企業茶點與會議餐點
展覽接待與貴賓點心吧
高鐵台南站旁活動餐點
MAPLAB Kitchen 台南外燴
```

Descriptions:

```text
會議、展覽、開幕與品牌接待適用。依活動流程規劃茶點、飲品與桌面配置，協助主辦單位穩定接待來賓。
```

```text
大臺南會展中心活動餐點規劃。手指食物、甜點飲品、貴賓接待與企業茶會配置，歡迎先用 LINE 說明日期與人數。
```

## Meta Ads Plan

Meta should not try to capture keyword demand. It should create memory and retarget warm audiences.

### Creative Direction

Use the Drive case after visual QA:

- Tea table overview.
- Finger-food details.
- Beverage station.
- Venue-context / meeting-break rhythm.
- Short reel cut from MP4/MOV only if no private meeting content is visible.

### Audience Direction

Do not modify current running engagement campaigns without approval.

Option A: retargeting only

- Website visitors to B2B pages.
- IG/FB engagers.
- Video viewers from venue case creative.
- Destination: venue page after publish.

Option B: new landing-page traffic ad set

- Geo: Tainan + nearby business corridor; consider broader Taiwan only for high-intent event organizers.
- Age: 28-60.
- Interests/behaviors to test: event planning, public relations, marketing manager, project management, business decision maker, exhibition, seminar, high-speed rail/business travel.
- Use existing verified A corporate decision-maker seed only if Owner approves.
- B PR seed remains `Needs UI Detail`; do not launch based on unverified assumptions.

### Meta Copy Draft

```text
大臺南會展中心的企業會議茶點，重點在於讓來賓能自然停留、取用與交流。

MAPLAB Kitchen 依活動流程安排手指食物、甜點飲品與桌面陳列，適合會議、展覽、開幕與品牌接待。
```

CTA:

- `了解更多`
- Landing: `https://www.maplabkitchen.com/icc-tainan-catering/?utm_source=meta&utm_medium=paid_social&utm_campaign=2026_icc_tainan_catering&utm_content={creative_id}`

## Tracking / Validation

Before launch:

- Published landing page returns 200.
- UTM URLs load correctly.
- LINE CTA visible and clickable.
- GA4/GTM/Meta Pixel read-only check confirms pageview and click tracking if available.
- Google Ads final URL is page-specific, not campaign-level blank.

After 14 days:

- Search terms reviewed.
- Negative keywords updated.
- CTR and LINE clicks reviewed.
- No budget increase unless search terms match enterprise/event intent.
