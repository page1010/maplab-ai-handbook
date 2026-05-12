import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .paths import OUTPUTS_DIR, ROOT


ASSET_LOG_SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
ASSET_LOG_SHEET_NAME = "工作表1"
GOOGLE_TOKEN_PATH = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
DEFAULT_QUOTE_ROOT = (
    Path.home()
    / "Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/外燴 訂單"
)


@dataclass
class AssetRecord:
    row: int
    year: str
    filename: str
    file_id: str
    category: str
    keywords: str
    alt_text: str
    seo_name: str
    status: str


def build_2025_case_match_report(
    year: str = "2025",
    limit: int = 120,
    target_date: str = "",
) -> Path:
    creds = _get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive_svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    rows = _read_asset_log_rows(sheets_svc)
    assets = [
        rec
        for rec in _normalize_asset_rows(rows)
        if rec.year == year and "外燴" in rec.category
    ]
    if limit > 0:
        assets = assets[:limit]

    quote_index = _build_quote_index(year)
    event_index = _load_timetree_lookup()
    candidates: Dict[str, Dict] = defaultdict(lambda: _empty_candidate())

    for asset in assets:
        meta = _read_drive_image_meta(drive_svc, asset.file_id)
        photo_date = _metadata_date(meta.get("photoTime") or "")
        if target_date and photo_date != target_date:
            continue
        if not photo_date:
            continue

        candidate = candidates[photo_date]
        candidate["date"] = photo_date
        candidate["assets"].append(
            {
                "asset_log_row": asset.row,
                "filename": asset.filename,
                "file_id": asset.file_id,
                "drive_url": f"https://drive.google.com/file/d/{asset.file_id}/view",
                "photo_time": meta.get("photoTime") or "",
                "seo_name": asset.seo_name,
                "keywords": asset.keywords,
                "alt_text": asset.alt_text,
                "suggested_dest_path": _suggest_dest_path(asset),
                "width": meta.get("width"),
                "height": meta.get("height"),
            }
        )
        candidate["quote_sheets"] = quote_index.get(photo_date, [])
        event_payload = event_index.get(photo_date) or {}
        candidate["timetree_events"] = event_payload.get("events", [])
        candidate["confidence"] = _score_candidate(candidate)
        candidate["confidence_notes"] = _confidence_notes(candidate)

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "year": year,
        "limit": limit,
        "target_date": target_date,
        "source": {
            "asset_log_sheet_id": ASSET_LOG_SHEET_ID,
            "asset_log_sheet_name": ASSET_LOG_SHEET_NAME,
            "quote_root": str(DEFAULT_QUOTE_ROOT / f"{year}外燴訂單"),
            "timetree_lookup": "data/timetree_events_2022_2026.json",
        },
        "matching_rule": [
            "ASSET_LOG row must be year=2025 and category contains 外燴.",
            "Drive image metadata must expose imageMediaMetadata.time.",
            "Photo date is matched to local quote .gsheet filename date.",
            "Photo date is matched to TimeTree catering event when available.",
            "Image recognition is not trusted as a primary key; it is only a QA layer after date/source match.",
        ],
        "candidates": sorted(
            candidates.values(),
            key=lambda item: (-item["confidence"], item["date"]),
        ),
    }

    out_dir = OUTPUTS_DIR / str(date.today()) / "T-A4-2025-asset-case-match"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "case_match_report.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown_summary(out.with_suffix(".md"), result)
    return out


def _empty_candidate() -> Dict:
    return {
        "date": "",
        "confidence": 0,
        "confidence_notes": [],
        "quote_sheets": [],
        "timetree_events": [],
        "assets": [],
    }


def _get_credentials() -> Credentials:
    with GOOGLE_TOKEN_PATH.open() as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes"),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data["token"] = creds.token
        GOOGLE_TOKEN_PATH.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    return creds


def _read_asset_log_rows(sheets_svc) -> List[List[str]]:
    resp = (
        sheets_svc.spreadsheets()
        .values()
        .get(spreadsheetId=ASSET_LOG_SHEET_ID, range=f"'{ASSET_LOG_SHEET_NAME}'!A1:J")
        .execute()
    )
    return resp.get("values", [])


def _normalize_asset_rows(rows: List[List[str]]) -> List[AssetRecord]:
    normalized: List[AssetRecord] = []
    for row_num, row in enumerate(rows[1:], start=2):
        padded = (row + [""] * 10)[:10]
        if _looks_like_year(padded[0]) and _looks_like_file_id(padded[2]):
            normalized.append(
                AssetRecord(
                    row=row_num,
                    year=padded[0].strip(),
                    filename=padded[1].strip(),
                    file_id=padded[2].strip(),
                    category=padded[3].strip(),
                    keywords=padded[4].strip(),
                    alt_text=padded[5].strip(),
                    seo_name=padded[6].strip(),
                    status=padded[8].strip(),
                )
            )
        elif _looks_like_file_id(padded[0]) and padded[3].strip():
            normalized.append(
                AssetRecord(
                    row=row_num,
                    year=padded[8].strip(),
                    filename=padded[1].strip(),
                    file_id=padded[0].strip(),
                    category=padded[3].strip(),
                    keywords=padded[4].strip(),
                    alt_text=padded[5].strip(),
                    seo_name=padded[2].strip(),
                    status=padded[9].strip(),
                )
            )
    return normalized


def _read_drive_image_meta(drive_svc, file_id: str) -> Dict:
    meta = (
        drive_svc.files()
        .get(
            fileId=file_id,
            fields="id,name,imageMediaMetadata(time,width,height),webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )
    image_meta = meta.get("imageMediaMetadata") or {}
    return {
        "id": meta.get("id"),
        "name": meta.get("name"),
        "photoTime": image_meta.get("time"),
        "width": image_meta.get("width"),
        "height": image_meta.get("height"),
        "webViewLink": meta.get("webViewLink"),
    }


def _build_quote_index(year: str) -> Dict[str, List[Dict[str, str]]]:
    root = DEFAULT_QUOTE_ROOT / f"{year}外燴訂單"
    index: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    if not root.exists():
        return index
    for path in sorted(root.glob("*.gsheet")):
        matched_date = _date_from_quote_filename(path.name, year)
        if not matched_date:
            continue
        doc_id = _read_gsheet_doc_id(path)
        index[matched_date].append(
            {
                "name": path.name,
                "path": str(path),
                "spreadsheet_id": doc_id,
                "url": f"https://docs.google.com/spreadsheets/d/{doc_id}/edit" if doc_id else "",
            }
        )
    return index


def _read_gsheet_doc_id(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return payload.get("doc_id") or ""


def _load_timetree_lookup() -> Dict[str, Dict]:
    path = ROOT / "data/timetree_events_2022_2026.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("lookup", {})


def _date_from_quote_filename(name: str, year: str) -> str:
    patterns = [
        rf"{year}\s+(\d{{1,2}})\s+(\d{{1,2}})",
        rf"{year}(\d{{1,2}})\s+(\d{{1,2}})",
    ]
    for pattern in patterns:
        m = re.search(pattern, name)
        if m:
            return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return ""


def _metadata_date(value: str) -> str:
    m = re.match(r"(\d{4}):(\d{2}):(\d{2})", value or "")
    if not m:
        return ""
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"


def _suggest_dest_path(asset: AssetRecord) -> str:
    kw = asset.keywords.lower()
    if any(token in kw for token in ["辦公室", "會議", "公司", "企業", "茶點"]):
        sub = "corporate"
    elif any(token in kw for token in ["開幕", "品牌"]):
        sub = "corporate"
    elif any(token in kw for token in ["生日", "週歲", "抓周"]):
        sub = "birthday"
    elif any(token in kw for token in ["婚", "wedding"]):
        sub = "wedding"
    elif "甜點" in kw:
        sub = "dessert"
    else:
        sub = "other"
    filename = asset.seo_name or asset.filename
    return f"MAPLAB_ASSETS/{asset.year}/catering/{sub}/{filename}"


def _score_candidate(candidate: Dict) -> int:
    score = 0
    if candidate["assets"]:
        score += 25
    if len(candidate["assets"]) >= 2:
        score += 10
    if candidate["quote_sheets"]:
        score += 30
    if candidate["timetree_events"]:
        score += 25
    if any("辦公室" in a["keywords"] or "茶點" in a["keywords"] for a in candidate["assets"]):
        score += 10
    return min(score, 100)


def _confidence_notes(candidate: Dict) -> List[str]:
    notes = []
    if candidate["assets"]:
        notes.append("ASSET_LOG has catering rows whose Drive metadata photo date matches this date.")
    if candidate["quote_sheets"]:
        notes.append("Local Google Drive quote sheet filename matches this date.")
    if candidate["timetree_events"]:
        notes.append("TimeTree catering event exists on this date.")
    if len(candidate["assets"]) >= 2:
        notes.append("Multiple photos on the same date point to the same event context.")
    return notes


def _write_markdown_summary(path: Path, payload: Dict) -> None:
    lines = [
        "# A4 2025 Asset Case Match Report",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Year: {payload['year']}",
        f"- Target date: {payload['target_date'] or 'auto'}",
        "",
        "## Top Candidates",
        "",
    ]
    for item in payload["candidates"][:10]:
        lines.extend(
            [
                f"### {item['date']} — confidence {item['confidence']}",
                "",
                f"- TimeTree: {', '.join(item['timetree_events']) or 'none'}",
                f"- Quote sheets: {', '.join(q['name'] for q in item['quote_sheets']) or 'none'}",
                "- Assets:",
            ]
        )
        for asset in item["assets"][:8]:
            lines.append(
                f"  - Row {asset['asset_log_row']}: `{asset['seo_name']}` / {asset['photo_time']} / {asset['drive_url']}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _looks_like_year(value: str) -> bool:
    return value.isdigit() and len(value) == 4 and 2000 <= int(value) <= 2100


def _looks_like_file_id(value: str) -> bool:
    return bool(value) and not value.isdigit() and len(value) >= 10 and any(c.isalpha() for c in value)
