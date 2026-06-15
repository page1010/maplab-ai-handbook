#!/usr/bin/env python3
"""Attach selected ICC Tainan images to the already-published landing page.

The WordPress image optimizer may keep media upload responses open while it
creates AVIF/WebP derivatives. This script treats slug search as the source of
truth after each upload attempt, then patches media alt/caption metadata.
"""

from __future__ import annotations

import base64
import csv
import json
import mimetypes
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
JOB_DIR = ROOT / "workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN"
ASSET_DIR = JOB_DIR / "wordpress_assets_icctn_001"
MANIFEST = ASSET_DIR / "asset_conversion_manifest_icctn_001.csv"
POST_ID = 1829
SITE = "https://www.maplabkitchen.com"
API = f"{SITE}/wp-json"
CASE_CATEGORY_ID = 170
TITLE = "大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB"
SLUG = "icc-tainan-catering"
EXCERPT = (
    "大臺南會展中心外燴與企業茶點案例。MAPLAB Kitchen 提供台南會展活動餐點、"
    "手指食物、飲品與貴賓接待餐桌配置，適合會議、展覽、開幕與品牌活動。"
)
RANK_MATH_META = {
    "rank_math_focus_keyword": "大臺南會展中心外燴, 大臺南會展中心茶點, 大臺南會展中心活動餐點, ICC Tainan catering",
    "rank_math_title": TITLE,
    "rank_math_description": EXCERPT,
}

SELECTED_IMAGES = [
    "maplab-icc-tainan-catering-table-overview-01.webp",
    "maplab-icc-tainan-catering-table-overview-02.webp",
    "maplab-icc-tainan-corporate-tea-table-03.webp",
    "maplab-icc-tainan-finger-food-dessert-display-04.webp",
    "maplab-icc-tainan-dessert-catering-detail-05.webp",
]


class WPError(RuntimeError):
    pass


def auth_header() -> str:
    user = os.environ.get("WP_USER", "").strip()
    app_password = os.environ.get("WP_APP_PASS", "").strip()
    if not user or not app_password:
        raise WPError("WP_USER and WP_APP_PASS are required")
    token = base64.b64encode(f"{user}:{app_password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


AUTH = auth_header()


def request_json(method: str, path: str, payload: dict | None = None, timeout: int = 60) -> dict | list:
    body = None
    headers = {
        "Authorization": AUTH,
        "Accept": "application/json",
        "User-Agent": "MAPLAB-A2-Image-Attach/1.0",
    }
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(f"{API}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8")) if data else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise WPError(f"{method} {path} failed: HTTP {exc.code}: {detail[:700]}") from exc


def upload_binary(path: Path, timeout: int = 20) -> dict | None:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    headers = {
        "Authorization": AUTH,
        "Accept": "application/json",
        "User-Agent": "MAPLAB-A2-Image-Attach/1.0",
        "Content-Type": content_type,
        "Content-Disposition": f"attachment; filename={path.name}",
    }
    req = urllib.request.Request(f"{API}/wp/v2/media", data=path.read_bytes(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8")) if data else None
    except (TimeoutError, socket.timeout):
        return None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 500 and "already exists" in detail.lower():
            return None
        raise WPError(f"media upload failed for {path.name}: HTTP {exc.code}: {detail[:700]}") from exc


def slug(filename: str) -> str:
    return Path(filename).stem.lower()


def load_manifest() -> dict[str, dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return {row["output_file"]: row for row in csv.DictReader(f)}


def find_media(filename: str) -> dict | None:
    target = slug(filename)
    query = urllib.parse.urlencode(
        {
            "search": target,
            "per_page": 100,
            "_fields": "id,slug,title,source_url,alt_text,caption,media_details",
        }
    )
    results = request_json("GET", f"/wp/v2/media?{query}", timeout=30)
    if not isinstance(results, list):
        return None
    for item in results:
        if item.get("slug") == target:
            return item
    return None


def wait_for_media(filename: str, seconds: int = 45) -> dict | None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        media = find_media(filename)
        if media:
            return media
        time.sleep(3)
    return None


def media_payload(row: dict[str, str]) -> dict:
    return {
        "title": Path(row["output_file"]).stem.replace("-", " "),
        "alt_text": row["alt_text"],
        "caption": row["caption"],
        "description": f"{row['caption']}。來源檔：{row['source_file']}；用途：{row['usage_note']}。",
    }


def ensure_media(row: dict[str, str]) -> tuple[dict, str]:
    output = row["output_file"]
    path = ASSET_DIR / output
    existing = find_media(output)
    if existing:
        media = existing
        action = "reused"
    else:
        created = upload_binary(path)
        media = created or wait_for_media(output)
        if not media:
            raise WPError(f"upload did not produce searchable media for {output}")
        action = "uploaded"
    updated = request_json("POST", f"/wp/v2/media/{media['id']}", media_payload(row), timeout=45)
    if isinstance(updated, dict):
        media = updated
    return media, action


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def p(text: str) -> str:
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def h2(text: str, anchor: str) -> str:
    return f'<!-- wp:heading {{"anchor":"{anchor}"}} -->\n<h2 class="wp-block-heading" id="{anchor}">{text}</h2>\n<!-- /wp:heading -->'


def ul(items: list[str]) -> str:
    body = "\n".join(f"<!-- wp:list-item -->\n<li>{item}</li>\n<!-- /wp:list-item -->" for item in items)
    return f'<!-- wp:list -->\n<ul class="wp-block-list">\n{body}\n</ul>\n<!-- /wp:list -->'


def button(label: str, href: str) -> str:
    return (
        '<!-- wp:button {"className":"is-style-outline"} -->\n'
        f'<div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="{href}">{label}</a></div>\n'
        "<!-- /wp:button -->"
    )


def quick_nav() -> str:
    buttons = "\n".join(
        [
            button("案例照片", "#case"),
            button("適合場景", "#event-types"),
            button("配置重點", "#setup"),
            button("進場檢查", "#logistics"),
            button("常見問題", "#faq"),
            button("LINE 詢問", "https://lin.ee/IP8nt4n"),
        ]
    )
    return '<!-- wp:buttons {"className":"maplab-quick-nav"} -->\n<div class="wp-block-buttons maplab-quick-nav">\n' + buttons + "\n</div>\n<!-- /wp:buttons -->"


def image_block(media: dict, row: dict[str, str]) -> str:
    src = media["source_url"]
    media_id = media["id"]
    alt = esc(row["alt_text"])
    caption = esc(row["caption"])
    return (
        f'<!-- wp:image {{"id":{media_id},"sizeSlug":"large","linkDestination":"none"}} -->\n'
        f'<figure class="wp-block-image size-large"><img src="{src}" alt="{alt}" class="wp-image-{media_id}"/>'
        f"<figcaption>{caption}</figcaption></figure>\n"
        "<!-- /wp:image -->"
    )


def faq_block() -> str:
    questions = [
        ("faq-icctn-catering", "大臺南會展中心活動可以安排外燴茶點嗎？", "可以先依活動日期、場地位置、進場時間、人數與用餐時段討論，再判斷適合會議茶點、展覽接待餐點或貴賓區點心吧。"),
        ("faq-icctn-meeting-refreshment", "會議茶點和展覽接待餐點怎麼配置？", "會議茶點通常重視拿取順手與補給穩定；展覽接待會更在意桌面呈現、來賓停留與交流節奏。MAPLAB 會依活動流程調整餐點大小、飲品與桌面配置。"),
        ("faq-icctn-vip", "如果有貴賓、講師或合作單位到場，餐點要怎麼安排？", "可先把貴賓抵達時間、致詞或交流時段標出來，再安排好拿取的小份量餐點、飲品補給與桌面位置，讓接待節奏比較清楚。"),
        ("faq-icctn-advance", "大臺南會展中心活動茶點需要提前多久確認？", "企業活動建議在活動前 2 至 4 週先確認方向。若活動規模較大、需要特殊動線或分區接待，建議更早提供資訊。"),
        ("faq-icctn-info", "詢問時需要提供哪些資訊？", "建議提供活動日期、預估人數、會議室或展區位置、進場與撤場時間、是否需要飲品桌或貴賓桌，以及現場桌椅、電源與垃圾處理方式。"),
    ]
    attrs = json.dumps({"questions": [{"id": qid, "title": q, "content": a, "visible": True} for qid, q, a in questions]}, ensure_ascii=False)
    items = "\n".join(
        f'<div class="rank-math-faq-item"><h3 class="rank-math-question">{esc(q)}</h3><div class="rank-math-answer"><p>{esc(a)}</p></div></div>'
        for _, q, a in questions
    )
    return f"<!-- wp:rank-math/faq-block {attrs} -->\n<div class=\"wp-block-rank-math-faq-block\">{items}</div>\n<!-- /wp:rank-math/faq-block -->"


def build_content(media: dict[str, dict], rows: dict[str, dict[str, str]]) -> str:
    img = lambda name: image_block(media[name], rows[name])
    parts = [
        p("大臺南會展中心外燴與企業茶點，會同時牽涉餐點數量、取餐動線、桌面畫面與來賓交流節奏。MAPLAB Kitchen 依會議、展覽、開幕與貴賓接待情境，整理台南會展活動餐點、手指食物、甜點飲品與餐桌配置。"),
        p("如果活動地點在 ICC Tainan 或高鐵台南站周邊，可以先提供日期、人數、場地區域與用餐時段，讓我們協助判斷茶點桌、飲品區與補餐節奏。"),
        quick_nav(),
        img("maplab-icc-tainan-catering-table-overview-01.webp"),
        h2("大臺南會展中心企業會議茶點案例", "case"),
        p("這場大臺南會展中心企業會議茶點，以中場休息與會後交流為主要情境。餐桌安排在來賓容易停留的位置，手指食物、甜點與飲品分區陳列，方便短時間取用，也讓主辦方在接待講師、合作單位與來賓時有清楚的節奏。"),
        img("maplab-icc-tainan-catering-table-overview-02.webp"),
        p("會展中心場域通常有明確的議程與人流，餐點桌需要乾淨、好辨識、補給穩定。桌面層次與器皿配置會影響現場照片，也會影響來賓靠近餐桌時的取餐速度。"),
        h2("哪些大臺南會展中心活動適合茶點外燴", "event-types"),
        ul([
            "企業工作會議、跨部門會議與研討會 Coffee Break",
            "展覽接待、招商說明會、產品發表與品牌活動",
            "開幕茶會、貴賓接待、講師休息區與合作單位交流",
            "高鐵台南站周邊企業活動、南科來賓接待與商務會議",
            "需要照片畫面、接待體面與取餐效率兼顧的活動餐點",
        ]),
        img("maplab-icc-tainan-corporate-tea-table-03.webp"),
        h2("茶點桌配置與取餐節奏", "setup"),
        p("企業會議茶點通常會從活動流程反推餐點形式。短暫休息時間適合手指食物與小份量甜點；展覽或品牌接待則會更重視桌面完整度、飲品補給與來賓停留位置。"),
        ul([
            "手指食物與小份量鹹點：適合短時間拿取與站立交流",
            "甜點與茶點：適合會議休息、展覽接待與品牌活動照片",
            "紅茶、麥茶、咖啡或冷飲：依活動時段與場地條件調整",
            "主桌、貴賓區與一般來賓動線：依現場桌椅與入口位置分流",
            "補餐與撤場節奏：配合議程、休息時間與會展中心進退場規定",
        ]),
        img("maplab-icc-tainan-finger-food-dessert-display-04.webp"),
        img("maplab-icc-tainan-dessert-catering-detail-05.webp"),
        h2("會展中心進場與現場規劃重點", "logistics"),
        p("在大臺南會展中心規劃活動外燴時，建議在詢問階段先整理進場、撤場、會議室位置與活動流程。這些資訊會影響餐桌位置、飲品補給、餐具數量與現場人力安排。"),
        ul([
            "活動日期、進場時間、撤場時間與實際用餐時段",
            "預估人數、貴賓人數、講師或合作單位接待需求",
            "樓層、會議室、展區位置與裝卸動線",
            "現場是否已有桌椅、電源、垃圾處理與備餐空間",
            "是否需要飲品桌、貴賓桌、分區補餐或會後交流餐點",
        ]),
        h2("延伸閱讀", "related"),
        ul([
            '<a href="https://www.maplabkitchen.com/corporate-tea-party-desserts/">台南會議茶點與企業茶會規劃</a>',
            '<a href="https://www.maplabkitchen.com/vip-expo-catering-business-meeting/">展覽接待與商務貴賓外燴</a>',
            '<a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">台南開幕茶會與品牌活動餐點</a>',
            '<a href="https://www.maplabkitchen.com/corporate-catering-tainan/">台南企業外燴服務總覽</a>',
        ]),
        h2("常見問題", "faq"),
        faq_block(),
        p('<a href="https://lin.ee/IP8nt4n">用 LINE 詢問大臺南會展中心活動茶點規劃</a>'),
    ]
    return "\n\n".join(parts)


def main() -> int:
    rows = load_manifest()
    media_by_file: dict[str, dict] = {}
    upload_rows = []
    for filename in SELECTED_IMAGES:
        media, action = ensure_media(rows[filename])
        media_by_file[filename] = media
        upload_rows.append({
            "output_file": filename,
            "media_id": media["id"],
            "source_url": media["source_url"],
            "action": action,
            "alt_text": rows[filename]["alt_text"],
            "caption": rows[filename]["caption"],
        })
        time.sleep(0.2)

    content = build_content(media_by_file, rows)
    content_file = JOB_DIR / "wordpress_draft_content_with_images.md"
    content_file.write_text(
        "# WordPress Content With Images — A2-SEO-ICCTN-001\n\n"
        f"Post ID: `{POST_ID}`\n"
        "Status: published_content_updated_with_selected_images\n\n"
        "## HTML Payload\n\n```html\n"
        + content
        + "\n```\n",
        encoding="utf-8",
    )
    featured = media_by_file["maplab-icc-tainan-catering-table-overview-01.webp"]["id"]
    post = request_json(
        "POST",
        f"/wp/v2/posts/{POST_ID}",
        {
            "title": TITLE,
            "slug": "icc-tainan-catering",
            "status": "publish",
            "content": content,
            "excerpt": EXCERPT,
            "categories": [CASE_CATEGORY_ID],
            "featured_media": featured,
        },
        timeout=60,
    )
    rm_error = None
    try:
        request_json("POST", "/rankmath/v1/updateMeta", {"objectID": POST_ID, "objectType": "post", "meta": RANK_MATH_META}, timeout=45)
    except Exception as exc:
        rm_error = str(exc)

    with (ASSET_DIR / "wp_selected_media_manifest_icctn_001.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["output_file", "media_id", "source_url", "action", "alt_text", "caption"])
        writer.writeheader()
        writer.writerows(upload_rows)
    result = {
        "post_id": POST_ID,
        "status": post.get("status"),
        "slug": post.get("slug"),
        "link": post.get("link"),
        "categories": post.get("categories"),
        "featured_media": post.get("featured_media"),
        "selected_media_count": len(upload_rows),
        "media_ids": [row["media_id"] for row in upload_rows],
        "rank_math_error": rm_error,
    }
    (JOB_DIR / "wordpress_image_attach_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
