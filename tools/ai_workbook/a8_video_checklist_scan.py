#!/usr/bin/env python3
"""Incrementally scan A8 Drive video-project folders into video_checklist.json.

Merges folder-name versions of the same video (e.g. "20260621說事實木地板開幕"
vs "0621說事實木地板開幕") into one entry, keyed on normalized date + event name.
Re-running is safe: existing manual annotations (completion_status, status_notes)
are never overwritten, only new/changed folders are merged in.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_YEAR = "2026"  # fallback century-year prefix for 4-digit MMDD folder names

DATE_PREFIX_RE = re.compile(r"^(\d{8}|\d{4})[-_]?(.*)$")
NOISE_RE = re.compile(r"[\s\-_,，。！？/／()（）]+")


def fetch_drive_folders_stub(dump_path: Path) -> list[dict]:
    """Stub Drive listing function.

    今版讀本地 JSON dump（由上層 orchestrator 用 Drive 連接器抓出種子資料寫入，
    格式見 workbook/a8/drive_dump_seed.json）。

    之後接 Drive API 時，把這個函式換成例如：
        service.files().list(
            q=f"'{ROOT_FOLDER_ID}' in parents and "
              "mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name,modifiedTime)",
        ).execute()
    回傳格式需維持 list[{"folder_id": str, "raw_name": str, "modified_time": str|None}]，
    呼叫端（merge_folder_into_checklist）不需要再改。
    """
    data = json.loads(dump_path.read_text(encoding="utf-8"))
    return data.get("folders", [])


def parse_folder_name(raw_name: str) -> tuple[str | None, str]:
    match = DATE_PREFIX_RE.match(raw_name.strip())
    if not match:
        return None, raw_name.strip()
    date_token, rest = match.groups()
    return date_token, rest.strip()


def normalize_date(date_token: str | None, default_year: str) -> str | None:
    if date_token is None:
        return None
    if len(date_token) == 8:
        return date_token
    if len(date_token) == 4:
        return f"{default_year}{date_token}"
    return None


def normalize_event_key(event_name: str) -> str:
    return NOISE_RE.sub("", event_name)


def make_video_id(normalized_date: str | None, event_name: str) -> str:
    date_part = normalized_date or "unknown-date"
    return f"{date_part}_{normalize_event_key(event_name)}"


def load_checklist(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "last_scan_at": None, "videos": []}
    return json.loads(path.read_text(encoding="utf-8"))


def find_video_by_folder_id(checklist: dict, folder_id: str) -> tuple[dict, dict] | None:
    for video in checklist["videos"]:
        for version in video["versions"]:
            if version["folder_id"] == folder_id:
                return video, version
    return None


def find_video_by_identity(checklist: dict, normalized_date: str | None, event_name: str) -> dict | None:
    key = normalize_event_key(event_name)
    for video in checklist["videos"]:
        if video["normalized_date"] == normalized_date and normalize_event_key(video["event_name_display"]) == key:
            return video
    return None


def find_video_by_id(checklist: dict, video_id: str) -> dict | None:
    for video in checklist["videos"]:
        if video["video_id"] == video_id:
            return video
    return None


def merge_folder_into_checklist(checklist: dict, folder: dict, scan_time: str, default_year: str) -> None:
    folder_id = folder["folder_id"]
    raw_name = folder["raw_name"]
    date_token, event_name = parse_folder_name(raw_name)
    normalized_date = normalize_date(date_token, default_year)

    existing = find_video_by_folder_id(checklist, folder_id)
    if existing is not None:
        _video, version = existing
        version["raw_name"] = raw_name
        version["raw_date_token"] = date_token
        version["modified_time"] = folder.get("modified_time")
        version["last_seen_scan"] = scan_time
        return

    version_entry = {
        "folder_id": folder_id,
        "raw_name": raw_name,
        "raw_date_token": date_token,
        "modified_time": folder.get("modified_time"),
        "first_seen_scan": scan_time,
        "last_seen_scan": scan_time,
    }

    video = find_video_by_identity(checklist, normalized_date, event_name)
    if video is not None:
        video["versions"].append(version_entry)
        return

    video_id = make_video_id(normalized_date, event_name)
    base_video_id, suffix = video_id, 2
    while find_video_by_id(checklist, video_id) is not None:
        video_id = f"{base_video_id}-{suffix}"
        suffix += 1

    checklist["videos"].append(
        {
            "video_id": video_id,
            "event_name_display": event_name,
            "normalized_date": normalized_date,
            "completion_status": "unknown",
            "status_notes": "",
            "versions": [version_entry],
        }
    )


def render_markdown(checklist: dict) -> str:
    lines = [
        "# A8 影片完成度 Checklist",
        "",
        "> 由 `tools/ai_workbook/a8_video_checklist_scan.py` 從 `video_checklist.json` 重新產生，不要手動編輯本檔；"
        "要加註記請改 `video_checklist.json` 裡的 `completion_status` / `status_notes`。",
        "",
        f"最後掃描：{checklist.get('last_scan_at') or '（尚未掃描）'}",
        "",
        "| video_id | 事件名稱 | 日期 | 完成狀態 | 版本數 | folder_id(s) |",
        "|---|---|---|---|---|---|",
    ]
    for video in sorted(checklist["videos"], key=lambda v: (v["normalized_date"] or "", v["video_id"])):
        folder_ids = ", ".join(v["folder_id"] for v in video["versions"])
        lines.append(
            f"| {video['video_id']} | {video['event_name_display']} | {video['normalized_date']} "
            f"| {video['completion_status']} | {len(video['versions'])} | {folder_ids} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", type=Path, default=Path("workbook/a8/drive_dump_seed.json"), help="Local Drive-folder-list JSON dump (stub input)")
    parser.add_argument("--checklist", type=Path, default=Path("workbook/a8/video_checklist.json"))
    parser.add_argument("--checklist-md", type=Path, default=Path("workbook/a8/video_checklist.md"))
    parser.add_argument("--default-year", default=DEFAULT_YEAR, help="Century-year prefix used for 4-digit MMDD folder names")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checklist = load_checklist(args.checklist)
    folders = fetch_drive_folders_stub(args.dump)
    scan_time = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for folder in folders:
        merge_folder_into_checklist(checklist, folder, scan_time, args.default_year)

    checklist["last_scan_at"] = scan_time

    args.checklist.parent.mkdir(parents=True, exist_ok=True)
    args.checklist.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.checklist_md.write_text(render_markdown(checklist), encoding="utf-8")
    print(f"Scanned {len(folders)} folders -> {len(checklist['videos'])} video(s). Checklist: {args.checklist}")


if __name__ == "__main__":
    main()
