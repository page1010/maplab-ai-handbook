# Skill: first-principles-check — 第一性原理檢查清單

> 版本：v1.0 ｜ 建立：2026-04-08 ｜ 來源：60+ session 事後檢討 + handoff/feedback/ + pitfalls

## 為什麼存在

過去 60+ session 裡，**大多數的連環錯誤都不是技術問題，是思考問題**：

- 修上一版的 bug 而不問「為什麼會有這個 bug？」
- 把「系統目前在做什麼」當成「使用者要什麼」
- 照著文件寫，不問「文件還成立嗎？」
- 接受「流程就是這樣」而不問「流程本來就該這樣嗎？」

結果：v3.1 → v3.8 連環錯（7 個版本全廢）、業務被迫填兩次單、default_price 誤判為 blocker、createSlidesFromSheet 幻覺追了好幾輪 ...

**任何 cold-start session 必讀。設計決策或 debug 超過 3 輪還沒解決 → 強制跑這份 checklist。**

---

## 使用時機

- **Cold start 必讀**（跟 pitfalls、glossary 並列為三件套）
- **開始任何設計決策或架構選擇前**
- **同一個問題 debug 第 3 輪還沒解決** → 強制停下來跑 checklist
- **Owner 問「為什麼要這樣？」時** → 用這個 checklist 回答，不要反射性解釋現況

---

## 鐵律 0：實況永遠勝過文件（Sheet is truth, repo is doc）

**在所有問題之前，先搞清楚真相來源的優先順序：**

| 真相順位 | 來源 | 為什麼 |
|---------|------|--------|
| **第一順位（Ground truth）** | 活系統：Google Sheet 實際儲存格、部署版 Apps Script 實際執行碼、live API 真實回傳、線上 UI 實際畫面 | 這是「此刻真的在運作的樣子」 |
| 第二順位（線索） | repo 底下任何 .md / handoff/ / layout doc / SOP / README | 這是「某個人當時寫給未來的人看的」。可能過期、可能 aspirational、可能作者自己也是憑印象 |

**規則：**
- 任何「現況是 X」的斷言，必須能追溯到第一順位。第二順位只能當線索，不能當結論。
- 工具失敗（token 過期、API 429、權限不足）不是退回文件的藉口，是觸發三層備援的訊號：API → MCP → Chrome 擴充 JS → computer-use 桌面截圖。**一定要拿到實況。**
- 文件 vs 實況衝突時：實況勝。同時開任務修文件，不要把文件當沒事。

**反面案例 — 信任 layout doc 結果把全系統帶進陰溝（2026-04-08）**：

`handoff/feedback/2026-04-02-quote-draft-v3-layout.md` 自稱「Code.gs 所有 cell references 的唯一真相來源」，裡面宣稱 QUOTE_DRAFT 的 `E2 = 活動日期值`。於是：

1. 2026-04-03 commit 4301369 `createQuote()` 照 layout doc 寫 `E2 ← eventDate`
2. `generateProposal_v2.gs` 也照 layout doc 讀 `E2 → eventDate`
3. 兩邊內部一致，看起來沒問題

2026-04-08 用 Chrome 擴充的 fetch 直接打 Google CSV export 端點讀 live sheet，發現：

- **C2~C5 和 E2~E5 都是標籤欄**（C2="客戶"、E2="\ndate"、E3="\n時間\n\n"、E4="規劃人數"、E5="餐點總件數"）
- **D2~D5 和 F2~F5 才是值欄**
- Layout doc 自己的 Row 3~5 mapping 都是「C=label、D=value、E=label、F=value」的對稱結構，**只有 Row 2 的 E2 被誤記成值欄** — 作者從截圖肉眼判讀時把標籤「\ndate」誤讀成日期值
- Code.gs 寫 E2 = 把模板的「date」標籤覆蓋掉（副本看起來沒標籤，像孤兒日期）
- generateProposal_v2.gs 讀 E3 = 把「\n時間\n\n」這個標籤字串當時間值塞進 Slide

**第一順位檢查本來只要打一個 CSV export 端點就會抓到。**沒人做，因為大家都信文件自稱的「唯一真相來源」。這是第二順位蓋過第一順位的典型災難。

**第一性原理答案**：`sheet.getRange('E2').getValue()` 比 `grep -n E2 handoff/*.md` 更接近真相。永遠從活系統 verify。

> 來源：commit 4301369 的全系統錯位事件、本次 2026-04-08 live sheet 驗證

---

## Checklist（每題都要答，不能跳過）

---

### 問題 1：業務的理想狀態是什麼？

- 如果沒有現在這套系統，人類會怎麼做這件事？
- 理想狀態下，使用者該填幾個欄位、點幾次按鍵、做幾個步驟？
- 目前系統距離理想狀態差多少？

**反面案例 — 業務填兩次單（2026-04-03~04）**：

v3.x 的整個開發週期，沒有任何一個 agent 問過「業務詢價一次應該填幾次單？」。
他們只問「如何修上一版的 bug」。最終結果：業務要在 QuoteForm 填一次基本資料，在 QUOTE_DRAFT 再手動填一次，因為 generateProposalV2 讀的是 D/E/F 欄，但 createQuote 寫到 B 欄（v3.8 回滾後的現況）。

**第一性原理答案**：一次輸入，多處讀取。填兩次是 bug，不是流程。

> 來源：`checkpoint(A5): QUOTE_DRAFT 欄位對齊` (commit 4301369)、pitfalls P4

---

### 問題 2：現況 ≠ 應然。你看到的是哪一個？

- 我現在描述的是「系統目前的行為」還是「系統應該的行為」？
- 它們一樣嗎？
- 如果不一樣，是 code 錯了還是設計錯了？

**反面案例 — default_price 誤判為 blocker（2026-04-04~07）**：

Items 的 D 欄 `default_price` 全空 → agent 宣告為 blocker，寫了完整調查報告（`2026-04-04-items-price-investigation.md`）。但 QUOTE_DRAFT 的 VLOOKUP 公式 `=VLOOKUP(D8, Items!C:E, 3, 0)` 查的是 **E 欄 `default_cost`**，不是 D 欄。D 欄從來沒被任何公式或函數讀取，根本不是 blocker。

現況（D 欄空）被誤判為問題，而應然（用 E 欄）才是正確設計。調查花了大量時間，最終 2026-04-07 撤銷（commit d233501）。

**第一性原理答案**：先問「有誰在讀這個欄位？」才能判斷它是否真的是問題。

> 來源：pitfalls P5、handoff/feedback/2026-04-04-items-price-investigation.md

---

### 問題 3：這個限制是真的還是假的？

- 「這件事做不到」是技術上做不到，還是上一版程式沒做而已？
- 「一定要這樣」是業務需求還是上個 agent 的錯誤猜測？
- 「從來都這樣」是習慣還是真實限制？

**反面案例 — createSlidesFromSheet 幻覺（2026-04-07）**：

多個 session 的 agent 以為 `createSlidesFromSheet()` 是「還沒實作」的待辦項目，準備要補實作。實際上這個函數從來不該存在 ── 它是 `.clasp.json` 指向 LINE 對話專案（而非報價系統）時看到的 LINE 專案函數清單，產生的幻覺。

「缺少的函數」被當成「需要新增的功能」，而真正的限制（clasp 指錯專案）完全沒人去查。

**第一性原理答案**：任何「缺失的函數」先問「它應該存在嗎？在哪個專案？」不要反射性去補實作。

> 來源：pitfalls P3、checkpoint aac5c75

---

### 問題 4：如果你從頭設計，你會這樣做嗎？

- 忘掉目前 code 是怎麼寫的
- 純粹從業務需求出發，你會設計什麼架構？
- 如果答案跟現況差很多 → 現況有問題，不是你理解錯

**反面案例 — v3.1→v3.8 連環錯（2026-04-03~04）**：

Code.gs 從 v3.1 迭代到 v3.8，共 8 個版本，每版都在修上一版的 bug。過程：
- v3.3 修 cell reference，破了 D 欄
- v3.5 修 D 欄，I/J 被 setValue 覆蓋
- v3.6 修 I/J 覆蓋，殘留模板 bug
- v3.7 修模板 bug，品項篩選邏輯又壞
- **v3.8 最終結局：完全回滾**，7 個版本工作全部作廢

從頭設計的答案很簡單：`makeCopy()` 複製模板 → 只寫客戶資料欄（D/E/F）→ 保留所有公式。但沒有任何一個 agent 停下來問這個問題。

**第一性原理答案**：從頭設計 = 複製模板、寫指定欄、不碰公式。七個版本猜的，一個問題就解決了。

> 來源：pitfalls P4、handoff/feedback/2026-04-04-a0-changes-audit.md

---

### 問題 5：文件說什麼 ≠ 實際是什麼，你確認過現況嗎？

- 文件是「某時刻的應然記錄」
- Sheet/DB/live system 是「此刻的實然」
- 動任何事之前，先確認實然（開 Sheet 看、跑 code 看、查公式）
- 不能用文件代替看現況

**反面案例 — 跳過原始文件直接寫 Code（2026-04-03~04）**：

`handoff/feedback/2026-04-02-quote-draft-v3-layout.md` 已有完整的 cell mapping 表，是 Code.gs 所有 cell reference 的唯一真相。但 v3.1 寫的時候沒讀這份文件，用猜的。v3.2 自我檢討後確認了問題（commit d7b478b），v3.3 又再次用猜的，再修出新 bug。

反過來說，2026-04-07 調查 default_price 問題時，agent 花了大量時間讀文件，卻沒有直接去 Sheets 看公式欄，而實際打開 Sheets 看公式只要 5 分鐘就能釐清。

**第一性原理答案**：文件 + 實況都要看。有衝突時，信實況，並更新文件。

> 來源：pitfalls P7、P5、commit d7b478b

---

## 觸發條件（紅旗情境 — 任何一個出現就必跑 checklist）

- Owner 說「為什麼要這樣？」或「這不對吧」
- Owner 說「我以為...」「我記得我請你...」
- 你正在修**第 3 次同一個錯誤**
- 你看到**版號連跳**（v3.1 → v3.2 → v3.3 ...）都在解同一個問題
- 你要動一個「大家都知道是這樣」的東西
- 你準備把**空欄位或缺失函數宣告為 blocker**
- 你準備把「使用者目前在做的事」當成「系統應該做的事」
- 你準備接受「流程本來就是這樣」的說法

---

## 做法（遇到紅旗時）

1. **停下來 30 秒**，不動手
2. 逐一回答 checklist 5 題，寫到對話或 task 描述裡
3. 如果答案顯示「現況是 bug」→ 修現況，不要繞過
4. 如果答案顯示「這是業務真實需求」→ 照做但記錄依據
5. 把結論告訴 Owner，確認方向後才動手

---

## 失敗案例彙總（這些都是沒跑 checklist 的下場）

| # | 案例 | 後果 | 對應問題 |
|---|------|------|---------|
| 1 | v3.1→v3.8 連環錯 | 7 個版本全廢，完全回滾 | Q4 |
| 2 | default_price blocker 誤判 | 花大量時間調查，最終撤銷 | Q2 |
| 3 | createSlidesFromSheet 幻覺 | 多 session 在追一個不存在的函數 | Q3 |
| 4 | 業務填兩次單 | 使用者配合程式 bug 運作 | Q1 |
| 5 | QUOTE_DRAFT 公式被 setValue 覆蓋 | 需要 Sheets 版本紀錄還原 | Q5 |
| 6 | clasp 推到 LINE 專案 | 報價系統 3 天沒被動到，所有改動推錯地方 | Q3/Q5 |
| 7 | Layout doc 把標籤欄 E2 誤當值欄，Code.gs + generateProposal_v2.gs 全跟著錯 | 寫入副本時覆蓋「date」標籤、產 Slide 把「\n時間\n\n」當時間值 | 鐵律 0（實況優先） |

詳情見 `skills/pitfalls/SKILL.md`。

---

## 與其他 skill 的關係（Cold-start 三件套）

| Skill | 角色 | 時機 |
|-------|------|------|
| `skills/pitfalls/SKILL.md` | 過去踩過的坑（回顧式） | Cold start 必讀 |
| `skills/first-principles-check/SKILL.md` | 決策前的思考框架（前瞻式） | Cold start 必讀 + 每次設計決策前 |
| `docs/glossary.md` | 術語統一定義（避免誤解） | Cold start 必讀 |

三者互補，缺一不可。

---

## 追加案例流程

任何 agent 發現新的連環錯誤或思考失誤，在本檔案「失敗案例彙總」表格追加一行，並在 commit 訊息註明：
```
first-principles-check: 追加 "<簡述>" 案例
```
