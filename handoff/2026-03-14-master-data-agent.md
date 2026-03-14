# 交接紀錄 — 2026-03-14 Master Data Agent (A5)

## 我是誰

- 角色：Master Data Agent
- 模型：Claude Opus 4.6（透過 Anthropic Browser Tool）
- 任務來源：用戶指令 — 修復 Dashboard + QUOTE_DRAFT 收尾 + 版本紀錄

## 本次完成事項

- [x] **Dashboard #REF! 修復** — A15 QUERY 公式加 LIMIT 10（commit: f7b2097）
- [x] **QUOTE_DRAFT v0.3 品項分類中文化** — 15 筆品項 category 從英文改中文
- [x] **GitHub v1.3 版本紀錄** — SECTION 6 + SECTION 9 更新（commit: f7b2097）

## 驗證確認

- Dashboard：A15 正常顯示 10 筆 overdue/partial 訂單，不再 #REF!
- QUOTE_DRAFT：C29:C43 分類已改為 甜點/餐食小點/主食/飲品
- GitHub：https://github.com/page1010/maplab-ai-handbook/blob/main/projects/maplab-master-data.md (v1.3)

---

## 🧠 經驗分享：遇到的困難、解決方法、工具使用

### 困難 1：Dashboard #REF! 根因診斷

**問題：** Dashboard A15 的 QUERY 公式顯示 #REF!，錯誤訊息為「系統未展開陣列結果，以免覆蓋 A26 中的資料」。

**診斷過程：**
1. 點擊 A15 讀取完整 QUERY 公式
2. 發現 QUERY 查詢 Orders!A2:AC 中 `Z = 'partial'` 且日期過期的記錄
3. 用 COUNTIFS 臨時公式測試 → 發現有 411 筆符合條件的記錄
4. A26 有「Prep List - Upcoming」佔位 → QUERY 試圖展開 411 行但被 A26 擋住

**曾嘗試問 Gemini：** ✅ 是的，有在 Gemini tab 詢問 Dashboard #REF! 修法，但 Gemini 給的回覆偏通用（建議檢查公式引用範圍），沒有針對「QUERY 陣列展開被下方儲存格擋住」這個具體問題給出答案。

**最終解決：** 自行判斷加 `LIMIT 10` 到 QUERY 語句中，限制輸出最多 10 行。這樣 A15:A24 顯示資料，A25 空白，A26 Prep List 不受影響。

**學到的經驗：**
- Google Sheets QUERY 的 array spill 特性：如果結果行數會覆蓋到下方有資料的儲存格，就會報 #REF!
- LIMIT 子句是控制 QUERY 輸出行數最簡單的方式
- 問 AI 時要給具體的錯誤訊息和公式內容，否則回覆容易偏通用

### 困難 2：Google Sheets 儲存格輸入覆蓋 vs 追加

**問題：** 在 QUOTE_DRAFT 品項 category 欄位（C29:C43）想把英文改中文，直接用 type 指令打字，結果中文被「追加」到英文後面（如 `dessert甜點`），而非替換。

**原因：** 在 Google Sheets 中，選取一個有值的儲存格後直接 type，行為等同於「進入編輯模式＋游標在文字末端」，所以打的字會接在原文後面。

**錯誤嘗試：** 用 Cmd+Z 撤銷了所有打字，但 Google Sheets 的 undo 堆疊是跨 sheet 的 —— 撤銷過頭會連 Dashboard 上的 QUERY 修復也一起還原。

**最終解決：** 改用 **Find & Replace**（尋找並取代）功能：
1. 先選取 C29:C43 範圍
2. 開啟 編輯 → 尋找並取代
3. 勾選「整個儲存格內容需相符」確保精準比對
4. 分四次替換：dessert→甜點、appetizer→餐食小點、main→主食、beverage→飲品

**學到的經驗：**
- Google Sheets 的 type 行為：會追加而非覆蓋。要覆蓋必須先 Delete 清空或用 Find & Replace
- Find & Replace 搭配「整個儲存格內容需相符」是批次修改最安全的方式
- Undo 堆疊跨 sheet：如果在不同 sheet 做了連續操作，undo 會回溯所有 sheet 的操作

### 困難 3：Google Sheets Frozen Rows 導致滾動失效

**問題：** QUOTE_DRAFT 有凍結行（rows 1-4 + row 28 header），導致用 scroll 指令滾動時，下方的品項資料看不到（被凍結區佔滿畫面）。

**解決：** 改用 Name Box（左上角儲存格參照輸入框）直接跳轉到目標儲存格（如 A35、A43），繞過滾動限制。

**學到的經驗：**
- 凍結行多的 Sheet，scroll 指令效果差。直接用 Name Box 輸入儲存格座標跳轉最快。

### 困難 4：GitHub CodeMirror 6 編輯器 API

**問題：** GitHub 的編輯模式使用 CodeMirror 6，不能直接操作 DOM 或用 type 指令精確插入文字到長文檔中間。

**解決：** 透過 JavaScript 找到 CodeMirror 6 的 view 物件：
```javascript
const cmContent = document.querySelector('.cm-content');
const view = cmContent.cmTile.view;
const text = view.state.doc.toString();
// 用 string replace 修改內容
view.dispatch({ changes: { from: 0, to: text.length, insert: newText } });
```

**學到的經驗：**
- GitHub 編輯器的 CM6 view 物件路徑是 `.cm-content` → `.cmTile.view`
- 用 `view.state.doc.toString()` 取得全文，string replace 修改後，用 `view.dispatch()` 整批寫回
- 這比試圖用鍵盤游標移動到文件特定位置更可靠

### 困難 5：GAS (Google Apps Script) Monaco 編輯器無法儲存

**問題（前次遺留）：** 在 Apps Script 編輯器中新建函式 tab，用 type 指令輸入 GAS 程式碼，但 Monaco 編輯器的 save 快捷鍵（Cmd+S）無法觸發——因為 type 操作不會標記 Monaco 的 dirty state。

**狀態：** 未解決。這是 Browser Tool 操作 Monaco 編輯器的已知限制。
**建議：** 需要執行 GAS 功能時，建議直接在已有的 .gs 檔案中追加程式碼，而非新開 tab。

---

## 工具使用總結

| 工具 | 用途 | 效果 |
|------|------|------|
| Anthropic Browser Tool (Claude Opus 4.6) | 主要操作——讀取/編輯 Sheets、GitHub commit | ✅ 主力 |
| Google Gemini | 詢問 Dashboard #REF! 修復方案 | ⚠️ 回覆偏通用，未解決具體問題 |
| Google Sheets Find & Replace | 批次替換品項分類（英文→中文）| ✅ 精準高效 |
| GitHub CodeMirror 6 JS API | 編輯 markdown 文件內容 | ✅ 可靠 |
| Google Sheets Name Box | 跳轉凍結行下方的儲存格 | ✅ 繞過滾動限制 |

## 有沒有問其他 AI？

- **Gemini：** ✅ 有問。在 Gemini tab 詢問 Dashboard #REF! 修法，但回覆偏通用未解決具體問題。最終自行診斷解決。
- **其他 AI：** 未使用。

---

## 未完成 / 卡點

- Row 5 隱藏分隔行：GAS unhideRows() 無法在新 tab 儲存（Monaco save 限制），標記為已知限制
- Items 命名規則對齊（v0.2 DST001 格式 vs ITEM_MASTER DES-MAC-001 格式）—— 待其他 agent 完成 ITEM_MASTER 填入後再對齊

## 下一棒待辦（按優先順序）

- P1 Master Data Agent：ITEM_MASTER 資料持續填入（截圖 + 逐條新增）
- P2 Master Data Agent：PRICE_MASTER 資料填入（依賴 ITEM_MASTER 完成）
- P3 Master Data Agent：Items 命名規則對齊至 ITEM_MASTER 格式
- P4 任意 Agent：GAS 腳本 MVP — Google Slides 模板替換 + PDF 匯出

## 關鍵資源

- GitHub repo：https://github.com/page1010/maplab-ai-handbook
- master-data.md (v1.3)：https://github.com/page1010/maplab-ai-handbook/blob/main/projects/maplab-master-data.md
- MAPLAB_外燴系統_v0.1：https://docs.google.com/spreadsheets/d/1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
- Gemini 對話：https://gemini.google.com/app/0c2119dc42bac5ec
