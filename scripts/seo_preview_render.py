#!/usr/bin/env python3
"""
seo_preview_render.py — 把 MD 草稿 render 成帶 MAPLAB 配色的 HTML 預覽。
寫入 state/seo_escalation_queue.jsonl（Visual Review 閘門，等 A0/Claude 人工過）。
HARD: 不 push、不發布、不碰 A6。
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Use bot venv's markdown if available, fallback to simple regex
try:
    import markdown as _md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

REPO = Path(__file__).parent.parent
PREVIEWS_DIR = REPO / "workbook" / "outputs" / "previews"
ESCALATION = REPO / "state" / "seo_escalation_queue.jsonl"

# MAPLAB 色彩系統 (maplab-visual-spec.md)
MAPLAB_CSS = """
:root {
  --cream:      #FAF7F2;
  --warm-beige: #EDE5D8;
  --olive:      #3A3A2E;
  --sage:       #8FA68E;
  --warm-brown: #8B5E3C;
  --text-main:  #3A3A2E;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Noto Sans TC", sans-serif;
  background: var(--cream);
  color: var(--text-main);
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 32px;
  line-height: 1.8;
  font-size: 16px;
}
h1 { font-size: 1.8em; color: var(--olive); border-bottom: 2px solid var(--sage); padding-bottom: 8px; }
h2 { font-size: 1.3em; color: var(--warm-brown); margin-top: 2em; }
h3 { font-size: 1.1em; color: var(--olive); }
a  { color: var(--warm-brown); text-decoration: underline; }
code, .img-alt-note { background: var(--warm-beige); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
blockquote { border-left: 4px solid var(--sage); margin-left: 0; padding-left: 16px; color: #666; }
table { border-collapse: collapse; width: 100%; margin: 1.2em 0; }
th { background: var(--warm-beige); padding: 8px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid var(--warm-beige); }
.cta-block { background: var(--warm-beige); border-left: 4px solid var(--sage); padding: 16px 20px; margin: 2em 0; border-radius: 6px; }
.checker-note { background: #f0f4ff; border: 1px dashed #99a; padding: 12px 16px; font-size: 0.88em; margin-top: 2em; }
"""

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — MAPLAB Preview</title>
<style>{css}</style>
</head>
<body>
{body}
<footer style="margin-top:3em;padding-top:1em;border-top:1px solid var(--warm-beige);font-size:0.8em;color:#888;">
MAPLAB Kitchen SEO Draft Preview — 生成時間: {ts} — 未發布
</footer>
</body>
</html>
"""


def simple_md_to_html(text: str) -> str:
    """Minimal Markdown → HTML without external deps."""
    html = text

    # HTML-escape first
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Code blocks ```
    html = re.sub(r"```[^\n]*\n(.*?)```", lambda m: f"<pre><code>{m.group(1)}</code></pre>", html, flags=re.DOTALL)

    # Comments <!-- ... --> → checker note
    html = re.sub(
        r"&lt;!--\s*CHECKER NOTE:(.*?)--&gt;",
        lambda m: f'<div class="checker-note"><strong>CHECKER NOTE</strong>{m.group(1)}</div>',
        html, flags=re.DOTALL
    )
    html = re.sub(r"&lt;!--(.*?)--&gt;", lambda m: f'<div class="img-alt-note">📷 {m.group(1).strip()}</div>', html, flags=re.DOTALL)

    # Headers
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # Bold/italic
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # Horizontal rule
    html = re.sub(r"^---+$", "<hr>", html, flags=re.MULTILINE)

    # LINE CTA block
    html = re.sub(
        r"(\*\*想了解 MAPLAB 如何協助您的活動？\*\*.*?\[INTERNAL_LINK_RECHECK_REQUIRED[^\]]*\])",
        lambda m: f'<div class="cta-block">{m.group(1)}</div>',
        html, flags=re.DOTALL
    )

    # Unordered lists
    def convert_ul(m):
        items = re.findall(r"^[\*\-\+]\s+(.+)$", m.group(0), re.MULTILINE)
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    html = re.sub(r"((?:^[\*\-\+]\s+.+\n?)+)", convert_ul, html, flags=re.MULTILINE)

    # Ordered lists
    def convert_ol(m):
        items = re.findall(r"^\d+\.\s+(.+)$", m.group(0), re.MULTILINE)
        return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"
    html = re.sub(r"((?:^\d+\.\s+.+\n?)+)", convert_ol, html, flags=re.MULTILINE)

    # Paragraphs (non-tag lines)
    lines = html.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
        elif stripped.startswith("<") or stripped.startswith("&"):
            result.append(stripped)
        else:
            result.append(f"<p>{stripped}</p>")
    html = "\n".join(result)

    return html


def render_draft(draft_path: str) -> dict:
    p = Path(draft_path)
    text = p.read_text(encoding="utf-8")

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1) if title_match else p.stem

    if HAS_MARKDOWN:
        body = _md_lib.markdown(text, extensions=["tables", "fenced_code"])
    else:
        body = simple_md_to_html(text)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    html = HTML_TEMPLATE.format(title=title, css=MAPLAB_CSS, body=body, ts=ts)

    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    out_name = p.stem + "-preview.html"
    out_path = PREVIEWS_DIR / out_name
    out_path.write_text(html, encoding="utf-8")

    return {
        "title": title,
        "draft_path": str(p),
        "preview_html": str(out_path),
        "preview_rel": f"workbook/outputs/previews/{out_name}",
    }


def write_escalation(gap_id: str, render_result: dict, review_path: str, qa_result: dict) -> str:
    """Write visual-review escalation entry. Returns entry id."""
    entry_id = hashlib.md5(f"{gap_id}_{render_result['preview_html']}".encode()).hexdigest()[:8]

    # Check for duplicate
    if ESCALATION.exists():
        for line in ESCALATION.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    if json.loads(line).get("id") == entry_id:
                        return entry_id  # Already written
                except Exception:
                    pass

    entry = {
        "id": entry_id,
        "routing_key": "seo_draft_visual_review",
        "gap_id": gap_id,
        "component": "seo_loop",
        "severity": "INFO",
        "status": "awaiting_visual_review",
        "description": f"{gap_id} 草稿已通過 QA，等待 A0/Claude 視覺驗證後方可發布",
        "owner_role": "A0_claude",
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "article_title": render_result["title"],
        "draft_path": render_result["draft_path"],
        "preview_html": render_result["preview_html"],
        "review_path": review_path,
        "qa_score": qa_result.get("score", 0),
        "qa_warnings": qa_result.get("warnings", []),
        "action_required": (
            "1. 開啟 preview_html 目視確認排版/配色/語氣\n"
            "2. 確認 6 盲點 FAQ 均覆蓋（詳 review_path）\n"
            "3. 確認無誤後更新此 entry status=approved，觸發發布流程"
        ),
        "publish_gate": "BLOCKED — 需 A0 視覺 + Owner approval 後才可執行發布",
    }

    ESCALATION.parent.mkdir(parents=True, exist_ok=True)
    with ESCALATION.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry_id


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: seo_preview_render.py <draft_path> <gap_id> [review_path] [qa_json]"}))
        sys.exit(1)

    draft_path = sys.argv[1]
    gap_id = sys.argv[2] if len(sys.argv) > 2 else "GAP-?"
    review_path = sys.argv[3] if len(sys.argv) > 3 else ""
    qa_result = {}
    if len(sys.argv) > 4:
        try:
            qa_result = json.loads(sys.argv[4])
        except Exception:
            pass

    render_result = render_draft(draft_path)
    entry_id = write_escalation(gap_id, render_result, review_path, qa_result)

    print(json.dumps({
        "status": "preview_ready",
        "preview_html": render_result["preview_html"],
        "escalation_id": entry_id,
        "escalation_path": str(ESCALATION),
        "message": "視覺閘門已啟動。請 A0/Claude 開啟 preview_html 確認後更新 escalation status=approved。",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
