#!/usr/bin/env python3
"""a0_line_baseline.py — 6619 回合:算 CONVERSATION_LOG 的「每日新 line_user_id」基線(唯讀)。
隱私:不印訊息內容與姓名,只印日期統計與匿名化尾碼。token 同 sheet_tail.py 作法。"""
import json
import re
from collections import defaultdict
from pathlib import Path

TOKEN = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
SID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"


def fetch():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    info = json.loads(TOKEN.read_text())
    info.pop("expiry", None)
    creds = Credentials.from_authorized_user_info(info)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    r = service.spreadsheets().values().get(
        spreadsheetId=SID, range="CONVERSATION_LOG!A:H",
        valueRenderOption="FORMATTED_VALUE").execute()
    return r.get("values", [])


def main():
    rows = fetch()
    hdr = rows[0]
    i_ts, i_sp, i_uid = hdr.index("timestamp"), hdr.index("speaker"), hdr.index("line_user_id")
    first_seen = {}
    msgs_per_uid = defaultdict(int)
    speakers = defaultdict(set)
    for row in rows[1:]:
        if len(row) <= max(i_ts, i_uid):
            continue
        ts, uid = row[i_ts].strip(), row[i_uid].strip()
        if not uid or not ts:
            continue
        m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", ts)
        if not m:
            continue
        d = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        msgs_per_uid[uid] += 1
        if len(row) > i_sp and row[i_sp].strip():
            speakers[uid].add(row[i_sp].strip())
        if uid not in first_seen or d < first_seen[uid]:
            first_seen[uid] = d
    print(f"總訊息列={len(rows)-1} 總獨立 line_user_id={len(first_seen)}")
    daily_new = defaultdict(list)
    for uid, d in first_seen.items():
        daily_new[d].append(uid)
    print("日期 | 新user數 | 匿名尾碼")
    for d in sorted(daily_new):
        if d >= "2026-08-25":
            tails = ",".join(u[-4:] for u in daily_new[d])
            print(f"{d} | {len(daily_new[d])} | {tails}")
    sep = "2026-09-01"
    before = [d for d in first_seen.values() if d < sep]
    print(f"(8/25 前首次出現的 user 總數={len(before)},最早={min(first_seen.values())})")


if __name__ == "__main__":
    main()
