import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, List

from .paths import OUTPUTS_DIR, ROOT


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
ASSET_LOG_SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
ASSET_LOG_SHEET_NAME = "工作表1"
ASSET_LOG_URL = f"https://docs.google.com/spreadsheets/d/{ASSET_LOG_SHEET_ID}/edit"
MAPLAB_ASSETS_FOLDER_ID = "1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy"
GOOGLE_TOKEN_PATH = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
GOOGLE_CREDENTIALS_PATH = Path.home() / ".claude" / "mcp-keys" / "google-credentials.json"


def build_photo_classification_plan(scan_dir: str = "data/telegram-photos") -> Path:
    base = ROOT / scan_dir
    files = []
    if base.exists():
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                files.append(p)

    plan = []
    for p in files:
        target_cluster = _infer_cluster(p.name)
        suggested_path = f"assets/{target_cluster}/{p.name}"
        plan.append(
            {
                "source": str(p.relative_to(ROOT)),
                "target_cluster": target_cluster,
                "suggested_target": suggested_path,
                "confidence": 0.55,
                "status": "proposed_only",
            }
        )

    counter = Counter([x["target_cluster"] for x in plan])
    payload = {
        "date": str(date.today()),
        "scan_dir": scan_dir,
        "total_images": len(plan),
        "cluster_counts": dict(counter),
        "rules": [
            "先產生分類計畫，不直接搬檔",
            "低信心項目交給 ollama/gemini 補分類",
            "人工核准後才 move",
        ],
        "items": plan,
    }
    out_dir = OUTPUTS_DIR / str(date.today()) / "T-A4-photo-classification-restart"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "classification_plan.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def build_asset_log_snapshot(limit: int = 2000) -> Path:
    rows = _read_asset_log_rows()
    records = _normalize_asset_log_rows(rows)
    if limit > 0:
        sample = records[:limit]
    else:
        sample = records

    category_counts = Counter(r.get("category") or "空白" for r in records)
    status_counts = Counter(r.get("status") or "空白" for r in records)
    year_counts = Counter(r.get("year") or "空白" for r in records)
    output = {
        "date": str(date.today()),
        "source": {
            "type": "google_sheet",
            "name": "MAPLAB_ASSET_LOG",
            "spreadsheet_id": ASSET_LOG_SHEET_ID,
            "sheet_name": ASSET_LOG_SHEET_NAME,
            "url": ASSET_LOG_URL,
            "maplab_assets_folder_id": MAPLAB_ASSETS_FOLDER_ID,
        },
        "total_rows": len(records),
        "category_counts": dict(category_counts),
        "status_counts": dict(status_counts),
        "year_counts": dict(year_counts),
        "sample_rows": sample[:50],
        "next_actions": [
            "Use verified MAPLAB_ASSETS root 1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy; old root 1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe returns Drive API 404.",
            "Run Drive organization in dry-run mode first.",
            "Use ASSET_LOG category/keywords/seo_name to copy photos into MAPLAB_ASSETS; do not delete originals.",
        ],
    }
    out_dir = OUTPUTS_DIR / str(date.today()) / "T-A4-photo-classification-restart"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "asset_log_snapshot.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _read_asset_log_rows() -> List[List[str]]:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("sheets", "v4", credentials=creds)
    resp = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=ASSET_LOG_SHEET_ID,
            range=f"'{ASSET_LOG_SHEET_NAME}'!A1:J",
        )
        .execute()
    )
    return resp.get("values", [])


def _normalize_asset_log_rows(rows: List[List[str]]) -> List[Dict[str, str]]:
    if not rows:
        return []
    records = []
    for row in rows[1:]:
        rec = _normalize_one_row(row)
        if rec.get("file_id") or rec.get("filename"):
            records.append(rec)
    return records


def _normalize_one_row(row: List[str]) -> Dict[str, str]:
    # Pioneer rows and batch rows have different column order. Detect by col A.
    padded = row + [""] * (10 - len(row))
    if padded[0].isdigit() and len(padded[0]) == 4:
        year, filename, file_id, category, keywords, alt_text, seo_name, tokens, status, timestamp = padded[:10]
        drive_url = f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""
    else:
        file_id, filename, seo_name, category, keywords, alt_text, drive_url, tokens, year, status = padded[:10]
        timestamp = ""
    return {
        "year": year,
        "filename": filename,
        "file_id": file_id,
        "category": category,
        "keywords": keywords,
        "alt_text": alt_text,
        "seo_name": seo_name,
        "tokens": tokens,
        "status": status,
        "timestamp": timestamp,
        "drive_url": drive_url or (f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""),
    }


def _infer_cluster(name: str) -> str:
    n = name.lower()
    if re.search(r"wedding|婚|宴|迎賓", n):
        return "wedding"
    if re.search(r"birthday|抓周|週歲|party", n):
        return "birthday"
    if re.search(r"corp|企業|會議|品牌|開幕", n):
        return "corporate"
    return "uncategorized"
