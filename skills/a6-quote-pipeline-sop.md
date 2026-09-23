# A6 Quote Pipeline SOP — 報價管線全景與降級操作規範
版本：v1.0 | 建立：2026-08-31 | 維護者：A0（Fable5）| 供 A6 bot 載入使用

> 本 SOP 是「考試與 SOP 建置前置」的產出：把報價相關的所有管線、資料源、
> 通道狀態與紅線寫成一份 A6 可直接執行的規範。
> 與 `skills/a6-rapid-quote-sop.md`（操作流程）、
> `docs/a6-a7-customer-to-quote-gym-sop.md`（readiness 十類欄位）互補，不取代。

---

## SECTION 0 — 管線全景（指向性心智圖，文字版）

```
客戶 (LINE OA)
   │
   ▼
A6 bot（Telegram/LINE 接口，助手不是決策者）
   │  intake_flow.py 十類欄位齊備後
   ▼
A5 quote engine (bot_a6/a5_quote_engine.py)
   │  讀 data/items_master.json（品項+成本+單位；default_price 全空）
   │  產出：Markdown 報價草稿 + GAS 觸發 JSON
   ▼
┌─────────── 正式產出層（雲端，目前離線）───────────┐
│ computer-use + Chrome 操作 A4 Google Sheet          │
│   → Sheet 內建公式 + 資料庫 → 產出正式報價單        │
│   → GAS 建立報價單副本（932 份歷史報價單在雲端）     │
└────────────────────────────────────────────────┘
   │
   ▼
業務人工確認 → 發給客戶（總價/人均制；成本與毛利率絕不外露）
```

**關鍵理解（Owner 2026-08-31 確認）：**
正式報價單的「定價能力」在 A4 Google Sheet 的公式與資料庫裡，
由 computer-use + Chrome 通道驅動。地端備份與 items_master 只有成本資料，
**沒有公式、沒有客戶單價** → 雲端通道斷線時，地端只能做「查詢」，不能做「定價」。

---

## SECTION 1 — 兩種報價制度（絕不混用）

| | 外燴（catering） | 外帶（takeout） |
|---|---|---|
| 計價方式 | 總價/人均制（例：50人 $40,000 = 人均 $800） | **單品單價制**（每品項 × 單價 × 份數） |
| 定價來源 | A4 Sheet 公式 + 預算回推 | 外帶菜單價目表（單價 ≠ 外燴內部成本） |
| 價目所在 | A4 Google Sheet（雲端） | google.site 預約外帶取餐頁（sites.google.com/view/maplabkitchen，菜單為**圖片**）+ Owner 曾貼過的菜單對照 |
| 附加費 | 服務費 10%、車馬費（待確認項） | 外帶打包盒歷史價 $8/個（archive/data/quote-specials.md） |

**紅線：外帶單價與外燴報價是兩套價格，不可用外燴成本或人均推算外帶單價。**

---

## SECTION 2 — 資料源優先序（查價時依序使用）

1. **A4 Google Sheet（唯一定價 truth source）** — 需 computer-use + Chrome 或
   Drive MCP 通道在線。在線→照 `a6-rapid-quote-sop.md` 正常流程。
2. **業務/Owner 當場貼上的價目** — 視為當日有效價，寫入案件紀錄。
3. **google.site 預約外帶取餐頁** — 外帶價目官方對外版；目前為圖片，
   bot 無 OCR 能力時只能給連結請業務對照，不可猜圖片內容。
4. **地端查詢層（唯讀，只有成本沒有售價）**：
   - `data/items_master.json` — 140+ 品項：item_id/品名/成本/單位（default_price 全空）
   - `archive/data/quote_items_deduped_v2.json` — 品名別名對照（同品多寫法歸一）
   - `archive/raw/a6-logs/` + `data/a6-logs/` — 歷史報價草稿（含成本結構）
   - `data/quote-terms-reference.md`、`archive/data/quote-specials.md` — 條款與特例
5. **地端 Drive 備份 `/Volumes/MacExternal/MAPLAB_from_GoogleDrive`（435G）** —
   照片/文件可用；**Google Sheets/Docs 只是雲端捷徑檔，試算表內容不在地端**。

---

## SECTION 3 — 找不到價格時的標準行為

1. **絕不編價**。沒有任何一級資料源給出售價時，不得輸出數字。
2. 回覆固定格式：列出「已找到成本資料的品項」與「查無售價的品項」兩欄，
   標明資料源與缺口。
3. 外帶案件查無單價 → 附 google.site 預約外帶取餐頁連結，請業務對照圖片價目，
   或請 Owner 貼上價目文字，貼上後依 Section 2 第 2 級處理。
4. 通道斷線 → 明說「A4 Sheet 通道目前離線，僅能提供成本查詢與品項比對」，
   不得宣稱已產出正式報價單。

**失敗案例（2026-07-06，data/a6-logs/2026-07-06.md）：**
業務要求「找外帶菜單幫我補上單位與價錢」，A6 回了一份無關的生成菜單。
教訓：查價請求必須逐品項對照回覆，找不到就說找不到，不得用生成內容充數。

---

## SECTION 4 — 通道狀態檢查（回覆前自查）

| 通道 | 用途 | 斷線時的降級 |
|---|---|---|
| computer-use + Chrome | 操作 A4 Sheet 產正式報價單 | 降級為地端查詢；報價單標「草稿・待雲端通道」 |
| Drive MCP | 讀雲端 Sheet/歷史報價單 | 同上 |
| GAS 觸發 | 建報價單副本 | 只出 Markdown 草稿，JSON 註明 pending |
| A6 gateway 白名單 argv | runtime-status / signal-status / repo-status / recent-commits / a6-self-test | 新增唯讀 quote-items argv 已獲 Owner 口頭核可（2026-08-31），落地前不得假設存在 |

---

## SECTION 5 — 紅線（違反即停止並上報）

- 對客戶**絕不揭露成本與毛利率**；客戶只看總價/人均（外燴）或單價×份數（外帶）。
- 不自行修改 Google Sheets、Items 主表、GAS、Drive、WordPress 或任何 truth source。
- 不編造價格、不引用「過去經驗」代替資料源。
- 秘密（token/金鑰/客戶個資）不進 repo、prompt、log。
- 未經業務確認的草稿不得發給客戶；A6 不得自我核准。

---

## SECTION 6 — 已知缺口（維護者待辦）

- [x] 外帶菜單已轉錄文字版（2026-08-31，`data/takeout_menu_catalog.md`，
      經 `scripts/fetch_takeout_menu.sh` 抓圖＋Fable5 讀圖）。
      **查核結論：google.site 外帶菜單原圖不含單價，只有品名＋最低訂量；
      訂購須知頁 20 張圖均為客人回饋截圖，亦無價目。**
- [ ] 外帶「單價」仍缺：不在 google.site、不在地端；truth source＝A4 試算表
      或 LINE 歷史報價，需 Owner 提供或雲端通道恢復後撈取。
- [ ] A6 gateway 唯讀 quote-items argv：已核可、未實作（需改 gateway + kickstart）。
- [ ] 2026-08-31 外帶詢價 8 品項中 5 項（辣雞翅口味/牛肉小鹹派/牛肉小漢堡/
      法式薯泥蛋沙拉三明治/芒果奶酪杯/煙燻鮭魚沙拉之精確對應）在 items_master
      僅有近似品項，正式對照需 A4 Sheet 或外帶價目表。
