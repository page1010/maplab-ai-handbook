# A4 Assets Round 001

日期：2026-05-26
角色：A4 素材處理支援 worker
工作範圍：只做檔案盤點與處理規格；不改原始照片、不轉檔、不輸出圖片、不上傳 WordPress、不發布。

## Source Folder

Owner 原始照片資料夾：

`/Users/pagemacmini/Desktop/案例分享wordpress用/`

本輪以 A2 已建立的 B2B landing plan 為準，先挑第一批能支撐企業會議、會議茶點、開幕茶會、品牌/VIP、文化場館的素材。部分 HEIC/JPG/PNG 在本環境無法直接視覺預覽，已依 Owner 檔名、已附圖畫面、尺寸與 A2 既有規劃做第一輪素材規格；進入實際裁切前仍需人工 visual QA。

## Slot Rules

| Slot | 建議尺寸 | 用途 | 裁切原則 |
|---|---:|---|---|
| `hero_16x9` | 1600 x 900 | WordPress 文章首圖 / Google landing proof | 保留完整場景、餐桌與場域關係 |
| `case_4x3` | 1200 x 900 | 文章案例段主圖 | 保留桌面、陳列與可識別場景 |
| `detail_1x1` | 1080 x 1080 | 內文細節 / 輪播單張 | 放大食物與擺盤，避開品牌或人臉 |
| `meta_4x5` | 1080 x 1350 | Meta feed | 主體置中，上下保留文字安全邊 |
| `story_9x16` | 1080 x 1920 | Story / Reels | 直式圖優先，保留上方安全區 |

## 第一批 B2B 優先圖

### 1. 企業會議

承接頁建議：`corporate-catering-tainan`、`brand-esg-catering-service`

| 原始檔 | 尺寸 | 建議 slot | 建議 WebP 檔名 | Alt text | Caption / Description 草案 | 風險與處理 |
|---|---:|---|---|---|---|---|
| `國泰建設財富管理論壇.png` | 1421x947 | `hero_16x9`, `case_4x3`, `meta_4x5` | `maplab-corporate-forum-cathay-wealth-management-hero.webp` | MAPLAB 台南企業外燴，國泰建設財富管理論壇茶點桌 | 財富管理論壇以正式桌面與精緻茶點呈現企業接待質感，適合放在企業外燴主入口作為高信任案例。 | 背板與企業名可保留作 case proof；投廣告前確認品牌露出可接受。 |
| `美麗代言人微商大會再創巔峰.PNG` | 1260x1533 | `case_4x3`, `meta_4x5`, `story_9x16` | `maplab-brand-conference-beauty-summit-case.webp` | MAPLAB 品牌大會活動茶點，微商大會外燴餐點陳列 | 品牌型大會適合支撐發表會、會員大會與活動餐點需求。 | 若畫面有人像或外部 logo 過大，Meta 廣告先裁掉；網站內文可作案例輔助。 |
| `賓士集團捐車送愛心活動.PNG` | 1272x1401 | `case_4x3`, `meta_4x5`, `story_9x16` | `maplab-brand-esg-benz-donation-event-case.webp` | MAPLAB 企業公益活動茶點，品牌 ESG 活動餐點服務 | 企業公益與品牌活動可作 ESG、記者會、品牌接待案例。 | 外部品牌 logo 高敏感；網站案例可用，廣告素材建議裁成餐點與活動桌面，不以 logo 為主。 |
| `產後護理之家聖誕餐會.JPG` | 3924x2943 | `hero_16x9`, `case_4x3`, `detail_1x1` | `maplab-institution-christmas-catering-case.webp` | MAPLAB 機構聖誕餐會外燴，節慶活動餐點桌 | 機構型節慶餐會可補企業員工活動、客戶接待與院所活動的場景。 | 聖誕主題季節性強，不宜放第一張 hero；可作企業活動延伸案例。 |

### 2. 會議茶點

承接頁建議：`corporate-tea-party-desserts`

| 原始檔 | 尺寸 | 建議 slot | 建議 WebP 檔名 | Alt text | Caption / Description 草案 | 風險與處理 |
|---|---:|---|---|---|---|---|
| `成大會議茶點.PNG` | 1290x2279 | `story_9x16`, `meta_4x5`, `detail_1x1` | `maplab-meeting-refreshment-ncku-library-story.webp` | MAPLAB 成功大學會議茶點，台南研討會點心外燴 | 成功大學圖書館總館會議茶點，適合說明研討會、講座與校園活動茶點配置。 | 原圖為長圖拼貼，做網站 hero 時需另裁 16:9；保留地點標籤但避免裁到餐點主體。 |
| `成大實驗室揭牌典禮.JPG` | 2034x1526 | `case_4x3`, `hero_16x9`, `meta_4x5` | `maplab-university-lab-opening-ncku-case.webp` | MAPLAB 成功大學實驗室揭牌典禮茶點，校園活動外燴 | 實驗室揭牌活動可支撐校園、研究單位與正式儀式茶點需求。 | 若畫面含人臉或校方 logo，廣告先裁餐桌區；網站案例需 Owner 最終核可。 |
| `長榮大學emba音樂會.JPG` | 3024x4032 | `story_9x16`, `meta_4x5`, `detail_1x1` | `maplab-university-emba-concert-tea-break.webp` | MAPLAB 長榮大學 EMBA 音樂會茶點，活動點心外燴 | EMBA 與校園活動茶點可放在會議茶點頁，說明不同規模與活動形式都能配置。 | 直式圖適合 story；若有明顯人臉先避開。 |
| `匹克球以球會友餐會.JPG` | 4032x3024 | `hero_16x9`, `case_4x3`, `detail_1x1` | `maplab-community-sports-pickleball-catering-case.webp` | MAPLAB 戶外社群活動餐會，運動交流活動茶點桌 | 社群活動與交流餐會可作會議茶點的輕鬆場景補充。 | To B 優先度低於校園與研討會；先作輔助圖，不放第一屏。 |

### 3. 開幕茶會

承接頁建議：`tainan-corporate-opening-tea-catering`

| 原始檔 | 尺寸 | 建議 slot | 建議 WebP 檔名 | Alt text | Caption / Description 草案 | 風險與處理 |
|---|---:|---|---|---|---|---|
| `amd辦公室開幕茶會.JPG` | 1645x2193 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-office-opening-amd-tea-party-case.webp` | MAPLAB 辦公室開幕茶會，科技公司開幕活動餐點 | 辦公室開幕茶會適合放在開幕茶會頁，強化科技公司與企業新據點案例。 | 外部品牌名敏感；廣告圖建議裁餐桌與場景，不突出 logo。 |
| `東京威力科創廠區開幕.HEIC` | 3024x4032 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-tech-factory-opening-tea-party-case.webp` | MAPLAB 科技廠區開幕茶會，企業開幕活動外燴 | 科技廠區開幕可作大型企業開幕、廠辦活動與正式接待案例。 | 檔案為 HEIC；轉檔前需確認人臉、制服、廠區標誌是否需避開。 |
| `興達海洋公司開幕茶會.JPG` | 1389x1042 | `hero_16x9`, `case_4x3`, `detail_1x1` | `maplab-company-opening-ocean-industry-tea-party.webp` | MAPLAB 公司開幕茶會，台南企業開幕茶點桌 | 公司開幕茶會適合直接支撐「開幕茶會」「公司開幕外燴」搜尋意圖。 | 尺寸接近 4:3，適合 case 圖；若需 hero 需左右補安全裁切。 |
| `家居與設計開幕茶會.PNG` | 1290x1712 | `meta_4x5`, `story_9x16`, `case_4x3` | `maplab-interior-design-opening-tea-party-case.webp` | MAPLAB 家居與設計開幕茶會，品牌空間開幕餐點 | 室內設計與家居品牌開幕適合串接商空、品牌與開幕茶會需求。 | 圖中若有店面或品牌 logo，廣告需裁切降低品牌佔比。 |
| `美學中心開幕茶會.jpg` | 936x976 | `detail_1x1`, `case_4x3`, `meta_4x5` | `maplab-aesthetic-center-opening-tea-party-detail.webp` | MAPLAB 美學中心開幕茶會，精緻點心與茶會佈置 | 小型開幕茶會可作內文細節圖，補充不同空間規模的配置方式。 | 原始解析度較低，不建議放 hero；適合 detail 或小尺寸內文圖。 |

### 4. 品牌 / VIP

承接頁建議：`vip-expo-catering-business-meeting`、`brand-esg-catering-service`

| 原始檔 | 尺寸 | 建議 slot | 建議 WebP 檔名 | Alt text | Caption / Description 草案 | 風險與處理 |
|---|---:|---|---|---|---|---|
| `上曜建設vip迎賓.PNG` | 1290x2262 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-real-estate-vip-reception-shangyao-story.webp` | MAPLAB 建設公司 VIP 迎賓茶點，建案接待外燴服務 | 高樓景觀與精緻點心能支撐建案 VIP 接待、預售屋說明會與商務接待場景。 | 外部案名與 logo 可作案例證據；廣告建議裁成餐點與空間氛圍。 |
| `泰嘉建設vip說明會.PNG` | 1290x2292 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-real-estate-vip-briefing-taijia-story.webp` | MAPLAB 建案 VIP 潛銷說明會茶點，房地產接待餐點 | 建案說明會茶點適合直接對應 VIP 接待與商務洽談 landing page。 | 原圖含建案模型與品牌文字，網站 case 可用；廣告需降低外部品牌主視覺。 |
| `松丹達麗vip茶會.PNG` | 1290x2270 | `story_9x16`, `meta_4x5`, `detail_1x1` | `maplab-real-estate-vip-tea-songdan-story.webp` | MAPLAB 建設 VIP 茶會點心，房地產客戶接待外燴 | 連續活動型 VIP 茶會可用來說明多日接待、銷售中心茶點與高端迎賓配置。 | 圖中有建案名稱；Meta 廣告先用餐點段落或桌面特寫。 |
| `宏福悅vip接待會.HEIC` | 3903x2927 | `hero_16x9`, `case_4x3`, `meta_4x5` | `maplab-real-estate-vip-reception-hongfuyue-hero.webp` | MAPLAB 房地產 VIP 接待會茶點，建案活動外燴 | 橫式高解析圖適合做 VIP 接待頁 hero 或案例主圖。 | HEIC 轉檔前需確認人臉與案名位置；若 logo 太大，改作 case 圖。 |
| `豪宅公設自辦派對.HEIC` | 3756x2902 | `hero_16x9`, `case_4x3`, `meta_4x5` | `maplab-luxury-residence-private-party-catering-case.webp` | MAPLAB 豪宅公設自辦派對外燴，住戶活動餐點服務 | 豪宅公設活動可作 VIP/高端住宅接待的延伸素材，支撐房地產與高端私宴。 | 偏 B2C 私宴；第一波可當 VIP 輔助，不放 Google Ads 主 landing hero。 |

### 5. 文化場館

承接頁建議：`daxin-art-museum-opening-catering`、`brand-esg-catering-service`

| 原始檔 | 尺寸 | 建議 slot | 建議 WebP 檔名 | Alt text | Caption / Description 草案 | 風險與處理 |
|---|---:|---|---|---|---|---|
| `大新美術館開幕茶會.JPG` | 2116x1588 | `hero_16x9`, `case_4x3`, `meta_4x5` | `maplab-art-museum-opening-daxin-hero.webp` | MAPLAB 大新美術館開幕茶會，藝文場館外燴餐點 | 美術館開幕茶會適合當文化場館案例主圖，呈現藝文活動與餐桌設計整合。 | 若場館標誌或人像入鏡，Meta 廣告需裁掉；網站可作案例 proof。 |
| `宮崎御所美術館開幕` | 1645x2193 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-art-museum-opening-miyazaki-story.webp` | MAPLAB 美術館開幕茶會，文化場館活動點心服務 | 直式圖適合故事型素材，補文化場館開幕與貴賓接待情境。 | 檔案無副檔名但可讀取尺寸；轉檔 manifest 要保留 source_path。 |
| `國立台灣史前博物館西拉雅特展.HEIC` | 2193x1645 | `hero_16x9`, `case_4x3`, `meta_4x5` | `maplab-museum-exhibition-siraya-opening-case.webp` | MAPLAB 國立台灣史前博物館西拉雅特展茶會，展覽活動外燴 | 博物館特展茶會可支撐展覽開幕、文化活動與品牌場域接待。 | 國立場館名稱可提升信任，但廣告投放前需確認場館識別露出可用。 |
| `台南美術館湯德章圓環美食.HEIC` | 1899x1899 | `detail_1x1`, `meta_4x5`, `case_4x3` | `maplab-tainan-art-museum-tangdezhang-food-event-detail.webp` | MAPLAB 台南美術館湯德章圓環美食專場，戶外藝文活動餐點 | 方圖適合做文化活動 detail 或 Meta feed，呈現戶外場域與餐點配置。 | 若畫面有路人或外部招牌，廣告前裁切到餐桌與場景即可。 |
| `湯德章圓環特展台南美食專場.JPG` | 3024x4032 | `story_9x16`, `meta_4x5`, `case_4x3` | `maplab-tangdezhang-exhibition-food-event-story.webp` | MAPLAB 湯德章圓環特展台南美食專場，展覽活動外燴 | 特展型戶外美食專場可補文化場館、策展活動與城市活動案例。 | 直式素材適合 story；前台 hero 需另裁 16:9。 |

## 不適合第一波廣告或需裁切處理

| 原始檔 | 原因 | 建議處理 |
|---|---|---|
| `誠品酒窖品酒會開幕.jpeg` | 明確酒類情境，Meta / Google 審核可能增加限制。 | 第一波不投廣告；若進網站案例，只放內文並避免酒瓶成主視覺。 |
| `賓士集團捐車送愛心活動.PNG` | 外部品牌 logo / 車廠識別可能敏感。 | 網站可作 ESG proof；廣告先裁餐點桌或活動茶點，不把品牌 logo 當主角。 |
| `國泰建設財富管理論壇.png` | 企業名與論壇背板可能清楚入鏡。 | 網站案例可用；投放前確認 Owner 允許品牌名露出，或裁成餐點桌與場域。 |
| `上曜建設vip迎賓.PNG`, `泰嘉建設vip說明會.PNG`, `松丹達麗vip茶會.PNG`, `宏福悅vip接待會.HEIC` | 建案名稱、模型、案場 logo 可能入鏡。 | VIP/房地產分眾很有價值，但廣告圖先以餐點與空間質感為主。 |
| `成大實驗室揭牌典禮.JPG`, `長榮大學emba音樂會.JPG` | 可能有人臉或校方識別。 | 若人臉清楚，先用餐桌特寫或背向/遠景；網站案例需 Owner 最終審。 |
| `老錢風生日派對.HEIC`, `純白主題風生日派對.jpg`, `戶外婚禮證婚場地.jpg`, `新居落成海鮮派對.JPG` | 偏 B2C 私宴/婚禮，不是第一批 To B landing 主證據。 | 留到第二波 party / wedding / luxury private event 內容；可作 Meta creative 後續測試。 |

## Conversion / Crop Manifest 欄位格式

下一步若要開始轉檔與裁切，建議建立 `asset_conversion_manifest_round_001.csv`，欄位如下：

```csv
source_path,source_filename,source_width,source_height,cluster,landing_slug,case_name,slot,target_width,target_height,crop_anchor,crop_note,output_filename,alt_text,caption,description,ad_ok,ad_restriction,needs_face_crop,needs_logo_crop,needs_alcohol_avoid,priority,owner_review_status
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `source_path` | 原始檔完整路徑，不移動、不覆蓋 |
| `cluster` | `corporate_meeting`, `meeting_refreshment`, `opening_tea`, `brand_vip`, `cultural_venue` |
| `landing_slug` | 對應 live WordPress slug，例如 `corporate-tea-party-desserts` |
| `slot` | `hero_16x9`, `case_4x3`, `detail_1x1`, `meta_4x5`, `story_9x16` |
| `crop_anchor` | `center`, `top`, `bottom`, `left`, `right`, `food_table`, `venue_context` |
| `crop_note` | 要保留或避開的元素，例如 `keep buffet table`, `avoid logo`, `avoid faces` |
| `output_filename` | 轉 WebP 後檔名，格式 `maplab-{scene}-{case}-{slot}.webp` |
| `ad_ok` | `yes`, `site_only`, `no_first_wave` |
| `ad_restriction` | 例如 `external_logo`, `possible_faces`, `alcohol`, `low_resolution`, `b2c_second_wave` |
| `owner_review_status` | `pending`, `approved`, `needs_crop`, `reject` |

## Next Action

1. A2/A3 先依本回報選每個 landing page 的 2-3 張主圖。
2. A4 下一輪再建立 conversion manifest，但仍不碰原圖。
3. Owner 核可後，才進行 WebP 輸出、裁切、WordPress media upload 或廣告素材套版。
