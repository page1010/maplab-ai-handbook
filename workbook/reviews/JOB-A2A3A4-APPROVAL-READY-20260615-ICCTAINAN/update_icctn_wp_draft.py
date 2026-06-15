#!/usr/bin/env python3
"""Update the approved ICC Tainan WordPress draft without publishing it.

Secrets are supplied at runtime through environment variables. Do not write
credentials, auth headers, cookies, or nonces to repo files or logs.
"""

from __future__ import annotations

import base64
import csv
import json
import mimetypes
import os
import re
import sys
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
POST_TYPE = "post"
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
    "maplab-icc-tainan-wide-refreshment-table-12.webp",
    "maplab-icc-tainan-catering-table-overview-01.webp",
    "maplab-icc-tainan-corporate-tea-table-03.webp",
    "maplab-icc-tainan-finger-food-dessert-display-04.webp",
    "maplab-icc-tainan-dessert-catering-detail-05.webp",
    "maplab-icc-tainan-dessert-and-drink-service-13.webp",
]


class WPError(RuntimeError):
    pass


def auth_header() -> str:
    user = os.environ.get("WP_USER", "").strip()
    app_password = os.environ.get("WP_APP_PASS", "").strip()
    if not user or not app_password:
        raise WPError("WP_USER and WP_APP_PASS are required in environment")
    token = base64.b64encode(f"{user}:{app_password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


AUTH = auth_header()


def request_json(method: str, path: str, payload: dict | None = None, headers: dict | None = None) -> dict | list:
    body = None
    request_headers = {
        "Authorization": AUTH,
        "Accept": "application/json",
        "User-Agent": "MAPLAB-A2-Draft-Updater/1.0",
    }
    if headers:
        request_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(f"{API}{path}", data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            if not data:
                return {}
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise WPError(f"{method} {path} failed: HTTP {exc.code}: {detail[:700]}") from exc


def upload_binary(path: Path, title: str) -> dict:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    headers = {
        "Authorization": AUTH,
        "Accept": "application/json",
        "User-Agent": "MAPLAB-A2-Draft-Updater/1.0",
        "Content-Type": content_type,
        "Content-Disposition": f"attachment; filename={path.name}",
    }
    req = urllib.request.Request(
        f"{API}/wp/v2/media",
        data=path.read_bytes(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise WPError(f"media upload failed for {path.name}: HTTP {exc.code}: {detail[:700]}") from exc


def slugify_filename(filename: str) -> str:
    return Path(filename).stem.lower()


def load_manifest() -> dict[str, dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return {row["output_file"]: row for row in csv.DictReader(f)}


def find_media_by_slug(slug: str) -> dict | None:
    query = urllib.parse.urlencode(
        {
            "search": slug,
            "per_page": 100,
            "_fields": "id,slug,title,source_url,alt_text,caption,media_details",
        }
    )
    results = request_json("GET", f"/wp/v2/media?{query}")
    if not isinstance(results, list):
        return None
    for item in results:
        if item.get("slug") == slug:
            return item
    return None


def media_meta_payload(row: dict[str, str]) -> dict:
    output = row["output_file"]
    title = Path(output).stem.replace("-", " ")
    return {
        "title": title,
        "alt_text": row["alt_text"],
        "caption": row["caption"],
        "description": f"{row['caption']}。來源檔：{row['source_file']}；用途：{row['usage_note']}。",
    }


def ensure_media(row: dict[str, str]) -> dict:
    output = row["output_file"]
    path = ASSET_DIR / output
    if not path.exists():
        raise WPError(f"missing asset: {path}")

    slug = slugify_filename(output)
    existing = find_media_by_slug(slug)
    if existing:
        updated = request_json("POST", f"/wp/v2/media/{existing['id']}", media_meta_payload(row))
        updated["_maplab_upload_action"] = "reused"
        return updated

    created = upload_binary(path, media_meta_payload(row)["title"])
    updated = request_json("POST", f"/wp/v2/media/{created['id']}", media_meta_payload(row))
    updated["_maplab_upload_action"] = "uploaded"
    return updated


def image_block(media: dict, row: dict[str, str], size_slug: str = "large") -> str:
    media_id = media["id"]
    src = media["source_url"]
    alt = html(row["alt_text"])
    caption = html(row["caption"])
    return (
        f'<!-- wp:image {{"id":{media_id},"sizeSlug":"{size_slug}","linkDestination":"none"}} -->\n'
        f'<figure class="wp-block-image size-{size_slug}"><img src="{src}" alt="{alt}" class="wp-image-{media_id}"/>'
        f"<figcaption>{caption}</figcaption></figure>\n"
        "<!-- /wp:image -->"
    )


def html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def paragraph(text: str) -> str:
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def heading(text: str, anchor: str, level: int = 2) -> str:
    return (
        f'<!-- wp:heading {{"level":{level},"anchor":"{anchor}"}} -->\n'
        f'<h{level} class="wp-block-heading" id="{anchor}">{text}</h{level}>\n'
        f"<!-- /wp:heading -->"
    )


def bullet_list(items: list[str]) -> str:
    body = "\n".join([f"<!-- wp:list-item -->\n<li>{item}</li>\n<!-- /wp:list-item -->" for item in items])
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
    return (
        '<!-- wp:buttons {"className":"maplab-quick-nav"} -->\n'
        f'<div class="wp-block-buttons maplab-quick-nav">\n{buttons}\n</div>\n'
        "<!-- /wp:buttons -->"
    )


def faq_block() -> str:
    questions = [
        {
            "id": "faq-icctn-catering",
            "title": "大臺南會展中心活動可以安排外燴茶點嗎？",
            "content": "可以先依活動日期、場地位置、進場時間、人數與用餐時段討論，再判斷適合會議茶點、展覽接待餐點或貴賓區點心吧。",
        },
        {
            "id": "faq-icctn-meeting-refreshment",
            "title": "會議茶點和展覽接待餐點怎麼配置？",
            "content": "會議茶點通常重視拿取順手與補給穩定；展覽接待會更在意桌面呈現、來賓停留與交流節奏。MAPLAB 會依活動流程調整餐點大小、飲品與桌面配置。",
        },
        {
            "id": "faq-icctn-vip",
            "title": "如果有貴賓、講師或合作單位到場，餐點要怎麼安排？",
            "content": "可先把貴賓抵達時間、致詞或交流時段標出來，再安排好拿取的小份量餐點、飲品補給與桌面位置，讓接待節奏比較清楚。",
        },
        {
            "id": "faq-icctn-advance",
            "title": "大臺南會展中心活動茶點需要提前多久確認？",
            "content": "企業活動建議在活動前 2 至 4 週先確認方向。若活動規模較大、需要特殊動線或分區接待，建議更早提供資訊。",
        },
        {
            "id": "faq-icctn-keywords",
            "title": "詢問時需要提供哪些資訊？",
            "content": "建議提供活動日期、預估人數、會議室或展區位置、進場與撤場時間、是否需要飲品桌或貴賓桌，以及現場桌椅、電源與垃圾處理方式。",
        },
    ]
    attr = json.dumps({"questions": [{"id": q["id"], "title": q["title"], "content": q["content"], "visible": True} for q in questions]}, ensure_ascii=False)
    items = "\n".join(
        [
            f'<div class="rank-math-faq-item"><h3 class="rank-math-question">{html(q["title"])}</h3>'
            f'<div class="rank-math-answer"><p>{html(q["content"])}</p></div></div>'
            for q in questions
        ]
    )
    return (
        f"<!-- wp:rank-math/faq-block {attr} -->\n"
        f'<div class="wp-block-rank-math-faq-block">{items}</div>\n'
        "<!-- /wp:rank-math/faq-block -->"
    )


def build_content(media_by_file: dict[str, dict], manifest_rows: dict[str, dict[str, str]]) -> str:
    img = lambda name: image_block(media_by_file[name], manifest_rows[name])
    parts = [
        paragraph(
            "大臺南會展中心外燴與企業茶點，重點通常不只在餐點數量，也在取餐動線、桌面畫面與來賓交流節奏。"
            "MAPLAB Kitchen 依會議、展覽、開幕與貴賓接待情境，整理台南會展活動餐點、手指食物、甜點飲品與餐桌配置。"
        ),
        paragraph(
            "如果活動地點在 ICC Tainan 或高鐵台南站周邊，可以先提供日期、人數、場地區域與用餐時段，讓我們協助判斷茶點桌、飲品區與補餐節奏。"
        ),
        quick_nav(),
        img("maplab-icc-tainan-wide-refreshment-table-12.webp"),
        heading("大臺南會展中心企業會議茶點案例", "case"),
        paragraph(
            "這場大臺南會展中心企業會議茶點，以中場休息與會後交流為主要情境。餐桌安排在來賓容易停留的位置，手指食物、甜點與飲品分區陳列，方便短時間取用，也讓主辦方在接待講師、合作單位與來賓時有清楚的節奏。"
        ),
        paragraph(
            "會展中心場域通常有明確的議程與人流，餐點桌需要乾淨、好辨識、補給穩定。桌面層次與器皿配置會影響現場照片，也會影響來賓靠近餐桌時的取餐速度。"
        ),
        img("maplab-icc-tainan-catering-table-overview-01.webp"),
        img("maplab-icc-tainan-corporate-tea-table-03.webp"),
        heading("哪些大臺南會展中心活動適合茶點外燴", "event-types"),
        bullet_list(
            [
                "企業工作會議、跨部門會議與研討會 Coffee Break",
                "展覽接待、招商說明會、產品發表與品牌活動",
                "開幕茶會、貴賓接待、講師休息區與合作單位交流",
                "高鐵台南站周邊企業活動、南科來賓接待與商務會議",
                "需要照片畫面、接待體面與取餐效率兼顧的活動餐點",
            ]
        ),
        img("maplab-icc-tainan-finger-food-dessert-display-04.webp"),
        heading("茶點桌配置與取餐節奏", "setup"),
        paragraph(
            "企業會議茶點通常會從活動流程反推餐點形式。短暫休息時間適合手指食物與小份量甜點；展覽或品牌接待則會更重視桌面完整度、飲品補給與來賓停留位置。"
        ),
        bullet_list(
            [
                "手指食物與小份量鹹點：適合短時間拿取與站立交流",
                "甜點與茶點：適合會議休息、展覽接待與品牌活動照片",
                "紅茶、麥茶、咖啡或冷飲：依活動時段與場地條件調整",
                "主桌、貴賓區與一般來賓動線：依現場桌椅與入口位置分流",
                "補餐與撤場節奏：配合議程、休息時間與會展中心進退場規定",
            ]
        ),
        img("maplab-icc-tainan-dessert-catering-detail-05.webp"),
        img("maplab-icc-tainan-dessert-and-drink-service-13.webp"),
        heading("會展中心進場與現場規劃重點", "logistics"),
        paragraph(
            "在大臺南會展中心規劃活動外燴時，建議在詢問階段先整理進場、撤場、會議室位置與活動流程。這些資訊會影響餐桌位置、飲品補給、餐具數量與現場人力安排。"
        ),
        bullet_list(
            [
                "活動日期、進場時間、撤場時間與實際用餐時段",
                "預估人數、貴賓人數、講師或合作單位接待需求",
                "樓層、會議室、展區位置與裝卸動線",
                "現場是否已有桌椅、電源、垃圾處理與備餐空間",
                "是否需要飲品桌、貴賓桌、分區補餐或會後交流餐點",
            ]
        ),
        heading("延伸閱讀", "related"),
        bullet_list(
            [
                '<a href="https://www.maplabkitchen.com/corporate-tea-party-desserts/">台南會議茶點與企業茶會規劃</a>',
                '<a href="https://www.maplabkitchen.com/vip-expo-catering-business-meeting/">展覽接待與商務貴賓外燴</a>',
                '<a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">台南開幕茶會與品牌活動餐點</a>',
                '<a href="https://www.maplabkitchen.com/corporate-catering-tainan/">台南企業外燴服務總覽</a>',
            ]
        ),
        heading("常見問題", "faq"),
        faq_block(),
        paragraph('<a href="https://lin.ee/IP8nt4n">用 LINE 詢問大臺南會展中心活動茶點規劃</a>'),
    ]
    return "\n\n".join(parts)


def public_safety_check(content: str) -> list[str]:
    failures = []
    forbidden_patterns = {
        "script tag": r"<script\b",
        "inline style": r"\sstyle=",
        "local path": r"file://|/Users/pagemacmini|/private/tmp|GoogleDrive-",
        "internal source name": r"工研院|在宅醫療科技推動計畫|跨部會工作小組",
        "hard guarantee": r"保證|唯一|最頂|CP值|便宜又大碗|錯過可惜|趕快預約",
        "salesy contrast": r"不是.{0,12}而是|不只.{0,12}也",
    }
    for label, pattern in forbidden_patterns.items():
        if re.search(pattern, content, flags=re.IGNORECASE):
            failures.append(label)
    return failures


def main() -> int:
    manifest_rows = load_manifest()
    missing = [name for name in SELECTED_IMAGES if name not in manifest_rows]
    if missing:
        raise WPError(f"selected image missing from manifest: {missing}")

    uploaded = {}
    upload_rows = []
    for row in manifest_rows.values():
        media = ensure_media(row)
        uploaded[row["output_file"]] = media
        upload_rows.append(
            {
                "output_file": row["output_file"],
                "media_id": media.get("id"),
                "source_url": media.get("source_url"),
                "action": media.get("_maplab_upload_action", "unknown"),
                "alt_text": media.get("alt_text") or row["alt_text"],
                "caption": row["caption"],
            }
        )
        time.sleep(0.1)

    content = build_content(uploaded, manifest_rows)
    failures = public_safety_check(content)
    if failures:
        raise WPError(f"public safety check failed: {', '.join(failures)}")

    content_path = JOB_DIR / "wordpress_draft_content_v2.md"
    content_path.write_text(
        "# WordPress Draft Content v2 — A2-SEO-ICCTN-001\n\n"
        "Status: synced_to_unpublished_wordpress_draft\n"
        f"Post ID: `{POST_ID}`\n"
        f"Title: `{TITLE}`\n"
        f"Slug: `{SLUG}`\n"
        "Includes: quick navigation buttons, selected WebP image blocks, case category, Rank Math FAQ block, internal links, LINE CTA.\n\n"
        "## HTML Payload\n\n```html\n"
        + content
        + "\n```\n",
        encoding="utf-8",
    )

    featured_id = uploaded["maplab-icc-tainan-wide-refreshment-table-12.webp"]["id"]
    update_payload = {
        "title": TITLE,
        "slug": SLUG,
        "status": "draft",
        "content": content,
        "excerpt": EXCERPT,
        "categories": [CASE_CATEGORY_ID],
        "featured_media": featured_id,
    }
    post_update = request_json("POST", f"/wp/v2/posts/{POST_ID}", update_payload)

    rankmath_result: dict | list | None = None
    rankmath_error = None
    try:
        rankmath_result = request_json(
            "POST",
            "/rankmath/v1/updateMeta",
            {
                "objectID": POST_ID,
                "objectType": POST_TYPE,
                "meta": RANK_MATH_META,
            },
        )
    except Exception as exc:
        rankmath_error = str(exc)
        fallback_payload = {"meta": RANK_MATH_META}
        try:
            request_json("POST", f"/wp/v2/posts/{POST_ID}", fallback_payload)
        except Exception as fallback_exc:
            rankmath_error += f" | WP REST meta fallback failed: {fallback_exc}"

    with (ASSET_DIR / "wp_media_upload_manifest_icctn_001.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["output_file", "media_id", "source_url", "action", "alt_text", "caption"])
        writer.writeheader()
        writer.writerows(upload_rows)

    result = {
        "post_id": POST_ID,
        "status": post_update.get("status"),
        "slug": post_update.get("slug"),
        "link": post_update.get("link"),
        "edit_url": f"{SITE}/wp-admin/post.php?post={POST_ID}&action=edit",
        "categories": post_update.get("categories"),
        "featured_media": post_update.get("featured_media"),
        "uploaded_or_reused_media_count": len(upload_rows),
        "selected_image_count": len(SELECTED_IMAGES),
        "rank_math_meta": {k: "set" for k in RANK_MATH_META},
        "rank_math_error": rankmath_error,
        "rank_math_result": rankmath_result,
        "content_chars": len(content),
        "public_safety_check": "pass",
        "published": post_update.get("status") == "publish",
    }
    (JOB_DIR / "wordpress_draft_update_v2_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({k: result[k] for k in ["post_id", "status", "slug", "featured_media", "uploaded_or_reused_media_count", "selected_image_count", "public_safety_check", "published"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
