#!/usr/bin/env python3
"""sheet_tail.py — 讀單一 Google Sheet 分頁的尾 N 列（唯讀）。

用途：5 秒驗證某個 live sheet 分頁「最後更新到哪天 / 還在不在寫」，
不必再靠人工開 sheet 或卡瀏覽器。

複用既有授權（不重造）：
  ~/.claude/mcp-keys/google-token.json + spreadsheets.readonly
  （與 bot_a6/case_store.py 同一把 token / 同一組 scope）

隱私：預設只印「列數 + 指定欄位（預設 timestamp,source）」，不 dump 訊息內容。
      顧客對話是敏感個資；要看內容請顯式加 --show-cols 並自行負責去識別。

範例：
  bot/venv/bin/python scripts/sheet_tail.py \
      --sheet-id 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg \
      --tab CONVERSATION_LOG --rows 5
"""
from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\..*")

DEFAULT_TOKEN = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def fetch_values(sheet_id: str, tab: str, cols: str, token_path: Path) -> list[list[str]]:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(token_path), scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{tab}!{cols}", valueRenderOption="FORMATTED_VALUE")
        .execute()
    )
    return result.get("values", [])


def main() -> int:
    ap = argparse.ArgumentParser(description="Read the last N rows of one Google Sheet tab (read-only).")
    ap.add_argument("--sheet-id", required=True)
    ap.add_argument("--tab", required=True)
    ap.add_argument("--cols", default="A:Z", help="A1 column span, default A:Z")
    ap.add_argument("--rows", type=int, default=5, help="how many trailing rows to show")
    ap.add_argument("--show-cols", default="timestamp,source",
                    help="header names to print (comma sep). 'ALL' dumps every column (may expose PII).")
    ap.add_argument("--token", default=str(DEFAULT_TOKEN))
    args = ap.parse_args()

    token_path = Path(os.path.expanduser(args.token))
    if not token_path.exists():
        print(f"ERROR: token not found: {token_path}")
        return 2

    values = fetch_values(args.sheet_id, args.tab, args.cols, token_path)
    if not values:
        print(f"[sheet_tail] {args.tab}: 0 rows returned (empty tab or no access).")
        return 0

    header = [h.strip() for h in values[0]]
    data = values[1:]
    total = len(data)
    tail = data[-args.rows:]
    first_row_no = total - len(tail) + 2  # +1 header, +1 to 1-based

    print(f"[sheet_tail] tab={args.tab}  data_rows={total}  header={header}")
    wanted = header if args.show_cols.upper() == "ALL" else [c.strip() for c in args.show_cols.split(",")]
    idx = {h: i for i, h in enumerate(header)}
    for n, row in enumerate(tail, start=first_row_no):
        padded = list(row) + [""] * max(0, len(header) - len(row))
        cells = {h: (padded[idx[h]] if h in idx and idx[h] < len(padded) else "") for h in wanted}
        pretty = "  ".join(f"{h}={cells[h]!r}" for h in wanted)
        print(f"  row {n}: {pretty}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
