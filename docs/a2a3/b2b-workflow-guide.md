# MAPLAB B2B Workflow Guide

版本：v1.0
建立：2026-05-11
目的：把今天這批 B2B 案例頁的整理方法、使用路徑與交接順序寫成可重複執行的指南。

## 2026-05-24 接續修正

Owner 已確認 Rank Math 退訂後，已設定好的 SEO 欄位先不要再設定。A2 接下來的工作是「案例寫作與素材對齊」，不是 RM 分數優化。

每次開始前先走這個最短路徑：

1. 讀 `CURRENT_STATUS.md` 最新 A2 live fact check。
2. 讀 `docs/a2a3/live-wordpress-audit.md` 的 Live URL map。
3. 讀 `docs/a2a3/b2b-case-inventory.md` 的 2026-05-24 live URL 修正。
4. 用 Owner 提供的照片與場次，填成 `可公開案例名 / 內部核對名 / 場景類型 / live URL / 可用照片` 五欄。
5. 只補真實案例與內連，不碰 Rank Math、不發布 WordPress。

## 這份指南在做什麼

這不是要先派給 OpenClaw。
它是讓人類先把一輪做完、看懂、修正好，再決定什麼地方只留一個小任務給 OpenClaw 當版本訓練測試。

## 先後順序

1. 先看 `docs/a2a3/b2b-case-inventory.md`
2. 再看 `docs/a2a3/b2b-crosswalk.md`
3. 再查 live URL 是否 200；planned slug 若 404，不要拿來當目標
4. 檢查草稿、SEO、圖片、案例是否對齊
5. 只補缺口，不補不存在的泛用入口
6. 最後才整理成技能或訓練任務

## 本批優先頁面

- `corporate-catering-tainan`
- `corporate-tea-party-desserts`
- `tainan-corporate-opening-tea-catering`
- `brand-esg-catering-service`
- `press-conference-catering`
- `vip-expo-catering-business-meeting`

暫不使用：
- `catering-corporate-tainan`
- `meeting-refreshment-catering-tainan`
- `opening-event-catering-tainan`
- `brand-event-catering`
- `school-event-catering-tainan`

原因：2026-05-24 前台查詢為 404，屬舊 workbench planned slugs。

## 每頁必看欄位

- `draft.md`
- `copy.md`
- `outline.md`
- `seo.md`
- `rankmath_payload.json`
- `source_bridge.md`
- `preview.html`
- `assets/`

## 檢查順序

### 1. 案例是否真實

先確認頁面裡的案例名是否能回到 IG、Drive、報價單或照片日期。

### 2. 類別是否對

確認頁面放在正確的 cluster，不跟別頁互搶。

### 3. 語氣是否對

- 不寫價格
- 不寫誇張形容
- 不用空泛讚美
- 先說場景，再說服務

### 4. 圖片是否對

- Hero 圖先看畫面
- Inline 圖補場景
- 不裁得太硬
- 不把原始素材改掉

### 5. SEO 是否對

- Title 對場景
- Focus keyword 對頁面
- Description 不要重複別頁
- Internal links 不要亂回首頁

## 使用路徑

### 人類工作路徑

- `Launchpad` → `B2B Case Inventory` → `B2B Crosswalk` → `handoff.html`
- 然後逐頁開 `preview.html` 檢查

### 桌面路徑

- `/Users/pagemacmini/Desktop/wordpress 素材庫/handoff.html`
- `/Users/pagemacmini/Desktop/wordpress 素材庫/preview.html`
- `/Users/pagemacmini/Desktop/MAPLAB_A2A3_Workbench/`

## 什麼時候才留小任務給 OpenClaw

只留一個很小的版本訓練測試，例如：

- 讀單一頁的 `draft.md`
- 檢查 `rankmath_payload.json`
- 回報是否缺案例或缺圖
- 不可發布
- 不可改主頁
- 不可碰整個 Drive

### 建議的小任務

```text
job_id: JOB-B2B-TRIAL-001
task_type: b2b_case_review
target: /Users/pagemacmini/Desktop/wordpress 素材庫/wordpress/corporate-tea-party-desserts
goal: 讀 draft.md, seo.md, rankmath_payload.json, preview.html，回報是否缺案例、缺圖、或與 inventory / crosswalk 不一致
rules:
- only review
- no publish
- no drive-wide scan
- no price output
```

## 這批的心得

1. 先對齊現有頁面，再補案例，比先生 8 個泛用頁穩。
2. 真案例名稱比泛用 landing page 文案更有辨識度。
3. Public copy 先拿掉價格，避免跟投放和真實案例互相干擾。
4. B2B 頁面先做穩，再考慮交給 OpenClaw 做批次訓練。
