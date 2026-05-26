# Ads Landing Settings — Round 008

日期：2026-05-26
狀態：Proposal only / Owner review required
角色：Antigravity-style Ads routing worker

## Guardrails

- 不開、不修改 Google Ads、Meta Ads、WordPress、Rank Math、secrets。
- Google Ads 只使用已驗證 live URL；不使用舊 404 planned slugs。
- Meta 現有互動廣告保持不動；另提獨立 landing-page traffic path。
- `互動廣告組合 A 企業窗口` 可作已驗證受眾 seed。
- `互動廣告組合 B 公關公司窗口` 保持 `Needs UI Detail`，不得複製 A 的受眾當成 B 事實。

## Google Ads

現況：13 個 phrase match keywords 目前同在 `Campaign 4：高意圖搜尋_南台灣外燴 / 廣告群組 1`。建議不直接改帳戶，先讓 Owner 核准是否拆成下列搜尋意圖 ad groups。

| Priority | Campaign / ad group 名稱建議 | 對應 live landing URL | UTM | 素材 / 案例 | 關鍵字 | 先不做什麼 | Owner approval required |
|---|---|---|---|---|---|---|---|
| P1 | `Campaign 4：高意圖搜尋_南台灣外燴` / `開幕茶會_辦公室` | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | `?utm_source=google&utm_medium=cpc&utm_campaign=b2b_case_opening_tea&utm_content=opening_tea_office` | AMD 辦公室開幕、東京威力科創廠區開幕、興達海洋公司開幕、美學中心開幕、家居與設計開幕 | `"台南開幕茶會"`, `"台南診所開幕茶會"`, `"台南辦公室外燴"` | 不改 budget / bid / conversion；不導到 `opening-event-catering-tainan` 404 slug | 核准拆 ad group、核准 final URL、核准品牌/場地名稱可否進廣告文案 |
| P1 | `Campaign 4：高意圖搜尋_南台灣外燴` / `會議茶點_研討會` | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | `?utm_source=google&utm_medium=cpc&utm_campaign=b2b_case_meeting_refreshment&utm_content=seminar_refreshment` | 成大會議茶點、成大實驗室揭牌、長榮大學 EMBA 音樂會 | `"台南會議茶點"`, `"台南研討會餐點"`, `"台南茶會點心"` | 不新增泛用「學校活動」頁；不導到 `meeting-refreshment-catering-tainan` 404 slug | 核准把會議/研討會詞集中到此頁，核准是否保留低搜尋量長尾詞 |
| P1 | `Campaign 4：高意圖搜尋_南台灣外燴` / `企業_品牌_公關` | umbrella: `https://www.maplabkitchen.com/corporate-catering-tainan/`; brand/public-benefit: `https://www.maplabkitchen.com/brand-esg-catering-service/`; PR: `https://www.maplabkitchen.com/press-conference-catering/` | `?utm_source=google&utm_medium=cpc&utm_campaign=b2b_case_corporate_brand_pr&utm_content={corporate_or_brand_or_pr}` | 國泰建設財富管理論壇、賓士集團捐車、微商大會、文化場館案例 | `"台南企業外燴"`, `"台南品牌活動外燴"`, `"活動公司 外燴 配合"`, `"公關公司 茶會 配合"` | 不把所有品牌/公關詞塞回單一泛用 URL；不改現有 keyword 狀態直到 Owner 核准 | 核准是否一組 ad group 內做 URL split，或拆成 `企業主入口` / `品牌活動公益` / `記者會公關` 三組 |
| P2 | `Campaign 4：高意圖搜尋_南台灣外燴` / `建案_VIP_展覽接待` | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | `?utm_source=google&utm_medium=cpc&utm_campaign=b2b_case_vip_expo&utm_content=real_estate_vip` | 上曜建設 VIP 迎賓、泰嘉建設 VIP 說明會、松丹達麗 VIP 茶會、宏福悅 VIP 接待會 | `建案說明會茶點`, `VIP 說明會外燴`, `展覽接待茶點`, `商務茶會` | 不急著新增 keyword；先等 P1 拆分和案例段落核准 | 核准是否作第二波 Search ad group |
| Park | To C 暫放 / 第二波 private event | 目前不列入本輪 To B landing path | N/A | 週歲、婚禮、生日、豪宅派對、新居落成 | `"台南週歲派對外燴"`, `"台南婚禮外燴"` | 本輪不導入 To B campaign，不用 B2B 案例頁承接 | 核准是否先暫放 To C keyword，避免干擾 B2B 搜尋意圖 |

## Meta Ads

現況：現有 `2026 B組"互動"行銷活動-cta` 是互動 / 粉專按讚 / IG 商業檔案瀏覽路徑，不是已確認的 WordPress landing-page traffic。建議保留現役互動廣告，另開獨立 traffic proposal。

| Priority | Campaign / ad set 名稱建議 | 對應 live landing URL | UTM | 素材 / 案例 | 受眾 | 先不做什麼 | Owner approval required |
|---|---|---|---|---|---|---|---|
| P1 | `2026 To B Landing Page Traffic — South Taiwan` / `A 企業決策者_台南+40km_LP Traffic` | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/`; `https://www.maplabkitchen.com/brand-esg-catering-service/`; `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=2026_b2b_lp_traffic&utm_content={opening_or_brand_or_vip}_{format}_{case}&utm_term=a_corporate_decision_maker` | AMD / 東京威力 / 興達開幕；國泰 / 賓士 / 美麗代言人；上曜 / 泰嘉 / 宏福悅 VIP | 已驗證 A seed：台南 +40km、30-60、所有性別；半導體、電機/電子/工業工程、銀行金融；商業計畫、中小企業、專案管理、企業管理、企業家、產品經理、創辦人、商業決策者 | 不改現有 `互動廣告組合 A 企業窗口`；不把互動 campaign 改成 traffic objective；不開 Advantage+ 擴張直到 Owner 核准 | 核准是否另建 LP traffic campaign；核准 A seed 可作第一組 traffic ad set；核准素材品牌/logo 可用範圍 |
| Hold | `2026 To B Landing Page Traffic — South Taiwan` / `PR_公關公司窗口_LP Traffic_Needs UI Detail` | `https://www.maplabkitchen.com/press-conference-catering/`; `https://www.maplabkitchen.com/brand-esg-catering-service/`; `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=2026_b2b_lp_traffic&utm_content=pr_window_{format}_{case}&utm_term=pr_window_needs_ui_detail` | 賓士集團捐車、微商大會、國泰論壇、台南美術館、史前博物館西拉雅特展 | B seed 只確認 row-level running；詳細受眾、地區、年齡、CTA、URL、Advantage+ 皆 `Needs UI Detail`。規劃方向可寫 PR、公關公司、活動企劃、媒體發布、品牌行銷 | 不 launch；不複製 A 受眾；不把 B 當已驗證 detailed targeting | 核准是否先只做 read-only B detail capture；B UI detail 補齊前不進 launch |
| P2 | `2026 To B Landing Page Traffic — South Taiwan` / `Seminar_Institution_LP Traffic` | `https://www.maplabkitchen.com/corporate-tea-party-desserts/`; support: `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | `?utm_source=meta&utm_medium=paid_social&utm_campaign=2026_b2b_lp_traffic&utm_content=seminar_institution_{format}_{case}&utm_term=institution_organizer_proposal` | 成大會議茶點、成大實驗室揭牌、長榮大學 EMBA 音樂會 | Proposal-only：大學、EMBA、講座、研討會、醫療/行政/HR/training/workshop；若 interest 不穩，用 page-specific creative + retargeting | 不假設 Meta interest 一定可選；不做 pixel/custom audience until verified | 核准是否作第二波 ad set；核准校名/場館名稱與照片露出方式 |
| P2 | `2026 To B Landing Page Traffic — South Taiwan` / `Retargeting_Meta Engagers_or_Site Visitors` | 依互動來源導回相同 cluster live URL | `?utm_source=meta&utm_medium=paid_social&utm_campaign=2026_b2b_lp_traffic&utm_content=retargeting_{cluster}_{format}&utm_term=retargeting_verified_only` | 用 P1 表現較好的 case creative | 只在 pixel、website visitors、Meta engagers、LINE inquiry converters 可被只讀驗證後使用 | 不聲稱 pixel/custom audience ready；不排除或建立受眾直到 UI 證據確認 | 核准是否檢查 pixel/custom audiences；核准 retargeting 規則和排除條件 |

## URLs To Exclude From Ads

以下舊 planned slugs 已被標記為 404，本輪 Google Ads / Meta Ads 均不使用：

- `https://www.maplabkitchen.com/catering-corporate-tainan/`
- `https://www.maplabkitchen.com/meeting-refreshment-catering-tainan/`
- `https://www.maplabkitchen.com/opening-event-catering-tainan/`
- `https://www.maplabkitchen.com/brand-event-catering/`
- `https://www.maplabkitchen.com/school-event-catering-tainan/`

## Owner Decision Checklist

1. 是否核准 Google Ads 先拆三組 P1：`開幕茶會_辦公室`、`會議茶點_研討會`、`企業_品牌_公關`。
2. 是否核准 Google Ads final URL 加 UTM 導到上述 live URLs。
3. 是否核准 To C keyword 先暫放，不混入本輪 To B campaign。
4. 是否核准 Meta 另建 `2026 To B Landing Page Traffic — South Taiwan`，保留現有互動廣告不動。
5. 是否核准 Meta 第一波只用 A 企業窗口受眾 seed，B 公關公司窗口等 UI detail 補齊。
6. 是否核准外部品牌、校名、場館、建案名稱與 logo 在廣告素材中的使用或裁切規則。
7. 是否核准 UTM 命名 convention，讓 Google / Meta traffic 與現有互動廣告分開看。
