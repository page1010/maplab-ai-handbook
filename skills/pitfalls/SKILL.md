# Skill: pitfalls — MAPLAB AI 協作重複失敗 pattern

> 版本：v1.0 ｜ 建立：2026-04-08 ｜ 來源：60+ session 事後檢討 + commit log + handoff/feedback/

## 為什麼存在

這份文件從 60+ 個舊 session 中提煉出 7 個重複失敗 pattern。
同一個坑被踩了 3-5 次以上，每次都要花 1-3 小時修復。

**任何新 session cold-start 必讀。開始 GAS/Sheets/clasp 任務前必掃對應章節。**

---

## 使用方式

- **Cold start**：掃一眼 Pattern 清單標題，確認自己沒在踩任何一個
- **開始高風險任務前**：GAS push / Sheet 寫入 / 版本迭代 → 讀對應 Pattern
- **遇到類似情境**：停下來對照「偵測訊號」，確認再繼續

---

## Pattern 清單

---

### P1: Clasp 推到錯的 GAS 專案

**真實案例**：
- `844995e` (2026-04-04)：A0 連續多天把 Code.gs v3.1~v3.8 全部 push 到 LINE 對話專案，報價系統的 GAS 完全沒被動到。發現時距離第一個錯誤 commit 已超過 3 天。
- `aac5c75` (2026-04-07)：createSlides.gs 幻覺清理時，再度確認 LINE 專案裡有報價系統的函數殘留。

**根本原因**：
`.clasp.json` 的 `scriptId` 指向 LINE 對話專案（`1Fkl34P7p395k0...`），而非報價系統（`1JIiPW_OUwNzB...`）。Agent 沒有在 push 前確認 scriptId，只看到 clasp 成功就以為推對了。

**偵測訊號**：
- 你準備執行 `clasp push` 但還沒確認 `.clasp.json` 內容 → **停**
- 剛 clasp push 完，但在 Sheet 裡「擴充功能 > Apps Script」看不到你改的函數 → **推到錯的專案了**
- 報價系統的 Code.gs 改動「消失了」→ **確認 scriptId**

**預防做法**：
1. `clasp push` 前必讀 `.clasp.json`，確認 `scriptId` 符合你的目標：
   - 報價系統 = `1JIiPW_OUwNzB4VHS4k0KHi7LYDdPlFgHWejotsY4KE3KdLTc3EB-0vpc`
   - LINE 對話 = `1Fkl34P7p395k0YzwY8hyhz7DAAsgA3CBgyumx9ImSOFoXu771lFABSi7`
2. 從 Sheet 的「擴充功能 > Apps Script」確認 Bound Script ID，不信任 repo 裡的 `.clasp.json`
3. 推完後，立刻在 Apps Script 編輯器確認函數存在

---

### P2: setValue 覆蓋 QUOTE_DRAFT 公式與下拉驗證

**真實案例**：
- `afdd067` (2026-04-04)：Code.gs 的 `writeItemsToQuote_()` 用 `setValue` 寫入品項名稱，同時清空了 I/J 欄的 VLOOKUP 公式，導致毛利率計算失效，需要用 Google Sheets 版本紀錄還原到 04-03 17:00。
- `7e54645` (2026-04-04)：v3.7 修復：改為只寫 D/G 欄，停止覆蓋 I/J 欄公式。
- `78cdb0c` (2026-04-04)：v3.8 再度修復：`createQuote` 移除品項篩選呼叫，確保不碰 D 欄公式。

**根本原因**：
GAS 的 `Range.setValue()` 會直接覆蓋公式，`clearDataValidations()` 會清除下拉驗證。Agent 沒有區分「可寫入」欄位與「公式保護」欄位就直接寫入。

**偵測訊號**：
- 你的 Code.gs 準備寫入 QUOTE_DRAFT 的某個 Range → 先確認那個 Range 是否有公式
- 你看到 I 欄或 J 欄原本有 VLOOKUP，但你的程式碼要 `setValue` 那個範圍 → **停**
- `clearDataValidations()` 的範圍包含 D8:D22 → **停，這是品項下拉驗證**

**預防做法**：
1. 讀 `handoff/feedback/2026-04-02-quote-draft-v3-layout.md` 確認每個欄的用途（公式欄 vs 輸入欄）
2. QUOTE_DRAFT 欄位分工：
   - **可寫入**：D 欄（品名，純文字）、G 欄（數量）、K 欄（系統狀態）
   - **禁止覆蓋**：I 欄（業務報價）、J 欄（小計）— 有 VLOOKUP 公式
3. 如需清除品項區，用 `clearContent()` 不要用 `setValue("")`，且只清指定範圍
4. `AGENT_RULES.md SECTION 11` 有完整 QUOTE_DRAFT 保護規則

---

### P3: 呼叫不存在的 GAS API 函數（幻覺）

**真實案例**：
- `2fa4c53` (2026-04-04)：`createSlides.gs:109` 寫 `presentation.moveSlide(slide, index)`，但 Google Slides API 沒有這個方法。正確是 `slide.move(index)`（Slide 物件的實例方法）。
- `aac5c75` (2026-04-07)：A0 在多個 session 呼叫 `createSlidesFromSheet()`，但這個函數從來不存在於報價系統專案。根本原因是 `.clasp.json` 指向 LINE 專案，看到 LINE 專案的函數清單就幻覺出來的。
- `aac5c75` (2026-04-07)：`LINE createSlides` — 從 LINE 專案的錯誤 scriptId 衍生出整套不存在的 Slide 生成流程。

**根本原因**：
1. Agent 憑印象或邏輯推測 API 方法名，沒有查官方文件
2. 混淆兩個 GAS 專案的函數清單，把 A 專案的函數當成 B 專案在呼叫

**偵測訊號**：
- 你準備呼叫一個 GAS 方法，但你沒有從官方文件或 `clasp pull` 結果確認它存在 → **先查**
- 你在寫 `presentation.someMethod()` → 查 [Apps Script Presentation Class](https://developers.google.com/apps-script/reference/slides/presentation)
- 你呼叫一個函數，GAS 回傳 `TypeError: xxx is not a function` → **那個函數不存在**

**預防做法**：
1. 呼叫 Slides API 前，到官方文件確認方法名：
   - `Presentation` 類別：`getSlides()`, `appendSlide()`, `insertSlide()`
   - `Slide` 類別：`move(index)`, `duplicate()`, `remove()`
   - **不存在**：`presentation.moveSlide()`, `createSlidesFromSheet()`
2. 呼叫本地函數前，先 `clasp pull` 確認函數清單（或從 Apps Script 編輯器確認）
3. 新寫任何函數前，先 `grep -r "functionName" scripts/apps-script/` 確認不重複

---

### P4: 版本漂移 — 每次迭代都破前一版

**真實案例**：
- 2026-04-03~04：Code.gs 從 v3.1 迭代到 v3.8，共 8 個版本。每個版本都修了上一版的 bug，但同時引入新 bug。過程中：v3.3 修 cell reference 但破 D 欄；v3.5 修 D 欄但 I/J 被覆蓋；v3.6 修 I/J 但殘留模板 bug；v3.7 修 I/J 覆蓋但品項篩選邏輯又壞。
- `bf487e2` (2026-04-04)：v3.3 大幅修改 cell reference，但沒有先讀版面文件確認，結果時間欄 E3 vs F3 又搞錯。
- `d7b478b` (2026-04-03)：v3.2 自我檢討：根因是沒讀 `2026-04-02-quote-draft-v3-layout.md` 就開始改 code。
- `78cdb0c` (2026-04-04)：**v3.8 最終結局 = 完全回滾**。放棄 v3.1~v3.7 所有迭代，退回接手前版本（客戶資料寫 B2:B9）。7 個版本工作全部作廢。根因：開始改 code 前沒讀 QUOTE_DRAFT 版面文件，不知道正確 cell 在哪裡，用猜的。
- **殘留問題（v3.8 回滾後）**：`generateProposal_v2.gs` 在 v3.x 時期按新版面寫成（讀 D2/E2/D3/D4/F4），v3.8 回滾後 createQuote 改寫 B 欄，導致 generateProposalV2 讀到空值，Slide 提案客戶姓名/日期/地點全部顯示 '-'。這就是「業務填兩次」的根源。

**根本原因**：
每次修 bug 只看症狀，沒有對照「版面真相來源文件」確認所有 cell reference 一次到位。改了一個地方，其他地方的假設就失效了。

**偵測訊號**：
- 你要改 Code.gs 的 cell reference，但你還沒讀 `handoff/feedback/2026-04-02-quote-draft-v3-layout.md` → **先讀**
- 你在 `v3.X` 上修 bug，但你不確定 v3.(X-1) 的變動是什麼 → **先 `git log --oneline` 確認前一版改了什麼**
- 你要加新功能但沒有先跑現有測試確認現狀正確 → **先測試**

**預防做法**：
1. 改 Code.gs 前，必讀 `handoff/feedback/2026-04-02-quote-draft-v3-layout.md`（cell reference 唯一真相）
2. 每次改動範圍控制在最小：只改你確認要改的欄位，不順手「清理」周邊代碼
3. `git diff HEAD~1` 確認上一個版本改了什麼，確保本次不會覆蓋
4. `AGENT_RULES.md SECTION 10` 要求每次改動前釐清需求，避免連鎖 bug

---

### P5: 狀態誤判 — 把 X 當成 blocker 其實是 Y

**真實案例**：
- `d233501` (2026-04-07)：調查結論是「Items.D 欄 `default_price` 全空 = blocker」，寫了完整的調查報告（`2026-04-04-items-price-investigation.md`），花了大量時間分析。但 2026-04-07 撤銷：QUOTE_DRAFT 的公式 `VLOOKUP(D, Items!C:E, 3, 0)` 查的是 **E 欄 `default_cost`**，不是 D 欄。D 欄從未被任何流程讀取，根本不是 blocker。

**根本原因**：
Agent 看到 D 欄全空 → 假設是問題 → 沒有實際追蹤公式引用路徑確認 → 宣告為 blocker。

**偵測訊號**：
- 你準備把某個空欄位宣告為 blocker → 先確認：「有哪個公式或函數實際讀這個欄位？」
- 你在 Sheets 看到一個空欄，但你沒有用 `Ctrl+H` 或 `FORMULATEXT` 確認它有無下游引用 → **先查**
- 調查報告超過 2 頁但你還沒有追蹤到真正的讀取路徑 → **返回確認引用**

**預防做法**：
1. 宣告 blocker 前，必須追蹤「讀取路徑」：
   - 公式引用：在 Sheets 點選儲存格，看公式欄位
   - GAS 引用：`grep -n "columnName\|欄位名" scripts/apps-script/*.gs`
2. 不同欄位分工要從文件確認（`handoff/feedback/` 最新版面文件），不從欄位名推測
3. D 欄（`default_price`）確認為不使用欄位，E 欄（`default_cost`）才是 VLOOKUP 目標

---

### P6: Session/角色混淆

**真實案例**：
- EXP-F008, EXP-F009 (2026-03-27)：A0 開了 30+ 個 Code task，每個都沒有貼 A1 recall prompt，導致每個 session 都是失憶狀態，重新推測自己的角色。
- EXP-S010 (2026-03-28)：Owner 重開 session 幫 A1 拿 MCP 工具時，session 誤以 A0 模式啟動，大改 `skills/mcp-usage-guide.md`，A1 完全失憶。
- `CURRENT_STATUS.md` 警告：「重開後先確認 cwd 為 maplab-ai-handbook/，再貼 A1 recall prompt。」

**根本原因**：
多個 Agent（A0/A1）共用同一個 Git repo，但身份靠 prompt 注入，不靠環境自動判斷。重開 session 沒有貼 recall prompt，或貼了錯的 prompt，導致 Agent 以錯誤身份執行操作。

**偵測訊號**：
- 新 session 開始，你不確定自己是 A0 還是 A1 → **先確認 cwd 和 CLAUDE.md**
- 你在修改 `skills/` 目錄的文件，但你以為你是 A0（Cowork，不在 repo 裡） → **身份混淆了**
- 你的 CURRENT_STATUS 跟記憶裡的不一樣 → **重新讀 AGENT_RECALL_PROMPTS.md**

**預防做法**：
1. 每次 session 開始，先確認：
   ```bash
   pwd  # 應為 maplab-ai-handbook/
   cat CLAUDE.md | head -5  # 確認是 A1 身份文件
   ```
2. Cold start 必須走完 CLAUDE.md 的完整啟動流程，不跳步
3. A0（Cowork）開 Code task 給 A1 時，必須在 prompt 裡包含 CLAUDE.md 引用或 A1 recall prompt
4. 有疑問先讀 `AGENT_RECALL_PROMPTS.md ## A1 段落`，不要假設

---

### P7: 跳過原始文件直接寫 Code

**真實案例**：
- `d7b478b` (2026-04-03)：v3.2 自我檢討確認：「handoff/feedback/2026-04-02-quote-draft-v3-layout.md 已有完整版面對照表，但我在寫 v3.1 時沒有讀這份文件就直接跑測試，用了舊的 cell references。」
- `bf487e2` (2026-04-04)：v3.3 再次用猜的 cell reference，修了 4 個但仍有 E3（時間）vs F3 錯誤。
- `2026-04-04-items-price-investigation.md`（已撤銷）：花了完整調查報告分析 D 欄，但事後確認只要讀公式就能在 5 分鐘內釐清。

**根本原因**：
Agent 傾向「先寫再測試」，不傾向「先讀文件再寫」。當文件已存在且是唯一真相時，跳過文件 = 保證寫錯。

**偵測訊號**：
- 你要寫 Code.gs 或改 GAS 邏輯，但你還沒讀 `handoff/feedback/` 的最新版面文件 → **先讀**
- 你要調查一個「為什麼 X 不工作」的問題，但你還沒看 Sheets 公式欄 → **先看公式**
- 你花超過 30 分鐘在一個問題上，但你還沒讀所有相關文件 → **停下來先讀完**

**預防做法**：
1. 改任何 GAS/Sheets 相關邏輯前，必讀順序：
   - `handoff/feedback/2026-04-02-quote-draft-v3-layout.md`（QUOTE_DRAFT cell mapping）
   - `handoff/feedback/2026-04-04-gas-architecture-issue.md`（GAS 專案架構）
   - `AGENT_RULES.md SECTION 10`（開發行動準則）
2. 調查問題的正確順序：讀公式 → 讀文件 → 才考慮寫程式
3. 文件是唯一真相，記憶不是

---

## P11: 文件標記 ≠ 實際狀態 — 必須驗證
> 來源：2026-04-12 A0 session — bot/DEPRECATED.md 說「棄用」但 PID 在跑

DEPRECATED / 已修復 / 已完成 / ✅ — 這些標記只代表「寫的人當時認為如此」。
驗證方式：ps aux / launchctl list / Chrome 眼見為憑 / git log。
不驗證就斷言 = 幻覺。

## P12: handoff log 必須完整讀完
> 來源：2026-04-12 A0 session — 只讀前 80 行就斷定 e2e 沒通過

未完成清單是 session 過程中的快照，後面的段落可能已經記錄完成。
只讀開頭就下結論 = 跟只看 commit message 不看 diff 一樣危險。

## P13: 檢查檔案存在用 ls，不用花式 one-liner
> 來源：2026-04-12 A0 session — python3 -c parse 失敗誤判為「檔案不存在」

ls -la path/to/file 是唯一可靠的存在性檢查。
用 cat | python3 -c 或 jq 等工具鏈，任何一環失敗都會誤報。

---

## 快速對照表

| 場景 | 對應 Pattern | 停下來做什麼 |
|------|------------|------------|
| 要 `clasp push` | P1 | 確認 `.clasp.json` scriptId |
| 要 `setValue` 寫入 Sheet | P2 | 確認目標 Range 沒有公式 |
| 呼叫 GAS API 方法 | P3 | 查官方文件確認方法名存在 |
| 改 Code.gs cell reference | P4 | 先讀版面文件 |
| 宣告某欄為 blocker | P5 | 追蹤引用路徑 |
| 不確定自己是哪個角色 | P6 | 讀 CLAUDE.md 確認身份 |
| 準備直接開始寫 code | P7 | 先讀完相關文件 |

---

## 關聯

- `AGENT_RULES.md`（基礎治理規則，SECTION 10/11）
- `handoff/feedback/`（本文件的原始案例來源）
- `skills/experience-log.md`（成功/失敗 EXP 紀錄）
- `skills/clasp-deploy-guide.md`（clasp 操作 SOP）
- `skills/sheet-version-restore/`（Sheets 版本還原技能）
