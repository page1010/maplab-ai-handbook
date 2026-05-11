import html
import json
from pathlib import Path
from typing import Any, Dict

from .paths import ROOT, WORKBOOK_DIR
from .photo_pipeline import MAPLAB_ASSETS_FOLDER_ID


def build_dashboard() -> Path:
    data = {
        "task_index": _load_json(WORKBOOK_DIR / "task_index.json"),
        "relation_graph": _load_json(WORKBOOK_DIR / "relation_graph.json"),
        "inferred_needs": _load_json(WORKBOOK_DIR / "inferred_needs.json"),
        "asset_log": _load_json(_latest_asset_snapshot()),
    }
    out = WORKBOOK_DIR / "dashboard.html"
    out.write_text(_render(data), encoding="utf-8")
    return out


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"missing": str(path.relative_to(ROOT))}
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_asset_snapshot() -> Path:
    matches = sorted(
        (WORKBOOK_DIR / "outputs").glob("*/T-A4-photo-classification-restart/asset_log_snapshot.json"),
        reverse=True,
    )
    if matches:
        return matches[0]
    return WORKBOOK_DIR / "outputs" / "missing" / "asset_log_snapshot.json"


def _render(data: Dict[str, Any]) -> str:
    tasks = data["task_index"].get("tasks", [])
    asset = data["asset_log"]
    source = dict(asset.get("source", {}))
    source["maplab_assets_folder_id"] = MAPLAB_ASSETS_FOLDER_ID
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MAPLAB AI Workbook</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172026; background: #f7f7f4; }}
    header {{ padding: 24px 28px 14px; background: #ffffff; border-bottom: 1px solid #d8d8d2; }}
    h1 {{ margin: 0 0 6px; font-size: 28px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    main {{ padding: 20px 28px 36px; display: grid; gap: 18px; }}
    section {{ background: #fff; border: 1px solid #d8d8d2; border-radius: 8px; padding: 16px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .metric {{ background: #f2f6f3; border: 1px solid #dce5dd; border-radius: 8px; padding: 12px; }}
    .metric strong {{ display: block; font-size: 24px; }}
    .muted {{ color: #687176; font-size: 13px; }}
    a {{ color: #1f5e56; text-decoration: none; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #ecece6; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #fafaf7; }}
    code {{ background: #f2f2ee; padding: 2px 5px; border-radius: 4px; }}
    .pill {{ display: inline-block; padding: 2px 7px; border-radius: 999px; background: #e9efe9; margin-right: 4px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  </style>
</head>
<body>
  <header>
    <h1>MAPLAB AI Workbook</h1>
    <div class="muted">任務閉環工作台：GitHub 真相源、A4 素材表、context pack、microtask、relation graph</div>
  </header>
  <main>
    <section>
      <h2>A4 Photo Assets</h2>
      <div class="grid">
        <div class="metric"><strong>{asset.get("total_rows", "n/a")}</strong><span class="muted">ASSET_LOG rows</span></div>
        <div class="metric"><strong>{_count(asset, "外燴")}</strong><span class="muted">外燴</span></div>
        <div class="metric"><strong>{_count(asset, "旅遊")}</strong><span class="muted">旅遊</span></div>
        <div class="metric"><strong>{_count(asset, "日常")}</strong><span class="muted">日常</span></div>
      </div>
      <p class="muted">
        Source: <a href="{html.escape(source.get("url", ""))}" target="_blank">MAPLAB_ASSET_LOG</a>
        · Sheet tab: <code>{html.escape(source.get("sheet_name", ""))}</code>
        · MAPLAB_ASSETS folder: <code>{html.escape(source.get("maplab_assets_folder_id", ""))}</code>
      </p>
      {_sample_rows(asset)}
    </section>
    <section>
      <h2>Workbook Outputs</h2>
      <p>
        <a href="./task_index.json">task_index.json</a> ·
        <a href="./relation_graph.json">relation_graph.json</a> ·
        <a href="./inferred_needs.json">inferred_needs.json</a> ·
        <a href="./context_packs/T-A6-001.md">T-A6-001 context pack</a> ·
        <a href="./microtasks/MT-T-A6-001-001.md">T-A6-001 microtask</a>
      </p>
    </section>
    <section>
      <h2>Task Index</h2>
      {_task_table(tasks)}
    </section>
  </main>
</body>
</html>
"""


def _count(asset: Dict[str, Any], key: str) -> Any:
    return asset.get("category_counts", {}).get(key, 0)


def _sample_rows(asset: Dict[str, Any]) -> str:
    rows = asset.get("sample_rows", [])[:8]
    if not rows:
        return "<p class=\"muted\">No sample rows yet.</p>"
    body = []
    for r in rows:
        body.append(
            "<tr>"
            f"<td>{html.escape(r.get('year', ''))}</td>"
            f"<td>{html.escape(r.get('category', ''))}</td>"
            f"<td>{html.escape(r.get('filename', ''))}</td>"
            f"<td>{html.escape(r.get('seo_name', ''))}</td>"
            f"<td><a href=\"{html.escape(r.get('drive_url', ''))}\" target=\"_blank\">Drive</a></td>"
            "</tr>"
        )
    return "<table><thead><tr><th>year</th><th>category</th><th>filename</th><th>seo_name</th><th>file</th></tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def _task_table(tasks: list) -> str:
    body = []
    for t in tasks[:30]:
        body.append(
            "<tr>"
            f"<td><code>{html.escape(t.get('task_id', ''))}</code></td>"
            f"<td>{html.escape(t.get('owner_agent', ''))}</td>"
            f"<td>{html.escape(t.get('status', ''))}</td>"
            f"<td>{html.escape(t.get('current_step', ''))}</td>"
            "</tr>"
        )
    return "<table><thead><tr><th>task</th><th>owner</th><th>status</th><th>current step</th></tr></thead><tbody>" + "".join(body) + "</tbody></table>"
