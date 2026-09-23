#!/usr/bin/env bash
# a0_bot_restart.sh — A0 自助重啟 Telegram bot(不需 Owner 動終端機)
# 背景:Owner 2026-08-28 msg 4296/4314 明令:授權即授權,不得再要求 Owner 開終端機。
# 機制:精準結束 launchd 追蹤的 bot.py 進程;com.maplab.telegrambot 的
# KeepAlive=true 會在 ThrottleInterval(30s)內自動重生,載入最新 bot.py
# (含 resume 白名單修正 beaec1d)。
# 安全:pkill pattern 鎖全路徑 maplab-ai-handbook/bot/bot.py,不會誤殺
# a6 bot、claude 進程或其他程式;每次重啟留 log 供稽核。
#
# 2026-09-22(Owner msg 5882 當輪發現):原本最後一行不論結果都寫
# 「pkill issued; launchd KeepAlive respawning」,**那是假收據**。實測在 resume
# 沙盒裡 pkill 根本匹配不到 bot 進程(連 pgrep 都看不到它),log 卻照樣寫成功,
# 於是「改完就重啟了」被誤信,程式其實沒生效(跟 a6 閘道 task #19 同一種坑)。
# 現在改成:記下重啟前的 PID、pkill 的實際結果碼、以及 15 秒後的 PID,
# PID 沒變就明寫 RESTART FAILED。收據要能被打臉,不然不算收據。
#
# 註(同日修):nohup 那段是雙引號字串,裡面 \$FOO 是「等子殼跑的時候才展開」,
# $FOO 是「現在就由外殼代入」。PID_BEFORE 只有外殼知道(子殼裡沒這個變數),
# 所以必須寫成不帶反斜線的 ${PID_BEFORE:-unknown};先前寫成 \${...} 導致
# 19:05 那筆 log 印成「RESTART OK: unknown -> 89665」。判斷用的是已代入的值,
# 結論沒錯,但印出來的收據少了一半資訊——那也該修。
set -u
LOG=/Users/pagemacmini/claude-daily-operations/state/a0_bot_restart.log
STAMP="$(date '+%Y-%m-%dT%H:%M:%S')"
JOB_LABEL="com.maplab.telegrambot"

bot_pid() {
  launchctl list "$JOB_LABEL" 2>/dev/null \
    | sed -n 's/.*"PID" = \([0-9]*\).*/\1/p' | head -n 1
}

PID_BEFORE="$(bot_pid)"
echo "[$STAMP] restart requested (caller pid $$, bot pid before=${PID_BEFORE:-unknown})" >> "$LOG"

# 延遲 2 秒再殺,讓呼叫方(回覆腳本)先乾淨收尾、回報送達;之後回頭查證 PID 有沒有換。
nohup /bin/bash -c "
  sleep 2
  /usr/bin/pkill -f 'maplab-ai-handbook/bot/bot.py'
  RC=\$?
  echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] pkill exit=\$RC (0=有殺到 1=沒有匹配的進程)\" >> '$LOG'
  sleep 15
  PID_AFTER=\$(launchctl list '$JOB_LABEL' 2>/dev/null | sed -n 's/.*\"PID\" = \([0-9]*\).*/\1/p' | head -n 1)
  if [ -z \"\$PID_AFTER\" ]; then
    echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] RESTART FAILED: launchd 查不到 PID,bot 可能沒起來\" >> '$LOG'
  elif [ \"\$PID_AFTER\" = '${PID_BEFORE:-none}' ]; then
    echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] RESTART FAILED: PID 仍是 \$PID_AFTER,沒有重啟(改動未生效)\" >> '$LOG'
  else
    echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] RESTART OK: ${PID_BEFORE:-unknown} -> \$PID_AFTER\" >> '$LOG'
  fi
" >/dev/null 2>&1 &
echo "[$STAMP] detached killer scheduled (fires in 2s, 驗證在 17s 後寫入)" >> "$LOG"
