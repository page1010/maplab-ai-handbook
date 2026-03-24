# media-limit-workaround.md — AI 工具媒體數量上限解決方案

版本：v2.0 | 建立：2026-03-17 | 更新：2026-03-24 | 維護：A2

## 何時用

當 AI 工具（Claude Browser / ChatGPT 等）讀取包含大量圖片的網頁時出現錯誤：

```
Too much media: 0 document pages + 101 images > 100
```

此錯誤表示頁面圖片數超過 AI 工具的媒體處理上限（通常為 100 張）。

## 根本原因

AI 瀏覽器工具對單一頁面的媒體數有硬性限制（約 100 張圖片）。觸發場景：

- Google Drive / Google 相簿的圖片資料夾（縮圖大量載入）
- WordPress 媒體庫列表頁
- 電商商品列表頁（大量產品圖）
- 社群媒體 feed
- 含大量 icon / avatar / 裝飾圖的頁面

## 基本解決方案（5 策略）

### 策略 1：用 get_page_text 取代截圖（推薦）

用純文字工具讀取頁面，完全避開圖片計數。

### 策略 2：用 read_page + ref_id 聚焦區塊

只讀取特定 DOM 區塊，減少被計入的圖片數。

### 策略 3：JavaScript 預先移除多餘圖片

```javascript
// 方法 A：移除所有非關鍵圖片
document.querySelectorAll('img:not(.critical)').forEach(img => img.remove());

// 方法 B：只保留前 N 張圖片
const imgs = document.querySelectorAll('img');
imgs.forEach((img, i) => { if (i >= 80) img.remove(); });

// 方法 C：移除特定區域的圖片
document.querySelectorAll('.sidebar img, footer img').forEach(img => img.remove());
```

### 策略 4：分段截圖

將長頁面拆成多次 scroll + screenshot，每次只擷取一小段。

### 策略 5：用 zoom 擷取特定區域

指定一個小區域截圖，只看特定元素。

---

## Google Drive 相簿專用方案（v2.0 新增）

### 問題場景

瀏覽 Google Drive 圖片資料夾（如 2025 年的相片）時，Grid View 一次載入大量縮圖，輕易超過 100 張限制。

### 策略 A：JavaScript 移除多餘縮圖後截圖

```javascript
// 保留前 50 個縮圖，移除其餘的
const thumbnails = document.querySelectorAll('[data-id] img');
thumbnails.forEach((img, i) => { if (i >= 50) img.remove(); });
```

### 策略 B：切換 List View

```javascript
// 切換到列表檢視（不顯示縮圖，圖片數大幅減少）
document.querySelector('[aria-label="清單檢視"], [aria-label="List view"]')?.click();
```

### 策略 C：用 JavaScript 直接取得檔案清單（不需截圖）

```javascript
// 從 DOM 讀取所有檔案的 ID 和名稱
const items = document.querySelectorAll('[data-id]');
const files = [];
items.forEach(el => {
  const id = el.getAttribute('data-id');
  const name = el.querySelector('[data-tooltip]')?.getAttribute('data-tooltip');
  if (id && id.length > 10 && name) files.push({ id, name });
});
JSON.stringify(files);
```

取得 ID 後直接用 drive.google.com/file/d/{ID}/view 開啟單張預覽（單張不超限）。

### 策略 D：分頁瀏覽 + 逐步捲動

1. 開啟資料夾後不要一次捲到底
2. 每次只看可見範圍內的圖片（12-20 張）
3. 用 zoom 工具放大特定區域檢查
4. 確認目標後用 file ID 開啟單張預覽頁

### 策略 E：搜尋篩選減少結果數

用日期或類型篩選限縮結果數量到 100 以內。

### 策略 F：用 read_page 取代 screenshot

read_page 工具不計算圖片數，可安全使用。搭配 filter:"interactive" 或 depth:3 減少輸出。

---

## Google Drive 選圖工作流程

結合 gdrive-to-wordpress-upload-guide.md 使用：

1. 先用 read_page 或 JavaScript 取得檔案 ID 清單（不截圖）
2. 逐張開啟 /file/d/{ID}/view 頁面（單張不超限）
3. 截圖確認照片內容是否適合
4. 執行上傳流程

---

## MAPLAB 常見場景

| 場景 | 建議策略 |
|------|---------|
| MAPLAB 首頁（logo 牆圖片多） | 策略 1 或 2 |
| SEO 文章頁內容 | 策略 1 |
| LINE 按鈕 HTML 結構 | 策略 2（聚焦 CTA 區塊） |
| Meta 廣告管理員儀表板 | 策略 4（分段截圖） |
| GTM 標籤設定 | 策略 1 或 5 |
| Google Drive 相簿挑選照片 | 策略 C + D（JS 取 ID 再單張預覽） |
| WordPress 媒體庫列表 | 策略 3（移除多餘縮圖）或策略 1 |
| Google 相簿大量瀏覽 | 策略 E（搜尋篩選）+ 策略 D |

## 預防措施

進入可能有大量圖片的頁面前，先問：

1. 我需要「看」圖片嗎？→ 不需要就用 get_page_text 或 read_page
2. 我需要看「所有」圖片嗎？→ 不需要就用 JS 先移除多餘的
3. 能不能一次只看一部分？→ 能就分段截圖或 zoom

### 自動防護腳本

```javascript
// 進入頁面後立即執行，將圖片數限制在 80 張以內
const MAX_IMAGES = 80;
const observer = new MutationObserver(() => {
  const imgs = document.querySelectorAll('img');
  if (imgs.length > MAX_IMAGES) {
    imgs.forEach((img, i) => { if (i >= MAX_IMAGES) img.remove(); });
  }
});
observer.observe(document.body, { childList: true, subtree: true });
```

## 版本紀錄

| 版本 | 日期 | 說明 | 建立者 |
|------|------|------|--------|
| v1.0 | 2026-03-17 | 初始版本 | A2 |
| v2.0 | 2026-03-24 | 大幅擴充：Google Drive 相簿專用 6 策略 + 工作流程 + 預防措施 + 自動防護腳本 | A2 |
