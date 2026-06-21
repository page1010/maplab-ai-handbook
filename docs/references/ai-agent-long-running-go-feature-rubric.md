# AI Agent 長時間自主運行（/go）+ Rubric 品味量化 — 對 B1-B4 / Investment OS / bot 設計的應用

> 記錄者：B1 Investment OS Builder
> 日期：2026-06-21
> 來源：YouTube — https://youtu.be/PpeCur6fEXc
> 性質：外部知識筆記（safe_file_only，不是系統變更，不影響任何 runtime）

---

## 影片核心

作者讓 AI agent 無人介入連續跑 27 小時。同一時期 Claude Code、OpenAI Codex
與另一家幾乎同時推出 `/go` 類功能：下一個目標後，agent 自己跑到完成，
不再「做一半就停下來問」或「假裝做完」。

**根因（Anthropic 2025 末研究）**：模型看到 context window 快滿時會草草收工——
作者稱這是「下班心態」。不是模型不會做，是它判斷「快沒空間了，先交卷」。

**運作原理** = 雙角色閉環：
- **Executor（實作者）**：照目標做事。
- **Reviewer（評審）**：每一輪對照目標檢查進度，沒達標就逼 executor 繼續，
  不接受「看起來做完了」當完成。
- 前身是社群的 Ralph Loop 插件。

**好的 GO prompt 五要素**：
1. **Outcome** — 目標是什麼。
2. **Verification** — 怎麼驗證算達標。
3. **Constraint** — 不能碰什麼、邊界在哪。
4. **Iteration policy** — 每輪要記錄：改了什麼 / 結果 / 下一步。
5. **Error handling** — 什麼情況要暫停回報，不能悶著頭繼續跑。

> 關鍵不是 prompt 技巧，而是把「完成」這個詞的定義寫清楚、寫死。

## 主觀工作怎麼量化：rubric

Anthropic 把「做一個漂亮網站」這種主觀任務拆成四維度：**設計品質 / 原創性 /
技術執行 / 可用性**。評分權重故意往模型的弱項偏（逼它在弱項上也要打磨），
rubric 當 benchmark 用；reviewer 不是讀程式碼打分，而是用 Playwright
截圖看「實際畫面」打分。美術館網站案例在第 10 輪自己長出 3D 空間創意——
不是 prompt 要求的，是 rubric 逼出來的迭代結果。

兩支影片共同結論：**關鍵是 evaluation（評分標準），不是 prompt engineering
或 context engineering**。

### 六步 SOP：把「品味」拆成可執行的 rubric

1. 先讓 AI 跑一個 baseline，不要一開始就微調 prompt。
2. 自己看 baseline，記下「皺眉的瞬間」+ 具體原因（不是「感覺不對」）。
3. 把皺眉點分類成維度（像上面的設計品質/原創性/技術執行/可用性）。
4. 每個維度寫「具體」案例，不是抽象禁令：
   - ❌「避免 AI 味」（太抽象，模型不知道要改什麼）
   - ✅「絕不用破折號」「不用『不是 A 而是 B』這種句型」
5. 用多樣案例取代單一案例，避免 overfitting：
   - 寫「博物館級質感」→ 所有產出都會變成博物館風。
   - 改成列出 11 種風格讓模型自己選一種，才不會收斂成單一樣板。
6. rubric 丟給 reviewer 跑；初期一定要人工抽查，確認 reviewer 的判斷
   跟你自己的眼睛一致。不一致就回去改 rubric，不是換 prompt。

> 一句話：rubric 表面上是給 AI 的評分標準，實際上是逼你把自己模糊的品味
> 寫成別人能執行的文字。

---

## 綁回 MAPLAB 目標：對 B1-B4 / Investment OS / bot 設計的應用

**1. B1-B4 本來就是 executor + reviewer，但缺「rubric」這一層。**
目前的角色拆分（B1 寫功能、B2 檢查資料流/錯誤、B3 存檔、B4 判斷
continue/pause/refactor）已經是 executor/reviewer 雛形，RSI v0 閉環
（`projects/invest-os-b-role-recursive-self-improvement.md`）也已經有
「B4 抓紅燈 → B2 分類 → B1 修 → B3 存檔」的迴圈。**但 B2 目前審查的標準
是個案判斷，沒有寫成 rubric。** 尤其是主觀輸出（Telegram digest 措辭、
報告格式、客戶文案語氣），目前靠 agent 自己「感覺對不對」，正是影片裡
「皺眉但說不出具體原因」的階段。建議 B2 Reviewer 正式採用 rubric：
先列維度（例如 Telegram digest 可拆成「資訊密度 / 是否有 Q&A 殘渣 /
是否標示資料層級 / 措辭是否內部流程語外洩」），再寫具體案例（像
pitfalls.md 裡已經有的「禁止 `取餐要順`、`動線穩`」就是現成的具體案例，
只是還沒被收進正式 rubric 文件）。

**2. Task Card 可以套五要素當標準模板，降低「任務定義模糊」。**
目前 `handoff/tasks/T-xxx.md` 已經有「上次做到/下一步/Blocker」，但缺
明確的 outcome/verification/constraint/iteration policy/error handling
五件事一起出現在同一張卡。對照 AGENT_STARTUP_PROTOCOL.md 的 Startup
Check（已經有 Test plan / Receipt path），其實已經涵蓋 verification；
真正缺的是 **constraint 寫清楚（哪些檔案/runtime 不能碰）** 和
**error handling 明確的暫停條件**，這兩塊目前散落在各個技能書和
pitfalls.md，沒有變成 task card 的固定欄位。

**3. Trading bot 的「正反立論 + 風報比」本身就是一份 rubric。**
Investment OS 的判斷邏輯（多層敘事、右側交易、左側預期差、嚴格風控）
如果寫成「正方論點 / 反方論點 / 風險報酬比」結構，性質上跟影片的
「設計品質/原創性/技術執行/可用性」四維度評分是同一件事——
都是把主觀判斷拆成可檢查的維度。差別是 Investment OS 目前這套邏輯是
B1-B4 共用的語言（`projects/b1-investment-logic-bridge.md`），但沒有被
明確標記成「這就是我們的 rubric」，也沒有像影片裡那樣用 reviewer
跑分數、跟蹤 reviewer 判斷是否跟人眼一致。

**4. 風險提醒：`/go` 無人長跑會放大既有的危險操作風險。**
影片的模式是「給目標、無人介入跑到完成」。如果這種無人長跑配上
Owner 先前提過的高風險 deploy 腳本模式（例如 `rsync --delete` 這類
會清空目標目錄的操作），一旦 reviewer 沒抓到、executor 又在無人看管
下重複執行，後果會被放大成大規模事故，而不是一次性的小錯。
**長跑前必須先把 constraint 和 error-handling 寫死**：
- 不碰 runtime 資料、secrets、broker/帳務、live WordPress/Ads 發布。
- 遇到不確定或卡住，立即停止並回報，不能「看起來像完成了」就算了。

這兩條目前已經分散在 `AGENT_RULES.md` SECTION 8.5（硬性禁止）和
B1-B4 Guardrails 裡，但都是針對「有人在看」的情境寫的。**建議下次
治理規則更新時，明確新增一條「無人長跑（/go 類、cron、長時間 background
task）前必須先確認 constraint/error-handling 已經寫進該任務的
prompt 或設定，不能依賴『agent 會自己注意』」**，並列入
`AGENT_RULES.md` 或 `skills/first-principles-check/SKILL.md` 的
檢查清單。這是本筆記建議事項，本次未實際修改任何治理規則。

---

## 來源

- YouTube：https://youtu.be/PpeCur6fEXc
