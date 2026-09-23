#!/bin/bash
# a0_gold_clean_phase1c.sh — phase1b follow-up: repeat the Drive filename search
# but INCLUDING shared drives (phase1b used default corpus = My Drive only).
# Read-only metadata search, same token/venv as sheet_tail.py; values never printed.
# Pushes a bot-代答 verdict; if this also misses, fallback = Owner mounts FABLE5_ARCHIVE.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$HOME/.maplab/a0_gold_clean.log"
BOT_ENV="/Users/pagemacmini/maplab-ai-handbook/bot/.env"
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python

VERDICT="$("$PY" - <<'PY' 2>>"$LOG"
import json, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

info = json.loads((Path.home()/".claude"/"mcp-keys"/"google-token.json").read_text())
info.pop("expiry", None)  # epoch-int expiry breaks google-auth; drop to force refresh
creds = Credentials.from_authorized_user_info(info)
drive = build("drive", "v3", credentials=creds, cache_discovery=False)

samples = ["1000_20250725_20250725", "1002_20250617_20250725", "line_booking"]
folder_ids = {}
for s in samples:
    r = drive.files().list(q=f"name contains '{s}' and trashed=false",
                           corpora="allDrives", includeItemsFromAllDrives=True,
                           supportsAllDrives=True,
                           fields="files(id,name,parents)", pageSize=10).execute()
    for f in r.get("files", []):
        for p in f.get("parents", []):
            folder_ids[p] = folder_ids.get(p, 0) + 1

if not folder_ids:
    print("共享雲端硬碟也查無樣本檔名,確定要走外接碟 FABLE5_ARCHIVE")
    sys.exit(0)

fid = max(folder_ids, key=folder_ids.get)
meta = drive.files().get(fileId=fid, fields="name", supportsAllDrives=True).execute()
count, token = 0, None
while True:
    r = drive.files().list(q=f"'{fid}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
                           corpora="allDrives", includeItemsFromAllDrives=True,
                           supportsAllDrives=True,
                           fields="nextPageToken,files(id)", pageSize=1000, pageToken=token).execute()
    count += len(r.get("files", []))
    token = r.get("nextPageToken")
    if not token:
        break
print(f"共享雲端硬碟資料夾「{meta.get('name','?')}」命中,檔案數 {count}")
PY
)"
echo "[$(date '+%Y-%m-%dT%H:%M:%S')] phase1c: ${VERDICT}" >> "$LOG"

TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
if [ -n "${TOKEN:-}" ] && [ -n "${CHAT:-}" ]; then
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT}" \
    --data-urlencode "text=【bot 代答・gold 清洗定位補查(5636)】${VERDICT}" >/dev/null
fi
