# HERMES 接手手冊:日常投資訊號報告 + SEO 專案問答

- 建立:2026-08-25 00:30|作者:A0/Fable5|情境:Fable5 週額度剩 18%,額度滿時 hermes 接日常
- hermes 角色:**判讀與答疑,不下單、不發布、不改生產設定**。所有投資輸出必標「研究判斷,非下單指令」。
- Owner 問問題時:先查本手冊的「去哪找答案」欄,答不了就誠實說「這要等 Fable5/Codex 額度回來」,不要腦補。

## 一、每日投資訊號產品線(全部走 launchd,不依賴任何 AI session 存活)

| 時間(週一–五) | 產品 | launchd label | 產出/日誌位置 |
|---|---|---|---|
| 07:00 | 早報(規則版) | com.investmentos.finance-morning-brief | runtime*/reports、data/logs/ |
| 03:05·15:20·22:05 | KOL 網紅雷達 | com.investmentos.kol-daily-research-refresh | 同上 |
| 16:20 | 強股故事+前幾名(動能) | com.investmentos.strong-stock-story-early | reports/limit_up_chip_story/ |
| 16:50 | 股期開盤劇本 | com.investmentos.stock-future-opening-playbook | reports/stock_future_order_plan/ |
| 18:45 | Owner 晚報 | com.investmentos.owner-evening-report | owner_evening_latest.md |
| 21:00 前後 | 籌碼日報 | com.investmentos.chip-daily-digest | data/logs/ |
| 22:10 | 研究摘要(已加 top3-gate) | com.investmentos.ai-hermes-research-telegram | data/logs/ai_hermes_research_telegram_launchd.out.log |

\* runtime = /Users/pagemacmini/.local/share/investmentos-telegram-operator

**每日點名(roll-call)**:上表每項當天應有一則 Telegram;缺席=去對應 out.log 看最後一段 JSON 的 status/exit_code。
已知弱點:16:20 的 ChatGPT 步驟約一半機率 valid:false → 整則不送。此時 rule-based 底稿其實已生成(reports/limit_up_chip_story/limit_up_chip_story_YYYY-MM-DD.md),hermes 可讀該檔向 Owner 摘要補位。

## 二、品質規範(接手也要守)

1. **查價 SOP**:docs/RESEARCH_PRICE_FRESHNESS_SOP.md——價格只准官方 API(scripts/twse_quote.sh,一行查多檔含資料日期);每個數字標日期;盤後交付必含當日收盤;SCFI/CCFI 是週五發布的週指標,標「MM/DD 發布值」。
2. **四問格式**:發生什麼變化/對我有何影響/下一步看什麼/什麼情況證明原判斷失效。
3. **通道**:回 Owner=scripts/a0_reply.sh(留收據);群組成果回交=scripts/notify_group.sh(僅限 Owner 群組派工的成果,平時靜默);財經成品走 TelbotFin 既有 job,不要手動另開通道。
4. 訊息不用反引號、說人話三段式、不發收據式空回報。

## 三、SEO 專案:去哪找答案

| 問題類型 | 去哪找 |
|---|---|
| SEO/廣告全局、派工規則 | maplab-ai-handbook/docs/a0-dispatch-operations-manual.md |
| 頁面/CMS/WordPress 現況 | maplab-ai-handbook/docs/(ad-buildout-plan、ansoff-mot-audience-matrix 等) |
| Windows SEO 工作機(win-01) | claude-daily-operations/state/(agent-bus heartbeat;停滯自 08-19,已知問題) |
| Antigravity 排程巡檢 | Antigravity.app workspace "Ads SEO WordPress Patrol"(勿打斷 live run) |
| 金流/投放閘門 | Owner 親自核:Google Ads+Gmail 券、對外投放(hermes 無權代核) |

## 四、目前系統快照(2026-08-25 00:30,方便答 Owner「現在怎麼樣」)

- 週額度:Fable5 已用 82%(quota_meter.json 會刷新,stale>180min 就說「以最後樣本為準」)。
- 晶技 3042 亂推已修:22:10 job 加了 top3-gate(>2 天舊資料不重播、非持股/watchlist 不推),已 dry-run 驗證。
- gemma4 已退役:7 個 worker 已殺、ollama 已卸載;**hermes 不要再用本地 gemma4**,用自己的雲端方案。
- 持股 ledger 資料庫損毀(data/position_ledger/ledger.sqlite3)→ 持股過濾閘暫時只剩 watchlist(SMH、2371),待修。
- 待辦總表:handoff/CARD_SYSTEM_BACKLOG_20260825.md(優先序在檔尾);08-22 兩個 16 點檔整天沒跑,原因未查明(機器沒睡,不是睡眠問題)。
- Owner 待裁決:晶技要不要進 watchlist;hermes 定位對齊(本手冊=第一版操作邊界,深層分工等 Fable5 額度回來對齊)。

## 五、hermes 明確不做

不下單/不轉帳;不發布 WordPress/不動生產設定;不動 launchd(壞了就記錄+回報,等 Fable5/Codex);不碰 bot/.env 等 secrets(用現成腳本,不讀值);不冒充 Fable5(標自己身分);拿不準的說拿不準。
