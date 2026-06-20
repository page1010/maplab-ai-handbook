# A5 報價與提案引擎部 — 核心技能書

版本：v1.0 | 建立：2026-03-26 | 維護：A1 Claude Code

> 80/20 原則：只寫最影響接單的 3 個技能 + 最容易卡住的點

---

## 技能 1：菜單自動搭配

**場景**：客戶說「30人、預算 3 萬、週歲派對」→ 推薦 2-3 套菜單方案含報價

**做法**：
1. 讀 MAPLAB_外燴系統_v0.1 的 Items 表（108 品項，4 類別）（舊名 MAPLAB_MasterData_Sheets）
2. 依活動類型篩選適合品項（週歲 → 排除酒類、加甜點比重）
3. 依預算和人數計算份量和品項數
4. 輸出 2-3 套方案：經濟版 / 標準版 / 豪華版

**容易卡住的點**：
- Items.D 欄 default_price 還沒填完 → 沒有價格就無法算報價，先問 Owner
- 品項編碼規則：APP=前菜、DST=甜點、MAIN=主菜、BEV=飲品，連號不跳號
- 份量換算：外燴不是餐廳，要考慮 buffet 式取餐量（通常比餐廳多 20-30%）

**必讀**：projects/maplab-master-data.md、handoff/field-naming-rules.md

---

## 技能 2：報價單快速生成

**場景**：客戶確認方案後 → 5 分鐘內產出正式報價單

### 強制流程：先用 Sheet 試算，不准只在聊天手算

任何 A5/A6/Codex 報價任務，只要使用者要「報價」「試算」「毛利」或「報價單連結」，完成標準都不是聊天裡給數字，而是：

1. 先讀過往規則：`skills/pitfalls/SKILL.md` 的 QUOTE_DRAFT 保護、`skills/a6-rapid-quote-sop.md` SECTION 7、`handoff/feedback/2026-04-02-quote-draft-v3-layout.md`、`docs/business-requirements/quote-sheet-print-range.md`。
2. 複製整份 `MAPLAB_外燴系統_v0.1`，或使用既有 GAS `createQuote` 產出的完整報價副本；不得在母版 `QUOTE_DRAFT` 直接測試。
3. 只在副本填寫可寫欄位：客戶資訊 D/F 欄、品項 D 欄、數量 F 欄、費用與總額欄。不得覆蓋母版或副本中的 Items 主表。
4. 品項必須優先使用現有下拉/Items `standard_name`，不要自創菜名或用模型想像品項。使用者指定「基本版」時，從既有常用品項/下拉清單選。
5. 讓 Sheet 公式或副本內 VLOOKUP 從 `Items!C:E` 計算成本，回讀試算結果後才回覆：菜單、總金額、訂單成本、毛利率、Sheet URL。
6. 對客戶文字不得揭露成本或毛利；成本/毛利只放內部回報。

### 學徒 agent 訓練 gate（OpenClaw / Hermes / local model）

若把 A5/A6 報價任務交給下游 agent，不能接受它自判 `PASS`。主管 agent 必須用以下 gate 校正：

1. payload 必須是 `action=createQuoteVariants`，且 `variants` 內是一個方案物件，方案物件底下才有 `menu` 陣列；不得把每個品項直接塞成 `variants[]`。
2. 使用者要求 10 道時，`menu` 必須剛好 10 列；不得用泛稱或模型翻譯名取代 Items 既有品名。
3. 必須使用既有 MAPLAB 品名與成本，不自創「意大利面 / 白飯 / 蛋糕 / 果汁」這類泛稱。
4. 若是 2026-06-18 15 人高毛利基本版正餐案例，標準驗收數字為：10 道、總金額 `NT$15,700`、訂單成本 `NT$3,140`、毛利率 `80.0%`、急件 50% 訂金 `NT$7,850`。
5. 不得在客戶版回覆揭露成本與毛利；急件只能說需預收 50% 訂金，且只能承諾餐檯桌面與用餐區佈置。
6. bot-facing 修改必須有 Chrome Telegram Web 實測；Sheet 產單必須回讀 `報價單!D2:F31` 與 `報價單!I7:J31`。

2026-06-20 訓練結論：OpenClaw main 與 Hermes 目前不得認證為 A5/A6 報價學徒。可暫用的學徒路徑只有直接 Ollama `qwen2.5:14b`，而且必須同時滿足：strict JSON prompt、客戶文案 `temperature=0`、固定核准模板、主管 deterministic grader。模型不得自由改寫「預收 50% 訂金」或桌面佈置承諾；若改成「一定比例訂金」、出現 `高毛利`、`成本`、`毛利`、`桌椅`、`背板`、`氣球`，一律 FAIL。

**做法**：
1. 從菜單方案帶入品項 + 單價 + 數量
2. 加入固定費用：外送費、場佈費、人力費（依距離和規模級距）
3. 輸出格式：Google Sheets QUOTE_DRAFT 模板
4. 客戶版（只有品項和總價）+ 內部版（含成本和毛利）

**容易卡住的點**：
- QUOTE_DRAFT 欄位定義見 handoff/tasks/T-A5-002.md
- 外送費級距還沒建立 → 先用固定值，之後再做級距表
- 不要自己發明定價，所有價格都從 Items 表拉

**必讀**：projects/slides-quotation-system.md

---

## 技能 3：本週活動簡報

**場景**：每週一產出本週工作概覽

**做法**：
1. 讀 TimeTree 資料（data/timetree_events_2022_2026.json）篩選本週日期
2. 列出：本週活動名稱 + 客戶 + 人數 + 場地
3. 標記：備料截止日、外送時間、特殊需求
4. 列出：待跟進報價（QUOTE_DRAFT 狀態為 pending 的）

**容易卡住的點**：
- TimeTree JSON 裡的客戶名是中文，注意編碼
- 活動可能臨時取消或改期，以最新 TimeTree 資料為準
- 不要列已完成的活動（已結案的在「已結案_Completed Orders」資料夾）

**必讀**：data/timetree_events_2022_2026.json

---

## 不需要做的（對這間公司規模不必要）

- ❌ 供應商管理系統（一頁廠商名錄就夠）
- ❌ 發票自動整理（規模還不需要）
- ❌ 庫存管理（外燴是按活動採購，不囤庫存）
- ❌ 複雜的成本分析模型（先用簡單的品項成本 × 數量）
