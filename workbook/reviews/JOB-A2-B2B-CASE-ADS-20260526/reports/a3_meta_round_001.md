# A3 Meta Ads ROUND-001 Report

日期：2026-05-26
角色：A3 Meta Ads 分眾支援 worker
來源：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md`

## Scope

- 本輪只做 Meta Ads 分眾、素材、landing page、UTM 規劃回報。
- 未進 Meta Ads Manager；所有 detailed targeting 名稱皆需 UI 驗證。
- 不修改 WordPress / Google Ads / Meta Ads。
- 不發布、不開 campaign、不改預算、不改 final URL。

## Ad Set Plan

| Ad set | Priority | Audience hypothesis | Creative angle | Priority photos | Final URL | UTM draft |
|---|---:|---|---|---|---|---|
| Real Estate VIP Reception | P1 | 建商、代銷、豪宅案場、VIP 接待與預售屋說明會窗口，需要「有質感、不打擾銷售流程」的茶點接待。 | 建案 VIP 說明會、豪宅迎賓、賞屋中心茶會。重點不是餐點多，而是提升接待質感與客戶停留。 | `上曜建設vip迎賓.PNG`, `泰嘉建設vip說明會.PNG`, `松丹達麗vip茶會.PNG`, `宏福悅vip接待會.HEIC`, `國泰建設財富管理論壇.png` | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_real_estate_vip&utm_content={creative_slug}` |
| Brand PR ESG Event | P1 | 品牌行銷、公關、CSR/ESG、企業活動窗口，需要可上鏡、可對外曝光、能承接媒體/貴賓的活動餐點。 | 品牌活動與 ESG 場景，強調「活動畫面完整、餐點可成為品牌接待的一部分」。 | `賓士集團捐車送愛心活動.PNG`, `美麗代言人微商大會再創巔峰.PNG`, `國泰建設財富管理論壇.png`, `國立台灣史前博物館西拉雅特展.HEIC`, `台南美術館湯德章圓環美食.HEIC` | `https://www.maplabkitchen.com/brand-esg-catering-service/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_brand_pr_esg&utm_content={creative_slug}` |
| Opening Tea Party | P1 | 新辦公室、新店面、新廠區、品牌空間、商空設計相關業主，正在準備開幕或揭牌活動。 | 開幕茶會不是單純擺點心，而是讓空間、花藝、餐點、來賓動線一起被拍得好看。 | `amd辦公室開幕茶會.JPG`, `東京威力科創廠區開幕.HEIC`, `興達海洋公司開幕茶會.JPG`, `美學中心開幕茶會.jpg`, `家居與設計開幕茶會.PNG`, `成大實驗室揭牌典禮.JPG` | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_opening_tea_party&utm_content={creative_slug}` |
| Seminar Institution Tea Break | P2 | 大學、EMBA、醫療/教育機構、研討會與講座承辦窗口，需要準時、乾淨、好分食、適合會議中場的茶點。 | 會議茶點、研討會 coffee break、校園活動點心桌。重點是可靠交付與會議節奏。 | `成大會議茶點.PNG`, `成大實驗室揭牌典禮.JPG`, `長榮大學emba音樂會.JPG`, `產後護理之家聖誕餐會.JPG` | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_seminar_institution&utm_content={creative_slug}` |
| Cultural Exhibition Opening | P2 | 美術館、策展單位、文化場館、藝文活動窗口，需要餐點與展場氣質一致，且適合開幕、特展、VIP 場。 | 藝文展覽與文化場館開幕案例，強調餐點不是背景，而是展場接待體驗的一部分。 | `大新美術館開幕茶會.JPG`, `宮崎御所美術館開幕`, `國立台灣史前博物館西拉雅特展.HEIC`, `台南美術館湯德章圓環美食.HEIC`, `湯德章圓環特展台南美食專場.JPG` | `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=b2b_case_cultural_exhibition&utm_content={creative_slug}` |

## Detailed Targeting UI Check

以下項目不可先當成 Meta Ads Manager 一定可選，需 Antigravity / A3 進 UI 驗證。

| Ad set | Candidate detailed targeting | Status | If unavailable |
|---|---|---|---|
| Real Estate VIP Reception | 房地產、豪宅、室內設計、建築設計、投資理財、財富管理、預售屋、房仲、建設公司相關興趣 | Needs UI Check | 改用 Advantage+ audience suggestion：房地產、室內設計、豪宅、財富管理語意；另切網站訪客 retargeting。 |
| Brand PR ESG Event | 公關、品牌行銷、活動企劃、企業社會責任、ESG、展覽、媒體、公關公司 | Needs UI Check | 改用品牌活動/展覽/行銷語意 suggestion，並建立看過品牌活動案例頁的 retargeting。 |
| Opening Tea Party | 創業、開店、商業空間設計、辦公室設計、室內設計、品牌經營、新創公司 | Needs UI Check | 改用開幕、商空、室內設計、品牌經營語意 suggestion；搭配地區與年齡層縮窄。 |
| Seminar Institution Tea Break | 大學、EMBA、教育、講座、研討會、醫療機構、行政管理、人力資源 | Needs UI Check | 改用教育/研討會/講座語意 suggestion；若職稱 targeting 不可用，先用 landing-page retargeting。 |
| Cultural Exhibition Opening | 美術館、藝文活動、策展、展覽、文化創意、設計、藝術 | Needs UI Check | 改用文化活動、展覽、藝術與設計語意 suggestion；可與 Brand PR ESG 共用 warm audience。 |

## Creative Rules For A2 Check

- 第一輪不要用 `誠品酒窖品酒會開幕.jpeg` 當 Meta 素材主圖；酒類畫面可能增加審核與投放限制。
- 第一輪不主打 `老錢風生日派對.HEIC`, `純白主題風生日派對.jpg`, `豪宅公設自辦派對.HEIC`, `新居落成海鮮派對.JPG`, `戶外婚禮證婚場地.jpg`；這批偏 B2C / 私人派對，等 B2B ad sets 跑順再做第二波。
- 優先使用場景完整、可看出企業/場館/接待脈絡的照片；食物 close-up 只當輪播第 2-4 張。
- 有明顯人臉、外部 logo、酒瓶、過多文字 overlay 的圖，進廣告前需裁切或改為網站內文輔助圖。

## A2 Next Recommendations

1. 先做 P1 三組：`Real Estate VIP Reception`、`Brand PR ESG Event`、`Opening Tea Party`。這三組最貼近 To B 客單與現有 live landing pages。
2. `Seminar Institution Tea Break` 可同步準備素材，但等 A2 把成大/長榮/機構案例段補進 `corporate-tea-party-desserts` 後再投。
3. `Cultural Exhibition Opening` 先當 P2；適合做形象與再行銷，不一定先當冷受眾主力。
4. Meta Ads Manager access check 前，不要把 detailed targeting 寫死；所有興趣項目都保留 `Needs UI Check`。
5. A2 下一條可交辦 Antigravity：進 Meta Ads Manager 只讀確認是否能看到 campaign/ad set 層級、是否可用 detailed targeting 或 Advantage+ audience suggestion、是否可看 website custom audience / pixel event。
6. A2 下一條可交辦素材 worker：先為 P1 三組各挑 3 張 `meta_4x5` 與 1 張 `story_9x16`，產出 WebP/JPG 檔名、alt、caption、slot description manifest。

## Blockers

- 未驗證 Meta Ads Manager access。
- 未驗證 Meta Pixel / website custom audience 是否存在。
- 未驗證 detailed targeting candidate 是否仍可選。
- 未確認各 landing page 是否已補入本批案例段；若 landing page 還是泛文，投放會降低轉換品質。
