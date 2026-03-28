# Slides Quotation System — MAPLAB Kitchen 簡報報價系統規劃
版本：v0.5 | 建立：2026-03-19 | 更新：2026-03-20 | 負責：跨專案業務協調（A4 Pipeline + A5 Master Data + Slides）
狀態：Phase 1 ✅ | Phase 2 ✅ | Phase 3 等待 A4 相片分類

---
## SECTION 0 — 專案目標與角色定位

### 目標
建立一套「從 Pipeline 照片 → Items 品項資料 → Google Slides 簡報」的自動化報價簡報系統。  
讓業務在 Google Sheets 選擇品項後，能一鍵生成包含對應產品照片的精美客戶簡報。

### 角色定位
本專案由**跨專案業務協調者**主導，橫跨：
- **A4 Pipeline Agent**：提供照片素材（Google Photos → Drive → 分類歸檔）
- **A5 Master Data Agent**：提供品項資料（Items sheet + ASSET_MASTER 圖片索引）
- **Gemini（Sheets 內建）**：協作生成 Slides 模板 + GAS 腳本

### 不在本次範圍
- 報價單串接（QUOTE_DRAFT ↔ Slides 動態品項替換）→ 待 T-A5-002 完成後再啟動
- 逆向報價模式 → 依賴 QUOTE_DRAFT 增強
- PDF 自動匯出 → 等模板定稿後實作

---

## SECTION 1 — 設計邏輯參考（管顧公司 + Landing Page 思維）

### 1.1 簡報設計原則（參考 McKinsey / Bain 風格）

| 原則 | 說明 | MAPLAB 應用 |
|------|------|-------------|
| **一頁一訊息** | 每頁只傳達一個核心概念 | 每頁固定用途，不混雜 |
| **金字塔結構** | 結論先行，細節後補 | 封面直接破題→再展開細節 |
| **視覺優先** | 用圖片說話，文字精簡 | 外燴照片是最強武器 |
| **CTA 明確** | 每份簡報都有行動呼籲 | 結尾 LINE 諮詢 + 聯絡資訊 |
| **信任堆疊** | 社會證明→專業背書→風險降低 | 數據→案例→FAQ→保證 |

### 1.2 Landing Page 轉換邏輯套用

外燴簡報本質上就是一份「離線 Landing Page」，遵循相同的說服路徑：

```
Hero（封面）→ Pain Point（客戶的需求）→ Solution（我們的服務）
→ Social Proof（案例/數據）→ Why Us（差異化）→ CTA（行動）
```

對應到 MAPLAB 簡報結構：

```
封面（品牌視覺衝擊）
  → 我們是誰（品牌簡介 + 信任數據）
    → 為您做什麼（服務範圍 + 活動類型）
      → 過往實績（案例照片 + 客戶見證）
        → 為什麼選我們（5 大優勢）
          → [動態] 本次推薦品項（從 Sheet 串接）
            → 服務流程（5 步驟）
              → 結尾 CTA（LINE / 電話 / Email）
              ```

              ---

              ## SECTION 2 — Slides 模板結構設計

              ### 2.1 整體頁面架構

              | 頁序 | 頁面名稱 | 類型 | 內容來源 | Alt Text 標記 |
              |------|----------|------|----------|---------------|
              | 1 | 封面 Cover | 🔒 固定 | 品牌素材 | `CoverImage` |
              | 2 | 品牌介紹 About Us | 🔒 固定 | 官網/IG 內容 | `AboutImage` |
              | 3 | 服務項目 Services | 🔒 固定 | 官網服務頁 | `ServiceImage1` `ServiceImage2` |
              | 4 | 過往實績 Portfolio | 🔒 固定 | IG 案例精選 | `PortfolioImage1-4` |
              | 5 | 為什麼選我們 Why Us | 🔒 固定 | 官網優勢區 | — |
              | 6 | 服務流程 Process | 🔒 固定 | 官網流程區 | — |
              | 7-N | 推薦品項 Items | 🔄 動態 | Sheet Items + Drive 照片 | `ItemImage_{{item_id}}` |
              | N+1 | 結尾 CTA | 🔒 固定 | LINE QR + 聯絡資訊 | `CTAImage` |

              ### 2.2 各固定頁詳細內容規劃

              #### 頁 1：封面 Cover
              - **主標題**：MAPLAB Kitchen | CATERING SERVICE
              - **副標題**：以「美感 × 節奏」打造專屬外燴體驗
              - **背景**：全版外燴場景照（精選最具視覺衝擊力的一張）
              - **底部資訊**：SINCE 2016 | 台南
              - **設計風格**：深色覆蓋層 + 白字，大器專業

              #### 頁 2：品牌介紹 About Us
              - **標題**：關於 MAPLAB Kitchen
              - **核心文案**：
                - 深耕台南，2016 年成立
                  - 外燴設計顧問，不只是餐點供應商
                    - 西式派對 / 品牌活動 / 婚禮茶會
                      - 以「美感 × 節奏」打造專屬外燴體驗
                      - **信任數據列**：
                        - 200+ 場活動經驗
                          - 50+ 企業客戶
                            - 98% 客戶滿意度
                              - 10 年深耕台南
                              - **配圖**：團隊工作照或精選場佈照

                              #### 頁 3：服務項目 Services
                              - **標題**：我們的服務範圍
                              - **三欄式排版**：
                                - 🎂 週歲/彌月派對 — 甜點桌、主題佈置、現場服務一次到位
                                  - 💒 浪漫婚禮外燴 — Candy Bar、帳篷晚宴、證婚派對
                                    - 🏢 企業品牌活動 — 發表會、記者會、尾牙、VIP 招待
                                    - **底部補充**：也承接生日派對、性別揭曉、品酒會、展覽茶會等

                                    #### 頁 4：過往實績 Portfolio
                                    - **標題**：精選案例
                                    - **四宮格排版**（對應 IG 精選案例）：
                                      - AMD 企業活動
                                        - Luca 的抓週派對
                                          - 誠品酒窖品酒會
                                            - 南科考古館西拉雅特展
                                            - **每格**：照片 + 活動名稱 + 類型標籤
                                            - **底部**：更多案例請見 Instagram @maplabkitchen

                                            #### 頁 5：為什麼選我們 Why Us
                                            - **標題**：為什麼選擇 MAPLAB Kitchen？
                                            - **五大優勢**（icon + 標題 + 一行說明）：
                                              - 🌿 在地深耕 — 熟悉台南文化脈絡與在地資源
                                                - 🎨 客製彈性 — 不提供僵化套餐，只提供最符合您需求的方案
                                                  - ✨ 美學呈現 — 將美感融入每一個細節
                                                    - 👨‍🍳 專業團隊 — 企劃、廚藝到現場服務，經驗豐富
                                                      - 🛡️ 食品安全 — 嚴格把關食材來源與製程

                                                      #### 頁 6：服務流程 Process
                                                      - **標題**：合作流程
                                                      - **五步驟橫向流程圖**：
                                                        1. 線上初步諮詢 → 2. 需求確認與精準報價 → 3. 菜單與主題客製化 → 4. 活動細節確認與合約 → 5. 現場專業執行
                                                        - **強調文字**：透明、簡單、安心

                                                        #### 頁 N+1：結尾 CTA
                                                        - **標題**：準備好打造您的專屬外燴體驗了嗎？
                                                        - **聯絡方式**：
                                                          - LINE 官方帳號 QR Code + @maplabkitchen
                                                            - 電話
                                                              - Email
                                                                - Instagram: @maplabkitchen
                                                                  - 官網: www.maplabkitchen.com
                                                                  - **地址**：台南市成德里合緯路二段 450 號

                                                                  ---

                                                                  ## SECTION 3 — 資料流架構（Pipeline → Items → Slides）

                                                                  ### 3.1 完整資料流

                                                                  ```
                                                                  [Google Photos] ──A4 Pipeline──→ [Google Drive MAPLAB_ASSETS]
                                                                                                          │
                                                                                                                                                  ▼
                                                                                                                                                                                   [ASSET_MASTER sheet]
                                                                                                                                                                                                                      asset_id → item_id → drive_file_id
                                                                                                                                                                                                                                                              │
                                                                                                                                                                                                                                                                                                      ▼
                                                                                                                                                                                                                                                                                                      [ITEM_MASTER sheet] ◄──────────── [Items sheet (v0.1)]
                                                                                                                                                                                                                                                                                                        item_id, item_name_zh,                │
                                                                                                                                                                                                                                                                                                          category, default_price               │
                                                                                                                                                                                                                                                                                                                                                  ▼
                                                                                                                                                                                                                                                                                                                                                                                [QUOTE_DRAFT / 品項選擇]
                                                                                                                                                                                                                                                                                                                                                                                                                        │
                                                                                                                                                                                                                                                                                                                                                                                                                                                                ▼
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              [Google Apps Script]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      │
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ▼
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            [Google Slides 模板]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             替換 {{佔位符}}
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              替換 圖片 (Alt Text)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      │
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ▼
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            [客戶報價簡報 PDF]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### 3.2 當前可用 vs 待建立
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 元件 | 狀態 | 說明 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |------|------|------|
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Items sheet (品項清單) | ✅ 已有 ~139 筆 | 甜點/鹹食/飲品，需去重完成 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | ITEM_MASTER (標準化主表) | 🔄 填入中 | A5 持續建檔 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | ASSET_MASTER (圖片索引) | 🔲 待建立 | 需 A4 Pipeline Phase 4 完成分類後建立 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Drive 照片庫 | 🔄 進行中 | A4 Phase 2/3 完成，Phase 4 待啟動 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Slides 模板 (固定頁) | 🔲 本次建立 | 由 Gemini 在 Sheets 側邊欄協助生成 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | GAS 腳本 (動態替換) | 🔲 待實作 | 等模板 + ASSET_MASTER 就緒 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### 3.3 圖片命名與 Alt Text 對應規則
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Slides 模板中的圖片佔位符使用 Alt Text 標記：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 固定頁圖片：`CoverImage`, `AboutImage`, `ServiceImage1` 等
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 動態品項圖片：`ItemImage_{{item_id}}` 例如 `ItemImage_DES-MAC-001`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            GAS 腳本邏輯：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1. 讀取 Sheet 選定品項的 item_id
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            2. 從 ASSET_MASTER 查詢對應 drive_file_id
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            3. 在 Slides 中找到對應 Alt Text 的形狀
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            4. 用 Drive 圖片 URL 替換該形狀
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ## SECTION 4 — Gemini 協作指令（Slides 模板生成）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### 4.1 第一階段：固定內容頁（本次實作）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            請 Gemini 在 Sheets 側邊欄執行以下任務：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            **Prompt 1 — 建立 Slides 模板骨架**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            請建立一份 Google Slides 簡報模板，用於 MAPLAB Kitchen 外燴報價使用。
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            簡報風格：專業、溫暖、以照片為主視覺。
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            配色：深灰 (#2C2C2C) + 暖白 (#F5F0EB) + 金色點綴 (#C9A96E)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            需要以下頁面：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1. 封面：MAPLAB Kitchen | CATERING SERVICE，副標「以美感×節奏打造專屬外燴體驗」，SINCE 2016
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            2. 關於我們：品牌介紹 + 4 個信任數據（200+場/50+企業/98%滿意/10年深耕）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            3. 服務項目：三欄（週歲派對/婚禮外燴/企業活動）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            4. 精選案例：四宮格照片區
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            5. 為什麼選我們：5 個優勢 icon 列表
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            6. 服務流程：5 步驟橫向流程圖
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            7. 品項展示頁（模板）：左圖右文，品名+說明+價格佔位符
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            8. 結尾 CTA：聯絡資訊 + LINE QR Code 區域
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            每頁圖片佔位符請設定 Alt Text 標記以便後續程式替換。
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### 4.2 第二階段：動態品項串接（暫不實作）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            待以下條件滿足後啟動：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - [ ] T-A5-001 Items 去重完成
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - [ ] T-A5-002 QUOTE_DRAFT 增強完成
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - [ ] ASSET_MASTER 建立且有圖片對應
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - [ ] A4 Phase 4 vision.py 完成照片分類
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ## SECTION 5 — 任務拆解與依賴
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Task ID | 任務 | 負責 | 前置條件 | 狀態 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |---------|------|------|----------|------|
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-001 | Slides 固定頁模板建立（透過 Gemini） | 業務協調 + Gemini | 無 | 🟢 本次執行 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-002 | 固定頁內容填入（文案+佈局微調） | 業務協調 | T-SLIDE-001 | 🟢 本次執行 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-003 | ASSET_MASTER sheet 建立 | A5 | A4 Phase 4 | 🔲 待開始 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-004 | GAS 腳本：文字替換 MVP | A5 / Gemini | T-SLIDE-001 | 🔲 待開始 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-005 | GAS 腳本：圖片替換 | A5 / Gemini | T-SLIDE-003 | 🔲 待開始 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-006 | QUOTE_DRAFT → Slides 全自動串接 | A5 | T-A5-002 + T-SLIDE-005 | 🔲 待開始 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | T-SLIDE-007 | PDF 自動匯出 + Drive 歸檔 | A5 | T-SLIDE-006 | 🔲 待開始 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ## SECTION 6 — 品牌素材來源整理
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### 官網 (maplabkitchen.com)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 首頁 Hero 大圖：外燴場景全景
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 信任數據：200+ / 50+ / 98% / 10年
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 服務說明：週歲、婚禮、企業三大類
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 5 大優勢：在地深耕/客製彈性/美學呈現/專業團隊/食品安全
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 5 步驟服務流程
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - FAQ 常見問題
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 客戶見證紀錄（連結 IG）
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### Instagram (@maplabkitchen)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 490 貼文 / 4919 粉絲
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 精選限動分類：慶生外燴、客人回饋、商務/會議外燴、特別節日餐敘、性別揭曉派對、婚禮外燴
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 代表性案例：AMD 企業活動、週歲派對（Luca/Yina）、誠品酒窖品酒會、南科考古館特展、科林研發茶會
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 品牌定位：西式派對 / 品牌活動 / 婚禮茶會
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ### Drive (MAPLAB_ASSETS)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 待 A4 Pipeline Phase 4 分類完成後，將有結構化的照片庫
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - 照片將按活動類型/日期歸檔，對應 ASSET_MASTER
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ## SECTION 7 — 版本紀錄
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 版本 | 日期 | 說明 | 更新者 |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |------|------|------|--------|
| v0.1 | 2026-03-19 | Slides structure + data flow + design logic + Gemini prompts | Claude |
| v0.2 | 2026-03-19 | User requirements update + template-based architecture + phased plan | Claude |

---

## SECTION 8 — User Requirements Update (v0.2)

### 8.1 User Requirements Summary

> Source: PM conversation confirmed (2026-03-19)

1. **Style Enhancement**: Reference premium PPT templates (color, font, whitespace, image ratio)
2. **Structure Changes**:
   - Page 6 (How It Works) -> **DELETE**, not needed
   - Page 7 (Menu Selection) -> **Showcase only**: item name + photo, NO price/qty/DESC for clients
3. **Template-Based Architecture**:
   - Current: each run creates a brand new deck -> user-added photos lost
   - Correct: maintain a **Master Template** (fixed pages with photos), button only copies template + inserts dynamic menu showcase pages
4. **Output Workflow**:
   - Export PDF for client -> does NOT affect original settings
   - Master Template never modified
   - Each client gets independent presentation file

### 8.2 Architecture: Template-Based

Master Template Slides (manually styled, never modified)
- P1: Cover (fixed + photo)
- P2: About Us (fixed + photo)
- P3: Services (fixed + photo)
- P4: Portfolio (fixed + photo)
- P5: Why Choose Us (fixed)
- P6: CTA Contact (fixed)

Button triggers GAS:
1. Copy Master Template
2. Read selected items from Sheet
3. Insert Menu Showcase pages between P5 and P6
4. Each item: name + photo (from Drive)
5. Output: client-specific presentation
6. Export PDF -> send to client
7. Master untouched

### 8.3 Updated Slides Page Structure

| Page | Name | Type | v0.1 Ref | Change |
|------|------|------|----------|--------|
| 1 | Cover | Fixed | P1 | No change |
| 2 | About Us | Fixed | P2 | Add photos manually |
| 3 | Services | Fixed | P3 | Add photos manually |
| 4 | Portfolio | Fixed | P4 | Add photos manually |
| 5 | Why Choose Us | Fixed | P5 | No change |
| 6~N | Menu Showcase | Dynamic | P7 revised | Name+photo only, NO price/qty/DESC |
| N+1 | CTA Contact | Fixed | P8->P6 | Moved to last |
| ~~X~~ | ~~Process~~ | ~~Deleted~~ | ~~P6~~ | ~~User confirmed not needed~~ |

### 8.4 Menu Showcase Page Specs

- **Per page**: 4-6 items (depends on layout)
- **Per item**: Item name (Chinese) + Photo
- **NOT shown**: Price, quantity, description (this is a showcase for clients, not a quote)
- **Photo source**: Drive MAPLAB_ASSETS (item_id -> drive_file_id via ASSET_MASTER)
- **Category logic**: Group by Items sheet category (Dessert/Savory/Beverage)

---

## SECTION 9 — Phased Work Plan

### Phase 1: Style Master Template ✅ DONE
- [x] Research premium PPT template styles (color, font, whitespace, image ratio)
- [x] Redesign existing Slides P1-P5 + CTA page (V2 created with premium design)
- [x] Delete P6 (Process) — removed in V2
- [x] Revise P7 to Menu Showcase template (name+photo only) — V2 P6
- [x] Manual beautification via beautifyV2() script
- [ ] User adds real photos to Master Template (user action)
- **Output**: One polished Master Template Slides

### Phase 2: Rewrite GAS to Template-Based ✅ DONE
- [x] New function generateClientProposal()
- [x] Logic: Copy Master -> Read selected items from Sheet -> Delete template menu page -> Insert dynamic menu showcase pages -> Return new Slides URL
- [x] Menu showcase inserts item names only (no photos yet, wait for ASSET_MASTER)
- [x] Test: Generated 28-page proposal (5 fixed + 22 dynamic menu + 1 CTA)
- [x] onOpen() menu: MAPLAB Slides -> Generate Client Proposal
- **Output**: generateProposal.gs — working one-click generation from Sheet menu bar

### Phase 3: Photo Integration
- [ ] Prerequisite: A4 Pipeline Phase 4 photo classification done
- [ ] Prerequisite: A5 builds ASSET_MASTER (item_id -> drive_file_id)
- [ ] GAS script adds photo insertion logic
- [ ] Test: Menu showcase pages auto-populate with photos
- **Output**: Menu showcase with name + photo

### Phase 4: Quote Integration (ON HOLD)
- [ ] Prerequisite: T-A5-002 QUOTE_DRAFT enhancement done
- [ ] QUOTE_DRAFT -> item selection -> trigger Slides generation
- [ ] PDF auto-export + Drive archiving
- **Output**: Complete automated quote-presentation workflow

### Dependency Map

Phase 1 -> Phase 2 -> Phase 4 (on hold)
Phase 2 -> Phase 3 -> Phase 4
Phase 3 depends on: A4 Phase 4 + A5 ASSET_MASTER

---

## SECTION 10 — Completed Items Log

| Item | Status | Date | Note |
|------|--------|------|------|
| v0.1 Planning Doc | Done | 2026-03-19 | This doc initial version with Slides structure + data flow + design logic |
| Slides v0.1 Skeleton | Done | 2026-03-19 | Generated 8-page deck via GAS createMAPLABSlides() |
| GAS createSlides.gs | Done | 2026-03-19 | Saved in MAPLAB_v0.1 Apps Script project |
| Slides File | Created | 2026-03-19 | "MAPLAB Kitchen - Catering Proposal" in Google Drive |
| v0.2 Requirements Update | Done | 2026-03-19 | Template-based architecture confirmed + phased plan |
| PPT Template Research | Done | 2026-03-20 | Studied Slidesgo Elegant Restaurant Business Proposal design patterns |
| GAS slidesV2.gs | Done | 2026-03-20 | createMAPLABSlidesV2() - 7pg premium design, no Process page |
| Slides V2 File | Created | 2026-03-20 | Catering Proposal v2 ID=1rRxwPK9Nsgb7oqoRiUOCFqu3iGNuw_zRKW3zeHbdHBY |
| V2 Design Verified | Done | 2026-03-20 | 7pg: Cover/About/Services/Portfolio/WhyUs/MenuShowcase/CTA |
| beautifyV2.gs | Done | 2026-03-20 | Font/color/line beautification applied to V2 slides |
| Phase 1 Complete | Done | 2026-03-20 | All checklist items done, V2 Master Template ready |
| Phase 2 Started | Done | 2026-03-20 | GAS template-based architecture rewrite |
| generateProposal.gs | Done | 2026-03-20 | Template-based generator: copy Master + insert dynamic menu pages |
| Phase 2 Test Run | Verified | 2026-03-20 | 28-page output: 5 fixed + 22 menu + 1 CTA, categories grouped correctly |
| onOpen() Menu | Done | 2026-03-20 | Sheet menu bar: MAPLAB Slides -> Generate Client Proposal |
| Phase 2 Complete | Done | 2026-03-20 | Template-based architecture working, Master never modified |
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | v0.2 | 2026-03-19 | User requirements + template-based architecture + phased plan | Claude Opus 4.6 |
| v0.3 | 2026-03-20 | V2 skeleton created + Phase 1 checklist updated | Claude Opus 4.6 |
| v0.4 | 2026-03-20 | Phase 1 complete + beautification + Phase 2 start | Claude Opus 4.6 |
| v0.1 | 2026-03-19 | 初始規劃：Slides 結構設計 + 資料流架構 + 設計邏輯參考 + Gemini 協作指令 | 跨專案業務協調 (Claude Opus 4.6) |
| v0.5 | 2026-03-20 | Phase 2 complete + cross-agent photo requirements for A4 Pipeline | Claude Opus 4.6 |


---

## SECTION 11 — 跨 Agent 相片需求規格（Slides → A4 Pipeline）

> 本節定義 Slides 報價簡報系統對 A4 Pipeline Agent 相片分類產出的具體需求。
> A4 在 Phase 4 vision.py 執行相片分類時，請參照本節規格，確保產出可被 Slides GAS 腳本直接使用。

### 11.1 全局架構：相片如何流入 Slides

```
A4 Pipeline (Phase 4)          A5 Master Data              Slides System (Phase 3)
─────────────────────          ──────────────              ────────────────────────
Google Photos Takeout           ITEM_MASTER                 generateClientProposal()
    │                           item_id (PK)                    │
    ▼                               │                          │
Gemini Vision 分類              ASSET_MASTER                    │
    │                           asset_id                       │
    ▼                           item_id (FK) ◄─── 關鍵橋接 ──► │
Drive MAPLAB_ASSETS/            drive_file_id                   │
  └── catering/                 photo_type                     │
       └── {category}/          is_primary                     │
            └── {item_id}/      quality_score                  │
                 └── photos     alt_text_zh                    │
                                    │                          │
                                    ▼                          ▼
                              GAS: 查 ASSET_MASTER → 取 drive_file_id → 插入 Slides
```

### 11.2 Slides 系統需要的相片類型

| 用途 | 頁面 | 需求數量 | 相片特徵 | 優先級 |
|------|------|----------|----------|--------|
| 封面背景 | P1 Cover | 1 張 | 全景外燴場景，高解析，橫向 16:9 | 🔴 最高 |
| 品牌介紹 | P2 About | 1 張 | 團隊工作照或精選場佈 | 🔴 最高 |
| 服務展示 | P3 Services | 2-3 張 | 週歲/婚禮/企業活動各一 | 🔴 最高 |
| 案例精選 | P4 Portfolio | 4 張 | 代表性活動場景（AMD/週歲/品酒/特展） | 🔴 最高 |
| 品項展示 | P6-N Menu | 每品項 1 張 | 餐點特寫、擺盤照，正方形或 4:3 | 🟡 高 |

### 11.3 對 A4 的具體需求：Drive 資料夾結構

**期望的資料夾層級：**

```
MAPLAB_ASSETS/
├── catering/                    ← 外燴專用素材（Slides 主要讀取來源）
│   ├── hero/                    ← 封面/全景照（高品質 16:9）
│   ├── team/                    ← 團隊/場佈照
│   ├── events/                  ← 按活動類型分
│   │   ├── birthday/            ← 週歲/彌月/生日
│   │   ├── wedding/             ← 婚禮外燴
│   │   ├── corporate/           ← 企業活動
│   │   └── other/               ← 品酒會/展覽等
│   └── items/                   ← ⭐ 品項照片（Slides Menu Showcase 核心）
│       ├── DES-MAC-001/         ← 對應 ITEM_MASTER item_id
│       │   ├── primary.webp     ← 主圖（Slides 優先使用）
│       │   └── alt_01.webp      ← 備選圖
│       ├── DES-MAC-002/
│       └── SAV-APZ-001/
├── daily/                       ← 日常照片（不進 Slides）
└── travel/                      ← 旅遊照片（不進 Slides）
```

**關鍵設計要求：**

1. **items/ 子資料夾必須用 item_id 命名**（如 `DES-MAC-001`），與 ITEM_MASTER 嚴格對應
2. **每個 item_id 資料夾必須有一張 primary 圖**（Slides 腳本預設取 primary）
3. **圖片格式統一為 WebP**（網頁載入快，Slides API 支援）
4. **外燴類照片（category=food/event）優先處理**，日常/旅遊可延後

### 11.4 對 A4 的具體需求：檔案命名規則

**品項照片命名格式：**
```
{item_id}_primary.webp          ← 主圖（必須）
{item_id}_alt_{seq2}.webp       ← 備選（選填）
{item_id}_detail_{seq2}.webp    ← 細節特寫（選填）
```

**範例：**
```
DES-MAC-001_primary.webp        ← 法式玫瑰馬卡龍主圖
DES-MAC-001_alt_01.webp         ← 備選角度
SAV-APZ-001_primary.webp        ← 義式香腸獵鳥盤主圖
```

**活動場景照命名格式（SEO 友善，A4 已有規則）：**
```
{event_type}-{keywords}-{YYYYMMDD}.webp
```

**範例：**
```
event-amd-corporate-catering-20250315.webp
event-wedding-candybar-outdoor-20240901.webp
```

### 11.5 對 A5 的具體需求：ASSET_MASTER Schema

A5 Master Data Agent 需建立 ASSET_MASTER sheet，作為 Slides GAS 腳本查詢圖片的唯一介面。

**ASSET_MASTER 必要欄位：**

| 欄位 | 型態 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| asset_id | string | ✅ | 唯一識別 AST-{SEQ4} | AST-0001 |
| item_id | string | ✅ | FK → ITEM_MASTER | DES-MAC-001 |
| drive_file_id | string | ✅ | Google Drive 檔案 ID | 1abc2def3ghi |
| drive_url | string | ✅ | 完整 Drive URL | https://drive.google.com/... |
| photo_type | enum | ✅ | primary / alt / detail | primary |
| is_primary | boolean | ✅ | 是否為主圖（GAS 查詢用） | TRUE |
| category | string | | 分類：food/event/team/hero | food |
| alt_text_zh | string | | 中文 ALT（SEO + 無障礙） | 法式玫瑰馬卡龍特寫 |
| quality_score | integer | | Gemini 評分 1-5 | 4 |
| source_event | string | | 來源活動（如有） | AMD 企業活動 |
| width | integer | | 圖片寬度 px | 1200 |
| height | integer | | 圖片高度 px | 800 |
| file_size_kb | integer | | 檔案大小 KB | 150 |
| processed_at | date | ✅ | 處理日期 | 2026-03-20 |

**GAS 查詢邏輯（Phase 3 將實作）：**
```javascript
// Slides GAS 腳本查詢品項主圖
function getItemPhoto(itemId) {
  var sheet = SpreadsheetApp.getActive().getSheetByName('ASSET_MASTER');
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === itemId && data[i][5] === true) { // item_id + is_primary
      return data[i][2]; // drive_file_id
    }
  }
  return null; // 無主圖，使用 placeholder
}
```

### 11.6 A4 Phase 4 分類時的額外標記需求

A4 目前的 Gemini Vision 分類 Prompt 產出：category / keywords / alt_text / is_food_photo / food_items / event_type / quality_score

**Slides 系統額外需要 A4 在分類時標記：**

| 新增欄位 | 說明 | 為什麼需要 |
|----------|------|-----------|
| matched_item_id | 比對到的 ITEM_MASTER item_id（如有） | Slides 靠 item_id 找圖，必須建立對應 |
| photo_orientation | landscape / portrait / square | Slides 封面需要 landscape，品項可接受 square |
| is_catering_usable | TRUE/FALSE | 快速過濾可用於外燴簡報的照片 |
| suggested_slide_usage | hero / about / portfolio / item / none | A4 可根據照片內容建議用途 |

**Gemini Prompt 擴充建議（給 A4）：**
```
在原有分類基礎上，額外判斷：
1. 這張照片是否適合用於外燴客戶簡報？(is_catering_usable: true/false)
2. 建議用於簡報的哪個位置？(suggested_slide_usage: hero/about/portfolio/item/none)
3. 如果是餐點照片，最接近 ITEM_MASTER 中的哪個品項？(matched_item_id 或 null)
4. 照片方向？(photo_orientation: landscape/portrait/square)
```

### 11.7 跨 Agent 交接觸發點

| 事件 | 觸發方 | 通知對象 | 記錄位置 |
|------|--------|----------|----------|
| A4 Phase 4 外燴分類完成 | A4 | Slides + A5 | CURRENT_STATUS + pipeline.md |
| A4 items/ 資料夾照片就緒 | A4 | Slides | CURRENT_STATUS Session Log |
| A5 ASSET_MASTER 建立完成 | A5 | Slides | master-data.md SECTION 6 |
| Slides Phase 3 開始 | Slides | A4 + A5 | slides-quotation-system.md |
| ITEM_MASTER 新增/修改品項 | A5 | A4（重新分類） | master-data.md + BOARD |
| 新照片入庫需更新 ASSET_MASTER | A4 | A5 | pipeline.md Session Log |

### 11.8 分階段對接時程

| 階段 | 時間點 | A4 需完成 | A5 需完成 | Slides 需完成 |
|------|--------|-----------|-----------|---------------|
| 階段 A | A4 Phase 4 啟動後 | 外燴照片分類 + quality_score | — | — |
| 階段 B | 分類結果出爐後 | items/ 資料夾建立 + primary 標記 | ASSET_MASTER sheet 建立 + 填入 | — |
| 階段 C | ASSET_MASTER 就緒後 | 持續補充照片 | 持續維護索引 | Phase 3 啟動：GAS 插入照片邏輯 |
| 階段 D | Phase 3 完成後 | — | — | 完整測試：一鍵生成含照片的提案簡報 |

### 11.9 重要約束提醒

1. **Slides Menu Showcase 只顯示品項名稱 + 照片**，不顯示價格/數量/說明

---

## SECTION 12 實際案例紀錄：台南文學館展覽開幕茶會 2026/5/27

### 12.1 案件概覽

| 欄位 | 內容 |
|------|------|
| 案件名稱 | 台南文學館展覽開幕茶會 |
| 客戶 | Czech Centre / Czech Centres |
| 客戶 ID | 48546038 |
| 客戶地址 | Václavské náměstí 816/49, 110 00 Praha 1（捷克總部） |
| 活動日期 | 2026/5/27（三）14:00–15:30 |
| 場地 | 台南文學館（一樓會議室）|
| 規模 | 30–40 人 |
| 餐點總件數 | 200 件 |
| **成交金額** | **TWD 23,000** |
| 訂金 | TWD 3,000 |

### 12.2 報價版本演進

| 版本 | 金額 | 狀態 |
|------|------|------|
| 版本一（Slide + Sheet）| TWD 28,000 | 未成交 |
| **版本二（Slide + Sheet）** | **TWD 23,000** | **✅ 成交** |

兩版本都有製作 Google Slides 簡報版 + Google Sheets 試算表版，並都有對外發送給客戶。最終以 23,000 版本成交。

### 12.3 最終成交菜單（23,000 版）

**SAVORY (5款)：**

| 品項 | 數量 |
|------|------|
| Aussie-style Tartare Shrimp Burger | 20 |
| Italian Basil Pesto Chicken Sandwich | 20 |
| Seasonal Tomato Bruschetta with Parmigiano *(NEW — 替換綠咖喱鹹派)* | 20 |
| Slow-Braised Neapolitan Spiced Pork Ball Skewer *(NEW — 替換虱目魚香腸)* | 25 |
| Tainan Shrimp Roll w/ Chef's Sour Plum Sauce | 25 |

**DESSERT (5款)：**

| 品項 | 數量 |
|------|------|
| Japanese Light Cheesecake | 15 |
| French Rose Lemon Tartlet | 20 |
| Orange Dark Chocolate Brownie | 25 |
| Rose Cream Berry Chantilly Cupcake | 15 |
| Caramel Mini Mille-feuille *(NEW — 替換磅蛋糕)* | 20 |

**BEVERAGES 6L (2款)：**

| 品項 |
|------|
| Assam Black Tea |
| Cold Brew Golden Buckwheat Tea |

### 12.4 Quotation / Invoice 格式規範（對外英文版）

此案首次使用英文版 Quotation/Invoice 格式，適用於外資客戶。格式標準應與報價系統 A5 共享：

1. **標題行**：MAP LAB KITCHEN + 副標題 + `Quotation / Invoice`
2. **客戶資訊欄位**：Client / Date / Event / Guests / Contact / Address
3. **Address 注意**：外資客戶使用捷克/海外總部地址，**非台灣地址**
4. **幣別**：一律使用 `TWD`（禁止使用 `NTD`）
5. **菜單分組**：SAVORY / DESSERT / BEVERAGES + 數量 + 金額
6. **費用摘要**：Item / Amount (TWD) / Notes
7. **英文條款**：Terms and Conditions of Service Agreement（4 Articles）
8. **Vendor Information**：銀行帳號放於文件最底部（Row 44）
   - 銀行：中國信託 CTCBTWTP / 西台南分行
   - 戶名：圖管實業社
   - 帳號：222540645172

### 12.5 報價系統格式維持目標（教訓 1）

未來報價系統一鍵輸出後，應維持「23000的副本」結構 **八九成相似**：

- 雖然資料庫以格子分隔存儲，視覺輸出結構應對應原始格式
- 此格式標準已記錄於本節，供 A5 quotation engine 參考
- 關鍵：不要因為 DB 結構不同而讓輸出格式跑版

### 12.6 此案技術教訓（教訓 2）

**Apps Script / Sheets 操作限制：**

- Monaco API `editor.executeEdits()` 修改 editor 文字後，不觸發 React 狀態更新 → Commit 按鈕失效
- 解法：每次用 Monaco API 後需手動點擊一次 Commit 按鈕才能激活
- Apps Script 函式下拉需滾動才能看到新加的函式
- Merged cell 換行：`Ctrl+Enter`（不是 Enter）
- 特殊字元（如【】）輸入可用 `document.execCommand('insertText')`
- Name Box 輸入 cell reference 時，如已在 edit mode 會把 reference 文字打進格子（需先 Esc 退出 edit mode）

**語言版本管理：**

- 中文版 → 台灣本地客戶（原始分頁格式）
- 英文版 Quotation/Invoice → 外資客戶（副本分頁，調整標題 + 客戶地址為海外總部）
- 兩版本保留在同一 Sheets 的不同分頁，方便對照管理

### 12.7 資源連結

| 資源 | ID |
|------|------|
| Google Slides（報價簡報）| `16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo` |
| Google Sheets（報價單）| `1lRkmSla8roVC7wgWjp46Nok8I6ipqVTzTyY2cI1L2Gw` |
| Apps Script（對齊工具）| `1jqPdpYxltfbzOrSVYlKZ_nnJTY0C0evjv1gTR2wFM69F5CqbOO4_0EO6` |
| 「23000的副本」分頁 gid | `2114602586` |
| Quotation-Invoice 分頁 gid | `2019046993` |
