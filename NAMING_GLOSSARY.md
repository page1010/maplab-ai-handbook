# NAMING_GLOSSARY — 稱謂表(誰是誰、是哪一層)

**建立:2026-09-23,依 Owner msg 6002 / 6004 / 6005 三則裁示。**
Owner msg 6005 原話:「先釐清這些稱謂才能發現問題出在哪裡」。

這份表的用途不是文字遊戲。**故障報告必須指到正確的層**——過去把席位登入過期、
launchd 路徑錯誤都講成「某個 agent 沒做事」,結果修法一直派到錯的層。

查核時間:2026-09-23 17:3x(PID 與心跳為當下實查值,會過期;判斷層級的分類不會)。

---

## 分層原則(先分類型,再談名字)

| 層 | 是什麼 | 壞掉的樣子 | 修法 |
|---|---|---|---|
| **模型** | 會寫字、會判斷的那個東西 | 答錯、亂編 | 換模型、改 prompt、加閘 |
| **角色名** | 工作角色,沒有實體 | 職責重疊、沒人認領 | 改章程 |
| **席位** | 可以放一個模型進去的位子 | **登入過期、心跳停** | **去那台重新登入** |
| **程式** | 固定邏輯,不產生判斷 | rc=127 路徑錯、逾時 | 修路徑、修程式 |
| **別家 app** | 不是我們寫的,額度也不是我們的 | 我們管不到 | 只能改用法 |

---

## 第 1 類:模型

⚠️ **msg 6029(2026-09-23)更正:這一類要再拆成兩層。**
Owner 原話:「你不是 fable5 你是 claude,底層模型是可切換的,你們公司的限額,所以可能是 sonet opus 等」。

| 名字 | 說明 |
|---|---|
| **Claude** | 產品/公司層。**對 Owner 的自稱一律寫這個**(msg 6002),而且**只寫到這一層為止**——因為底下那顆模型會換。 |
| **底層模型** | 真正在跑的那顆:`claude-fable-5` / `claude-opus-5` / `claude-sonnet-5` / `claude-opus-4-8` / `claude-fable-5-1`…。**會因為額度被 CLI 換掉,不是固定的**,所以**不可以把模型名寫死在自稱或標頭裡**。 |

**實證(這條 A0 session 的逐字稿統計,2026-09-23)**:同一條 session 已經跑過
`claude-fable-5` 15,016 則、`claude-opus-5` 3,035 則、`claude-sonnet-5` 777 則、
`claude-opus-4-8` 141 則、`claude-fable-5-1` 70 則——**五顆模型、同一條線、同一個 session id**。

**怎麼查「現在是哪顆」**:`bash scripts/a0_model_now.sh`。
規則:`state/a0_session.json` 的 `model` 欄是 **bot 呼叫時要求的模型(願望)**,
逐字稿每則 assistant 的 `"model"` 欄才是**事實**;**兩者不一致時以逐字稿為準**。
(現況就是不一致:`a0_session.json` 寫 `claude-fable-5`、`updated` 停在 2026-08-22,
但本視窗實際跑 `claude-opus-5`。)

## 第 2 類:角色名(沒有實體)

| 名字 | 說明 |
|---|---|
| **Fable5 / A0** | 這條 Telegram 線的**角色名/線別代號**,不是獨立人格,也**不是模型名**。底下是 Claude,再底下是當時那顆可切換的模型。**「Fable5」這個字來自最初指定的 `claude-fable-5`,但模型早就換過很多次,名字留下來只當線別標籤**(msg 6029)。 |
| **B1–B4** | Builder / Reviewer / Archivist / System-Patrol 迴圈。 |
| **IOS-\*** | MACRO / HEDGE / BLACKSWAN / CHIP / SURFACE / HYGIENE … 共 16 個,定義在 investment-os 的 role registry。**是 prompt 角色,不是程式,不會自己動。** |

## 第 3 類:席位(裡面跑什麼模型不固定)

| 名字 | 實體 | 2026-09-23 實查狀態 |
|---|---|---|
| **win-os** | Windows 機器上的 **Claude session 管理者**。**檔案側一律寫 `win-01`**(machine_id、卡號 `win01-*`、`diag/win-01/` 已寫死,改字串會讓跑中的卡對不上);**對 Owner 的文字寫 win-os**。worker 呼叫 `claude -p` **不帶 `--model`**,所以裡面是哪個模型這邊不知道也不該假設。 | 🔴 **死**。heartbeat 17:25 `status=busy` 只代表卡被撿走;`diag/win-01/seo-cases-drive-batch-20260910.exec-tail.log` 16:55 `rc=1` `Failed to authenticate: OAuth session expired`;hermes 接手 17:18 `rc=124` 逾時無收據。**今日零產出。** |
| **mac-mini** | 本機。`bus.config.json` 裡 `role=orchestrator`, `domains=["all"]`。 | 🟢 活著(這個 session 就在上面)。 |
| **invest** | agent-bus 的第三個席位(`inbox/invest/`、`worker_invest.sh`)。 | 🔴 **心跳停在 `2026-08-21T00:15:25`**,`status=idle`、`active_sessions=0`。**停了約 33 天沒人發現。** |

## 第 4 類:程式(固定邏輯,不產生判斷)

| 名字 | 路徑 | 2026-09-23 實查 |
|---|---|---|
| **bot.py** | `maplab-ai-handbook/bot/bot.py`,launchd `com.maplab.telegrambot` | 🟢 **PID 89665 活著**。收 Telegram 訊息寫進 `a0_inbox.jsonl`,再用 `claude -p --resume` 叫醒這個 session。⚠️ **`bot/DEPRECATED.md` 寫著它已棄用、plist 已 unload——那份文件是錯的**(已於本日加註)。 |
| **hermes_telegram_gateway.py** | `maplab-ai-handbook/bot_a6/`,launchd `com.maplab.a6bot` | 🟢 PID 33950。**第二條 Telegram 線(a6,客服用)**,與 a0 線互不相通。 |
| **run_spread_paper.py** | `investment-os/scripts/` | 🟢 PID 81970。模擬交易引擎,**執行層零 LLM**。 |
| **worker_win01.sh / orchestrator.sh / worker_invest.sh** | `agent-bus/` | 搬運工:撿卡、起 session、寫回執。**不做判斷。** |
| **a0_reply_from_file.sh** | `maplab-ai-handbook/scripts/` | 回 Owner 的唯一出口,內含第三人稱閘(L3)。 |

## 第 5 類:別家的 app(額度與帳號都不是我們的)

| 名字 | 實體 | 實查 |
|---|---|---|
| **codex** | `/Applications/ChatGPT.app` 內的 Codex(OpenAI) | 🟢 在跑(PID 83728 起)。 |
| **antigravity** | `/Applications/Antigravity IDE.app`(Google) | 🟢 在跑(PID 432)。派工走 `agent-bus/inbox/antigravity/` 卡片。 |
| **hermes** | `~/.hermes/hermes-agent` + `Hermes.app`,**第三方 agent 框架,不在我們 repo** | 🟢 gateway PID 38295、desktop PID 44340。 |
| **openclaw** | node gateway `:18789` + 它專屬的 Chrome(`~/.openclaw/browser`) | 🟢 PID 742 / Chrome PID 22408。瀏覽器操作工。 |

---

## 釐清之後浮出來的問題(msg 6005 要的答案)

1. **文件說不存在的東西正在生產線上跑**:`bot/DEPRECATED.md` 宣告 bot.py 棄用、plist 已 unload,實際 PID 89665 撐著整條 Telegram 線。照那份文件修系統的人會直接拆掉生產線。
2. **invest 席位停了 33 天沒人發現**:因為它被當成「一個 agent」而不是「一個席位」,沒有人去看它的心跳與登入。
3. **win-os 席位登入過期**:跟第 2 點同一種病——席位層的故障被講成「agent 不做事」,所以修法一直找錯層。
4. **四個 launchd 排程死在路徑層**:`com.maplab.compounding-patrol`(`LastExitStatus=32512` = exit **127** 找不到執行檔)、`sched-daily-standup`、`sched-runtime-health` 同為 127,`line-cloud-gym` exit 1。

**共同病根**:以上四個故障**沒有一個發生在模型層**,全部在**席位登入**與**程式路徑**。
名詞混在一起的時候,「某個 agent 沒做事」這句話會把修法派到錯的層,於是同一個病重複復發。

**查現況的正確做法**:查席位看 `agent-bus/diag/<machine>/*.exec-tail.log` 與 `heartbeat/<machine>.json` 的時間戳,**不要只看 `status`**(heartbeat 會說 busy);查程式看 `launchctl list` 的 `LastExitStatus`;查模型才看回答內容。
