# SEO & Ads Agent — MAPLAB 廣告技術文件

> 本文件記錄 MAPLAB Kitchen Meta 廣告帳號的技術設定狀態，供 AI agent 接手使用。
> 每次工作後請更新 Last Updated。

**Last Updated：2026-03-16 | A3 Ads Monitor Agent（Claude Sonnet 4.6）**

---

## 基本資訊

| 項目 | 值 |
|------|-----|
| 廣告帳號 ID | 318634712 |
| 企業管理平台 ID | 215690449213844 |
| Meta Pixel ID | 228166994905799 |
| GTM 容器 ID | GTM-T2Z52GP |
| GTM 容器域名 | www.maplabkitchen.com |
| 粉絲專頁 | Map Lab Kitchen 旅圖 |
| Instagram | @maplabkitchen |
| 網站 | www.maplabkitchen.com |

---

## Meta Pixel 串接確認

**狀態：✅ 已確認透過 GTM 部署**

- Pixel ID：228166994905799
- GTM 標籤名稱：`Facebook Pixel ID 228166994905799`
- 標籤類型：自訂 HTML
- 觸發條件：All Pages
- 關鍵參數：`fbq('set','agent','tmgoogletagmanager', '228166994905799')`
- 事件管理工具狀態：Meta 像素 使用中，過去 28 天 840 個事件

**注意**：GTM 中存在兩個 Facebook 標籤：
1. Facebook Pixel ID 228166994905799（主要，6年前建立）
2. FBpixel（6年前建立）

建議確認是否重複觸發，避免 Pixel 重複計算。

---

## 現有運行中策略（2026-03-16 截取）

### Meta 廣告帳號 318634712

| 行銷活動 | 狀態 | 預算 | 備註 |
|---------|------|------|------|
| 開發潛在客戶2026 | 開啟 | NT$100/日 | 空殼無廣告組合，建議暫停 |
| 2026 B組 互動行銷活動-cta | 開啟 | 廣告組合預算 | 花費 NT$5,015，結束 2026/6/30 |

活躍廣告組合（B組）：策略一-冷受眾-台南高雄25-40歲（adset ID: 52608263444730）進行中編輯中

### Google Ads 帳號 844-336-3178

| 廣告活動 | 狀態 | 預算 | 本週成效 |
|---------|------|------|---------|
| 最高成效（Performance Max）| 已啟用 | NT$300/日 | 曝光 12,564、花費 $768.70、轉換 2 次（待驗證）|

---

## 策略建議紀錄

### v1.4 — 2026-03-16 | A3 Claude | 策略一冷受眾 TA 設定建議

**背景：**
接手任務為協助設定 Meta 廣告策略一（冷受眾 1+2：家庭慶典族 + 婚禮女性）的受眾描述欄位與廣告素材製作。

**已有運行中策略觀察：**
- B組互動行銷活動-cta（企業窗口 + 公關窗口）目前仍在投放，結束日為 2026/6/30
- 開發潛在客戶2026 每日 NT$100 白燒（空殼無廣告組合）
- 5~8號 Instagram 貼文推廣全部花費 NT$0（建了但沒開）
- 策略一廣告組合（52608263444730）目前處於「編輯中」狀態，尚未發佈

**策略一 TA 設定建議（AI 廣告受眾描述欄位）：**

已填入 Meta 廣告組合「描述你的廣告受眾」欄位的完整描述：

目標受眾為台南、高雄 25–45 歲、有消費力的女性。她們通常已有婚姻或伴侶關係，正在籌備週歲、派對、婚禮或企業接待類活動。她們重視生活美感，願意花錢外包專業服務，不喜歡將就。她們不是在比價，而是在找「值得信任、有品味、能幫自己省力」的品牌。常出現在 IG 美食、花藝、婚禮、育兒相關帳號，偶爾購買高端親子課程或質感家居用品，也關注在地品牌活動。適合展示 MAPLAB 的場景美感照與客戶真實案例，強調「一桌一桌做出來的質感」。

**策略一建議（補足什麼 TA、為什麼）：**

現有 B組互動活動主打企業窗口與公關窗口，但缺少「有消費力的女性家庭決策者」這層受眾。
策略一目標是補足漏斗第一層的冷受眾，特別是：
- 冷受眾 1（家庭慶典族）：3–4月週歲、抓周需求升溫，現在投放時機最佳
- 冷受眾 2（婚禮與質感派對族）：5–6月婚禮旺季前哨，現在開始建立品牌印象

這兩個 TA 目前在帳號內完全沒有對應的冷受眾廣告在跑（B組主打互動/已知受眾），所以策略一是真正補漏斗頂端的行動。

**素材方向（C款 — 婚禮/質感派對）：**
- 背景：@maplabkitchen Instagram 婚禮風桌景照（白色窗簾 + 綠色花藝 + 玫瑰金燈具 + 甜點桌）
- 格式：1080x1080 Instagram 方形
- Canva 設計連結：https://www.canva.com/design/DAHD4wpehE4/bRsNDBSCLqJz7bB9SGmNPw/edit
- 計畫版本：
  - C-1：主標「質感不是偶然」/ 副標「是一桌一桌做出來的」/ CTA「@maplabkitchen · 洽詢外燴」
  - C-2：主標「這樣的畫面，可以是你的婚禮」/ CTA「@maplabkitchen · 南台灣外燴」
  - C-3：主標「派對美學，從餐桌開始」/ CTA「了解更多 · maplabkitchen.com」

**目前困難：**
1. Meta 廣告操作限制：Meta 廣告管理員的操作（填寫、發佈廣告）需使用者明確確認才能執行，Claude 不能自行 acting，只能輔助規劃與填寫建議。
2. Canva 素材尚未加文字層：Canva 設計中已放置背景圖，但文字層（C-1/C-2/C-3）尚未完成，仍需繼續製作。
3. IG 圖片取得問題：從 Instagram 擷取圖片時截圖包含 UI 介面（黑色頂底欄），已用 Canva Position 工具偏移解決，但非理想的乾淨素材。

**暫時解決方案：**
1. Meta 廣告設定：本文件留下完整設定條件與 TA 建議，供使用者確認後自行執行或再授權 Claude 逐步執行
2. Canva 素材：繼續完成文字層，三版本製作完成後供使用者預覽再上傳到 Meta
3. 圖片品質：建議用戶直接提供原始圖片，或找到 Google 雲端中 MAPLAB 原始活動照

---

## 版本紀錄

| 版本 | 日期 | 說明 | 執行者 |
|------|------|------|--------|
| v1.0 | 2026-03-11 | 初始版本（Notion 文件） | Human |
| v1.1 | 2026-03-13 | 策略一廣告組合審查 + GTM Pixel 串接確認 | Claude (Sonnet 4.6) |
| v1.2 | 2026-03-13 | B 類整合（Gemini 分工）+ 相關連結補充 | Claude (Sonnet 4.6) |
| v1.3 | 2026-03-16 | 策略一冷受眾受眾描述填寫進度 + Canva C款素材 WIP | Claude (Sonnet 4.6) |
| v1.4 | 2026-03-16 | 補充現有策略觀察 + 完整 TA 建議 + 困難與解法 | Claude (Sonnet 4.6) |

---

## 相關連結

- Notion 廣告策略主文件：MAPLAB 廣告投放策略 TA 與預算紀錄 v1.0
- Notion 三策略補充計畫：MAPLAB Meta 廣告三策略補充計畫 v1.0
- Meta 事件管理工具：https://eventsmanager.facebook.com/events_manager2/list/dataset/228166994905799/
- GTM 容器：https://tagmanager.google.com/#/container/accounts/6000782046/containers/30897681
- Canva 設計（C款 WIP）：https://www.canva.com/design/DAHD4wpehE4/bRsNDBSCLqJz7bB9SGmNPw/edit

---

## B 類整合 — Gemini 分工與支線任務

> 更新：2026-03-13 | 以下任務原本是「無技術文件的支線任務」，現整合到本文件統一管理。

### B1 — Gemini 廣告數據分析

**執行者：Gemini**（Google 生態系原生整合優勢）

| 任務 | 說明 | 工具 |
|------|------|------|
| Google Ads API 數據抓取 | 定期抓取廣告成效數據 | ads_agent.py（maplab-Detasys）|
| Google Sheets 廣告儀表板 | 建立廣告數據可視化表格 | Google Sheets + Gemini |
| 廣告優化建議 | 分析 CTR / CPC / ROAS，給出調整建議 | Gemini 分析 |

**當前狀態：** 待開始（前置：OAuth 修復完成後）

### B2 — Gemini SEO 關鍵字收集

**執行者：Gemini**（Search Console API 整合）

**當前狀態：** 待開始
