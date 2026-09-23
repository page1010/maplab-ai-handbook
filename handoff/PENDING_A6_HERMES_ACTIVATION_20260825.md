# 已啟動：A6 bot 交接給 Hermes（Owner 指示，2026-08-25）

- 狀態：**2026-08-25 12:27 已完成 live 重啟與 Owner Telegram round-trip**。
- 已完成:bot_a6/hermes_telegram_gateway.py(純標準庫,OpenRouter 免費鏈,Owner-only 白名單)、run_daemon.sh 已改指到閘道、hermes config.yaml 預設模型已改雲端(C-2)。
- 舊 bot_a6.py 進程 PID 1068 自 08-24 09:35 殭屍化(Bad Gateway 後輪詢停),它還握著 A6 token 的 getUpdates。

## 啟動步驟

1. 執行 `bash scripts/a6_hermes_activate.sh`。腳本先 py_compile，再處理舊程序；60 秒內沒起來會 exit 1。
2. 驗證:tail bot_a6/hermes_gateway.log 應出現「hermes gateway start; chain=...; openrouter_key=yes」;再看 Owner 對 A6 bot 發 /start 有無回【hermes】值班訊息。

安全修正（Codex 2026-08-25）：啟動器改成 `set -euo pipefail`、失敗明確 exit 1，且不再把可能含 Owner 對話摘要的 log tail 到終端。

Preflight：`bash -n` PASS；gateway `py_compile` PASS。`com.maplab.a6bot` 已由 launchd 啟動
`bot_a6/hermes_telegram_gateway.py`；Telegram Web 對 `@maplab_a6_bot` 送 `/start`，真實讀回
`【hermes】值班中。問我每日投資訊號、系統狀態、SEO 專案都可以；答不了的我會明說要等 Fable5。`
完整收據：`workbook/reviews/JOB-A6-HERMES-ACTIVATION-20260825/telegram_roundtrip.md`。

## 驗證後補做

- 首答格式已驗：標【hermes】且明寫答不了要等 Fable5，不冒充 Fable5。
- 投資內容的「研究判斷」標籤仍應在第一個真投資問答另驗；本輪 `/start` 不冒充投資回答。
- 注意：log 僅在本機私下排障，不貼聊天、不 commit；首答完成前不得宣稱 Telegram 可用。

## Resume Prompt

我是接手 A6 Hermes Telegram 的 MAPLAB agent。先讀 cold-start、本卡與 activation receipt。A6 gateway 已
由 `com.maplab.a6bot` 常駐，`/start` 真 surface 往返已通。下一步只用一題不含客戶資料與持股的公開資訊
問題驗證回答品質、來源與「研究判斷」標籤；失敗就保留 gateway 並標 degraded，不得把私人資料送免費端點。

## 同批待重啟:主 bot(腳本推送修補,e4a42c1)

- bot/bot.py 的 _a0_resume_ask 已加 --allowedTools 放行 a0_reply.sh/a0_reply_from_file.sh/notify_group.sh,
  修 Owner「解決腳本推送問題」——續接視窗過去每次被權限閘攔,只能靠 bot 轉送最終文字。
- 生效需主 bot 重啟(重啟方式依它現行的啟動方式;重啟瞬間 relay 會斷幾秒,launchd/KeepAlive 型會自動回來)。
- 重啟後驗證:下一個續接視窗跑 a0_reply.sh 應直接成功並在 a0_replies.jsonl 留收據。
