# GO / 長跑提示詞標準模板

> 來源：`docs/references/ai-agent-long-running-go-feature-rubric.md`
> 用途：任何要讓 agent 無人介入跑多輪（`/go` 類、background task、cron 觸發的長任務）
> 之前，先用這份模板把「完成」定義寫死。**不是 prompt 技巧，是把模糊的完成標準變成
> 可檢查的五件事。**
> 使用方式：複製本檔到實際任務（或貼進 task card 的 Definition of Done 區塊），
> 把五段都填滿才能開始無人長跑。任何一段留空 = 不能開始。

---

## 1. Outcome（完成狀態）

**填寫說明**：用一句話描述「完成時世界看起來是什麼樣子」，不是「做了什麼動作」。
要可以讓另一個人（不是你）讀完就知道何時該喊停。

**範例**：
> 完成狀態：`bot_a6/a5_quote_engine.py` 的 `build_sheet_quote_payload()`
> 對任意輸入的人數+主食/毛利需求，都能產出合法 `createQuoteVariants` payload，
> 且 GAS 回傳的 Google Sheet `報價單!D2:F31` 沒有空白品項列、`I7:J31` 毛利率
> 落在 70%-85% 之間。

---

## 2. Verification（如何驗證）

**填寫說明**：寫出**誰**來檢查、**用什麼工具**檢查，優先用外部客觀工具
（測試套件、py_compile、Playwright 截圖、live API 回讀、ffprobe 等），
不要寫「模型自己覺得做完了」。如果驗證只能靠人眼，要明確寫「需要人眼介入」，
不能假裝是自動化驗證。

**範例**：
> 驗證：
> 1. `pytest -q tests/test_a5_quote_engine.py` 全綠。
> 2. 用 3 組不同人數/預算組合各跑一次，讀回 Google Sheet
>    `報價單!D2:F31` 與 `I7:J31`，人工核對毛利率落在範圍內。
> 3. 不接受「模型輸出看起來合理」當完成依據。

---

## 3. Constraint（不能動什麼）

**填寫說明**：列出長跑期間絕對不能碰的東西。**至少要包含**：
- runtime 資料（live DB、正式 Sheet、broker/帳務）
- secrets / `.env` / API keys / cookies
- `main` branch（長跑只能在 worktree/sandbox/branch 上跑，看
  `docs/governance/unattended-run-safety.md`）
- 任何需要 Owner 批准才能做的動作（發布 WordPress、改 Ads 預算等，
  見 `AGENT_RULES.md` SECTION 8.5）

**範例**：
> 不能動：
> - 不直接寫 `MAPLAB_外燴系統_v0.1` 正式 Sheet，只能在 `makeCopy()` 出來的副本上跑。
> - 不讀 `.env`、不印出任何 token/key。
> - 不 push `main`；所有改動留在本地分支等 review。
> - 不下單、不建模擬單（Investment OS 任務適用）。

---

## 4. Iteration Policy（每輪記錄）

**填寫說明**：規定每一輪 executor 跑完後，必須往一份 **append-only** 日誌寫一筆，
包含三件事：**改了什麼 / 結果是什麼（含失敗）/ 下一步打算做什麼**。
不得覆寫舊紀錄，只能往後追加——這份日誌本身就是長跑唯一的事後稽核依據。

**範例**：
> 每輪結束後 append 一筆到
> `workbook/reviews/JOB-<TASK>-<DATE>/iteration_log.jsonl`：
> ```json
> {"round": 3, "changed": "改 build_sheet_quote_payload() 處理 0 人數邊界",
>  "result": "pytest 28/30 pass，2 fail 是既有已知問題",
>  "next": "修第 29 個測試的 mock 資料"}
> ```

---

## 5. Error Handling（何時暫停回報）

**填寫說明**：列出**遇到什麼情況必須立刻停下來回報，不能硬幹繼續**。
至少要包含：連續 N 輪沒進展、碰到 Constraint 列的禁區、驗證工具本身壞掉、
token/時間/iteration 上限到了（見 `docs/governance/unattended-run-safety.md`）。

**範例**：
> 立刻暫停回報的情況：
> - 連續 3 輪 `pytest` 失敗數沒有下降。
> - 任何一輪需要寫 Constraint 列出的禁區（例如要改正式 Sheet）。
> - 跑滿 20 輪或 2 小時，不論是否完成。
> - 驗證工具本身出錯（例如 GAS API timeout），不能跳過驗證直接判定完成。

**填寫指引（自主/升級判準，Escalation Policy，2026-06-21 新增）**：
判斷「要不要回頭問 Owner」的標準：

- **可逆 ＋ 低風險 ＋ 在 scope 內** → agent 自己決定、繼續執行，**不准回頭問
  Owner**（回頭問等於偷懶/下班心態）。
- **符合任一即必須暫停回報**：不可逆動作、碰 runtime 資料、碰
  secrets/.env/金錢、push main 或改真相來源、或任務目標本身模糊未定義。
- **一句話原則**：可逆的自己扛，不可逆的才升級。

見 `AGENT_RULES.md` SECTION 19「自主/升級判準」、
`docs/governance/unattended-run-safety.md` 同名段落——三處措辭一致。
