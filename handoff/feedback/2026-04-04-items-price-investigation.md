# 問題調查：Items.default_price（D 欄）全空導致品項篩選失效

建立：2026-04-04 ｜ 調查者：A1

---

## 問題描述

Items 表 D 欄（default_price / 售價）全部為空值。
Code.gs 的品項篩選邏輯讀取 D 欄作為售價，空值時 `Number("")` = 0，導致：
- 舊版（v3.2 之前）：price=0 → 毛利率計算失效 → 品項被篩選器跳過 → D 欄寫入全空白
- 症狀：報價單 D8:D19 一片空白，沒有任何品項被寫入

---

## 根因追溯（從 git log + 文件比對）

### Schema 定義（schema-v0.1.md，2026-03-14）
Items 表原始設計中有 `unit_price`（標準售價）和 `cost_per_unit`（成本）兩個欄位。
但 GAS 實際讀取的欄位索引對照（Code.gs v3.5c 行 39 注釋）：
```
A=序號, B=品名, C=品類, D=售價, E=成本, K=圖片URL
```

### 推斷時序
1. **2026-03-14**：schema-v0.1.md 定義 Items 表含 `unit_price`（必填）和 `cost_per_unit`（選填）
2. **2026-03-27 前後**（T-A5-001 完成期）：A5 實際建立 Items 表時，只填了 E 欄（default_cost 成本），D 欄（default_price）留空
3. T-A5-002 踩坑紀錄已明確記載：「G 欄查的是 cost 不是 price：Items.D default_price 全空，但 Items.E default_cost 有值」
4. **2026-04-04（v3.5c commit）**：Code.gs 加入 workaround — 若 D 欄為空，以 `cost / (1 - minMargin)` 反推最低售價

### 為何 D 欄當初是空的？
從文件推斷為**建表時的遺漏**（非刻意設計）：
- schema-v0.1.md 標示 `unit_price` 為必填，但 T-A5-001 完成紀錄中無法確認 D 欄是否有填值
- T-A5-002 首次操作時發現 D 欄全空，記錄在踩坑 #3
- 沒有任何文件說明 D 欄留空是刻意的

### v2 線上版（quote-system-v2.md）的處理方式
v2 規格文件（projects/quote-system-v2.md）中品項篩選的設計是：
- 業務自己在 QUOTE_DRAFT 的 D 欄下拉選品項（不走 GAS 自動篩選）
- G 欄用 VLOOKUP 查 Items.E（成本），非 Items.D（售價）
- 所以 v2 線上版設計上不需要 default_price，可以正常運作

**問題發生在**：v2 轉 v3（GAS 自動篩選品項）時，新邏輯需要 D 欄售價計算毛利率，但 D 欄仍是空的。

---

## 目前 Workaround（v3.5c）

```javascript
// Code.gs 行 324-327
// 若沒有 default_price，依 minMargin 反推最低售價
if (!price || price <= 0) {
  price = cost / (1 - minMargin);
}
```

反推邏輯：用 `成本 / (1 - 最低毛利率)` 算出勉強符合毛利門檻的最低售價。
預設 minMargin = 0.3（30%）。此反推售價僅用於品項篩選邏輯，不會寫入報價單。

**限制**：反推售價是下限，不是 Owner 實際想賣的價格。品項排序和預算分配可能因此不準。

---

## 需要 Owner 提供的資訊

| 問題 | 說明 |
|------|------|
| **每個品項的建議售價** | Items 表 D 欄（108 筆），Owner 填入後 GAS 自動篩選才能用真實售價計算毛利 |
| **是否需要固定售價？** | 還是每次報價售價都由業務手定？如果業務每次手定，D 欄可永遠留空，繼續用反推 |
| **最低毛利率門檻** | 目前 minMargin=0.3（30%），確認是否正確 |

---

## 代辦事項

- [ ] **Owner 填入 Items D 欄售價**（108 筆）— 優先度高，影響品項篩選準確度
- [ ] 若 Owner 確認售價由業務手定，則在 Code.gs 和文件中說明反推是永久設計，加強 log
- [ ] T-A5-002 Blocker 已有記錄（Items.D default_price 全空），確認本調查後可關閉此 blocker
- [ ] 測試：填入幾筆真實售價後，確認品項篩選邏輯選出正確品項

---

## 相關文件

- `handoff/tasks/T-A5-001.md` — Items 表建立紀錄
- `handoff/tasks/T-A5-002.md` — QUOTE_DRAFT 公式踩坑（含 G欄查cost非price說明）
- `handoff/archive/schema-v0.1.md` — Items 欄位原始定義（unit_price 必填）
- `scripts/apps-script/Code.gs` 行 307-327 — 品項讀取 + 反推邏輯
