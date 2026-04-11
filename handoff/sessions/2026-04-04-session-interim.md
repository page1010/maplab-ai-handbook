# Session Note: 2026-04-04 Interim（A0 + A1）

日期：2026-04-04
記錄者：A1
狀態：本日 session 中途記錄（非 session 結束）

---

## 今天完成了什麼

### GAS / 報價系統
- **doPost 路由**：GAS Web App v12 doPost 已上線（2026-04-03 晚間），支援 A6 用 curl POST 觸發報價
- **createSlides.gs**：建立 Slide 報價簡報 GAS 腳本（T-A5-004）
- **syncQuoteStatus**：報價狀態同步邏輯
- **appsscript.json scope**：補齊必要 OAuth scope（Slides/Drive/Sheets）
- **Code.gs v3.8**：還原至接手前版本（createQuote 只寫 B2-B9/H1-H2/M-N/A30-A31，不碰 D 欄公式）

### 治理
- AGENT_RULES v3.9 新增 SECTION 11：QUOTE_DRAFT 保護規則
- 建立 skills/sheet-version-restore/SKILL.md
- 建立 skills/check-rules/SKILL.md（含 QUOTE_DRAFT 公式完整性檢查）
- 更新 CURRENT_STATUS.md：記錄 QUOTE_DRAFT 毀損事件與治理回應

---

## 今天搞砸了什麼（🚨 重大教訓）

### QUOTE_DRAFT 公式覆蓋事件
**發生時間**：2026-04-04 session 期間（多次迭代）

**根本原因**：
- A0 在 createQuote 函數中使用 `setValue` 寫入 I 欄（VLOOKUP 公式格）
- A0 使用 `clearDataValidations` 清除 QUOTE_DRAFT 的 D 欄下拉驗證
- 未在副本上測試，直接在主系統 Sheet 運行

**影響**：
- QUOTE_DRAFT I 欄（品項名稱 VLOOKUP）全部被靜態值覆蓋
- D 欄（品項選擇下拉選單）驗證被清除，業務無法使用
- MVP 報價系統完全損壞

**修復方式**：
- Owner 使用 Google Sheets > 檔案 > 版本記錄 > 查看版本記錄
- 還原到 2026-04-03 17:00 版本

---

## 怎麼修的

1. Google Sheets 版本紀錄還原（非 GAS 版本控制，是 Sheet 資料還原）
2. Code.gs clasp push v3.8 重置為接手前的安全版本

---

## 新增治理規則

| 規則 | 位置 | 內容摘要 |
|------|------|---------|
| AGENT_RULES SECTION 11 | AGENT_RULES.md | QUOTE_DRAFT 模板保護：禁止 setValue I/J 欄，禁止 clearDataValidations，禁止主 Sheet 測試 |
| 版本恢復 SOP | skills/sheet-version-restore/SKILL.md | Google Sheets 版本紀錄還原步驟 |
| 公式完整性檢查 | skills/check-rules/SKILL.md | clasp push 前必做 5 項檢查清單 |

---

## 踩坑清單（2026-04-04）

| # | 坑 | 解法 |
|---|----|----|
| 1 | setValue 寫公式格 = 公式消失 | createQuote 永遠不寫 I/J 欄，這些是模板公式 |
| 2 | clearDataValidations 清下拉 = 業務功能消失 | createQuote 不動 D 欄，下拉驗證是模板設定 |
| 3 | 主 Sheet 直接測試 = 真實資料受損 | 所有 GAS 測試必須先 makeCopy 在副本上跑 |
| 4 | 版本紀錄還原影響所有分頁 | 還原後必須確認 SALES_INTAKE 等其他分頁資料完整 |
| 5 | GAS 版本控制 ≠ Sheet 資料版本控制 | clasp 只管程式碼，Sheet 資料要靠 Sheets 自己的版本記錄 |

---

---

## Slide v2 開發進度（T-A5-004）

### 第三輪測試結果（2026-04-04 下午）

**狀態：基本成功**

本輪修正項目：
- **move bug 修正**：元素移動邏輯錯誤已修正
- **圖片裁切**：品項圖片裁切處理正常
- **空白格移除**：品項數量不足時多餘格子正確移除
- **slide-production-rules 技能**：新增 skills/slide-production-rules/ 技能書

---

## 後續待辦

- [ ] 確認 Code.gs v3.8 在副本上測試 createQuote 正常（Owner 確認）
- [ ] T-A5-004 createSlides.gs 繼續開發（需副本測試）
- [ ] A4 S11 Colab 確認（ETA 已過，需 commit 確認完成）
- [ ] Slide v2 第四輪測試（視 Owner 回饋決定是否繼續迭代）
