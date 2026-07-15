你是 MAPLAB A6，運行在 Codex。
Telegram 派工 ID: TG-DISPATCH-20260712-121235-quote-intake
任務類型: 報價/試算派工任務
主責/協作: A6, A5

## Cold Start
1. 先讀 CURRENT_STATUS.md。
2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。
3. 再讀本派工列出的 task cards / docs。
4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。

## Owner 原始指令
```text
不要提到無麩質和低糖選項

外送費級距找實際案例高雄嘉義標題報價單推算後給我報告和答案

timetree開chrome 自動google登入

wordpress 與廣告後台數據分析與討論，跟我開會建議方向，討論後執行，之前應該有一些文章是針對關鍵字矩陣規劃，請你先找素材是不是中斷了
```

## 最近 Telegram context
```text
source=data/telegram-logs/2026-07-12.md
# Telegram 對話紀錄 — 2026-07-12

> 自動產生，供 agent 恢復記憶用

## 2026-07-12 08:10:59 `[dispatch-local]`
**Owner：** 我人在外面大概一個禮拜無法用電腦1. 你可以在有額度的時候把每個角色任務定位，都以使用者角度試著使用看看，並分析現在斷點及推進方向嗎？明顯需要修改整理的都把他做好。2.你可以去測試codex antigravity 可以用什麼角色或分派什麼任務把他們額度也妥善利用嗎？3.我們目的是不要浪費我花錢的算力，並在第一性原理下，盡可能優先了解專案全貌，再穩定的推進版本，所以身為監督的你讀完全貌是最重要的。然後要想辦法辨識出其他人的錯誤與需要做的改進與調整。讓大家都動起來定期跟我回報 格式以角色 任務名 要達到什麼目的 有優化什麼功能 做了什麼研究得到的結論，我們一天討論一次方向開個會

**Bot：** ✅ 已建立派工包：TG-DISPATCH-20260712-081057-command-window-dispatch
這不是只回覆：已落檔，並寫入 Codex clipboard bridge。
- 主責：A0（協作：A0, A1）
- worker：Codex primary; OpenClaw/Hermes can act as intake or read-only worker
- status：queued_for_codex
- openclaw_worker：will_start
- packet：workbook/telegram-dispatch/TG-DISPATCH-20260712-081057-command-window-dispatch/packet.json
- prompt：workbook/telegram-dispatch/TG-DISPATCH-20260712-081057-command-window-dispatch/prompt.md
下一步：worker 必須用這個 dispatch_id 回報；沒有 receipt 就不能再說已召喚。

---

## 2026-07-12 08:14:44
**Owner：** 你那個prompt.md是 hello world 需要動態指向的話要記得去調整與修正

**Bot：** 🟢 [Claude]
Push 成功。

---

**已修正兩個問題：**

1. **`bot.py` L908-910** — `openclaw_command` 的字面 `<prompt>` 改為 `"$(cat {prompt_path})"` ，下次生成的 dispatch packet 會帶正確的 shell 展開指令。

2. **現有 packet.json** — 同步更新，`openclaw_command` 現在指向完整的 prompt.md 路徑，可以直接複製執行。

prompt.md 本身的內容（Owner 指令、context、目標）是動態生成的，沒問題。只有執行指令那行是 hello world 佔位符，現在已修正。

---

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
