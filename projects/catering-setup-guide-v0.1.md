# MAPLAB Catering Setup Guide / Styling Intelligence v0.1

日期：2026-09-19  
狀態：MVP architecture / Codex-ready  
母任務：GitHub Issue #26

## 北極星

把 MAPLAB 過去活動的「擺桌經驗」從人的腦中搬成可重複、可測試、可交接的決策系統。

輸入一場活動的場地、桌型、人數、菜單、可用器皿與真實 reference case，輸出：
- 俯視配置
- 正視高度層次
- 餐點 ↔ 器皿對應
- 客人取餐動線
- 補餐 / 工作人員動線
- 現場 setup checklist
- 風險旗標
- 一頁式現場指引
- 活動後 learning receipt

## 系統分層

### Layer 0 — Truth sources
- 真實案例照片：A4 asset index / ASSET_LOG / fact-first matching
- 品項 / 器皿 / 成本：A5 master data
- 視覺規範：`skills/maplab-visual-spec.md`
- 本系統規則：本 repo

### Layer 1 — Deterministic constraint engine
不得由 LLM 自由決定：
- 桌面容量
- 安全間距
- 桌邊碰撞風險
- 補餐通道
- 客人流向
- 溫控 / 風 / 日照 / 蟲害風險
- 飲品與主餐堵塞
- 高低層次最小要求
- MISSING_INPUT

### Layer 2 — Styling advisor
在 hard constraints 內提出 2–3 種風格方案：
- 企業：低密度、乾淨、動線優先
- 週歲：可增加柔性花材與高度變化
- 婚禮：有層次但避免裝飾壓過食物
- 開幕：品牌視覺焦點 + 快速拿取

不得宣稱單一方案「最好看」。

### Layer 3 — Preview
第一版只要：
- SVG top-down
- SVG / HTML front elevation
- zone label
- height label
- arrows for guest / refill flow
- risk markers

AI 生成的圖一律標 `CONCEPT_PREVIEW`。

### Layer 4 — Human approval
人員可覆寫：
- item position
- tray choice
- flower placement
- height
- flow
- refill station

所有人工改動保留 diff。

### Layer 5 — Post-event learning
活動後以真實照片 + 現場回饋產出：
- 哪些規則有效
- 哪些位置壅塞
- 哪些器皿不合適
- 哪裡補餐困難
- 哪些高度/視覺配置成功
- 新 rule candidate

新規則不自動生效，需 human approval。

## Input contract

最小欄位：
- event_type
- guest_count
- venue.indoor_outdoor
- venue.table_count
- venue.table_width_cm
- venue.table_depth_cm
- menu[]
- available_assets
- constraints[]
- reference_photo_ids[]

缺少硬資料時：
`status = MISSING_INPUT`
並列出 `missing_fields[]`，禁止猜值。

## Output contract

- `setup-plan.json`
- `setup-guide.md`
- `setup-preview.svg` / `setup-preview.html`
- `assumptions.json`
- `post-event-review.md`（活動後）

## 圖像原則

1. 真實 MAPLAB 案例只能來自 A4。
2. 不生成可被誤認為實拍的假食物照。
3. 可生成：
   - schematic
   - wireframe
   - annotated overlay
   - stylized concept preview
4. 所有概念圖必須明示 `CONCEPT_PREVIEW`。
5. 若使用真實照片做 overlay，不改變食物內容，只做標註與區域建議。

## v0.1 成功條件

- 相同輸入 → 相同 deterministic layout output
- 至少 12 tests
- 4 種活動 fixture
- 3 種環境 fixture
- 1–3 桌支援
- 2–3 層高度
- guest / refill flow 可視化
- 缺資料不幻覺
- 人類改動可追溯
- post-event feedback 可產生 rule candidate

## 不做

- 3D 場景
- 手機 App
- 自動採購
- 自動改報價
- 自動寫回 Master Data
- 生成假實拍案例
- 自動宣告「最佳設計」

## 版本紀錄

### 2026-09-19｜v0.1
迭代原因：現有照片、品項與視覺規範已具備，但缺少把擺設經驗轉成可複利決策層。

新原則：
- deterministic constraints first
- AI styling second
- real case / concept preview 分離
- 每場活動留下 learning receipt
