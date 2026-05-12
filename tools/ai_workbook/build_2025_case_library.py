import io
import json
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .asset_case_matcher import _get_credentials
from .paths import OUTPUTS_DIR, ROOT


REPORT_PATH = (
    OUTPUTS_DIR / str(date.today()) / "T-A4-2025-asset-case-match" / "case_match_report.json"
)
DESKTOP_CASE_ROOT = Path.home() / "Desktop" / "2025案例"

CASE_SPECS = [
    {
        "date": "2025-04-24",
        "folder": "ToB/會議茶點/2025-04-24_科林研發日_企業會議茶點",
        "public_name": "科林研發日企業茶點外燴",
        "seo_category": "台南會議茶點外燴 / 台南企業茶會 / 台南品牌活動外燴",
        "audience": "To B",
        "scene": "會議茶點",
        "sheet_hint": "科林研發股份有限公司 / Lam Day 科林研發日",
        "asset_terms": ["corporate-event", "branded", "customized", "event-refreshments"],
        "public_notes": [
            "企業活動需要準時、好拿取、視覺整齊的茶點配置。",
            "這組素材適合放在會議茶點、企業茶會、品牌活動承接頁。",
            "可強調客製化企業識別小插旗、個別點心與飲品配置。",
        ],
    },
    {
        "date": "2025-02-19",
        "folder": "ToB/企業茶會/2025-02-19_亞綸科技開春聚餐",
        "public_name": "亞綸科技開春聚餐茶點外燴",
        "seo_category": "台南企業外燴 / 台南公司茶會 / 台南會議茶點外燴",
        "audience": "To B",
        "scene": "企業茶會",
        "sheet_hint": "亞綸科技股份有限公司 / 開春聚餐",
        "asset_terms": ["office-event", "office"],
        "public_notes": [
            "小型企業聚餐可用茶點與輕食整理成不佔空間的餐檯。",
            "這組素材適合補企業外燴頁的真實案例區。",
        ],
    },
    {
        "date": "2025-02-15",
        "folder": "ToB/開幕茶會/2025-02-15_開幕茶會_住商不動產與美甲店_待分流",
        "public_name": "開幕茶會外燴案例",
        "seo_category": "台南開幕茶會外燴 / 台南開幕點心 / 品牌開幕外燴",
        "audience": "To B",
        "scene": "開幕茶會",
        "sheet_hint": "住商不動產開幕茶會 + 美甲店開幕茶會，同日素材需人工視覺分流",
        "asset_terms": ["opening", "tea-party", "grand-opening", "business-opening"],
        "public_notes": [
            "開幕茶會重點是第一印象、動線與賓客停留感。",
            "這批素材可先做開幕頁案例骨架，正式發文前需再人工分辨是哪一場。",
        ],
    },
    {
        "date": "2025-02-06",
        "folder": "ToB/品牌活動_建案/2025-02-06_建案開工典禮",
        "public_name": "建案開工典禮茶點外燴",
        "seo_category": "台南品牌活動外燴 / 台南建案發表餐點 / 台南開工典禮茶點",
        "audience": "To B",
        "scene": "品牌活動",
        "sheet_hint": "建案開工典禮",
        "asset_terms": ["bruschetta", "macarons", "snacks", "tiramisu", "dessert-savory"],
        "public_notes": [
            "建案與品牌活動可用精緻小點建立接待感。",
            "這組素材適合品牌活動、建案發表、開工典禮長尾頁。",
        ],
    },
    {
        "date": "2025-05-04",
        "folder": "ToC/生日週歲派對/2025-05-04_慶生派對_兜兜親子空間",
        "public_name": "親子空間慶生派對外燴",
        "seo_category": "台南生日派對外燴 / 台南週歲派對外燴 / 台南家庭聚會外燴",
        "audience": "To C",
        "scene": "生日派對",
        "sheet_hint": "慶生派對 / 兜兜親子空間",
        "asset_terms": ["birthday", "kids", "children", "cream-puffs"],
        "public_notes": [
            "親子派對素材可呈現甜點桌、兒童活動空間與輕食配置。",
            "適合週歲生日頁、家庭聚會頁與再行銷素材。",
        ],
    },
    {
        "date": "2025-05-10",
        "folder": "ToC/生日週歲派對/2025-05-10_週歲派對_輕輕的說",
        "public_name": "週歲派對外燴案例",
        "seo_category": "台南週歲派對外燴 / 台南生日派對外燴 / 台南抓週外燴",
        "audience": "To C",
        "scene": "週歲派對",
        "sheet_hint": "週歲派對 / 輕輕的說",
        "asset_terms": ["first-birthday", "birthday-party", "baked-sandwiches"],
        "public_notes": [
            "週歲案例適合補強目前已突圍的週歲頁，並導流到到府外燴主頁。",
            "素材可用於真實案例區與 FAQ 後的信任補強。",
        ],
    },
    {
        "date": "2025-01-29",
        "folder": "ToC/家庭聚會_入厝/2025-01-29_新居入厝派對",
        "public_name": "新居入厝派對外燴",
        "seo_category": "台南家庭聚會外燴 / 台南入厝外燴 / 台南派對外燴",
        "audience": "To C",
        "scene": "家庭聚會",
        "sheet_hint": "新居入厝",
        "asset_terms": ["buffet", "canape", "glazed-ribs", "hot-food", "pasta"],
        "public_notes": [
            "入厝與家庭聚會重點是大人小孩都方便取用，餐點有飽足感。",
            "可補家庭聚會頁與到府外燴頁的情境案例。",
        ],
    },
    {
        "date": "2025-02-08",
        "folder": "ToC/性別揭曉派對/2025-02-08_性別揭曉派對_單張待補",
        "public_name": "性別揭曉派對外燴",
        "seo_category": "台南性別派對外燴 / 台南派對外燴 / 台南家庭聚會外燴",
        "audience": "To C",
        "scene": "性別揭曉派對",
        "sheet_hint": "性別揭曉派對",
        "asset_terms": ["party-buffet-spread"],
        "public_notes": [
            "目前同日可用照片少，先保留成待補案例。",
            "可作為性別派對關鍵字的草稿入口，不建議直接當完整案例發布。",
        ],
    },
]

BAD_ASSET_TERMS = [
    "quotation",
    "order-form",
    "receipt",
    "menu",
    "restaurant",
    "ramen",
    "korean",
    "japanese-street",
    "food-truck",
    "inquiry-form",
]


def build_2025_desktop_case_library(max_assets_per_case: int = 5) -> Path:
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"Missing case match report: {REPORT_PATH}")

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    by_date = {item["date"]: item for item in report.get("candidates", [])}

    creds = _get_credentials()
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    DESKTOP_CASE_ROOT.mkdir(parents=True, exist_ok=True)
    cases: List[Dict] = []

    for spec in CASE_SPECS:
        candidate = by_date.get(spec["date"])
        case_dir = DESKTOP_CASE_ROOT / spec["folder"]
        assets_dir = case_dir / "assets"
        previews_dir = case_dir / "previews"
        assets_dir.mkdir(parents=True, exist_ok=True)
        previews_dir.mkdir(parents=True, exist_ok=True)

        selected = _select_assets(candidate or {}, spec, max_assets_per_case)
        downloaded = []
        for asset in selected:
            local_name = _asset_local_name(asset)
            local_path = assets_dir / local_name
            preview_path = previews_dir / (Path(local_name).stem + ".jpg")
            if not local_path.exists():
                _download_drive_file(drive, asset["file_id"], local_path)
            _make_preview(local_path, preview_path)
            downloaded.append(
                {
                    "asset_log_row": asset.get("asset_log_row"),
                    "filename": asset.get("filename"),
                    "seo_name": asset.get("seo_name"),
                    "keywords": asset.get("keywords"),
                    "alt_text": asset.get("alt_text"),
                    "photo_time": asset.get("photo_time"),
                    "drive_url": asset.get("drive_url"),
                    "local_asset": str(local_path),
                    "local_preview": str(preview_path) if preview_path.exists() else "",
                }
            )

        case_payload = _case_payload(spec, candidate or {}, downloaded)
        (case_dir / "case_manifest.json").write_text(
            json.dumps(case_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (case_dir / "internal_evidence.md").write_text(
            _internal_evidence_md(case_payload), encoding="utf-8"
        )
        (case_dir / "public_case_notes.md").write_text(
            _public_case_notes_md(case_payload), encoding="utf-8"
        )
        cases.append(case_payload)

    root_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_root": str(DESKTOP_CASE_ROOT),
        "source_report": str(REPORT_PATH),
        "case_count": len(cases),
        "cases": [
            {
                "public_name": item["public_name"],
                "date": item["date"],
                "audience": item["audience"],
                "scene": item["scene"],
                "seo_category": item["seo_category"],
                "folder": item["folder"],
                "asset_count": len(item["assets"]),
                "confidence": item["confidence"],
            }
            for item in cases
        ],
    }
    (DESKTOP_CASE_ROOT / "case_manifest.json").write_text(
        json.dumps(root_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DESKTOP_CASE_ROOT / "README_INDEX.md").write_text(
        _root_index_md(root_payload), encoding="utf-8"
    )
    (DESKTOP_CASE_ROOT / "index.html").write_text(
        _root_gallery_html(cases), encoding="utf-8"
    )
    return DESKTOP_CASE_ROOT


def _select_assets(candidate: Dict, spec: Dict, limit: int) -> List[Dict]:
    assets = candidate.get("assets", [])
    terms = [term.lower() for term in spec.get("asset_terms", [])]

    def score(asset: Dict) -> int:
        hay = " ".join(
            str(asset.get(field, "")).lower()
            for field in ["seo_name", "keywords", "filename", "alt_text"]
        )
        if any(bad in hay for bad in BAD_ASSET_TERMS):
            return -100
        value = 0
        for term in terms:
            if term in hay:
                value += 20
        if asset.get("width") and asset.get("height"):
            value += 3
        if not str(asset.get("filename", "")).lower().endswith(".png"):
            value += 5
        return value

    ranked = sorted(assets, key=score, reverse=True)
    return [asset for asset in ranked if score(asset) >= 0][:limit]


def _asset_local_name(asset: Dict) -> str:
    original = asset.get("filename") or "asset"
    ext = Path(original).suffix or ".bin"
    stem = _safe_slug(asset.get("seo_name") or Path(original).stem)
    row = asset.get("asset_log_row") or "row"
    return f"{row}_{stem}{ext}"


def _download_drive_file(drive, file_id: str, path: Path) -> None:
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    path.write_bytes(buffer.getvalue())


def _make_preview(source: Path, dest: Path) -> None:
    if dest.exists():
        return
    if source.suffix.lower() in [".jpg", ".jpeg"]:
        dest.write_bytes(source.read_bytes())
        return
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(source), "--out", str(dest)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        if source.suffix.lower() == ".png":
            dest.write_bytes(source.read_bytes())


def _case_payload(spec: Dict, candidate: Dict, assets: List[Dict]) -> Dict:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "date": spec["date"],
        "public_name": spec["public_name"],
        "audience": spec["audience"],
        "scene": spec["scene"],
        "seo_category": spec["seo_category"],
        "folder": str(DESKTOP_CASE_ROOT / spec["folder"]),
        "sheet_hint": spec["sheet_hint"],
        "confidence": candidate.get("confidence", 0),
        "confidence_notes": candidate.get("confidence_notes", []),
        "quote_sheets": candidate.get("quote_sheets", []),
        "timetree_events": candidate.get("timetree_events", []),
        "public_notes": spec["public_notes"],
        "assets": assets,
        "public_safety": [
            "Public draft must not include price, headcount, private phone, private address, or local file paths.",
            "Use Drive links and local paths only in internal evidence.",
            "Visual QA is still required before WordPress publishing.",
        ],
    }


def _internal_evidence_md(case: Dict) -> str:
    lines = [
        f"# {case['public_name']} — internal evidence",
        "",
        f"- Date key: {case['date']}",
        f"- Audience: {case['audience']}",
        f"- Scene: {case['scene']}",
        f"- SEO category: {case['seo_category']}",
        f"- Confidence: {case['confidence']}",
        f"- Sheet hint: {case['sheet_hint']}",
        f"- Folder: `{case['folder']}`",
        "",
        "## Quote Sheets",
    ]
    for sheet in case["quote_sheets"]:
        lines.append(f"- [{sheet.get('name')}]({sheet.get('url')})")
    lines.extend(["", "## TimeTree Events"])
    for event in case["timetree_events"]:
        lines.append(f"- {event}")
    lines.extend(["", "## Assets"])
    for asset in case["assets"]:
        lines.append(
            f"- Row {asset['asset_log_row']}: `{asset['seo_name']}` / {asset['photo_time']} / "
            f"[Drive]({asset['drive_url']}) / local `{asset['local_asset']}`"
        )
    lines.extend(["", "## Public Safety"])
    for item in case["public_safety"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _public_case_notes_md(case: Dict) -> str:
    lines = [
        f"# {case['public_name']}",
        "",
        f"- 建議頁面: {case['seo_category']}",
        f"- 分類: {case['audience']} / {case['scene']}",
        "",
        "## 可公開案例說明草稿",
        "",
    ]
    for note in case["public_notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## 建議圖片與 Alt Text"])
    for asset in case["assets"]:
        alt = asset.get("alt_text") or asset.get("keywords") or case["public_name"]
        lines.append(f"- <相片 {Path(asset['local_preview'] or asset['local_asset']).name}> {alt}")
    lines.extend(
        [
            "",
            "## 發文前提醒",
            "",
            "- 發文前需人工看圖確認畫面與本案例相符。",
            "- 不放價格、人數、私人地址、電話或本機路徑。",
        ]
    )
    return "\n".join(lines) + "\n"


def _root_index_md(payload: Dict) -> str:
    lines = [
        "# 2025 案例素材庫",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Source report: `{payload['source_report']}`",
        f"- Case root: `{payload['case_root']}`",
        "",
        "## 分類索引",
        "",
        "| 分類 | 場景 | 案例 | SEO 用途 | 照片數 | 資料夾 |",
        "|---|---|---|---|---:|---|",
    ]
    for case in payload["cases"]:
        lines.append(
            f"| {case['audience']} | {case['scene']} | {case['public_name']} | "
            f"{case['seo_category']} | {case['asset_count']} | `{case['folder']}` |"
        )
    lines.extend(
        [
            "",
            "## 使用規則",
            "",
            "- `internal_evidence.md` 是內部核對用，可含日期、報價單、Drive link。",
            "- `public_case_notes.md` 是公開稿可用方向，不得補入價格、人數、電話、私人地址或本機路徑。",
            "- 每篇 WordPress 發文前仍需人工視覺 QA，尤其是同日多場活動的資料夾。",
        ]
    )
    return "\n".join(lines) + "\n"


def _root_gallery_html(cases: List[Dict]) -> str:
    cards = []
    for case in cases:
        previews = []
        for asset in case["assets"][:5]:
            preview = asset.get("local_preview") or asset.get("local_asset")
            if preview:
                rel = Path(preview).relative_to(DESKTOP_CASE_ROOT)
                previews.append(
                    f'<figure><img src="{_html_escape(str(rel))}" alt="{_html_escape(asset.get("alt_text") or asset.get("seo_name") or "")}">'
                    f'<figcaption>{_html_escape(asset.get("seo_name") or asset.get("filename") or "")}</figcaption></figure>'
                )
        quote_links = []
        for sheet in case.get("quote_sheets", []):
            if sheet.get("url"):
                quote_links.append(
                    f'<a href="{_html_escape(sheet["url"])}">{_html_escape(sheet.get("name") or "quote sheet")}</a>'
                )
        drive_links = []
        for asset in case["assets"][:5]:
            drive_links.append(
                f'<a href="{_html_escape(asset.get("drive_url") or "")}">Row {asset.get("asset_log_row")}</a>'
            )
        safety = "待視覺確認" if "待" in case["folder"] or len(case["assets"]) < 3 else "可進下一步草稿"
        cards.append(
            f"""
            <section class="case-card">
              <div class="gallery">{''.join(previews) or '<p class="muted">No preview</p>'}</div>
              <div class="case-meta">
                <p class="eyebrow">{_html_escape(case['audience'])} / {_html_escape(case['scene'])}</p>
                <h2>{_html_escape(case['public_name'])}</h2>
                <table>
                  <tr><th>SEO 用途</th><td>{_html_escape(case['seo_category'])}</td></tr>
                  <tr><th>日期鍵</th><td>{_html_escape(case['date'])}</td></tr>
                  <tr><th>報價/事件線索</th><td>{_html_escape(case['sheet_hint'])}</td></tr>
                  <tr><th>信心分數</th><td>{case['confidence']}</td></tr>
                  <tr><th>狀態</th><td>{_html_escape(safety)}</td></tr>
                  <tr><th>Google Sheet</th><td>{'<br>'.join(quote_links) or 'none'}</td></tr>
                  <tr><th>Drive 圖片</th><td>{'<br>'.join(drive_links)}</td></tr>
                  <tr><th>本機資料夾</th><td><code>{_html_escape(case['folder'])}</code></td></tr>
                </table>
              </div>
            </section>
            """
        )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>2025 MAPLAB 案例素材庫</title>
  <style>
    :root {{
      --ink: #20201d;
      --muted: #706c64;
      --line: #ddd6c8;
      --paper: #faf7f0;
      --accent: #2f6d57;
      --surface: #fffdf8;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Noto Sans TC", sans-serif;
      color: var(--ink);
      background: var(--paper);
    }}
    header {{
      padding: 32px clamp(20px, 4vw, 54px) 20px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .lead {{ margin: 0; max-width: 820px; color: var(--muted); line-height: 1.7; }}
    main {{ padding: 24px clamp(16px, 4vw, 54px) 48px; }}
    .case-card {{
      display: grid;
      grid-template-columns: minmax(320px, 1.1fr) minmax(360px, 0.9fr);
      gap: 22px;
      margin: 0 0 28px;
      padding: 18px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .gallery {{
      display: grid;
      grid-template-columns: repeat(5, minmax(86px, 1fr));
      gap: 10px;
      align-content: start;
    }}
    figure {{ margin: 0; }}
    img {{
      display: block;
      width: 100%;
      aspect-ratio: 4 / 3;
      object-fit: cover;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #eee7da;
    }}
    figcaption {{
      margin-top: 5px;
      font-size: 11px;
      line-height: 1.35;
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .eyebrow {{
      margin: 0 0 4px;
      color: var(--accent);
      font-weight: 700;
      font-size: 13px;
    }}
    h2 {{ margin: 0 0 14px; font-size: 22px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{
      vertical-align: top;
      text-align: left;
      padding: 9px 8px;
      border-top: 1px solid var(--line);
      line-height: 1.55;
    }}
    th {{ width: 108px; color: var(--muted); font-weight: 600; }}
    a {{ color: var(--accent); }}
    code {{ font-size: 12px; overflow-wrap: anywhere; color: #5b4636; }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 980px) {{
      .case-card {{ grid-template-columns: 1fr; }}
      .gallery {{ grid-template-columns: repeat(3, minmax(86px, 1fr)); }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>2025 MAPLAB 案例素材庫</h1>
    <p class="lead">這份頁面只做內部整理：左側看素材預覽，右側看 SEO 場景、日期鍵、Google Sheet 與 Drive 證據。正式公開稿不可包含價格、人數、電話、私人地址或本機路徑。</p>
  </header>
  <main>
    {''.join(cards)}
  </main>
</body>
</html>
"""


def _html_escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _safe_slug(value: str) -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value.strip(), flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "asset"
