#!/usr/bin/env bash
# a0_watchdog.sh — A0 未回訊息看門狗(Owner 2026-08-29:「可以讓 hermes 或 openclaw 叫醒你」)
# 機制:launchd 每 10 分鐘跑一次。若 a0_inbox 最後一則超過 AGE_MIN 分鐘未回、
# 且沒有其他 resume 進程在跑,就用 bot 同款 claude -p --resume 直接喚醒 A0
# session 補處理(回覆一樣走 a0_reply 腳本留收據,與 bot 相容)。
# 不經 Telegram、不需 hermes;bot 900s 強殺後的漏網訊息由這裡兜底。
set -u
STATE=/Users/pagemacmini/claude-daily-operations/state
INBOX=$STATE/a0_inbox.jsonl
REPLIES=$STATE/a0_replies.jsonl
SESSION_FILE=$STATE/a0_session.json
LOG=$STATE/a0_watchdog.log
LOCK=/tmp/a0_watchdog.lock
AGE_MIN=20
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

log() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] $*" >> "$LOG"; }

# lockfile(含過期回收:鎖超過 30 分鐘視為殭屍)
if [ -e "$LOCK" ]; then
  if [ -n "$(find "$LOCK" -mmin +30 2>/dev/null)" ]; then rm -f "$LOCK"; else exit 0; fi
fi
trap 'rm -f "$LOCK"' EXIT
touch "$LOCK"

# 已有 resume 在跑就不搶(bot 或前一輪 watchdog)
if pgrep -f "claude -p --resume" >/dev/null 2>&1; then exit 0; fi

read -r PENDING_TS PENDING_TEXT <<EOF2
$(/usr/bin/python3 - "$INBOX" "$REPLIES" <<'PYEOF'
import json, sys, datetime
inbox, replies = sys.argv[1], sys.argv[2]
def last_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [l for l in f.read().splitlines() if l.strip()]
    except FileNotFoundError:
        return []
inb = last_lines(inbox)
if not inb:
    sys.exit(0)
last = json.loads(inb[-1])
# 只看 Owner 私訊(群組 chat_id<0 不歸 watchdog 管)
if int(last.get("chat_id", 0)) < 0:
    sys.exit(0)
answered = {json.loads(l).get("reply_to_inbox_ts") for l in last_lines(replies)}
if last.get("ts") in answered:
    sys.exit(0)
age = (datetime.datetime.now() - datetime.datetime.fromisoformat(last["ts"])).total_seconds()
if age < 20 * 60:
    sys.exit(0)
text = (last.get("text") or "").replace("\n", " ")[:1500]
print(last["ts"] + "\t" + text)
PYEOF
)
EOF2

if [ -z "${PENDING_TS:-}" ]; then exit 0; fi

SID=$(/usr/bin/python3 -c "import json;print(json.load(open('$SESSION_FILE')).get('session_id',''))" 2>/dev/null)
[ -z "$SID" ] && SID="3a3df70f-b5ce-4c45-9d85-6651d7022e4b"

ALLOW=$(/usr/bin/python3 - <<'PYEOF'
import glob
scripts = sorted(glob.glob("/Users/pagemacmini/maplab-ai-handbook/scripts/*.sh"))
print(",".join(f"Bash({p}{s}:*)" for s in scripts for p in ("bash ", "")))
PYEOF
)

log "waking A0 for unanswered inbox ts=$PENDING_TS"
PROMPT="【watchdog 喚醒】你是 A0/Fable5,同 session 續接。bot 的 resume 之前被強殺,以下 Owner 訊息(inbox ts=$PENDING_TS)尚未回覆。請照協定:git pull cdo → 比對 inbox/replies → 用 scripts/a0_reply_from_file.sh 回覆這一則(回覆開頭標【Fable5 本人・同 session 續接】,不宣稱未完成的事)。優先在 5 分鐘內把回覆送出,重活拆到回覆之後。Owner 訊息:$PENDING_TEXT"

cd /Users/pagemacmini/Documents || exit 1
claude -p --resume "$SID" --output-format text --allowedTools "$ALLOW" "$PROMPT" >> "$LOG" 2>&1
log "wake attempt finished (exit=$?)"
