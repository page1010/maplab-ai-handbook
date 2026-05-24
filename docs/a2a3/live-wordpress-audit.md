# MAPLAB Live WordPress Audit

版本：v1.1
日期：2026-05-24
用途：發文前先對齊 live WordPress 架構，避免互搶關鍵字與補錯頁。

## Live Snapshot

- Published pages: 6
- Published posts: 57
- 檢查方式：WordPress public REST + 前台 HTTP 200/404，不登入後台、不讀 Rank Math paid UI。
- Rank Math 狀態：Owner 已退訂；既有設定先保留，不再新增/調整 RM 設定。案例寫作只處理公開內容、URL 對應、內連與素材證據。

## 2026-05-24 A2 To B live fact check

### 結論

網站確實已經往 To B 經營：首頁有企業活動訊號，`企業外燴案例` category 有 15 篇，企業 / 會議 / 開幕 / 品牌 / 記者會 / 展覽接待相關內容已成形。

但目前狀態是「B2B 內容群已成形」，不是「企業案例中心完成」。下一步不是再調 Rank Math，也不是再生泛用頁，而是用 Owner 提供的照片與場次補真實案例。

### Live URL map（以這張表為準）

| 用途 | Live URL | WP type / ID | 狀態 |
|---|---|---:|---|
| 企業外燴主入口 | `https://www.maplabkitchen.com/corporate-catering-tainan/` | post 586 | 200 |
| 會議茶點 / 研討會 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` | post 924 | 200 |
| 開幕茶會 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` | post 1205 | 200 |
| 品牌活動 / VIP / 展覽開幕 | `https://www.maplabkitchen.com/brand-esg-catering-service/` | post 945 | 200 |
| 記者會 / 發表會 | `https://www.maplabkitchen.com/press-conference-catering/` | post 879 | 200 |
| 展覽 VIP 接待 | `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/` | post 261 | 200 |
| 文化場館案例 | `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/` | post 1048 | 200 |

### Planned slugs that are not live

以下 slug 來自舊 task card / local workbench，2026-05-24 前台查詢為 404。不要把它們當成發文或內連目標：

| Planned slug | Live replacement |
|---|---|
| `catering-corporate-tainan` | `corporate-catering-tainan` |
| `meeting-refreshment-catering-tainan` | `corporate-tea-party-desserts` |
| `opening-event-catering-tainan` | `tainan-corporate-opening-tea-catering` |
| `brand-event-catering` | `brand-esg-catering-service` |
| `school-event-catering-tainan` | 尚無 live 對應，先不要內連 |

### 已確認的 public pages（WP page type）

1. `homepage-v2` - 台南外燴｜MAPLAB Kitchen CATERING SERVICE
2. `tainan-party-venue` - 派對流程怎麼規劃？場地、餐點、預算一次搞懂！｜MAPLAB 外燴教學文
3. `join-maplab-catering-partner` - 外燴加盟合作平台-加入我們
4. `about-us-maplabkitchen` - About us
5. `工商代購服務`
6. `privacy-policy`

注意：B2B 主要入口目前是 published posts，不是 WP pages。不要再把 `corporate-catering-tainan` 誤記為 page type。

## 目前的結構判讀

### 1. 核心主頁已存在

`corporate-catering-tainan` 已是明確的 B2B 主入口（published post），不應再用泛用頁面重複說一遍企業外燴。

### 2. 支援頁已存在

`press-conference-catering`、`tainan-party-venue`、`tainan-catering-recommendation` 都屬於支援頁或教學頁，不是要再複製的商業入口。

### 3. 這批工作應該做的是補案例，不是補更多泛用頁

第一輪先處理：
- 企業會議 / 茶點 / 辦公室
- 開幕 / 品牌活動 / VIP 接待
- 學校 / 研討會 / 畢典
- 文化場館 / 展覽 / 建案

## 發文前的語氣規則

發文前都沿用 A2/A3 的品牌語氣：

- 說場景，不硬講賣點
- 用具體名詞，不用空泛形容
- 不寫價格
- 不用誇張推銷語
- 先寫真案例，再寫 FAQ，再寫 CTA
- 句子保持穩定、安靜、專業

## 發文前的檢查順序

1. 看 `b2b-case-inventory.md`，確認這頁是不是這一輪該補的頁
2. 看 `b2b-crosswalk.md`，確認案例能回到 IG / Drive / 報價單 / 相片日期
3. 先查 live URL 是否 200；若 planned slug 是 404，不要當目標
4. 打開 `wordpress 素材庫/wordpress/<slug>/preview.html` 看草稿與圖文（若本機素材存在）
5. 只讀 `rankmath_payload.json` 的 title / description / focus keyword；Rank Math 已退訂，不再設定
6. 檢查內連是否只導向對應 cluster
7. 最後再用 Browser / Computer Use 看實際版面與圖片裁切

## 這次不要做的事

- 不要再先生 8 個泛用主頁
- 不要先寫價格
- 不要把支援案例寫成主頁重複內容
- 不要讓新頁互搶關鍵字
- 不要在沒有 visual QA 前直接發文

## 最短使用路徑

`live-site audit -> case inventory -> case photo intake -> preview -> visual QA -> Owner approval`

## 給後續 Agent 的一句話

先看 live WordPress 架構，再補 B2B 真案例，最後才發文。
