# MAPLAB A0~A8 全組織職能地圖與關聯調用架構 (Organizational System Map)

> 版本：v1.0 | 建立：2026-10-02 | 治理層級：A0 總調度秘書與 Hermes 共同認知契約
> 適用對象：Hermes、Codex、Antigravity、Gemini、Claude 與所有協作 Agent

---

## 0. MAPLAB 企業本質與核心生意

- **企業主體**：MAPLAB 是台南的外燴品牌，官網 `www.maplabkitchen.com`。
- **核心生意**：到場外燴整案（客製化茶會、婚宴、抓周、商務開幕、企業酒會），另有外帶單品。
- **價格體系隔離**：到場外燴與外帶單品價格體系不同，不得混用。
- **定價原則**：在地定價基準為台南在地行情 × 1.35（此係數、成本與底層毛利**嚴禁出現在對外檔案**）。
- **協同內部線**：
  1. `maplab-ai-handbook`：餐飲外燴業務、SEO、廣告、素材與自動化報價。
  2. `investment-os`：自營策略研究與模擬交易（不動真錢）。
  3. 音樂/內容線：YouTube 頻道、影音再製、熟齡健康（A8-FITNESS）。

---

## 1. A0 ~ A8 角色責任矩陣與邊界契約

| 角色代號 | 角色名稱 | 核心責任 | 核心工具與資產 | 絕對紅線（不做什麼） | 協作邊界 |
|---|---|---|---|---|---|
| **A0** | **Dispatch Secretary**<br/>總調度秘書 | 跨系統任務分派、Owner 入口管理、全貌 Review、進度追蹤 | Chrome Extension 任務模組、Task Queue、Agent Bus | 不直接取代各專職角色，不擅自下單或對外發布 | 面向 Owner 與各 Agent，發卡與催辦 |
| **A1** | **System Orchestrator**<br/>系統協調與管線維護 | 程式碼維護、系統巡檢 (Patrol)、Items 表主資料維護、Debug | Git、GitHub Actions、Launchd、`scripts/patrol.sh` | 未經測試不可直接修改生產環境核心腳本 | 負責系統底層修復與代碼架構 |
| **A2** | **Ads SEO WordPress Patrol**<br/>廣告、SEO 與官網巡檢 | SEO 文章產出、RankMath 關鍵字、WordPress 內容上架、廣告數據巡檢 | WordPress REST API、Search Console、Meta Ads API | 嚴禁私自發布未經 Owner 審核的文章與上線廣告 | 提供流量與搜尋曝光，轉化引流至 A6/A7 |
| **A3** | **Ads Growth Studio**<br/>廣告增長工作室 | 廣告投放策略、受眾分析、文案與素材組合、ROAS 監控 | Meta Ads Manager、Google Ads、廣告文案庫 | 嚴禁私自調整廣告預算或啟用高風險廣告活動 | 與 A2 協同，將廣告成果交由 Owner 審查 |
| **A4** | **Photo Archive**<br/>相簿與影像管線 | 活動照片歸檔、WebP 轉檔、Drive 標籤化、素材預排 (Prelayout) | Google Photos、Google Drive (`/Volumes/MacExternal/`)、ExifTool | 不修改原始大圖，不破壞 EXIF，不外洩客資/兒童照 | 提供圖片素材與 URL 給 A2/A3/A5/A6 |
| **A5** | **Quotation Engine**<br/>報價與提案引擎部 | 菜單品項主資料庫 (Items 表)、成本毛利邏輯 (毛利率 ≥ 70%)、報價公式 | Google Sheets Master Data、GAS `createQuote` 腳本 | 不直接面對客戶，不自行決定折扣或招待 | 提供標準價格與報價單生成能力給 A6 |
| **A6** | **Sales Rapid Response**<br/>業務快反應部隊 | 業務快速反應、接收自然語言需求產出報價單草稿 + Slide 提案 | Telegram Bot (`@maplab_a6_bot`)、GAS Web App、`quote_calc.py` | 不直接對客發布價格、不承諾檔期、不選菜、不判飲食安全 | 服務業務 Mina，3秒產出報價草稿供確認 |
| **A7** | **Service Desk**<br/>客戶服務台 | 客服常見問題 (FAQ)、菜色介紹、交通流程、過敏與禁忌食材諮詢 | FAQ 知識庫、LINE OA 對話記錄、菜單手冊 | 不得給予未經廚師確認的嚴重過敏保證 | 將確認需求轉交 A6 報價 |
| **A8** | **Content Repurposing Pipeline**<br/>內容再製管線 | 活動案例影片分鏡、短影音腳本、NotebookLM 知識整理、YouTube 運營 | NotebookLM、YouTube Studio、Suno、剪輯腳本 | 嚴禁未經審核直接發布影片至官方公開頻道 | 將 A4 素材轉化為長尾內容資產 |
| **A8-FITNESS** | **Senior Fitness Director**<br/>熟齡健身動態指導 | 熟齡/銀髮族健康促進動作庫、跟練影片分鏡、安全動作指引 | 動態運動生理指引、分鏡表、YouTube 影音 | 嚴禁提供醫療診斷或未經物理治療審核之高風險動作 | 品牌公益與長輩關懷內容輸出 |

---

## 2. 系統全貌關聯圖與調用路線 (Workflow Routes)

### 路線 A：報價系統 Google Sheets / GAS 調用路線 (Quotation Route)
```
客戶詢價 (LINE / 電話) 
  ↓
業務 Mina 拋出需求文字 (例: 40人 $35000 開幕茶會)
  ↓
A6 / Hermes 接收指令
  ↓
呼叫本地試算 `quote_calc.py` (比對人數、預算、毛利率 ≥ 70%、骨架 skeleton)
  ↓
組裝 `form_data` POST 至 `GAS_QUOTE_URL` (Google Apps Script Web App)
  ↓
GAS 執行 action: `createQuote`
  ↓
從主工作表複製 `QUOTE_DRAFT` 範本，生成獨立報價 Sheet 副本 (URL)
  ↓
GAS 執行 action: `createSlide` (依據報價資料自動生成 Google Slides 簡報)
  ↓
A6 回傳 Google Sheet + Google Slide 連結給 Mina (摘要標註待確認事項)
  ↓
Mina 人工確認 → 輸出 PDF / 發送給客戶
```

### 路線 B：圖片與多媒體素材調用路線 (Asset Pipeline Route)
```
活動現場拍攝原始照
  ↓
A4 Photo Archive 接收
  ↓
本地工作區處理 (`/Volumes/MacExternal/MAPLAB_WORKSPACE/` 或本機目錄)
  ↓
WebP 輕量化轉檔 + 自動校正 EXIF Orientation
  ↓
上傳 Google Drive / 雲端目錄，寫入主資料表 (Items / Prelayout Table)
  ↓
分流提供：
  ├→ A2/A3：官網文章精選圖與 Meta 廣告素材
  ├→ A5/A6：報價單菜色預覽圖與 Google Slides 提案簡報
  └→ A8：YouTube 短影音與活動紀錄素材
```

### 路線 C：任務調度與派工反饋閉環 (Dispatch & Feedback Loop)
```
Owner / 使用者入口 (Chrome Extension / Telegram / Cowork)
  ↓
A0 總調度秘書 (解析任務、識別所屬專業領域、選派 A1~A8)
  ↓
派發 Task Card 至 `agent-bus/inbox/` 或專案目錄
  ↓
專職 Agent (A1/A2/A3/A4/A5/A6/A7/A8) 執行
  ↓
產出驗證收據 (Receipt / Changed Paths / Diff)
  ↓
回寫 `agent-bus/outbox/` 與 `shared/agent-status.md`
  ↓
### 路線 D：報價核心參數與基準（A5/A6 共享規則）
- **外燴低消**：$10,000 元整（預算低於此門檻需 alert 業務 Mina）。
- **毛利率底線**：70%（品項成本 / 報價需 < 30%，不足時自動替換為同類別更低成本品項）。
- **車馬費門檻**：Google Maps 導航 30 分鐘以內免費；超過 30 分鐘收取 `max(km × $6, min × $50)`。
- **搬運費標準**：有電梯一律免費；無電梯 2 樓無人手協助 $1,000 / 有人手協助 $500。
- **合約四版本與訂金**：
  - `to_c`：個人活動（訂金基準 baseline $3,000，Mina 可彈性調整）。
  - `to_b_deposit`：企業客戶有訂金（預設）。
  - `to_b_full`：企業無訂金例外。
  - `to_b_marketing`：行銷／公關公司專用。
  - **企業判定條件**：公司抬頭有填，或活動類型包含「尾牙、春酒、企業、公司、記者會、開幕、酒會」。

---

## 3. 企業決策邏輯與文化鐵律

1. **核心原則 0（時間權重與真相）**：
   - 資料越新越接近現況，衝突時信新的，舊的標為歷史快照。
   - 真相在檔案與 Live 系統，不在 Agent 記憶中。
2. **決策五問（遇到沒寫過的事）**：
   - (1) 對使用者有幫助嗎？
   - (2) 為什麼要？
   - (3) 為什麼不要？
   - (4) 有沒有更好的做法？
   - (5) 以後如何避免卡死在這個點？
3. **溝通人話原則（原則 1）**：
   - 主詞必須用人看得懂的標題/名稱，內部代碼（如 `T-A6-001`）只能放在括號內。
4. **缺陷棘輪（原則 2）**：
   - 抓到缺陷必須立即沉澱為檢查清單、閘門腳本或模板必填項，只進不退。
5. **增量交付原則（原則 9）**：
   - 交付必須是「What / So what / Now what」，輸出可行動的增量，而非資訊搬運。
