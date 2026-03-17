# gtm-conversion-setup.md — MAPLAB GTM 轉換事件設定 SOP

**版本：v1.0 | 建立：2026-03-17 | 維護：A3 Ads Monitor Agent（Claude Sonnet 4.6）**

> 本文件由 A3 全權負責維護。設定完成後請更新「執行狀態」欄位並推送至 main。
> 執行者：使用者或具備 GTM 操作權限的任何 Agent / 工程師。

---

## 為什麼需要設定轉換事件

目前 Google PMax 過去 30 天顯示 **7 次轉換，CPA NT$322**，但轉換事件的定義不明確：

- 不確定這 7 次是「LINE 點擊」、「表單送出」，還是 GTM/GA4 自動偵測的替代事件（如捲動深度、頁面停留）
- 若是替代事件被誤算，PMax 的出價策略正在對錯誤目標優化
- Meta Pixel 目前 28 天有 840 個事件，但沒有設定自訂轉換，無法追蹤真正的詢問行為

**設定正確轉換事件後：**

- PMax 機器學習對正確目標優化（點擊 LINE / 送出詢問）
- Meta 廣告可以依轉換優化出價，CPA 有機會從目前 NT$322 降至 NT$150–200
- 未來可做再行銷（轉換過的人、未轉換但點過的人）

---

## 帳號資訊

| 項目 | 值 |
|------|-----|
| GTM 容器 ID | GTM-T2Z52GP |
| GTM 帳號 | accounts/6000782046/containers/30897681 |
| GTM 網址 | https://tagmanager.google.com/#/container/accounts/6000782046/containers/30897681 |
| Meta Pixel ID | 228166994905799 |
| Meta 事件管理工具 | https://eventsmanager.facebook.com/events_manager2/list/dataset/228166994905799/ |
| Google Ads 帳號 | 844-336-3178 |
| 網站 | www.maplabkitchen.com |

---

## 要設定的三個轉換事件

| 優先順序 | 事件名稱 | 對應行為 | 重要性 |
|---------|---------|---------|--------|
| ① 最高 | LINE 點擊 | 用戶點擊 LINE 按鈕或 line.me 連結 | 主要詢問管道 |
| ② 高 | 表單送出 | 用戶送出詢問表單 | 次要詢問管道 |
| ③ 中 | 電話點擊 | 用戶點擊電話號碼（行動裝置）| 補充追蹤 |

---

## 前置確認：處理重複 Pixel

進入 GTM 前，先確認目前已知的兩個 FB 標籤：

- 標籤 1：Facebook Pixel ID 228166994905799
- 標籤 2：FBpixel（名稱）

**必須確認這兩個標籤是否重複觸發，若是，刪除其中一個，只保留 Pixel ID 正確的那個。**

確認步驟：

1. 進入 GTM → 標籤
2. 找到所有包含「Facebook」或「fbq」的標籤
3. 點開每個標籤，確認 Pixel ID 是否都是 228166994905799
4. 若有一個 ID 不同或是舊的 Pixel，停用該標籤
5. 若兩個 ID 相同，只保留一個，停用另一個

---

## 事件 ① LINE 點擊追蹤

### GTM 觸發條件

- 觸發條件類型：點擊 — 僅連結
- 觸發條件名稱：`Trigger - LINE Click`
- 觸發時機：部分點擊
- 條件：`Click URL` 包含 `line.me` 或 `lin.ee`

### Meta Pixel 標籤

- 標籤類型：自訂 HTML
- 標籤名稱：`Meta - LINE Click Event`
- HTML 內容：

```html
<script>
  fbq('track', 'Contact', {content_name: 'LINE Click'});
</script>
```

- 觸發條件：`Trigger - LINE Click`

### Google Ads 轉換標籤

- 標籤類型：Google Ads 轉換追蹤
- 標籤名稱：`GA - LINE Click Conversion`
- 轉換 ID 和標籤：從 Google Ads 後台建立後複製（見「Google Ads 轉換動作建立」章節）
- 觸發條件：`Trigger - LINE Click`

---

## 事件 ② 表單送出追蹤

### GTM 觸發條件

- 觸發條件類型：表單送出
- 觸發條件名稱：`Trigger - Form Submit`
- 觸發時機：部分表單
- 條件：`Page URL` 包含 `maplabkitchen.com`
- ⚠️ 勾選「等待標籤」和「確認表單有效性」

### Meta Pixel 標籤

- 標籤類型：自訂 HTML
- 標籤名稱：`Meta - Form Submit Event`
- HTML 內容：

```html
<script>
  fbq('track', 'Lead', {content_name: 'Form Submit'});
</script>
```

- 觸發條件：`Trigger - Form Submit`

### Google Ads 轉換標籤

- 標籤類型：Google Ads 轉換追蹤
- 標籤名稱：`GA - Form Submit Conversion`
- 觸發條件：`Trigger - Form Submit`

---

## 事件 ③ 電話點擊追蹤

### GTM 觸發條件

- 觸發條件類型：點擊 — 僅連結
- 觸發條件名稱：`Trigger - Phone Click`
- 觸發時機：部分點擊
- 條件：`Click URL` 包含 `tel:`

### Meta Pixel 標籤

- 標籤類型：自訂 HTML
- 標籤名稱：`Meta - Phone Click Event`
- HTML 內容：

```html
<script>
  fbq('track', 'Contact', {content_name: 'Phone Click'});
</script>
```

- 觸發條件：`Trigger - Phone Click`

### Google Ads 轉換標籤

- 標籤類型：Google Ads 轉換追蹤
- 標籤名稱：`GA - Phone Click Conversion`
- 觸發條件：`Trigger - Phone Click`

---

## Google Ads 後台：建立轉換動作

在 GTM 設定 Google Ads 標籤前，需要先在 Google Ads 建立轉換動作，取得轉換 ID 和標籤。

1. 進入 Google Ads → 目標 → 轉換
2. 點擊「+ 新增轉換動作」
3. 類別：網站
4. 建立三個轉換動作：

| 轉換動作名稱 | 類別 | 計算方式 |
|------------|------|---------|
| LINE詢問點擊 | 聯絡 | 每次 |
| 表單送出詢問 | 提交潛在客戶表單 | 每次 |
| 電話點擊 | 電話通話 | 每次 |

5. 建立後，每個轉換動作會產生一組「轉換 ID」和「轉換標籤」
6. 將這組 ID 填入對應的 GTM 標籤

---

## GTM 發布

設定完三個事件後：

1. 點擊 GTM 右上角「提交」
2. 版本名稱填入：`轉換事件設定 — LINE / 表單 / 電話`
3. 點擊「發布」
4. 使用 GTM 預覽模式 + Meta Pixel Helper 驗證事件觸發

---

## 驗證方法

### Meta Pixel Helper（Chrome 擴充套件）

1. 安裝 Meta Pixel Helper
2. 前往 maplabkitchen.com 點擊 LINE 按鈕
3. 檢查是否觸發 `Contact` 事件，content_name = "LINE Click"
4. 若沒有觸發，回到 GTM 確認觸發條件設定

### Google Ads 轉換驗證

1. Google Ads → 目標 → 轉換
2. 確認「最近的轉換」有記錄
3. 等待 24–48 小時後確認完整資料

### Meta 事件管理工具

1. 進入事件管理工具
2. 確認 Contact 和 Lead 事件出現在清單中
3. 確認事件是否有測試記錄

---

## 設定完成後的追蹤指標

| 指標 | 確認位置 | 目標 |
|------|---------|------|
| LINE 點擊次數（月）| Google Ads 轉換 | 建立基準後追蹤 |
| 表單送出次數（月）| Google Ads 轉換 | 建立基準後追蹤 |
| Meta Lead 事件數 | Meta 事件管理工具 | 建立基準後追蹤 |
| PMax CPA | Google Ads | 目標從 NT$322 降至 NT$200 以下 |

---

## 執行狀態

| 事件 | GTM 觸發條件 | GTM Meta 標籤 | GTM Google 標籤 | GA 轉換動作 | 已驗證 |
|------|------------|-------------|---------------|-----------|--------|
| LINE 點擊 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未建立 | ⬜ |
| 表單送出 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未建立 | ⬜ |
| 電話點擊 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未設定 | ⬜ 未建立 | ⬜ |
| 重複 Pixel 確認 | ⬜ 未確認 | — | — | — | ⬜ |

> 執行者完成後，請將 ⬜ 改為 ✅ 並 commit 到 main。

---

## 給其他 Agent 的備註

### A2 SEO Agent
轉換事件設定完成後，你的 landing page 需要包含 LINE 按鈕和詢問表單，GTM 才能追蹤到轉換。請確認以下頁面都有：
- LINE 連結（line.me 或 lin.ee 格式）
- 詢問表單（嵌入式或跳轉頁）

### A4 Pipeline Agent / A5 Data Agent
轉換事件觸發後的資料會出現在：
- Google Ads 轉換報表
- Meta 事件管理工具
- GA4（若有連結 GTM）

請注意事件命名規則：Meta 用 Contact / Lead，Google 用自訂名稱（LINE詢問點擊 / 表單送出詢問 / 電話點擊）。

---

## 版本紀錄

| 版本 | 日期 | 說明 | 執行者 |
|------|------|------|--------|
| v1.0 | 2026-03-17 | 初始版本：三個轉換事件完整 SOP + 驗證方法 + Agent 備註 | A3 Claude Sonnet 4.6 |
