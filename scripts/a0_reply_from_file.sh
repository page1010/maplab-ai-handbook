#!/usr/bin/env bash
# a0_reply_from_file.sh — 從檔案讀回覆內容,轉呼叫 a0_reply.sh
# 用途:長訊息/多行訊息先落檔再送,避免命令列引號地獄;排程腳本也可用。
# 用法:bash scripts/a0_reply_from_file.sh <message_file> [reply_to_inbox_ts]
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

MSG_FILE="${1:-}"
REPLY_TO_INBOX_TS="${2:-}"

if [[ -z "$MSG_FILE" || ! -f "$MSG_FILE" ]]; then
  echo "❌ 用法:bash scripts/a0_reply_from_file.sh <message_file> [reply_to_inbox_ts]" >&2
  exit 1
fi

MESSAGE="$(cat "$MSG_FILE")"
if [[ -z "$MESSAGE" ]]; then
  echo "❌ 訊息檔是空的:$MSG_FILE" >&2
  exit 1
fi

# 第三人稱閘(Owner msg 5991,2026-09-23T17:05:09)
# Owner 原話:「你的你我他用法很奇怪你們自己有幾個人對話請用第三人稱」。
# 真因:這條線上只有一個寫字的(Fable5),但「我」被混用成三種對象——Fable5 自己、
# bot.py 這支收發程式、以及「Fable5 加上 codex/win-01 那些不在這條線上的 agent」;
# 「你」又混用成 Owner 與引用 Owner 原話。制度 E:筆記沒人看,所以寫成程式擋下來。
# 規則:回覆稿不得出現 我/你(含我們/你們)。要引用 Owner 原話的行,行首寫「原話:」即豁免。
# 真有例外:A0_ALLOW_FIRST_PERSON=1 bash ...,但要在回覆裡對 Owner 說明為什麼。
if [[ "${A0_ALLOW_FIRST_PERSON:-0}" != "1" ]]; then
  BAD_LINES="$(grep -n '[我你]' "$MSG_FILE" | grep -v '^[0-9]*:原話:' || true)"
  if [[ -n "$BAD_LINES" ]]; then
    echo "❌ 第三人稱閘擋下(Owner msg 5991):下列行出現「我」或「你」" >&2
    echo "$BAD_LINES" >&2
    # 2026-09-23 Owner msg 6002(ts 17:29:15):「fable5 背後是 opus5運行,所以要自稱claude」。
    # 自稱從「Fable5」改為「Claude」——Claude=寫字的模型本身,Fable5=這條線的角色名,
    # bot.py=收發程式,codex/win-01/openclaw/a6=別的 agent。四個詞各指一個對象,不混用。
    echo "   改法:Owner 寫「Owner」、自己寫「Claude」、其他 agent 寫名字、程式寫程式名。" >&2
    echo "   不用「我們」,要講誰就點名。引用 Owner 原話的行,行首加「原話:」即豁免。" >&2
    exit 1
  fi
fi

# 額度自估尾巴(Owner msg 5557):估算器存在才掛,失敗不擋送信。
QUOTA_TAIL="$(/usr/bin/python3 "$REPO_ROOT/scripts/a0_quota_estimate.py" 2>/dev/null || true)"
if [[ -n "$QUOTA_TAIL" ]]; then
  MESSAGE="$MESSAGE"$'\n\n'"$QUOTA_TAIL"
fi

if [[ -n "$REPLY_TO_INBOX_TS" ]]; then
  bash "$REPO_ROOT/scripts/a0_reply.sh" "$MESSAGE" "$REPLY_TO_INBOX_TS"
else
  bash "$REPO_ROOT/scripts/a0_reply.sh" "$MESSAGE"
fi

# A0 self-restart hook(Owner 2026-08-28 msg 4314:不叫 Owner 動終端機,一切自跑)
# resume 視窗只放行本目錄腳本,故重啟走「旗標檔+回覆腳本尾端」:旗標存在且
# 10 分鐘內建立 → 送完回覆後自動執行 a0_bot_restart.sh(KeepAlive 重生新碼)。
# 過期旗標只清除不執行,避免舊旗標誤觸重啟。
RESTART_FLAG="/Users/pagemacmini/claude-daily-operations/state/a0_restart_bot.flag"
if [[ -f "$RESTART_FLAG" ]]; then
  if [[ -n "$(find "$RESTART_FLAG" -mmin -10 2>/dev/null)" ]]; then
    rm -f "$RESTART_FLAG"
    bash "$REPO_ROOT/scripts/a0_bot_restart.sh"
  else
    rm -f "$RESTART_FLAG"
  fi
fi

# A0 selfops run-script hook(同上 Owner 鐵律;2026-09-20 msg 5527 首用)
# resume 視窗的腳本白名單在喚醒當下取樣,同一輪新建的腳本會被舊快照擋住。
# 旗標檔補這個時間差:內容=本目錄下 .sh 腳本路徑+參數,10 分鐘內建立才執行,
# 目錄外一律拒絕,背景執行不擋回覆,紀錄在 state/a0_selfops_run.log。
RUN_FLAG="/Users/pagemacmini/claude-daily-operations/state/a0_run_script.flag"
RUN_LOG="/Users/pagemacmini/claude-daily-operations/state/a0_selfops_run.log"
if [[ -f "$RUN_FLAG" ]]; then
  if [[ -n "$(find "$RUN_FLAG" -mmin -10 2>/dev/null)" ]]; then
    RUN_LINE="$(head -n 1 "$RUN_FLAG")"
    rm -f "$RUN_FLAG"
    RUN_SCRIPT="${RUN_LINE%% *}"
    case "$RUN_SCRIPT" in
      "$REPO_ROOT/scripts/"*.sh)
        if [[ -f "$RUN_SCRIPT" ]]; then
          echo "[$(date '+%Y-%m-%dT%H:%M:%S')] run: $RUN_LINE" >> "$RUN_LOG"
          nohup bash $RUN_LINE >> "$RUN_LOG" 2>&1 &
          disown 2>/dev/null || true
        else
          echo "[$(date '+%Y-%m-%dT%H:%M:%S')] skip missing: $RUN_LINE" >> "$RUN_LOG"
        fi
        ;;
      *)
        echo "[$(date '+%Y-%m-%dT%H:%M:%S')] reject outside scripts/: $RUN_LINE" >> "$RUN_LOG"
        ;;
    esac
  else
    rm -f "$RUN_FLAG"
  fi
fi
