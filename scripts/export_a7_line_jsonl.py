#!/usr/bin/env python3
"""export_a7_line_jsonl.py — A7 LINE 訓練資料 JSONL exporter (T-HQ-001 P6)

讀取 a6_case_store.sqlite3，把「客戶問句 → 業務回覆」配對輸出成 JSONL。
每行格式：{"prompt": "...", "completion": "...", "case_id": "...", "date": "..."}

注意：LINE webhook 只接收客戶→OA 訊息，DB 中目前無業務回覆側資料。
- `--pairs` 模式（預設）：嘗試配對，目前因資料限制會輸出 0 pairs。
- `--inputs-only` 模式：只輸出客戶問句（prompt only），用於意圖分類訓練。
  完整雙向訓練資料需 LINE OA Manager CSV 匯出（見 skills/a6-system-operations.md）。

不讀 secrets、不連網、不寫回 SQLite。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "case-store" / "a6_case_store.sqlite3"
DEFAULT_OUT = REPO_ROOT / "data" / "a7-training" / "line_qa_pairs.jsonl"

TAIPEI = timezone(timedelta(hours=8))


def fetch_message_pairs(db_path: Path, since_iso: str | None = None) -> list[dict]:
    """Return list of (customer_msg, staff_reply) pairs from LINE conversations."""
    if not db_path.exists():
        print(f"[warn] DB not found: {db_path}. Exporting 0 pairs.", file=sys.stderr)
        return []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        where = ""
        params: list = []
        if since_iso:
            where = "WHERE timestamp_iso >= ?"
            params = [since_iso]

        rows = conn.execute(
            f"""
            SELECT msg_id, case_id_sheet, timestamp_iso, speaker, message
            FROM raw_messages
            {where}
            ORDER BY case_id_sheet, timestamp_iso
            """,
            params,
        ).fetchall()

    pairs: list[dict] = []
    by_case: dict[str, list] = {}
    for row in rows:
        case = row["case_id_sheet"]
        by_case.setdefault(case, []).append(dict(row))

    for case_id, msgs in by_case.items():
        for i, msg in enumerate(msgs):
            if msg["speaker"].lower() in ("customer", "客戶", "line_user", "client"):
                next_staff = next(
                    (
                        m
                        for m in msgs[i + 1 :]
                        if m["speaker"].lower() not in ("customer", "客戶", "line_user", "client")
                    ),
                    None,
                )
                if next_staff and next_staff["message"].strip():
                    pairs.append(
                        {
                            "prompt": msg["message"].strip(),
                            "completion": next_staff["message"].strip(),
                            "case_id": case_id,
                            "date": (msg["timestamp_iso"] or "")[:10],
                        }
                    )
    return pairs


def _fetch_all_customer_messages(db_path: Path, since_iso: str | None = None) -> list[dict]:
    """Return all customer messages as prompt-only records (no completion)."""
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        where = "WHERE source='LINE'"
        params: list = []
        if since_iso:
            where += " AND timestamp_iso >= ?"
            params = [since_iso]
        rows = conn.execute(
            f"""
            SELECT msg_id, case_id_sheet, timestamp_iso, speaker, message
            FROM raw_messages
            {where}
            ORDER BY timestamp_iso
            """,
            params,
        ).fetchall()
    return [
        {
            "prompt": r["message"].strip(),
            "case_id": r["case_id_sheet"],
            "speaker": r["speaker"],
            "date": (r["timestamp_iso"] or "")[:10],
        }
        for r in rows
        if r["message"].strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export A7 LINE training pairs to JSONL")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite DB path")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSONL path")
    parser.add_argument("--since", default=None, help="ISO date filter e.g. 2026-01-01")
    parser.add_argument("--dry-run", action="store_true", help="Print stats only, no file write")
    parser.add_argument(
        "--inputs-only",
        action="store_true",
        help="Export customer messages only (prompt-only JSONL, no completion pairing)",
    )
    args = parser.parse_args()

    if args.inputs_only:
        records = _fetch_all_customer_messages(args.db, args.since)
        print(f"[info] {len(records)} customer messages from {args.db}")
        if args.dry_run:
            for r in records[:3]:
                print(json.dumps(r, ensure_ascii=False))
            return
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[info] Written to {args.out}")
        return

    pairs = fetch_message_pairs(args.db, args.since)
    print(f"[info] Exported {len(pairs)} QA pairs from {args.db}")
    if not pairs:
        print("[warn] 0 pairs — LINE webhook 只含客戶訊息，業務回覆側資料尚未接入。")
        print("[hint] 用 --inputs-only 可輸出客戶問句清單。")

    if args.dry_run:
        for p in pairs[:3]:
            print(json.dumps(p, ensure_ascii=False))
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"[info] Written to {args.out}")


if __name__ == "__main__":
    main()
