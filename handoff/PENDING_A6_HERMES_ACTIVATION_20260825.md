# 待啟動:A6 bot 交接給 hermes(Owner 指示,2026-08-25)

- 狀態:**線已接好,差一個重啟動作**(本窗口 kill/python 被權限閘攔)
- 已完成:bot_a6/hermes_telegram_gateway.py(純標準庫,OpenRouter 免費鏈,Owner-only 白名單)、run_daemon.sh 已改指到閘道、hermes config.yaml 預設模型已改雲端(C-2)。
- 舊 bot_a6.py 進程 PID 1068 自 08-24 09:35 殭屍化(Bad Gateway 後輪詢停),它還握著 A6 token 的 getUpdates。

## 啟動步驟(任何有進程權限的 A0 窗口,兩條命令)

1. kill 1068(launchd com.maplab.a6bot KeepAlive 會在 30 秒內用新的 run_daemon.sh 重生=直接跑 hermes 閘道)
   - 若 PID 已變:pkill -f "bot_a6/bot_a6.py"
   - 若 launchd job 沒載入:launchctl load ~/Library/LaunchAgents/com.maplab.a6bot.plist(plist 在 bot_a6/ 有副本)
2. 驗證:tail bot_a6/hermes_gateway.log 應出現「hermes gateway start; chain=...; openrouter_key=yes」;再看 Owner 對 A6 bot 發 /start 有無回【hermes】值班訊息。

## 驗證後補做

- 首答品質抽查一則(hermes 鐵則:標【hermes】、不冒充 Fable5、投資答案標研究判斷)。
- 把本卡狀態改「已啟動+時間」;通知 Owner A6 bot 視窗可用。
- 注意:語法未經機器驗證(本窗口 python 被攔),若啟動報錯先看 hermes_gateway.log 與 launchd_stderr.log。

## 同批待重啟:主 bot(腳本推送修補,e4a42c1)

- bot/bot.py 的 _a0_resume_ask 已加 --allowedTools 放行 a0_reply.sh/a0_reply_from_file.sh/notify_group.sh,
  修 Owner「解決腳本推送問題」——續接視窗過去每次被權限閘攔,只能靠 bot 轉送最終文字。
- 生效需主 bot 重啟(重啟方式依它現行的啟動方式;重啟瞬間 relay 會斷幾秒,launchd/KeepAlive 型會自動回來)。
- 重啟後驗證:下一個續接視窗跑 a0_reply.sh 應直接成功並在 a0_replies.jsonl 留收據。
