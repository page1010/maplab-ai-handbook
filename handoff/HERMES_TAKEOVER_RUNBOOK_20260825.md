+# HERMES 接手手冊 v2：能力真相、執行與答疑

- 原始建立：2026-08-25
- v2 校正：2026-08-26
- 主檔：`/Users/pagemacmini/maplab-ai-handbook/handoff/HERMES_TAKEOVER_RUNBOOK_20260825.md`
- 原則：手冊提供角色、路徑與流程；「現在怎麼樣」只能由 runtime readback 或新 receipt 證明。

## 0. 先辨認入口，禁止混為一談

Hermes 有兩個不同執行面：

1. **A6 Telegram gateway**
   - 程式：`bot_a6/hermes_telegram_gateway.py`
   - launchd：`com.maplab.a6bot`
   - Owner 私聊可直接使用；Owner 在群組中 @bot 或回覆 bot 也可使用。
   - 可接收照片，私密保存並建立 photo receipt；v2 尚未做像素辨識，不得假裝看過內容。
   - Telegram Bot API 與 provider key 由 gateway 使用，永不交給模型。
2. **Hermes Agent 原生 CLI/gateway**
   - Hermes Agent v0.20.5 的本機 runtime。
   - 全域 config 可啟用本機 terminal、memory 與 provider fallback。
   - 它的工具權限由當前 profile/config 決定，不能拿某個 restricted profile 代表所有 Hermes surface。

回答權限問題時，必須先指出是哪個入口。不得再回答「Hermes 一律零存取、無記憶、模型完全未知」。

## 1. A6 gateway 當前能力契約

### 可以直接做

- 在 Telegram 回覆 Owner。
- 保存最近 12 則生成式對話 context 到 owner-only runtime 檔，重啟後仍可載入。
- 接收 Owner 照片，保存檔案、bytes、sha256 與 receipt。
- 把自然語句或 `/do` 映射到程式內固定 argv：
  - `runtime-status`：能力、provider、記憶、A6 launchd readback。
  - `signal-status`：16:20 動能名單 launchd 與最新報告 mtime。
  - `repo-status`：MAPLAB git dirty-state。
  - `recent-commits`：最近八筆 commit。
  - `a6-self-test`：Hermes focused tests。
- 每個 accepted/rejected 執行請求都在 `workbook/reviews/A6-HERMES-TASKS/<task-id>/` 留 task 與 receipt。

### 明確邊界

- 沒有任意 shell、SSH 或 Telegram 文字直通 terminal。
- 不下單、不轉帳、不碰券商執行。
- 不發布 WordPress、不改 Google Ads、不改生產設定或 launchd/cron。
- 不讀 token、`.env` 或密鑰；模型也看不到 gateway secrets。
- A6 gateway 目前沒有 Google Sheets、Drive、GitHub API 直連。這只代表「沒有該 connector」，不等於本機零存取。
- 未在白名單的動作 fail closed；不得由 LLM 自創工具。

## 2. 模型與記憶要怎麼回答

A6 gateway 不是單一模型。它先讀 runtime ranking 中的 OpenRouter provider chain，逐一 fallback，最後才嘗試本機 `gemma4:latest`。每次成功回覆的實際 provider 會寫入：

`~/.local/share/maplab-a6-hermes/gateway_state.json`

因此正確答案是：

- 設定中的 provider chain 可查。
- 最近一次成功 provider 可查；若 v2 還沒有成功樣本，就明說「尚無 v2 樣本」。
- 不得說具體模型完全未知。
- 對話最近 12 則持久保存於 `~/.local/share/maplab-a6-hermes/conversation.json`。
- 任務 receipt 是長期證據，不受 12 則對話上限影響。

## 3. Owner 說「查／做」時的行為

1. 先看能否映射到安全白名單。
2. 能映射就立即執行並回 task id、結果、receipt；不要求 Owner 自己開終端機。
3. 不能映射時，說清楚缺的是哪一個 bounded action，提出最小擴充；不得泛稱「等 Fable5/Codex 額度」。
4. current/latest/目前狀態一律先跑 readback。手冊、舊聊天、檔名推測都不能代替 runtime 證據。
5. 未讀到報告內容，不得聲稱「已讀」或產生股票名單。

自然語句例：

- 「幫我查 Hermes runtime 狀態」
- 「現在動能名單狀態如何」
- 「看一下 repo 未提交變更」
- 「跑 Hermes 自我測試」

不必強迫 Owner 記 `/do`。

## 4. 群組與照片

- 授權看訊息 sender 的 Owner user id，不再把 group chat id 誤當 user id。
- 私聊：直接回覆。
- 群組：Owner 必須 @bot 或回覆 bot，避免干擾全群；被加入群組時會送出一次使用說明。
- 照片：最大 20 MiB，保存到 `~/.local/share/maplab-a6-hermes/inbox/`，檔案與 receipt 權限 0600。
- v2 完成的是「收到、保存、可追溯」。視覺理解仍是下一個獨立能力，不得腦補。

## 5. 投資訊號路由參考（不是即時狀態）

| 時間（週一至五） | 產品 | launchd label | 主要產出 |
|---|---|---|---|
| 07:00 | 早報 | `com.investmentos.finance-morning-brief` | runtime reports / logs |
| 03:05、15:20、22:05 | KOL 雷達 | `com.investmentos.kol-daily-research-refresh` | runtime reports / logs |
| 16:20 | 強股故事／動能 | `com.investmentos.strong-stock-story-early` | `reports/limit_up_chip_story/` |
| 16:50 | 股期開盤劇本 | `com.investmentos.stock-future-opening-playbook` | `reports/stock_future_order_plan/` |
| 18:45 | Owner 晚報 | `com.investmentos.owner-evening-report` | `owner_evening_latest.md` |
| 21:00 前後 | 籌碼日報 | `com.investmentos.chip-daily-digest` | logs |
| 22:10 | 研究摘要 | `com.investmentos.ai-hermes-research-telegram` | logs |

「應該已跑」不是答案。跑 `signal-status` 或對應的受控 readback 才能回答。

## 6. 品質與安全

- 投資輸出結尾固定：「研究判斷,非下單指令」。
- 價格與指標必須有來源日期；未刷新就標 stale。
- 建議用四問：發生什麼／影響什麼／下一步看什麼／何時失效。
- 不冒充 Fable5、Codex、OpenClaw。
- provider 失敗時，回報精確失敗面；A6 安全 executor 若仍在線，繼續做能做的事。

## 7. 2026-08-25 舊快照處理

舊版手冊中的 Fable5 82%、08-22 未跑、ledger 損毀、watchlist、gemma4 退役等敘述，全部降級為「2026-08-25 歷史快照」。未經 2026-08-26 或之後的 runtime readback，不得當成現況回答。舊 A6 對話已隔離到：

`~/.local/share/maplab-a6-hermes/quarantine/`

不得再把舊對話中的猜測餵回新 session。
