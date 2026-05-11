# MAPLAB Live WordPress Audit

版本：v1.0
日期：2026-05-11
用途：發文前先對齊 live WordPress 架構，避免互搶關鍵字與補錯頁。

## Live Snapshot

- Published pages: 6
- Published posts: 57

### 已確認的核心頁

1. `homepage-v2` - 台南外燴｜MAPLAB Kitchen CATERING SERVICE
2. `corporate-catering-tainan` - 台南企業外燴推薦｜2026 品牌活動、展會、記者會規劃 - MAPLAB
3. `press-conference-catering` - 記者會餐點推薦：5 步打造高質感品牌活動餐飲｜MAPLAB
4. `tainan-party-venue` - 派對流程怎麼規劃？場地、餐點、預算一次搞懂！｜MAPLAB 外燴教學文
5. `tainan-catering-recommendation` - 台南外燴全攻略 2026｜企業尾牙、婚禮、週歲派對一站搞懂 - MAPLAB
6. `privacy-policy`

## 目前的結構判讀

### 1. 核心主頁已存在

`corporate-catering-tainan` 已是明確的 B2B 主頁，不應再用泛用頁面重複說一遍企業外燴。

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
3. 打開 `wordpress 素材庫/wordpress/<slug>/preview.html` 看草稿與圖文
4. 檢查 `rankmath_payload.json` 的 title / description / focus keyword
5. 檢查內連是否只導向對應 cluster
6. 最後再用 Browser / Computer Use 看實際版面與圖片裁切

## 這次不要做的事

- 不要再先生 8 個泛用主頁
- 不要先寫價格
- 不要把支援案例寫成主頁重複內容
- 不要讓新頁互搶關鍵字
- 不要在沒有 visual QA 前直接發文

## 最短使用路徑

`live-site audit -> case inventory -> crosswalk -> preview -> Rank Math -> visual QA -> publish`

## 給後續 Agent 的一句話

先看 live WordPress 架構，再補 B2B 真案例，最後才發文。
