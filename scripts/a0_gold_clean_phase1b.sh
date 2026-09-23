#!/bin/bash
# a0_gold_clean_phase1b.sh — locate the per-thread LINE conversation CSVs in
# Google Drive (they are not on local disk; phase1 confirmed). Read-only Drive
# metadata search via the same token/venv as sheet_tail.py (values never printed).
# Pushes a bot-代答 verdict: folder found + file count, or not-found.
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

# sample filenames referenced by line_booking_pairs.csv
samples = ["1000_20250725_20250725", "1002_20250617_20250725"]
folder_ids = {}
for s in samples:
    r = drive.files().list(q=f"name contains '{s}' and trashed=false",
                           fields="files(id,name,parents)", pageSize=5).execute()
    for f in r.get("files", []):
        for p in f.get("parents", []):
            folder_ids[p] = folder_ids.get(p, 0) + 1

if not folder_ids:
    print("Drive 也查無样本檔名")
    sys.exit(0)

fid = max(folder_ids, key=folder_ids.get)
meta = drive.files().get(fileId=fid, fields="name").execute()
count, token = 0, None
while True:
    r = drive.files().list(q=f"'{fid}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
                           fields="nextPageToken,files(id)", pageSize=1000, pageToken=token).execute()
    count += len(r.get("files", []))
    token = r.get("nextPageToken")
    if not token:
        break
print(f"Drive 資料夾「{meta.get('name','?')}」命中,檔案數 {count}")
PY
)"
echo "[$(date '+%Y-%m-%dT%H:%M:%S')] phase1b: ${VERDICT}" >> "$LOG"

TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
if [ -n "${TOKEN:-}" ] && [ -n "${CHAT:-}" ]; then
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT}" \
    --data-urlencode "text=【bot 代答・gold 清洗定位(5636)】${VERDICT}" >/dev/null
fi
