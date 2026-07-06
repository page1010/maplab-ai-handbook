#!/usr/bin/env python3
"""
wp_publish_draft.py — 從 Notion vault 取 WP App Password，建 WP draft（不發布）。

Runtime 安全設計：
  1. NOTION_TOKEN 從 $NOTION_TOKEN env var 讀入，不存 repo、不印出、不進 log
  2. WP email + app_password 從 Notion 頁面取得，用完丟棄，不存 repo、不印出
  3. 只輸出：WP draft ID + preview URL（不含任何憑證）
  4. 如要略過 Notion 直接測（dev only）：export WP_USER=xxx WP_APP_PASSWORD='xxx'

用法：
  NOTION_TOKEN='secret_xxx' python3 scripts/wp_publish_draft.py <draft_md_path> <gap_id>

HARD: 不發布(status=draft only)、不改已存在文章、不印明文密碼。
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO = Path(__file__).parent.parent

NOTION_VAULT_PAGE_ID = "320ab0806d5c80e0be95f298399d2c44"
NOTION_API_BASE      = "https://api.notion.com/v1"
NOTION_VERSION       = "2022-06-28"

WP_BASE = "https://www.maplabkitchen.com/wp-json/wp/v2"


# ── Notion 取密 ────────────────────────────────────────────────────────────────

def notion_get(path: str, token: str) -> dict:
    url = f"{NOTION_API_BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def extract_text_from_block(block: dict) -> str:
    btype = block.get("type", "")
    rich = block.get(btype, {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich)


def fetch_wp_credentials_from_vault(token: str) -> tuple[str, str]:
    """
    讀 Notion vault 頁面，解析 WP Email + Application Password。
    只在 function 內存活，不傳出明文到上層 log。
    回傳 (wp_user, wp_app_password) 或 raise 若找不到。
    """
    # 取 page blocks
    data = notion_get(f"/blocks/{NOTION_VAULT_PAGE_ID}/children?page_size=50", token)
    blocks = data.get("results", [])

    wp_user = ""
    wp_pass = ""

    for block in blocks:
        text = extract_text_from_block(block).strip()
        if not text:
            continue

        # 嘗試多種格式：
        # "WordPress Email: xxx@xxx"
        # "WordPress Email：xxx@xxx"
        # "WP_USER=xxx@xxx"
        m = re.search(r"(?:WordPress\s+Email|WP[_\s]USER)\s*[=:：]\s*(\S+@\S+)", text, re.I)
        if m:
            wp_user = m.group(1).strip()

        # "Application Password: xxxx xxxx xxxx xxxx xxxx xxxx"
        # "WP_APP_PASSWORD=xxxx xxxx xxxx"
        m2 = re.search(
            r"(?:Application\s+Password|WP[_\s]APP[_\s]PASS(?:WORD)?)\s*[=:：]\s*(.{10,})",
            text, re.I
        )
        if m2:
            wp_pass = m2.group(1).strip().rstrip("。.,，")

        if wp_user and wp_pass:
            break

    if not wp_user or not wp_pass:
        # 嘗試 child page 或 table (如果頁面是 DB)
        raise RuntimeError(
            "Notion vault 頁面未找到 WP 憑證。\n"
            "請確認頁面格式：'WordPress Email: xxx' 和 'Application Password: xxxx xxxx' 在同一頁面 blocks 內。\n"
            f"Page ID: {NOTION_VAULT_PAGE_ID}"
        )

    return wp_user, wp_pass


# ── MD → HTML（簡化轉換，保留 MAPLAB 樣式）────────────────────────────────────

def md_to_wp_blocks(md_path: Path) -> str:
    """
    把 MD 草稿轉成 WP compatible HTML（去掉 CHECKER NOTE comment）。
    內鏈佔位符保留（上線前手動換）。
    """
    text = md_path.read_text(encoding="utf-8")
    # 移除 HTML comment (CHECKER NOTE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    lines = text.split("\n")
    html_parts = []
    in_table = False
    table_buf: list[str] = []

    def flush_table():
        nonlocal in_table
        if not table_buf:
            return
        rows = [r for r in table_buf if r.strip()]
        html_parts.append('<table><tbody>')
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            html_parts.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        html_parts.append('</tbody></table>')
        table_buf.clear()
        in_table = False

    for line in lines:
        stripped = line.strip()

        # Table
        if stripped.startswith("|"):
            if re.match(r"^\|[-| :]+\|$", stripped):
                continue  # separator row
            if not in_table:
                in_table = True
            table_buf.append(stripped)
            continue
        elif in_table:
            flush_table()

        if not stripped:
            html_parts.append("")
            continue

        # Headings
        if stripped.startswith("### "):
            html_parts.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_parts.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            # H1 → skip (WP page title handles it)
            pass
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_parts.append(f"<li>{stripped[2:]}</li>")
        elif stripped.startswith("---"):
            html_parts.append("<hr>")
        else:
            # Inline markdown
            p = stripped
            p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
            p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
            p = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", p)  # remove links (RECHECK)
            html_parts.append(f"<p>{p}</p>")

    if in_table:
        flush_table()

    # Wrap consecutive <li> in <ul>
    result = "\n".join(html_parts)
    result = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f"<ul>{m.group(0)}</ul>", result, flags=re.DOTALL)

    return result


# ── WP REST API ───────────────────────────────────────────────────────────────

def wp_create_draft(wp_user: str, wp_pass: str, title: str, content: str, slug: str) -> dict:
    """
    POST to WP REST API. status=draft only. 不發布。
    回傳 WP response dict（含 id, link, preview_url）。
    明文憑證僅在此 function 內，不印出。
    """
    cred = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
    auth_header = f"Basic {cred}"
    # 馬上清除明文（Python GC 不保證但盡力）
    del wp_pass

    payload = json.dumps({
        "title": title,
        "content": content,
        "slug": slug,
        "status": "draft",
        "comment_status": "closed",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{WP_BASE}/posts",
        data=payload,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WP REST HTTP {e.code}: {body[:300]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: wp_publish_draft.py <draft_md_path> <gap_id>", file=sys.stderr)
        sys.exit(1)

    draft_path = Path(sys.argv[1])
    gap_id     = sys.argv[2]

    if not draft_path.exists():
        print(f"ERROR: draft not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    # ── 取憑證（runtime，不進 log）────────────────────────────────────────────
    wp_user = os.environ.get("WP_USER", "")
    wp_pass = os.environ.get("WP_APP_PASSWORD", "")

    if wp_user and wp_pass:
        # Dev override: env vars 直接提供
        print(f"[wp_publish] Using WP_USER env var (dev mode)", file=sys.stderr)
    else:
        notion_token = os.environ.get("NOTION_TOKEN", "")
        if not notion_token:
            print(
                "ERROR: 需要 NOTION_TOKEN env var（或 WP_USER + WP_APP_PASSWORD）\n"
                "  export NOTION_TOKEN='secret_xxx'\n"
                "  python3 scripts/wp_publish_draft.py <draft> <gap_id>",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"[wp_publish] Fetching WP credentials from Notion vault...", file=sys.stderr)
        try:
            wp_user, wp_pass = fetch_wp_credentials_from_vault(notion_token)
            print(f"[wp_publish] Vault: credentials found for {wp_user[:3]}***", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Vault fetch failed: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            del notion_token  # 清除 token

    # ── 讀草稿，取 title ───────────────────────────────────────────────────────
    md_text = draft_path.read_text(encoding="utf-8")
    h1_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    title = h1_match.group(1) if h1_match else draft_path.stem
    slug  = draft_path.stem  # e.g. hr-admin-meeting-catering-guide-tainan

    content_html = md_to_wp_blocks(draft_path)

    # ── 建 WP draft ────────────────────────────────────────────────────────────
    print(f"[wp_publish] Creating WP draft: slug={slug}", file=sys.stderr)
    try:
        result = wp_create_draft(wp_user, wp_pass, title, content_html, slug)
    except Exception as e:
        print(f"ERROR: WP draft creation failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        wp_user = "***"  # clear
        wp_pass = "***"

    draft_id   = result.get("id", "?")
    draft_link = result.get("link", "")
    # WP draft preview URL
    preview_url = f"https://www.maplabkitchen.com/?p={draft_id}&preview=true"

    output = {
        "status": "draft_created",
        "gap_id": gap_id,
        "wp_post_id": draft_id,
        "wp_draft_link": draft_link,
        "preview_url": preview_url,
        "slug": slug,
        "title": title,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n[wp_publish] Done. Preview URL: {preview_url}", file=sys.stderr)


if __name__ == "__main__":
    main()
