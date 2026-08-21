你是 MAPLAB A6，運行在 Codex。
Telegram 派工 ID: TG-DISPATCH-20260821-120023-quote-intake
任務類型: 報價/試算派工任務
主責/協作: A6, A5

## Cold Start
1. 先讀 CURRENT_STATUS.md。
2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。
3. 再讀本派工列出的 task cards / docs。
4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。

## Owner 原始指令
```text
目前股價55.9試算本益比 說個好故事
```

## 最近 Telegram context
```text
source=data/telegram-logs/2026-08-21.md
# Telegram 對話紀錄 — 2026-08-21

> 自動產生，供 agent 恢復記憶用

## 2026-08-21 00:34:43
**Owner：** 呼叫fable5 你可以自行閱讀上面貼過來的嗎？

**Bot：** 🟢 [Claude]
可以，上面貼過來的對話我已經讀到了（Telegram 轉發內容整段都在我的 context 裡），不需要另外開檔案讀取。

不過要澄清一點：我目前這個 session 是 **A1（Sonnet 5）**，不是 Fable 5。如果你是想指定讓 Fable 5 處理這類任務，我這邊的身份跟模型底層對不上——要嘛你直接跟 Fable 5 的 session/視窗對話，要嘛請 A0 那邊的 dispatch 路由過去（看 commit `ae486eb` 提到的 "A0"-prefix 直接通道）。

需要我針對上面那段對話內容做什麼後續動作嗎？（例如整理成任務卡、回報 R0x 狀態、或針對 Meta 廣告指引繼續往下做）

---

## 2026-08-21 08:46:18 `[dispatch-local]`
**Owner：** seo部分你當核稿和確認方向的，沒問題就發，目前看行政外燴推薦Hr的部分把無麩質特殊飲食敘述拿掉，---格式通病，服務亮點不用自己說，動線好拿取說法不要再出現很AI,客戶與場景背景直接寫在標題，但問題是我不希望出現在標題是要去做，去研究客戶IG官網,圖片場景說故事，讚美一下，不是只在標題 +line可以上line圖示嗎？-----

**Bot：** ✅ 已建立派工包：TG-DISPATCH-20260821-084616-ads-performance-review
這不是只回覆：已落檔，並寫入 Codex clipboard bridge。
- 主責：A3（協作：A3, A2, A1）
- worker：Codex primary; OpenClaw read-only browser proof if logged-in Ads UI is needed
- status：queued_for_codex
- openclaw_worker：will_start
- packet：workbook/telegram-dispatch/TG-DISPATCH-20260821-084616-ads-performance-review/packet.json
- prompt：workbook/telegram-dispatch/TG-DISPATCH-20260821-084616-ads-performance-review/prompt.md
下一步：worker 必須用這個 dispatch_id 回報；沒有 receipt 就不能再說已召喚。

---

## 2026-08-21 08:48:55
**Owner：** claude gpt 高風險圓桌指的是什麼

**Bot：** 🟢 [Claude]
「Claude GPT 高風險圓桌」是 **Investment OS**（`/Users/pagemacmini/Documents/New project`）裡的機制，正式名稱是 **「AI Hermes 圓桌會議」**，關鍵事實：

**它是什麼：**
- 每天平日 21:40（原 21:30）用 OpenClaw 操控 Chrome，把當日 Top 3 雷達候選股的 prompt 貼進 Owner 固定的 ChatGPT project（`ai hermes 圓桌會議`），讓 **GPT** 做研究判讀 → 產出 consensus/proposal → 寫回 `research_model_outputs`
- **不是** Hermes 本地模型在判讀，Hermes/腳本只是排程觸發器；**不走 API**、**不下實單**、**不碰券商帳戶**（見 `pitfalls.md` 錯誤170、`CURRENT_STATUS.md`）

**為什麼是「高風險」：**
因為牽涉到股票交易判斷，屬於財務決策範疇。系統治理規則（`AGENT_RULES.md`／`docs/governance/unattended-run-safety.md` 第6條）規定：
> 高風險面（下單、改交易帳務、發布外部內容）預設唯讀，只能「提議」不能「執行」

所以圓桌產出的只是**模擬單/研究建議**，不會自動變成真實下單。

**「Claude」在裡面的角色：**
Claude（Codex/A1/B1 這條線）負責維護跑這個流程的腳本（`run_radar_sim_gpt_research_loop.py`、price anchor 安全補丁等），**不是**去跟 GPT 一起「討論」——真正產生判讀內容的是 GPT，Claude 這邊是寫程式/巡檢/修 bug 的角色。

這是 Investment OS 專案的機制，跟 MAPLAB 這邊目前的 Meta 廣告任務無關。需要我對照確認這個排程現在是否還在正常跑嗎？

---

## 2026-08-21 08:50:12
**Owner：** 既然是模擬單就不要出現高風險字眼吸引我目光與分散注意力

**Bot：** 🟢 [Claude]
已記下：以後描述 AI Hermes 圓桌會議這類唯讀/模擬性質的流程，回報時會用「模擬單研究流程」等中性措辭，不再用「高風險」字眼吸引注意力。

---

## 2026-08-21 10:18:24 `[dispatch-local]
…（截斷）
```

## 必讀來源
- handoff/tasks/T-A6-001.md
- handoff/tasks/T-A5-002.md
- projects/line-quote-assistant.md
- projects/maplab-master-data.md

## 本輪目標
整理活動需求、品項、數量、預算、毛利/成本口徑與待確認欄位，再交給 A6/A5 產出報價草稿或 Sheet payload。

## 需要取得/驗證的資料
- event type, date/time, location, headcount, budget, service fee and logistics assumptions
- menu preferences, dietary restrictions, item mapping, margin/cost risk
- whether the required output is draft text, Sheet payload, or a formal quote link

## 邊界
- do not invent a Google Sheet or quote URL
- do not expose internal costs to customers
- if Sheet/GAS write is required, route through A5 and report the real artifact URL only after creation

## 輸出契約
請回報：
1. Startup Check：角色、環境、任務、資料來源。
2. 已做的事：真的讀了哪些檔案/資料或執行了哪些 read-only checks。
3. 結論：分成 verified facts、reasonable inference、missing data、next action。
4. 若需要 Owner：只列 5 分鐘內可完成的具體動作。
5. 若要寫回：列出要改的檔案與理由，未核准不得碰 live external settings。
