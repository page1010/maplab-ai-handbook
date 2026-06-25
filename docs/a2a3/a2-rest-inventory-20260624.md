# A2 REST Inventory — maplabkitchen 外燴站

日期：2026-06-24  
角色：A2 SEO 內容  
狀態：file-only evidence / public GET only  
邊界：只讀 public REST + public sitemap；未登入 WordPress、未讀 secrets、未發布、未改線上、未 push、未 commit。

## Public GET Evidence

### Posts REST

- Endpoint: `https://www.maplabkitchen.com/wp-json/wp/v2/posts?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type`
- HTTP: `200`
- Header: `X-WP-Total: 58`
- Header: `X-WP-TotalPages: 1`
- Body count: `58`

### Pages REST

- Endpoint: `https://www.maplabkitchen.com/wp-json/wp/v2/pages?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type`
- HTTP: `200`
- Header: `X-WP-Total: 6`
- Header: `X-WP-TotalPages: 1`
- Body count: `6`

### Post Sitemap

- Endpoint: `https://www.maplabkitchen.com/post-sitemap.xml`
- HTTP: `200`
- Sitemap `<url>` count: `57`
- `icc-tainan-catering`: not found in `post-sitemap.xml`
- New candidate slugs not found in `post-sitemap.xml`: `campus-seminar-catering-tainan`, `nanke-tech-company-catering`, `reception-center-vip-catering-tainan`, `school-event-catering-tainan`

## Planning Conclusions

- Public REST confirms `58` published posts and `6` published pages.
- `icc-tainan-catering` is live as post `1829`, status `publish`, type `post`, link `https://www.maplabkitchen.com/icc-tainan-catering/`.
- `icc-tainan-catering` is absent from `post-sitemap.xml`; treat as sitemap/indexing registration drift, not as unpublished-page evidence.
- REST/page inventory shows no collision for proposed new slugs: `campus-seminar-catering-tainan`, `nanke-tech-company-catering`, `reception-center-vip-catering-tainan`.
- Public REST cannot see private drafts, scheduled posts, trashed posts, Rank Math metadata, GSC indexing state, or authenticated WordPress duplicate drafts. Those remain authenticated/draft checks.

## B2B Scope Rows

| ID | Date | Modified | Slug | Title |
|---:|---|---|---|---|
| 1829 | 2026-06-15T15:25:12 | 2026-06-16T20:49:21 | `icc-tainan-catering` | 大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB |
| 1205 | 2026-03-15T08:44:52 | 2026-06-02T12:26:26 | `tainan-corporate-opening-tea-catering` | 台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB |
| 1048 | 2025-11-27T21:54:55 | 2026-06-16T11:01:50 | `daxin-art-museum-opening-catering` | 大新美術館開幕外燴｜展覽開幕茶會餐點案例｜MAPLAB Kitchen |
| 945 | 2025-09-01T15:41:36 | 2026-06-15T16:00:39 | `brand-esg-catering-service` | 台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB |
| 924 | 2025-07-14T15:16:20 | 2026-06-16T11:01:36 | `corporate-tea-party-desserts` | 台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB |
| 879 | 2025-07-10T11:39:37 | 2026-06-15T21:03:12 | `press-conference-catering` | 記者會餐點推薦｜讓品牌活動更有記憶點的關鍵一刻 |
| 586 | 2025-05-21T09:20:06 | 2026-06-02T12:47:37 | `corporate-catering-tainan` | 台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB |
| 261 | 2025-03-15T10:21:10 | 2026-06-16T11:03:08 | `vip-expo-catering-business-meeting` | 展覽外燴推薦｜VIP 點心吧與商務派對接待首選服務:MAPLAB Kitchen |

## Pages Inventory

| ID | Date | Modified | Slug | Title |
|---:|---|---|---|---|
| 1674 | 2026-04-20T12:32:27 | 2026-04-20T12:32:55 | `privacy-policy` | 隱私權政策 |
| 1250 | 2026-03-16T13:53:49 | 2026-03-23T10:31:53 | `homepage-v2` | 台南外燴｜MAPLAB Kitchen CATERING SERVICE |
| 209 | 2025-03-12T15:55:37 | 2025-06-20T21:33:43 | `join-maplab-catering-partner` | 外燴加盟合作平台-加入我們 |
| 44 | 2025-02-13T11:39:04 | 2025-05-08T22:44:37 | `about-us-maplabkitchen` | About us |
| 46 | 2025-02-12T23:03:44 | 2025-05-04T15:25:51 | `%e5%b7%a5%e5%95%86%e4%bb%a3%e8%b3%bc%e6%9c%8d%e5%8b%99` | 工商代購服務 |
| 15 | 2025-02-12T21:22:45 | 2025-07-14T11:50:22 | `tainan-party-venue` | 派對流程怎麼規劃？場地、餐點、預算一次搞懂！｜MAPLAB 外燴教學文 |

## Posts Inventory

Full public posts inventory is preserved by ID/date/modified/slug/title below.

| ID | Date | Modified | Slug | Title |
|---:|---|---|---|---|
| 1829 | 2026-06-15T15:25:12 | 2026-06-16T20:49:21 | `icc-tainan-catering` | 大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB |
| 1246 | 2026-03-16T12:25:26 | 2026-06-19T16:32:26 | `tainan-catering-line-inquiry-guide` | 台南外燴 LINE 詢問指南：第一次詢問要準備哪些資訊？ |
| 1245 | 2026-03-16T12:24:33 | 2026-06-19T16:32:21 | `tainan-catering-sustainability-guide` | 台南外燴綠色餐點指南｜減碳食材、環保包裝、在地理念全方位 |
| 1244 | 2026-03-16T12:23:47 | 2026-06-15T21:02:21 | `tainan-catering-not-suitable-situations` | 台南外燴不適合哪些場合？5 個選擇外燴前必須知道的關鍵 |
| 1243 | 2026-03-16T12:22:55 | 2026-06-19T16:32:11 | `maplab-kitchen-brand-story` | MAPLAB Kitchen 品牌故事：台南外燴專業團隊，成立 2016 年 |
| 1242 | 2026-03-16T12:22:09 | 2026-06-19T16:32:09 | `tainan-catering-vs-restaurant-private-room` | 台南外燴 vs 餐廳包廂包場：哪個更適合你的活動？完整比較 |
| 1241 | 2026-03-16T12:21:22 | 2026-06-19T16:32:05 | `tainan-catering-customer-reviews` | 台南外燴客戶評價：真實 Google 五星口碑分享 |
| 1239 | 2026-03-16T12:18:43 | 2026-06-19T15:20:46 | `tainan-outdoor-party-catering-menu` | 台南戶外派對外燴菜單推薦：漢堡、串燒、甜點完整規劃 |
| 1238 | 2026-03-16T12:17:58 | 2026-06-19T15:17:58 | `tainan-catering-afternoon-tea-menu` | 台南外燴下午茶菜單推薦：企業茶會、開幕、婚禮迎賓完整指南 |
| 1237 | 2026-03-16T12:17:11 | 2026-06-19T15:17:13 | `tainan-catering-buffet-menu` | 台南外燴 Buffet 菜單推薦：6–10 道精緻輕食完整規劃 |
| 1236 | 2026-03-16T12:16:12 | 2026-06-19T15:16:24 | `tainan-catering-buffet-vs-traditional` | 台南外燴辦桌 vs Buffet 怎麼選？2026 完整比較指南 |
| 1233 | 2026-03-15T09:33:03 | 2026-06-19T15:15:42 | `tainan-catering-faq` | 台南外燴常見問題大全｜費用、預約、菜單、服務一次解答 |
| 1232 | 2026-03-15T09:32:23 | 2026-06-19T15:14:51 | `tainan-catering-service-process` | 台南外燴服務流程｜從詢價到活動結束 7 大步驟完整說明 |
| 1231 | 2026-03-15T09:31:48 | 2026-06-19T15:14:18 | `tainan-catering-vs-restaurant` | 台南外燴 vs. 餐廳包廂｜費用、彈性、服務完整比較指南 |
| 1230 | 2026-03-15T09:31:08 | 2026-06-19T15:13:28 | `tainan-catering-menu-guide` | 台南外燴菜單推薦｜歐式 Buffet、台味小點、立食茶點完整比較 |
| 1229 | 2026-03-15T09:30:29 | 2026-06-19T15:12:26 | `tainan-catering-venue-guide` | 台南外燴場地推薦｜草坪、古蹟、文創空間場地導覽 |
| 1227 | 2026-03-15T09:26:14 | 2026-06-16T21:46:48 | `tainan-picnic-catering` | 台南野餐外燴｜公園、海邊、草坪戶外美食饗宴規劃 |
| 1226 | 2026-03-15T09:25:35 | 2026-06-16T21:46:46 | `tainan-family-gathering-catering` | 台南家庭聚會外燴｜年節家族聚餐、親子派對完整規劃 |
| 1224 | 2026-03-15T09:24:31 | 2026-06-16T21:46:44 | `tainan-birthday-party-catering` | 台南生日派對外燴｜從兒童派對到成人壽宴一手包辦 |
| 1222 | 2026-03-15T09:23:35 | 2026-06-16T21:46:42 | `tainan-full-moon-baby-catering` | 台南滿月酒外燴｜傳統油飯到現代精緻菜色一站規劃 |
| 1220 | 2026-03-15T09:22:35 | 2026-06-19T15:13:22 | `tainan-wedding-celebration-party-catering` | 台南證婚派對外燴｜打造親密歡樂的現代婚禮慶典 |
| 1218 | 2026-03-15T08:55:31 | 2026-06-19T15:13:19 | `tainan-wedding-catering-cost` | 台南婚宴外燴費用完整指南｜各規模婚禮預算怎麼抓 |
| 1217 | 2026-03-15T08:54:50 | 2026-06-19T15:13:16 | `tainan-wedding-welcome-canapes` | 台南婚禮迎賓茶點外燴｜讓賓客第一口就驚艷的茶點規劃 |
| 1215 | 2026-03-15T08:53:47 | 2026-06-19T15:13:13 | `tainan-outdoor-wedding-catering` | 台南戶外婚禮外燴｜草坪、古蹟、海邊場地外燴規劃 |
| 1213 | 2026-03-15T08:52:42 | 2026-06-19T15:11:42 | `tainan-small-wedding-catering` | 台南小型婚禮外燴推薦｜50 人以下草坪婚禮、居家婚宴 |
| 1211 | 2026-03-15T08:51:35 | 2026-06-16T21:21:34 | `tainan-corporate-catering-cost` | 台南企業外燴費用｜尾牙、茶會、開幕活動預算怎麼抓 |
| 1209 | 2026-03-15T08:47:25 | 2026-06-16T21:19:10 | `tainan-launch-event-catering` | 台南發表會外燴｜新品上市、記者會、VIP 晚宴外燴規劃 |
| 1207 | 2026-03-15T08:46:17 | 2026-06-16T21:17:47 | `tainan-anniversary-catering` | 台南週年慶外燴｜員工感謝日、品牌週年慶餐飲方案 |
| 1205 | 2026-03-15T08:44:52 | 2026-06-02T12:26:26 | `tainan-corporate-opening-tea-catering` | 台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB |
| 1201 | 2026-03-15T08:27:00 | 2026-06-16T21:36:23 | `tainan-corporate-gathering-catering` | 台南公司聚餐外燴｜20～100 人場地外燴規劃指南 |
| 1199 | 2026-03-14T22:44:29 | 2026-06-16T21:36:20 | `tainan-year-end-party-catering-2026` | 台南尾牙外燴推薦 2026｜企業尾牙餐點規劃、費用說明完整指南 |
| 1168 | 2026-03-12T10:26:07 | 2026-06-19T16:34:39 | `tainan-catering-cost-guide` | 台南外燴費用怎麼算？2026 完整價格說明與預算指南 |
| 1093 | 2026-01-02T11:56:21 | 2026-06-16T11:01:42 | `tainan-catering-venue-selection-2026` | 2026 台南外燴場地挑選指南：5 個問題，讓活動更從容 |
| 1084 | 2025-12-01T16:03:36 | 2026-06-16T11:01:40 | `corporate-tea-party-catering-tips` | 台南企業茶會外燴｜6 個容易被忽略的細節：動線・留白・視覺 |
| 1048 | 2025-11-27T21:54:55 | 2026-06-16T11:01:50 | `daxin-art-museum-opening-catering` | 大新美術館開幕外燴｜展覽開幕茶會餐點案例｜MAPLAB Kitchen |
| 1027 | 2025-11-18T10:02:26 | 2026-06-15T21:03:11 | `policy-cancellation` | 【MAP LAB 外燴｜定金、取消與服務條款】 |
| 994 | 2025-11-12T13:11:38 | 2026-03-27T21:04:48 | `tainan-beef-soup-story-kinguang` | ｜MAPLAB 日常誌｜台南｜金廣牛肉湯｜金廣海產 |
| 945 | 2025-09-01T15:41:36 | 2026-06-15T16:00:39 | `brand-esg-catering-service` | 台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB |
| 924 | 2025-07-14T15:16:20 | 2026-06-16T11:01:36 | `corporate-tea-party-desserts` | 台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB |
| 879 | 2025-07-10T11:39:37 | 2026-06-15T21:03:12 | `press-conference-catering` | 記者會餐點推薦｜讓品牌活動更有記憶點的關鍵一刻 |
| 698 | 2025-06-20T23:38:21 | 2026-06-15T21:03:14 | `tainan-custom-catering-menu` | 台南外燴菜單推薦｜20道客製化餐點設計靈感｜MAPLAB Kitchen |
| 683 | 2025-06-20T21:30:44 | 2026-06-15T21:03:16 | `tainan-catering-guide` | 台南外燴全攻略｜台南到府外燴、台南派對外燴與活動餐點｜MAPLAB |
| 586 | 2025-05-21T09:20:06 | 2026-06-02T12:47:37 | `corporate-catering-tainan` | 台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB |
| 564 | 2025-05-12T12:30:32 | 2026-06-16T11:01:32 | `tainan-opening-houseparty-catering` | 想讓你的開幕或入厝活動「有面子又不累」？ |
| 541 | 2025-05-11T13:13:30 | 2026-06-15T21:03:20 | `florist-partners-tainan` | 【台南花藝推薦】MAPLAB 精選 5 位花藝品牌，一場派對的靈魂來自細節 |
| 498 | 2025-05-07T17:07:24 | 2026-06-16T11:01:45 | `catering-one-year-old-party-tainan` | 【2026 最新】台南週歲派對外燴懶人包｜菜單、場地、價格一次搞懂！ |
| 450 | 2025-05-05T17:09:29 | 2026-06-15T21:03:22 | `tai-nan-wai-hui-chang-di-tui-jian-2023` | 台南外燴場地推薦｜MAPLAB 精選 7 間派對場地 |
| 403 | 2025-05-04T16:05:23 | 2026-06-15T21:03:24 | `tainan-picnicbox-partybox-recommend` | 台南野餐餐盒推薦：必備外帶輕食組合 |
| 345 | 2025-03-15T15:06:10 | 2026-06-15T21:03:25 | `business-opening-party-ideas` | 企業開幕派對：從傳統儀式到現代慶典 |
| 332 | 2025-03-15T14:38:22 | 2026-05-11T20:59:39 | `gender-reveal-party-tips` | 性別揭曉派對外燴｜Gender Reveal 餐點與甜點桌規劃｜MAPLAB |
| 322 | 2025-03-15T14:04:19 | 2026-06-15T21:03:27 | `first-birthday-party-zhuazhou-tainan` | 抓周 & 週歲派對：讓寶寶的成長時刻更難忘 |
| 319 | 2025-03-15T13:32:37 | 2026-06-15T21:03:29 | `outdoor-catering-camping-picnic` | 露營 & 野餐外燴怎麼選？一步一步打造完美戶外饗宴 |
| 272 | 2025-03-15T11:12:03 | 2026-06-15T21:03:31 | `%e7%af%80%e6%85%b6%e6%b4%be%e5%b0%8d%e5%a4%96%e7%87%b4%e6%80%8e%e9%ba%bc%e9%81%b8%ef%bc%9f5-%e5%a4%a7%e9%97%9c%e9%8d%b5%e6%89%93%e9%80%a0%e5%ae%8c%e7%be%8e%e6%b0%9b%e5%9c%8d` | 節慶派對外燴怎麼選？5 大關鍵打造完美氛圍 |
| 261 | 2025-03-15T10:21:10 | 2026-06-16T11:03:08 | `vip-expo-catering-business-meeting` | 展覽外燴推薦｜VIP 點心吧與商務派對接待首選服務:MAPLAB Kitchen |
| 253 | 2025-03-15T09:09:13 | 2026-06-15T21:03:32 | `%e6%88%b6%e5%a4%96-bbq-%e5%a4%96%e7%87%b4%e6%80%8e%e9%ba%bc%e9%81%b8%ef%bc%9f5-%e5%80%8b%e8%ae%93%e6%b4%be%e5%b0%8d%e6%9b%b4%e5%ae%8c%e7%be%8e%e7%9a%84%e9%97%9c%e9%8d%b5` | 戶外 BBQ 外燴怎麼選？使你的烤肉派對更完美的關鍵 |
| 247 | 2025-03-14T16:51:18 | 2026-06-16T11:03:10 | `elder-birthday-catering-tainan` | 長輩壽宴外燴：讓家人團聚，溫馨慶祝的5個原因 |
| 238 | 2025-03-14T16:18:28 | 2026-06-15T21:03:37 | `wedding-catering-vs-banquet-tainan` | 婚宴外燴 vs. 傳統桌菜：哪個更適合你的夢幻婚禮？ |
| 219 | 2025-03-12T17:39:24 | 2026-06-15T21:03:38 | `office-catering-planning-tips` | 辦公室外燴怎麼選？5 大必知規劃技巧 |
