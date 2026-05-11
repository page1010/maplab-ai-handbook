#!/usr/bin/env python3
"""
Move A4 assets from MAPLAB_ASSET_LOG into MAPLAB_ASSETS.

This script copies files into a structured Drive hierarchy while keeping
the original files intact. It resolves the actual source file by searching
for the recorded filename inside the year's Google Photos folder.

Default hierarchy:
  MAPLAB_ASSETS/{year}/{category}/{subfolder?}

Use --apply to perform real copies. Without --apply, the script prints a plan.
"""

import argparse
import io
import json
import sys
from datetime import datetime
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
SHEET_TAB = "工作表1"
SOURCE_ROOT_FOLDER_ID = "1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz"
DEST_ROOT_FOLDER_ID = "1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy"
TOKEN_PATH = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
REPORT_DIR = Path("/Users/pagemacmini/maplab-ai-handbook/workbook/outputs")
CHECKPOINT_NAME = "checkpoint.json"


@dataclass
class AssetRow:
    source_row: int
    sheet_file_id: str
    filename: str
    seo_name: str
    category: str
    keywords: str
    year: str


def get_credentials() -> Credentials:
    with TOKEN_PATH.open() as f:
        td = json.load(f)
    creds = Credentials(
        token=td.get("token"),
        refresh_token=td.get("refresh_token"),
        token_uri=td.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=td.get("client_id"),
        client_secret=td.get("client_secret"),
        scopes=td.get("scopes"),
    )
    if creds.expired and creds.refresh_token:
        print("  Token expired, refreshing...")
        creds.refresh(Request())
        td["token"] = creds.token
        with TOKEN_PATH.open("w") as f:
            json.dump(td, f, indent=2)
    return creds


def read_rows(sheets_svc) -> List[List[str]]:
    resp = (
        sheets_svc.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range=f"'{SHEET_TAB}'!A1:J")
        .execute()
    )
    return resp.get("values", [])


def normalize_rows(rows: List[List[str]]) -> List[AssetRow]:
    if not rows:
        return []

    normalized: List[AssetRow] = []
    for idx, row in enumerate(rows[1:], start=2):
        parsed = normalize_row(idx, row)
        if parsed:
            normalized.append(parsed)
    return normalized


def normalize_row(row_num: int, row: List[str]) -> Optional[AssetRow]:
    padded = (row + [""] * 10)[:10]

    # Schema A: file_id | original_name | seo_name | category | keywords | alt_text | drive_url | ... | year | file_type
    if looks_like_file_id(padded[0]) and padded[3].strip():
        sheet_file_id = padded[0].strip()
        filename = padded[1].strip()
        seo_name = padded[2].strip() or filename or sheet_file_id
        category = padded[3].strip()
        keywords = padded[4].strip()
        year = padded[8].strip() if len(padded) > 8 else ""
        return AssetRow(row_num, sheet_file_id, filename, seo_name, category, keywords, year)

    # Schema B: year | filename | file_id | category | keywords | alt_text | seo_name | ... | status | timestamp
    if looks_like_year(padded[0]) and looks_like_file_id(padded[2]):
        year = padded[0].strip()
        filename = padded[1].strip()
        sheet_file_id = padded[2].strip()
        category = padded[3].strip()
        keywords = padded[4].strip()
        seo_name = padded[6].strip() or filename or sheet_file_id
        return AssetRow(row_num, sheet_file_id, filename, seo_name, category, keywords, year)

    return None


def looks_like_year(value: str) -> bool:
    return value.isdigit() and len(value) == 4 and 2000 <= int(value) <= 2100


def looks_like_file_id(value: str) -> bool:
    if not value:
        return False
    if value.isdigit():
        return False
    return len(value) >= 10 and any(c.isalpha() for c in value)


def resolve_folder_path(category: str, keywords: str) -> List[str]:
    cat = (category or "").strip()
    kw = (keywords or "").lower()

    category_root = "other"
    if "外燴" in cat:
        category_root = "catering"
    elif "旅遊" in cat:
        category_root = "travel"
    elif "日常" in cat:
        category_root = "daily"

    if category_root == "catering":
        for name, triggers in [
            ("birthday", ["生日", "birthday", "寶寶", "週歲", "抓周"]),
            ("wedding", ["婚禮", "wedding"]),
            ("corporate", ["企業", "開幕", "尾牙", "corporate", "會議", "品牌"]),
            ("dessert", ["甜點", "蛋糕", "布丁", "塔", "puff"]),
        ]:
            if any(t.lower() in kw for t in triggers):
                return [category_root, name]
        return [category_root, "other"]

    if category_root == "travel":
        return [category_root]
    if category_root == "daily":
        return [category_root]
    return [category_root]


def find_or_create_folder(drive_svc, name: str, parent_id: str, cache: Dict[str, str], dry_run: bool) -> str:
    key = f"{parent_id}:{name}"
    if key in cache:
        return cache[key]

    q = (
        "mimeType='application/vnd.google-apps.folder' "
        f"and name='{name}' and '{parent_id}' in parents and trashed=false"
    )
    resp = drive_svc.files().list(q=q, fields="files(id,name)").execute()
    files = resp.get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        if dry_run:
            folder_id = f"dry_{name}"
            print(f"  [DRY_RUN] folder {name}")
        else:
            folder = drive_svc.files().create(
                body={
                    "name": name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id],
                },
                fields="id",
            ).execute()
            folder_id = folder["id"]
            print(f"  folder {name} -> {folder_id}")

    cache[key] = folder_id
    return folder_id


def find_existing_folder(drive_svc, name: str, parent_id: str, cache: Dict[str, str]) -> Optional[str]:
    key = f"{parent_id}:{name}:existing"
    if key in cache:
        return cache[key] or None

    q = (
        "mimeType='application/vnd.google-apps.folder' "
        f"and name='{name}' and '{parent_id}' in parents and trashed=false"
    )
    resp = drive_svc.files().list(q=q, fields="files(id,name)").execute()
    files = resp.get("files", [])
    folder_id = files[0]["id"] if files else ""
    cache[key] = folder_id
    return folder_id or None


def list_folder_files(drive_svc, folder_id: str) -> Dict[str, str]:
    files: Dict[str, str] = {}
    page_token = None
    while True:
        resp = drive_svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken,files(id,name,mimeType)",
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        for item in resp.get("files", []):
            if item.get("mimeType") != "application/vnd.google-apps.folder":
                files[item.get("name", "")] = item.get("id", "")
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def list_folder_file_names(drive_svc, folder_id: str) -> Set[str]:
    return set(list_folder_files(drive_svc, folder_id).keys())


def find_file_by_name(
    drive_svc,
    folder_id: str,
    filename: str,
    cache: Dict[str, Dict[str, str]],
) -> Optional[str]:
    if folder_id not in cache:
        cache[folder_id] = list_folder_files(drive_svc, folder_id)
    return cache[folder_id].get(filename) or None


def file_exists_in_folder(drive_svc, folder_id: str, filename: str, cache: Dict[str, Set[str]]) -> bool:
    if folder_id not in cache:
        cache[folder_id] = list_folder_file_names(drive_svc, folder_id)
    return filename in cache[folder_id]


def build_destination_path(year: str, target_parts: List[str], target_name: str) -> str:
    parts = ["MAPLAB_ASSETS", year]
    parts.extend(target_parts)
    parts.append(target_name)
    return "/".join(part for part in parts if part)


def write_sheet_locations(sheets_svc, updates: List[Tuple[int, str, str, str]]) -> None:
    if not updates:
        return
    data = []
    for row_num, dest_path, dest_url, move_status in updates:
        data.append(
            {
                "range": f"'{SHEET_TAB}'!L{row_num}:N{row_num}",
                "values": [[move_status, dest_path, dest_url]],
            }
        )
    sheets_svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()


def checkpoint_path() -> Path:
    return REPORT_DIR / "2026-05-05" / "T-A4-photo-move" / CHECKPOINT_NAME


def build_run_key(args: argparse.Namespace) -> str:
    limit_key = "all" if args.run_all else str(args.limit)
    return (
        f"sheet={SHEET_ID}|tab={SHEET_TAB}|year={args.year or 'any'}|"
        f"offset={args.offset}|limit={limit_key}|run_all={args.run_all}|batch_size={args.batch_size}"
    )


def load_checkpoint(path: Path, run_key: str, start_over: bool) -> Dict[str, object]:
    if start_over or not path.exists():
        return {
            "version": 1,
            "run_key": run_key,
            "next_index": 0,
            "copied": 0,
            "skipped": 0,
            "failed": 0,
            "last_row": None,
            "last_status": None,
            "updated_at": None,
        }
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": 1,
            "run_key": run_key,
            "next_index": 0,
            "copied": 0,
            "skipped": 0,
            "failed": 0,
            "last_row": None,
            "last_status": None,
            "updated_at": None,
        }
    if state.get("run_key") != run_key:
        return {
            "version": 1,
            "run_key": run_key,
            "next_index": 0,
            "copied": 0,
            "skipped": 0,
            "failed": 0,
            "last_row": None,
            "last_status": None,
            "updated_at": None,
        }
    return state


def save_checkpoint(path: Path, state: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(state)
    payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def update_checkpoint(
    state: Dict[str, object],
    path: Path,
    next_index: int,
    copied: int,
    skipped: int,
    failed: int,
    asset: AssetRow,
    status: str,
    note: Optional[str] = None,
) -> None:
    state.update(
        {
            "next_index": next_index,
            "copied": copied,
            "skipped": skipped,
            "failed": failed,
            "last_row": asset.source_row,
            "last_sheet_file_id": asset.sheet_file_id,
            "last_filename": asset.filename,
            "last_status": status,
        }
    )
    if note is not None:
        state["last_note"] = note
    save_checkpoint(path, state)


def copy_file(drive_svc, file_id: str, filename: str, dest_folder_id: str, dry_run: bool) -> Optional[str]:
    if dry_run:
        print(f"  [DRY_RUN] copy {file_id} -> {filename}")
        return f"dry_copy_{file_id}"
    meta = {"name": filename, "parents": [dest_folder_id]}
    copied = drive_svc.files().copy(fileId=file_id, body=meta, fields="id").execute()
    return copied.get("id")


def build_filename(asset: AssetRow, mime: str = "image/jpeg") -> str:
    ext = ""
    if "/" in mime:
        subtype = mime.split("/", 1)[1].lower()
        ext = ".jpg" if subtype in ("jpeg", "jpg") else f".{subtype}"
    if "." in asset.filename:
        ext = "." + asset.filename.rsplit(".", 1)[-1].lower()
    base = asset.seo_name or asset.filename or asset.file_id
    if ext and not base.lower().endswith(ext.lower()):
        return base + ext
    return base


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="perform real Drive copy operations")
    ap.add_argument("--limit", type=int, default=50, help="max rows to process")
    ap.add_argument("--offset", type=int, default=0, help="skip first N normalized rows")
    ap.add_argument("--year", default="", help="optional year filter, e.g. 2024")
    ap.add_argument("--run-all", action="store_true", help="process all matching rows in one run")
    ap.add_argument("--batch-size", type=int, default=250, help="chunk size when using --run-all")
    ap.add_argument("--start-over", action="store_true", help="ignore existing checkpoint and start from the first matching row")
    args = ap.parse_args()

    dry_run = not args.apply
    cpath = checkpoint_path()
    run_key = build_run_key(args)
    state = load_checkpoint(cpath, run_key, args.start_over)
    start_index = int(state.get("next_index") or 0)
    print("=" * 72)
    print("A4 asset move start")
    print(
        f"apply={args.apply} dry_run={dry_run} limit={args.limit} offset={args.offset} "
        f"year={args.year or 'any'} run_all={args.run_all} batch_size={args.batch_size} start_index={start_index}"
    )
    print(f"checkpoint={cpath}")
    print("=" * 72)

    creds = get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive_svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    rows = read_rows(sheets_svc)
    assets = normalize_rows(rows)
    if args.year:
        assets = [a for a in assets if a.year == args.year]
    if args.run_all:
        assets = assets[args.offset :]
    else:
        assets = assets[args.offset : args.offset + args.limit]
    if start_index > len(assets):
        start_index = len(assets)
    assets = assets[start_index:]
    effective_limit = len(assets)

    print(f"normalized_assets={effective_limit}")
    if not assets:
        print("No assets matched.")
        return 0

    folder_cache: Dict[str, str] = {}
    source_cache: Dict[str, str] = {}
    exists_cache: Dict[str, bool] = {}
    copied = int(state.get("copied", 0) or 0)
    skipped = int(state.get("skipped", 0) or 0)
    failed = int(state.get("failed", 0) or 0)
    category_counter = Counter()
    year_counter = Counter()
    report_rows = []
    sheet_updates: List[Tuple[int, str, str, str]] = []

    batches = [assets]
    if args.run_all:
        batches = [assets[i : i + args.batch_size] for i in range(0, len(assets), args.batch_size)]

    processed_offset = start_index
    for batch_index, batch in enumerate(batches, start=1):
        if args.run_all:
            print(f"batch={batch_index}/{len(batches)} size={len(batch)}")

        for i, asset in enumerate(batch, start=1):
            current_index = processed_offset
            year = asset.year or "unknown"
            category_counter[asset.category] += 1
            year_counter[year] += 1

            year_folder_name = f"{year} 年的相片" if year != "unknown" else year
            source_parent = find_existing_folder(drive_svc, year_folder_name, SOURCE_ROOT_FOLDER_ID, folder_cache)
            if not source_parent:
                failed += 1
                report_rows.append({
                    "row": asset.source_row,
                    "sheet_file_id": asset.sheet_file_id,
                    "status": "source_year_missing",
                    "filename": asset.filename,
                    "year": year,
                    "folder": SOURCE_ROOT_FOLDER_ID,
                })
                print(f"[{i}] fail row={asset.source_row} {asset.filename}: source year folder missing")
                processed_offset += 1
                if args.apply:
                    update_checkpoint(state, cpath, processed_offset, copied, skipped, failed, asset, "source_year_missing")
                continue

            target_year_name = year
            parent = find_or_create_folder(drive_svc, target_year_name, DEST_ROOT_FOLDER_ID, folder_cache, dry_run=dry_run)
            target_parts = resolve_folder_path(asset.category, asset.keywords)

            source_file_id = find_file_by_name(drive_svc, source_parent, asset.filename, source_cache)
            if not source_file_id:
                failed += 1
                report_rows.append({
                    "row": asset.source_row,
                    "sheet_file_id": asset.sheet_file_id,
                    "status": "source_missing",
                    "filename": asset.filename,
                    "year": year,
                    "folder": source_parent,
                })
                print(f"[{i}] fail row={asset.source_row} {asset.filename}: source file not found in {year_folder_name}")
                processed_offset += 1
                if args.apply:
                    update_checkpoint(state, cpath, processed_offset, copied, skipped, failed, asset, "source_missing")
                continue

            target_parent = parent
            for part in target_parts:
                target_parent = find_or_create_folder(drive_svc, part, target_parent, folder_cache, dry_run=dry_run)

            target_name = build_filename(asset)
            dest_path = build_destination_path(year, target_parts, target_name)
            if not dry_run and file_exists_in_folder(drive_svc, target_parent, target_name, exists_cache):
                existing_target_file_id = find_file_by_name(drive_svc, target_parent, target_name, source_cache)
                existing_target_url = (
                    f"https://drive.google.com/file/d/{existing_target_file_id}/view"
                    if existing_target_file_id
                    else ""
                )
                skipped += 1
                report_rows.append({
                    "row": asset.source_row,
                    "sheet_file_id": asset.sheet_file_id,
                    "source_file_id": source_file_id,
                    "status": "skipped_exists",
                    "target": target_name,
                    "folder": target_parent,
                    "dest_path": dest_path,
                    "dest_url": existing_target_url,
                })
                if existing_target_url:
                    sheet_updates.append((asset.source_row, dest_path, existing_target_url, "skipped_exists"))
                print(f"[{i}] skip exists row={asset.source_row} {target_name}")
                processed_offset += 1
                if args.apply:
                    update_checkpoint(state, cpath, processed_offset, copied, skipped, failed, asset, "skipped_exists", dest_path)
                continue

            try:
                new_id = copy_file(drive_svc, source_file_id, target_name, target_parent, dry_run=dry_run)
                if new_id:
                    new_url = f"https://drive.google.com/file/d/{new_id}/view"
                    copied += 1
                    report_rows.append({
                        "row": asset.source_row,
                        "sheet_file_id": asset.sheet_file_id,
                        "source_file_id": source_file_id,
                        "status": "copied" if not dry_run else "planned",
                        "target": target_name,
                        "folder": target_parent,
                        "dest_path": dest_path,
                        "dest_url": new_url,
                        "new_id": new_id,
                    })
                    if not dry_run:
                        sheet_updates.append((asset.source_row, dest_path, new_url, "copied"))
                    print(f"[{i}] ok row={asset.source_row} {asset.filename} -> {target_name}")
                    processed_offset += 1
                    if args.apply:
                        update_checkpoint(state, cpath, processed_offset, copied, skipped, failed, asset, "copied", dest_path)
                else:
                    failed += 1
            except Exception as exc:
                failed += 1
                report_rows.append({
                    "row": asset.source_row,
                    "sheet_file_id": asset.sheet_file_id,
                    "source_file_id": source_file_id,
                    "status": "failed",
                    "error": str(exc),
                    "dest_path": dest_path,
                })
                print(f"[{i}] fail row={asset.source_row} {asset.filename}: {exc}")
                processed_offset += 1
                if args.apply:
                    update_checkpoint(state, cpath, processed_offset, copied, skipped, failed, asset, "failed", str(exc))

    if args.apply:
        write_sheet_locations(sheets_svc, sheet_updates)
        state["sheet_updates_applied"] = len(sheet_updates)
        save_checkpoint(cpath, state)

    report_dir = REPORT_DIR / "2026-05-05" / "T-A4-photo-move"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "report.json").write_text(
        json.dumps(
            {
                "apply": args.apply,
                "dry_run": dry_run,
                "limit": args.limit,
                "offset": args.offset,
                "year": args.year,
                "run_all": args.run_all,
                "batch_size": args.batch_size if args.run_all else None,
                "checkpoint_path": str(cpath),
                "checkpoint_start_index": start_index,
                "checkpoint_next_index": processed_offset,
                "copied": copied,
                "skipped": skipped,
                "failed": failed,
                "category_counts": dict(category_counter),
                "year_counts": dict(year_counter),
                "sheet_updates": len(sheet_updates),
                "effective_limit": effective_limit,
                "rows": report_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print(f"done copied={copied} skipped={skipped} failed={failed}")
    print(f"report={report_dir / 'report.json'}")
    print("=" * 72)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
