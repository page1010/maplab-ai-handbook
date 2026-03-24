# Google Drive → WordPress 雲端圖片上傳技能書

版本：v1.0 | 建立：2026-03-24 | 更新者：A2

## 概要

本技能書記錄如何在不經過使用者手動下載/上傳的情況下，將 Google Drive 的圖片直接傳送至 WordPress 媒體庫。流程完全在瀏覽器端完成，無需任何額外外掛或伺服器端工具。

## 適用場景

- 從 Google Drive 相簿挑選照片上傳至 WordPress 文章
- 批次為文章設定精選圖片
- SEO 圖片優化（alt text + 檔名關鍵字）

## 前置條件

1. 瀏覽器已登入 Google Drive（有相片存取權限）
2. 瀏覽器已登入 WordPress 後台（具有上傳媒體權限）
3. WordPress REST API 可用（`wpApiSettings.nonce` 存在）
4. 兩個 tab 同時開啟：Google Drive 相片預覽 + WordPress 後台

## 核心流程（5 步驟）

### Step 1：在 Google Drive Tab 開啟目標圖片預覽

在 Google Drive 資料夾中點擊目標圖片，開啟預覽頁面。確認圖片內容符合需求（無兒童臉部、無他牌 logo）。

### Step 2：擷取 Google Drive 預覽圖片的 Blob

在 Google Drive 預覽頁 tab 執行以下 JavaScript：

```javascript
// 取得頁面上的預覽圖片（drive-viewer 格式）
(async () => {
  const img = document.querySelector('img[src*="drive-viewer"]');
  if (!img) throw new Error('找不到預覽圖片元素');
  
  const resp = await fetch(img.src, { credentials: 'include' });
  if (!resp.ok) throw new Error('圖片擷取失敗: ' + resp.status);
  
  window._imageBlob = await resp.blob();
  console.log('Blob ready:', window._imageBlob.size, 'bytes,', window._imageBlob.type);
})();
```

**重要**：此步驟利用同源（same-origin）cookie 存取 Google Drive viewer 產生的圖片 URL。

### Step 3：透過 Clipboard API 跨 Tab 傳送圖片

在 Google Drive 預覽頁 tab 執行（需先確保文件有焦點）：

```javascript
(async () => {
  const blob = window._imageBlob;
  const imgUrl = URL.createObjectURL(blob);
  const img = new Image();
  
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
    img.src = imgUrl;
  });
  
  // 繪製到 Canvas 並轉為 PNG（Clipboard API 要求 PNG 格式）
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  canvas.getContext('2d').drawImage(img, 0, 0);
  
  const pngBlob = await new Promise(r => canvas.toBlob(r, 'image/png'));
  await navigator.clipboard.write([
    new ClipboardItem({ 'image/png': pngBlob })
  ]);
  
  URL.revokeObjectURL(imgUrl);
  console.log('圖片已複製到剪貼簿:', pngBlob.size, 'bytes');
})();
```

**注意**：執行前需先點擊頁面確保 document focused，否則 Clipboard API 會拒絕存取。

### Step 4：在 WordPress Tab 讀取剪貼簿並上傳至 REST API

切換到 WordPress 後台 tab，確保頁面有焦點後執行：

```javascript
(async () => {
  // 從剪貼簿讀取圖片
  const clipboardItems = await navigator.clipboard.read();
  let imageBlob = null;
  
  for (const item of clipboardItems) {
    for (const type of item.types) {
      if (type.startsWith('image/')) {
        imageBlob = await item.getType(type);
        break;
      }
    }
    if (imageBlob) break;
  }
  
  if (!imageBlob) throw new Error('剪貼簿中無圖片');
  
  // 準備上傳
  const formData = new FormData();
  formData.append('file', new File([imageBlob], 'your-seo-filename.png', { type: imageBlob.type }));
  formData.append('title', '中文 SEO 標題');
  formData.append('alt_text', '含關鍵字的替代文字描述');
  formData.append('caption', '圖片說明');
  
  // 上傳至 WordPress REST API
  const resp = await fetch('/wp-json/wp/v2/media', {
    method: 'POST',
    headers: { 'X-WP-Nonce': wpApiSettings.nonce },
    credentials: 'include',
    body: formData
  });
  
  const data = await resp.json();
  console.log('上傳成功! ID:', data.id, 'URL:', data.source_url);
})();
```

### Step 5：設定為文章精選圖片（可選）

```javascript
(async () => {
  const postId = 123; // 目標文章 ID
  const mediaId = 456; // 上一步取得的媒體 ID
  
  await fetch(`/wp-json/wp/v2/posts/${postId}`, {
    method: 'POST',
    headers: {
      'X-WP-Nonce': wpApiSettings.nonce,
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({ featured_media: mediaId })
  });
  
  console.log('精選圖片已設定');
})();
```

## SEO 命名規範

### 檔名格式
`maplab-{場景關鍵字}-{內容描述}.png`

範例：
- `maplab-wedding-catering-buffet-setup.png`（婚禮外燴）
- `maplab-birthday-party-dessert-table.png`（生日派對）
- `maplab-corporate-event-tea-party.png`（企業茶會）

### Alt Text 格式
`MAPLAB Kitchen {場景}｜{具體描述，含長尾關鍵字}`

範例：
- `MAPLAB Kitchen 外燴自助餐派對佈置｜精緻餐點擺盤與木質層架展示`
- `MAPLAB Kitchen 婚禮甜點桌｜客製化翻糖蛋糕與馬卡龍塔佈置`
- `MAPLAB Kitchen 企業茶會外燴｜商務活動精緻手作點心`

## 圖片選擇規範

1. **禁止**：兒童臉部（無法霧化處理，直接跳過）
2. **禁止**：他牌 logo（如 MUC COFFEE 等，需確認後才使用）
3. **優先**：食物近拍、佈置全景、無人場景
4. **一篇一圖**：每篇文章一張精選圖片 + 一張縮圖即可
5. **內容匹配**：婚禮文→婚宴場景、生日文→派對佈置、企業文→商務活動、菜單文→食物特寫

## 注意事項與限制

### 圖片品質
- Google Drive viewer 預覽最大寬度為 1600px
- 圖片經由 Canvas→PNG 轉換，再由 Imagify 自動轉為 WebP/AVIF
- 最終品質適合網頁使用，但非原始解析度

### 技術限制
- **Clipboard API 需要 document focus**：執行前必須先點擊頁面
- **跨域限制**：無法直接從 Google Drive fetch 到 WordPress（CORS）
- **Nonce 有效期**：WordPress REST API nonce 有時效性，過期需重新整理頁面

### 失敗的方法（踩坑紀錄）
1. WordPress tab → fetch Google Drive URL → CORS 阻擋
2. Google Drive tab → fetch 下載 URL → Failed to fetch
3. upload_image tool → WordPress plupload 不觸發
4. upload_image drag-drop → WordPress plupload 不觸發  
5. Google Drive tab → POST to WordPress async-upload.php → 跨域阻擋
6. img crossOrigin='anonymous' → Google Drive 圖片需驗證，載入失敗

### 成功的方法
Google Drive viewer fetch（同源）→ Canvas → PNG Blob → Clipboard API → WordPress tab 讀取 → REST API upload

## 批次作業流程

對需要精選圖片的文章逐篇處理：

1. 查詢缺少精選圖片的文章列表
2. 根據文章主題到 Google Drive 2025 相簿挑選匹配照片
3. 執行 Step 1-4 上傳並設定 alt text
4. 執行 Step 5 設定為精選圖片
5. 記錄到 seo-ads-agent.md

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-24 | 初版建立：完整流程 + 踩坑紀錄 + SEO 規範 | A2 |
