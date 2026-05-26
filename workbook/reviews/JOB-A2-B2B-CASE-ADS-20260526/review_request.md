# JOB-A2-B2B-CASE-ADS-20260526 Review Request

日期：2026-05-26
角色：A2 搜尋流量作戰部
任務：Owner 提供案例照片後，對照 live WordPress 架構，安排案例文章補強、Google Ads landing page、Meta 分眾廣告與圖片 SEO 基本功。

## Scope Guard

- 不發布 WordPress 內容。
- 不新增或修改 Rank Math 付費功能設定；Owner 已退訂，既有設定先凍結。
- Owner 這批貼出的照片視為可進公開案例流程，不再分 `public/internal/private`。
- 這批先補現有 live 文章的真案例與素材，不先開新的泛用主頁。
- Google Ads / Meta Ads 先做 access check、final URL matrix、關鍵字與受眾規劃，不直接開跑或改預算。

## Live URL Verification

2026-05-26 前台 HTTP 快速驗證：

| 用途 | Live URL | 狀態 |
|---|---|---:|
| 企業外燴主入口 | `https://www.maplabkitchen.com/corporate-catering-tainan/` | 200 |
| 會議茶點 / 研討會 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | 200 |
| 開幕茶會 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | 200 |
| 品牌活動 / VIP / 展覽開幕 | `https://www.maplabkitchen.com/brand-esg-catering-service/` | 200 |
| 記者會 / 發表會 | `https://www.maplabkitchen.com/press-conference-catering/` | 200 |
| 展覽 VIP 接待 | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | 200 |
| 文化場館案例 | `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` | 200 |

不要用的舊 slug：`catering-corporate-tainan`, `meeting-refreshment-catering-tainan`, `opening-event-catering-tainan`, `brand-event-catering`, `school-event-catering-tainan`，本次驗證皆為 404。

## Current Site Diagnosis

網站內容已經在往 To B 經營：企業外燴、會議茶點、開幕茶會、品牌活動、記者會、展覽 VIP 接待、文化場館案例都已有 live 承接頁。問題不是沒有 B2B 方向，而是案例證據還不夠集中，廣告也需要把每個搜尋意圖導到更精準的 existing article landing page。

本批照片的任務是把「我們做過」補成可被搜尋與廣告讀懂的結構：

- 每個頁面補 2-5 個真案例段落。
- 每個案例有場景、用途、照片插槽、CTA。
- 每張圖轉 WebP、設定 SEO 檔名、alt、caption、slot 描述。
- Google Ads 用搜尋意圖分流到現有文章。
- Meta 用興趣/行為分眾導到最接近的案例頁。

## Case Placement Plan

| Live landing page | 要補的案例 | 文章角色 | Google Ads 意圖 | Meta 分眾 |
|---|---|---|---|---|
| `corporate-catering-tainan` | 國泰建設財富管理論壇、產後護理之家聖誕餐會、企業/機構型活動總覽 | 企業主入口，承接「公司需要外燴」的總需求 | 台南企業外燴、公司茶會、企業餐點、員工活動餐點 | 企業主、行政總務、人資、品牌/活動窗口 |
| `corporate-tea-party-desserts` | 成大會議茶點、成大實驗室揭牌、長榮大學 EMBA 音樂會 | 會議、研討會、校園活動、講座茶點 | 會議茶點、研討會茶點、台南會議外燴、大學活動茶點 | 大學/教育、醫學中心、講座、EMBA、行政窗口 |
| `tainan-corporate-opening-tea-catering` | AMD 辦公室開幕、東京威力科創廠區開幕、興達海洋公司開幕、美學中心開幕、家居與設計開幕 | 開幕茶會主承接頁 | 開幕茶會、公司開幕外燴、辦公室開幕茶點、品牌開幕餐點 | 創業、公司開幕、室內設計、商空設計、品牌經營 |
| `brand-esg-catering-service` | 賓士集團捐車、國泰建設論壇、國立台灣史前博物館西拉雅特展、台南美術館湯德章圓環美食、微商大會 | 品牌活動 / ESG / 展覽活動的形象頁 | 品牌活動外燴、企業活動茶點、VIP 茶會、展覽開幕外燴 | 品牌行銷、公關、CSR/ESG、展覽、藝文活動 |
| `press-conference-catering` | 賓士集團捐車、微商大會、可對外曝光的發表/媒體活動 | 新聞性、發布會、活動曝光頁 | 記者會茶點、發表會外燴、產品發表會餐點 | PR、公關公司、活動企劃、媒體發布 |
| `vip-expo-catering-business-meeting` | 上曜建設 VIP 迎賓、泰嘉建設 VIP 說明會、松丹達麗 VIP 茶會、宏福悅 VIP 接待會 | 建案、展覽、VIP 接待與商務洽談 | VIP 接待茶點、建案說明會茶點、展覽外燴、商務茶會 | 房地產、豪宅、室內設計、財富管理、展覽 |
| `daxin-art-museum-opening-catering` | 大新美術館開幕茶會、宮崎御所美術館開幕、台南美術館湯德章圓環、國立台灣史前博物館特展 | 文化場館與藝術展開幕案例頁 | 美術館開幕茶會、展覽茶會、藝文活動外燴 | 美術館、藝文展覽、策展、文化活動 |

## Photo Asset Matrix

| 原始檔 | 第一落點 | 圖片角色 | 建議 SEO 檔名 |
|---|---|---|---|
| `國泰建設財富管理論壇.png` | `corporate-catering-tainan`, `brand-esg-catering-service` | Hero / case proof | `maplab-corporate-forum-cathay-wealth-management-hero.webp` |
| `成大會議茶點.PNG` | `corporate-tea-party-desserts` | Hero / meeting case | `maplab-meeting-refreshment-ncku-library-hero.webp` |
| `成大實驗室揭牌典禮.JPG` | `corporate-tea-party-desserts`, `tainan-corporate-opening-tea-catering` | University opening case | `maplab-university-lab-opening-ncku-case.webp` |
| `長榮大學emba音樂會.JPG` | `corporate-tea-party-desserts` | School / EMBA case | `maplab-university-emba-concert-tea-break.webp` |
| `amd辦公室開幕茶會.JPG` | `tainan-corporate-opening-tea-catering` | Office opening hero | `maplab-office-opening-amd-tea-party-hero.webp` |
| `東京威力科創廠區開幕.HEIC` | `tainan-corporate-opening-tea-catering` | Tech factory opening | `maplab-tech-factory-opening-tea-party-hero.webp` |
| `興達海洋公司開幕茶會.JPG` | `tainan-corporate-opening-tea-catering` | Company opening case | `maplab-company-opening-ocean-industry-tea-party.webp` |
| `家居與設計開幕茶會.PNG` | `tainan-corporate-opening-tea-catering` | Interior/design opening | `maplab-interior-design-opening-tea-party.webp` |
| `美學中心開幕茶會.jpg` | `tainan-corporate-opening-tea-catering` | Opening case | `maplab-aesthetic-center-opening-tea-party.webp` |
| `賓士集團捐車送愛心活動.PNG` | `brand-esg-catering-service`, `press-conference-catering` | ESG / press case | `maplab-brand-esg-benz-donation-event.webp` |
| `美麗代言人微商大會再創巔峰.PNG` | `brand-esg-catering-service`, `press-conference-catering` | Brand conference case | `maplab-brand-conference-catering-beauty-summit.webp` |
| `上曜建設vip迎賓.PNG` | `vip-expo-catering-business-meeting`, `brand-esg-catering-service` | Real estate VIP hero | `maplab-real-estate-vip-reception-shangyao.webp` |
| `泰嘉建設vip說明會.PNG` | `vip-expo-catering-business-meeting` | Real estate briefing case | `maplab-real-estate-vip-briefing-taijia.webp` |
| `松丹達麗vip茶會.PNG` | `vip-expo-catering-business-meeting` | Real estate VIP case | `maplab-real-estate-vip-tea-songdan.webp` |
| `宏福悅vip接待會.HEIC` | `vip-expo-catering-business-meeting` | Real estate reception case | `maplab-real-estate-vip-reception-hongfuyue.webp` |
| `大新美術館開幕茶會.JPG` | `daxin-art-museum-opening-catering` | Cultural venue hero | `maplab-art-museum-opening-daxin-hero.webp` |
| `宮崎御所美術館開幕` | `daxin-art-museum-opening-catering` | Cultural venue case | `maplab-art-museum-opening-miyazaki-case.webp` |
| `國立台灣史前博物館西拉雅特展.HEIC` | `daxin-art-museum-opening-catering`, `brand-esg-catering-service` | Museum exhibition case | `maplab-museum-exhibition-siraya-opening-catering.webp` |
| `台南美術館湯德章圓環美食.HEIC` | `daxin-art-museum-opening-catering`, `brand-esg-catering-service` | Cultural outdoor case | `maplab-tainan-art-museum-tangdezhang-food-event.webp` |
| `湯德章圓環台南美食.JPG` | `daxin-art-museum-opening-catering` | Supporting angle | `maplab-tangdezhang-circle-tainan-food-event.webp` |
| `湯德章圓環特展台南美食專場.JPG` | `daxin-art-museum-opening-catering` | Supporting angle | `maplab-tangdezhang-exhibition-food-event.webp` |
| `誠品酒窖品酒會開幕.jpeg` | `brand-esg-catering-service` | Reference only for first batch ads | `maplab-opening-wine-cellar-catering-reference.webp` |
| `匹克球以球會友餐會.JPG` | second batch / social case | Community event | `maplab-community-sports-pickleball-catering.webp` |
| `產後護理之家聖誕餐會.JPG` | `corporate-catering-tainan` | Institutional holiday case | `maplab-institution-christmas-catering-nursing-center.webp` |
| `老錢風生日派對.HEIC` | second batch / party article | High-end private party | `maplab-old-money-birthday-party-catering.webp` |
| `純白主題風生日派對.jpg` | second batch / party article | Birthday party hero | `maplab-white-theme-birthday-party-catering.webp` |
| `豪宅公設自辦派對.HEIC` | second batch / party or VIP support | Luxury residence party | `maplab-luxury-residence-private-party-catering.webp` |
| `豪宅公設自辦派對例2.JPG` | second batch / party or VIP support | Luxury residence detail | `maplab-luxury-residence-party-dessert-table.webp` |
| `新居落成海鮮派對.JPG` | second batch / private party | Food detail / premium menu | `maplab-housewarming-seafood-party-catering.webp` |
| `戶外婚禮證婚場地.jpg` | second batch / wedding article | Wedding venue visual | `maplab-outdoor-wedding-ceremony-catering.webp` |

`誠品酒窖品酒會開幕.jpeg` 第一輪不建議當廣告素材主圖，因為酒類畫面容易讓平台審核與投放限制變複雜；可先留作網站案例參考或內文輔助圖。

## Google Ads Landing Page Matrix

先讓 Antigravity 驗證目前 Google Ads 帳戶與 keyword/search theme 頁面是否可進入，再做變更提案。

| Ad group / intent | Keyword draft | Final URL |
|---|---|---|
| 企業外燴主需求 | `台南企業外燴`, `公司外燴`, `企業茶會`, `台南公司茶會`, `台南外燴推薦` | `https://www.maplabkitchen.com/corporate-catering-tainan/` |
| 會議茶點 / 研討會 | `會議茶點`, `台南會議茶點`, `研討會茶點`, `講座茶點`, `大學活動茶點` | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` |
| 開幕茶會 | `開幕茶會`, `公司開幕外燴`, `辦公室開幕茶點`, `開幕點心`, `台南開幕茶會` | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` |
| 品牌活動 / VIP | `品牌活動外燴`, `企業活動茶點`, `VIP 接待茶點`, `展覽開幕茶會`, `高端外燴` | `https://www.maplabkitchen.com/brand-esg-catering-service/` |
| 建案 / 展覽 VIP | `建案說明會茶點`, `VIP 說明會外燴`, `展覽接待茶點`, `商務茶會` | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` |
| 記者會 / 發表會 | `記者會茶點`, `發表會外燴`, `產品發表會茶點`, `媒體活動茶點` | `https://www.maplabkitchen.com/press-conference-catering/` |
| 美術館 / 展覽開幕 | `美術館開幕茶會`, `展覽茶會`, `藝文活動外燴`, `文化活動茶點` | `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` |

Google Ads UTM 草案：

`?utm_source=google&utm_medium=cpc&utm_campaign=b2b_case_{cluster}&utm_content={adgroup}`

UTM 只加在廣告 final URL，不改 WordPress slug。

## Meta Ads Interest Segments

Meta 的 detailed targeting 可用項目會變動，所以 Antigravity / A3 要進 Ads Manager 實際確認可選 interest。若 interest 不可選，改用 Advantage+ audience suggestion + website retargeting。

| Ad set | 內容角度 | 素材優先 | Landing page |
|---|---|---|---|
| Real Estate VIP | 建案說明會、豪宅公設、VIP 迎賓、預售屋接待 | 上曜、泰嘉、松丹達麗、宏福悅、國泰 | `vip-expo-catering-business-meeting`, `brand-esg-catering-service` |
| Brand / PR / Event | 品牌活動、ESG、記者會、發表會、展覽開幕 | 賓士、微商大會、國泰、台南美術館 | `brand-esg-catering-service`, `press-conference-catering` |
| Opening Tea Party | 新辦公室、新店、新場館、開幕茶會 | AMD、東京威力、興達海洋、美學中心、家居與設計 | `tainan-corporate-opening-tea-catering` |
| Seminar / Institution | 會議茶點、講座、研討會、EMBA、校園活動 | 成大、成大實驗室、長榮 EMBA | `corporate-tea-party-desserts` |
| Premium Private Party | 豪宅派對、生日、婚禮、新居落成 | 老錢風、純白生日、豪宅公設、新居海鮮、戶外婚禮 | second batch landing pages after B2B case pass |

Meta UTM 草案：

`?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_{segment}&utm_content={creative_slug}`

## Image SEO And Slot Rules

| Slot | Size target | Crop | Use |
|---|---:|---|---|
| `hero_16x9` | 1600 x 900 WebP, under 350 KB | 以餐桌/場景為主，避免裁掉活動識別 | WordPress article hero / OG fallback |
| `case_4x3` | 1200 x 900 WebP, under 280 KB | 保留場地與餐桌關係 | 文章案例段 |
| `detail_1x1` | 1080 x 1080 WebP, under 220 KB | 食物細節，不放太多文字 overlay | 內文、社群輪播 |
| `meta_4x5` | 1080 x 1350 WebP/JPG | 主體置中，上下保留 8-12% 安全邊 | Meta feed |
| `story_9x16` | 1080 x 1920 JPG/WebP | 保留上方文字安全區 | Reels/Story |

每張圖需有：

- SEO filename：`maplab-{scene}-{case}-{slot}.webp`
- Alt text：用中文描述「品牌 + 地點/場景 + 用途」，例如 `MAPLAB 台南會議茶點，成功大學圖書館總館研討會點心桌`
- Caption：寫案例情境，不寫空泛形容詞
- Description：包含主關鍵字 + 案例名 + 場景用途
- Internal link target：只連到同 cluster 的 live URL

## Antigravity Access Check Prompt

2026-05-26 A2 已先做一次只讀 Chrome access check，結果見 `access_check.md`：WordPress `post=586` 編輯頁可進入，Google Ads account `844-336-3178` 的 `搜尋關鍵字` 頁可進入。Antigravity 下一步不是重做結論，而是把檢查擴到 7 個 live post、Google Ads campaign/ad group/final URL matrix、Meta Ads ad set 層級。

請透過 Chrome Extension 召喚高能力 Google 生態執行助手 Antigravity，使用以下交辦。A2 保持管理方，Antigravity 只做 access check 與回報，不做任何發布、預算、關鍵字、final URL 或 WordPress 儲存動作。

```text
我是 Antigravity，運行在 Chrome / Google ecosystem assistant，任務是替 A2 驗證 MAPLAB B2B case ads workflow 的 WordPress 與 Google Ads 可操作頁面。

先讀：
1. CURRENT_STATUS.md
2. pitfalls.md
3. docs/a2a3/live-wordpress-audit.md
4. docs/a2a3/b2b-case-inventory.md
5. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md
6. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/access_check.md

限制：
- 不發布 WordPress。
- 不按 Update / Publish / Save / Apply。
- 不修改 Google Ads 預算、關鍵字、search themes、final URL、conversion goal。
- Rank Math 已退訂，既有設定凍結，不做 Focus Keyword / schema / paid UI 調整。

要驗證：
1. WordPress：是否能進入下列 live post 的編輯頁或至少前台頁面，記錄 post title、slug、是否可看到媒體插入或文章內容區。
   - corporate-catering-tainan
   - corporate-tea-party-desserts
   - tainan-corporate-opening-tea-catering
   - brand-esg-catering-service
   - press-conference-catering
   - vip-expo-catering-business-meeting
   - daxin-art-museum-opening-catering

2. Google Ads：是否能進入 campaign / ad group / keyword 或 PMax search themes / final URL 設定頁。
   - 記錄目前 campaign 名稱。
   - 記錄是否存在 Search campaigns、PMax asset groups、keywords、search themes、final URL 或 URL expansion 設定。
   - 記錄目前 conversion action 名稱與主要/次要狀態，只讀不改。

3. Meta Ads：是否能進入 Ads Manager 的 campaign/ad set 層級，確認 detailed targeting 或 Advantage+ audience suggestion 是否可用。
   - 只記錄目前可選介面，不新增廣告。

輸出：
- access_check.md：每個系統是否進得去、停在哪一頁、截圖或可視證據描述。
- google_ads_landing_matrix.md：目前 campaign/ad group/search theme/final URL 對照，標示可改與不可改的地方。
- wordpress_target_check.md：7 個 live URL 的 title、slug、是否可編輯、建議插入案例段位置。
- blockers.md：若不能登入或看不到頁面，寫明試過什麼、卡在哪裡、Owner 5 分鐘內要做什麼。
```

## A2 Next Work

1. 先用這份 matrix 寫第一批 4 個 B2B cluster 的案例段草稿。
2. Antigravity 回報 access check 後，再決定是否進 WordPress 草稿或只做本機 preview。
3. A3/Meta 只在 landing page 與追蹤確認後規劃受眾，不直接上廣告。
4. A4 或素材管線負責 WebP 轉檔、裁切、alt/caption/description manifest。
5. Owner review 後才允許任何 WordPress 發布或 Ads 設定變更。
