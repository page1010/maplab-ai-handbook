# Skill: slide-production-rules — Slide 提案簡報產出規範

## 觸發條件
任何產出 Google Slides 提案簡報的任務

## 規範（所有 Slide 產出必須遵守）

### 圖片處理
- 圖片必須先裁切成固定比例（寬高比 210:110 或約 1.9:1），再插入 Slide
- 不可以用 fit/stretch 讓圖片變形填滿框框
- 用 weserv.nl proxy 裁切：`?url=...&w=800&h=420&fit=cover&output=jpg&q=80`
- 裁切焦點應該在菜品上（cover 模式會自動 center crop）
- Drive 圖片的來源 URL：`https://drive.google.com/uc?export=download&id=FILE_ID`
- weserv.nl 失敗時，DriveApp.getBlob() 作為備援（但原圖可能比例不對）

### 空白格處理
- Menu Showcase 頁面品項不滿 6 格時，空的格子直接不建立
- 不要留空白框、placeholder 文字（如 [photo]）、或空白佔位
- 提案 proposal 是正式文件，空白不專業

### 頁面順序
- 固定頁面（封面、服務、作品、優勢、合作夥伴、Logo 牆）在前
- 動態頁面（Menu Showcase）在中間
- Quotation 報價頁在 Menu 之後
- Terms & Conditions 在 Quotation 之後
- Ready to Create 結尾頁永遠在最後

### 結尾頁處理方式
- 刪除模板動態頁時，先找到 Ready to Create 頁（搜尋文字含 'Ready' + 'Create'）
- 刪除其他動態頁時跳過它，保留引用
- 所有動態頁新增完畢後，呼叫 `readyToCreateSlide.move(pres.getSlides().length - 1)` 移至最後

### 無圖品項
- 沒有 image_url 的品項：只放品名文字，不放任何圖片相關元素
- 不要顯示 [photo]、[Photo]、placeholder、或空白圖框
- 品名標籤位置：無圖時垂直置中於格子（iy + 50），有圖時在圖下方（iy + 114）

### 踩坑紀錄
- 2026-04-04：第一版產出圖片被拉伸、空白格留白、結尾頁順序錯、[photo] 文字殘留
- 根因：
  1. 圖片插入前沒有透過 weserv.nl 裁切成正確比例
  2. [photo] 佔位符在圖片載入失敗時沒有被移除
  3. 刪頁邏輯沒有考慮結尾頁位置，導致結尾頁消失或順序錯誤
  4. Drive 圖片直接用 getBlob() 取得原圖，比例不一定符合框框
