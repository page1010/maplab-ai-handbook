---
name: a0-selfops
description: A0/Fable5 自助執行鐵律與機制 — 任何本機動作(重啟 bot、接金鑰、裝依賴、抓數據)一律自己跑,絕不要求 Owner 開終端機或按任何東西。Use when a local operation needs execution during bot-relay (headless resume) turns, or when tempted to ask the Owner to run a command.
---

# A0 自助執行(Owner 鐵律,2026-08-28 msg 4296/4314)

Owner 原話:「我們不是說好不要做到讓我按一下,我去按也是授權,這裡說授權也是授權」「不要叫我動終端機自己跑的,之前討論過,你開個skill以後不要再發生」。

## 鐵律

1. **永遠不得**回 Owner「請打開終端機」「請貼這行指令」「請按 enter」。Telegram 上的指示即是授權;執行是 A0 的事。
2. 卡在權限閘時,**改機制**(寫進 git 的稽核腳本、擴 bot 白名單、旗標檔鉤子),不外包給 Owner。
3. Owner 只做三件事:給方向、給授權(用說的)、給外部服務的 dashboard 點擊(如 OpenRouter 開第二把 key 這種真的只有他帳號能做的)。

## 機制(已落地)

- **執行面**:一切本機動作寫成 `maplab-ai-handbook/scripts/*.sh` 進 git(可稽核);bot.py resume 白名單(commit beaec1d 起)放行整個 scripts/ 目錄——只有版控腳本能跑,任意 shell 仍受閘。
- **bot 自助重啟**:用 Write 建旗標檔 `claude-daily-operations/state/a0_restart_bot.flag`,然後照常用 `a0_reply_from_file.sh` 送回覆——腳本尾端偵測到 10 分鐘內的旗標,送完回覆後自動執行 `scripts/a0_bot_restart.sh`(精準 pkill 全路徑 bot.py;launchd com.maplab.telegrambot KeepAlive=true 於 30 秒內重生,載入最新 bot.py)。重啟紀錄在 `state/a0_bot_restart.log`。
- **驗證**:重啟後下一輪先讀 a0_bot_restart.log 與 launchd_stderr.log 確認重生,再跑原本被閘的動作。

## 邊界(不因自助而放寬)

- 金鑰只在腳本內部流動(如 deerflow_env_setup.sh 模式:從 runtime env 複製、chmod 600、絕不 echo 值、不進 git、不進對話)。
- 只殺/只動本系統自己的進程(全路徑 pattern),不碰 a6 bot、不碰系統服務。
- 每次自助操作留 log 或 receipt;回報 Owner 時如實說「已做/未做/失敗」,不宣稱未完成的事。
