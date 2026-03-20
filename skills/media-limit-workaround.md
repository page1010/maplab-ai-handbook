# media-limit-workaround.md — AI 工具媒體數量上限解決方案

**版本：v1.0 | 建立：2026-03-17 | 維護：A2 SEO Content Agent（Claude Opus 4.6）**

---

## 何時用

當 AI 工具（Claude Browser / ChatGPT 等）讀取包含大量圖片的網頁時出現錯誤：
`Too much media: 0 document pages + 101 images > 100`

此錯誤表示頁面圖片數超過 AI 工具的媒體處理上限（通常為 100 張）。

---

## 解決方案（優先順序）

### 策略 1：用 `get_page_text` 取代截圖（推薦）
- 用純文字工具讀取頁面，完全避開圖片計數
- - 適用場景：只需要讀文字內容，不需要看視覺排版
 
  - ### 策略 2：用 `read_page` + `ref_id` 聚焦區塊
  - - 只讀取特定 DOM 區塊，減少被計入的圖片數
    - - 適用場景：只需要頁面某個段落或表格
     
      - ### 策略 3：分段截圖
      - - 將長頁面拆成多次 scroll + screenshot
        - - 每次只擷取一小段，不超過上限
         
          - ### 策略 4：用 `zoom` 擷取特定區域
          - - 指定一個小區域截圖
            - - 適用場景：只需要看某個特定元素
             
              - ### 策略 5：用 JavaScript 移除非關鍵圖片
              - ```javascript
                document.querySelectorAll('img:not(.critical)').forEach(img => img.remove());
                ```
                - 移除不需要的圖片後再截圖
                - - 適用場景：必須截圖但頁面圖片太多
                 
                  - ---

                  ## MAPLAB 常見場景

                  | 場景 | 建議策略 |
                  |------|---------|
                  | 讀取 MAPLAB 首頁（客戶 logo 牆很多圖片）| 策略 1 或 2 |
                  | 檢查 SEO 文章頁內容 | 策略 1 |
                  | 確認 LINE 按鈕 HTML 結構 | 策略 2（聚焦 footer 或 CTA 區塊）|
                  | 查看 Meta 廣告管理員儀表板 | 策略 3（分段截圖）|
                  | 確認 GTM 標籤設定 | 策略 1 或 4 |

                  ---

                  ## 版本紀錄

                  | 版本 | 日期 | 說明 | 建立者 |
                  |------|------|------|--------|
                  | v1.0 | 2026-03-17 | 初始版本 | A2 Claude Opus 4.6 |
