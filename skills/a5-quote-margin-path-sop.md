# 報價毛利路徑 SOP（最新正典）— v1.0 2026-09-09

適用：所有 agent（A0/A6/Codex/Hermes）。本 SOP 記錄的是 2026-09-06~09
小肚肚 Open House 實案跑通的路徑（Owner msg 4993–5003 裁定），
**取代任何 agent 自行推斷的報價路徑**。改動本路徑＝Owner gate。

## 0. 一句話

成本查 Items、售價錨成交案、頻率查 932 份、毛利只進內部表、
對外照文學館格式、每個數字帶來源、查無不編價。

## 1. 數字來源紀律（鐵律）

| 要什麼 | 唯一來源 | 讀法 |
|---|---|---|
| 品項成本 | A4 Sheet `Items` 分頁（126 列正典；本地 data/items_master.json 為快照） | `bot/venv/bin/python scripts/sheet_tail.py --sheet-id 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg --tab Items`（2026-09-09 已修通 int-expiry/invalid_scope） |
| 售價錨 | 成交案（現行錨＝文學館 23,000/200件，slides-quotation-system SECTION 12） | 件均/人均回推 |
| 品項頻率（配菜依據） | 932 份報價 archive/data/quote-items-all.md ＋ 2026 OrderLines | 便宜多配、貴的少配（Owner 5002：成本15-16→30-40件；20-23→30件；30→25件；40→20件） |
| 加購服務成本 | 廠商實際回覆報價 | 詢價中＝留空標「待廠商回覆」 |
| 查無來源 | **留空標缺口，絕不編價** | |

## 2. 毛利計算（內部）

工作表結構照 projects/margin-sheet-prototype-20260908.md 三分頁：
內部毛利表（品項/成本/份數/報價分攤/毛利率/來源）→ 加購服務區 → 對外報價單。
毛利率=(報價−成本)/報價；**目前僅食材層毛利**（人力/運輸/耗材成本抓法待 Owner 定）。
實案基準：40人 300件 成本≈6,710、報價35,000 → 食材層毛利≈80.8%。

## 3. 對外格式（比照文學館成交版，SECTION 12.4）

標題 MAP LAB KITCHEN + Quotation → 客戶資訊六欄 → SAVORY/DESSERT/BEVERAGES
分組＋數量 → 費用摘要 Item/Amount(TWD)/Notes → 服務範圍★七點 → 條款 →
銀行資訊置底（中國信託／**圖蕾實業社**——2026-09-09 authoritative Drive 校正，
舊模板寫「圖管」為誤）。幣別一律 TWD 禁 NTD。
**成本與毛利絕不出現在對外文件**；外燴人均制與外帶單品制絕不混用。
範例成品：data/a6-logs/2026-09-09-clinic-openhouse-quotation-formatted-draft.md。

## 4. 角色分工

- 任何 agent：可做草稿計算與格式化，一律標「草稿，未對客戶發出」。
- Hermes：只做 intake 與草稿整理（gym SOP v3.1），不報價不承諾檔期。
- 對客發送、最終價格、目標毛利率：**只有 Owner/Mina**。

## 5. Slide 報價書規格（v0.1 草案——Owner 交辦「制定 slide 規格與 SOP」，待核）

文學館案兩版都是 Slide＋Sheet 雙格式對外發送（SECTION 12.2），故 Slide 版為正式產出物之一。

頁面規格（依成交版反推，待 Owner 核定後凍結）：
1. 封面：MAP LAB KITCHEN＋案名＋日期＋Quotation
2. 客戶資訊頁（12.4 六欄）
3. 菜單頁 ×2-3：SAVORY／DESSERT／BEVERAGES 分組，每品項配 A4 相片庫照片（等 A4 照片分類產出）
4. 費用摘要頁（Item/Amount/Notes）
5. **加購項頁（Owner 5095 裁定 2026-09-10）：攝影／花藝／插旗等加購項併入
   同一張報價 slide 不另出版，並配一張示意圖說明加購內容（此點已核定）**
6. 服務範圍★七點頁
7. 條款＋銀行資訊頁
製作方式：QUOTE_DRAFT Sheet 資料 → GAS 文字替換模板（T-SLIDE-004，尚待實作）；
實作前先人工複製文學館成交版 Slide 改內容。禁止：成本毛利、NTD、未授權相片。

## 6. 訓練掛鉤

Hermes gym R7+ 的教材以本 SOP 為準：訓「照路徑走」，不訓「發明路徑」。
