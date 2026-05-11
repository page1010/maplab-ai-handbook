#!/usr/bin/env python3
"""Recover MAPLAB Kitchen keyword ownership through WP REST + Rank Math.

This script intentionally keeps the edit surface small:
- Rank Math title / description / focus keyword
- published post title where the live H1 is misaligned
- a marked internal-link / FAQ support block that can be replaced or removed

Credentials are read from environment variables only:
  WP_USERNAME
  WP_APP_PASSWORD
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEWS_DIR = REPO_ROOT / "workbook" / "reviews"
BASE_URL = "https://www.maplabkitchen.com"
USER_AGENT = "MAPLAB-A1-RankMath-Recovery/1.0"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec="seconds")


TARGETS: dict[str, dict[str, Any]] = {
    "homepage": {
        "type": "pages",
        "id": 1250,
        "object_type": "post",
        "title": None,
        "rank_math": {
            "rank_math_focus_keyword": "台南外燴推薦, 台南到府外燴, 台南派對外燴",
            "rank_math_title": "台南外燴推薦｜台南到府外燴、台南派對外燴與企業茶會｜MAPLAB",
            "rank_math_description": "MAPLAB Kitchen 提供台南外燴推薦、台南到府外燴、台南派對外燴與企業茶會餐點規劃，依活動場景整理菜單、動線與餐桌配置。",
        },
        "block": None,
    },
    "guide": {
        "type": "posts",
        "id": 683,
        "object_type": "post",
        "title": "台南外燴全攻略｜台南到府外燴、台南派對外燴與活動餐點｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "台南到府外燴, 台南派對外燴",
            "rank_math_title": "台南外燴全攻略｜台南到府外燴、台南派對外燴與活動餐點｜MAPLAB",
            "rank_math_description": "整理台南到府外燴、台南派對外燴、週歲生日、開幕茶會與企業活動餐點規劃重點，協助你依人數、場地與活動節奏找到合適配置。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:guide START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">台南到府外燴與派對外燴，適合哪些活動？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>如果活動不在餐廳或宴會廳舉行，到府外燴會更需要先確認空間、動線、取餐位置與雨備。MAPLAB Kitchen 會依活動性質調整餐點形式，讓餐桌能服務現場，而不是只把餐點送到現場。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/catering-one-year-old-party-tainan/">週歲派對外燴</a>：適合家庭聚會、抓周、生日與親友小型派對。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/corporate-catering-tainan/">企業外燴</a>：適合公司茶會、品牌接待、內部活動與商務交流。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">開幕茶會外燴</a>：適合品牌開幕、診所開幕、展覽開幕與貴賓接待。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/corporate-tea-party-desserts/">會議茶點外燴</a>：適合研討會、講座、學校活動與企業會議。</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">FAQ：台南到府外燴需要先準備什麼？</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>通常會先確認日期、地點、人數、活動時間、是否需要桌面配置與現場服務。若場地在戶外，也會一起看電力、遮蔽、取餐動線與雨備。</p>
<!-- /wp:paragraph -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:guide END -->
""",
    },
    "corporate": {
        "type": "posts",
        "id": 586,
        "object_type": "post",
        "title": "台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "台南企業外燴",
            "rank_math_title": "台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB",
            "rank_math_description": "MAPLAB Kitchen 提供台南企業外燴、公司茶會、會議茶點、開幕茶會與品牌活動餐點規劃，協助行政、公關與活動窗口穩定安排現場。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:corporate START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">台南企業外燴的四個延伸場景</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>企業活動不只是一種餐點需求。不同窗口在意的重點也不同：會議重視準時與好拿取，開幕茶會重視第一印象，品牌活動重視畫面與接待節奏。若你正在整理活動方向，可以從以下場景開始對照。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/corporate-tea-party-desserts/">台南會議茶點外燴</a>：適合研討會、學校講座、企業會議與內部訓練。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">台南開幕茶會外燴</a>：適合公司、診所、品牌空間與展覽開幕。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/brand-esg-catering-service/">台南品牌活動外燴</a>：適合 VIP 接待、發表會、賞車活動與建案活動。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/tainan-launch-event-catering/">新品發表與記者會餐點</a>：適合需要品牌記憶點與現場動線的活動。</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:corporate END -->
""",
    },
    "opening": {
        "type": "posts",
        "id": 1205,
        "object_type": "post",
        "title": "台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "台南開幕茶會, 開幕茶會流程",
            "rank_math_title": "台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB",
            "rank_math_description": "台南開幕茶會外燴規劃，從開幕典禮流程、貴賓接待、茶點配置到取餐動線，協助品牌、診所與公司活動呈現穩定第一印象。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:opening START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">開幕茶會流程可以怎麼安排？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>開幕活動通常會有報到、簡短致詞、剪綵或導覽，再進入交流與拍照。餐點配置會建議放在不阻擋主視覺與動線的位置，讓來賓在等待、交流與活動結束後都能自然取用。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item --><li>活動前：確認桌面位置、取餐方向、飲品補給與垃圾回收動線。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li>活動中：以好拿取、不滴落、方便交流的茶點為主。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li>活動後：保留可拍照的餐桌畫面，作為品牌活動紀錄的一部分。</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>若活動延伸到記者會、VIP 接待或展覽開幕，也可以參考 <a href="https://www.maplabkitchen.com/brand-esg-catering-service/">台南品牌活動外燴</a> 與 <a href="https://www.maplabkitchen.com/corporate-catering-tainan/">台南企業外燴</a> 的規劃方式。</p>
<!-- /wp:paragraph -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:opening END -->
""",
    },
    "brand": {
        "type": "posts",
        "id": 945,
        "object_type": "post",
        "title": "台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "台南品牌活動外燴",
            "rank_math_title": "台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB",
            "rank_math_description": "台南品牌活動外燴規劃，適合發表會、VIP 接待、賞車活動、建案活動與展覽開幕，依品牌調性安排餐點、飲品與桌面節奏。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:brand START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">台南品牌活動外燴，重點在接待節奏與畫面一致</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>品牌活動的餐桌不是單純補充點心，而是來賓停留、交流與拍照時會看到的現場元素。規劃時會一起考慮品牌色調、取餐動線、餐點大小、飲品補給與現場服務節奏。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">開幕茶會</a>：適合品牌空間、診所、展間與新店開幕。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/tainan-launch-event-catering/">新品發表會</a>：適合需要媒體、貴賓或合作夥伴接待的活動。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/corporate-tea-party-desserts/">會議茶點</a>：適合品牌說明會、講座與企業交流。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><a href="https://www.maplabkitchen.com/corporate-catering-tainan/">企業外燴</a>：適合更完整的公司活動餐點規劃。</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:brand END -->
""",
    },
    "meeting": {
        "type": "posts",
        "id": 924,
        "object_type": "post",
        "title": "台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "台南會議茶點",
            "rank_math_title": "台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB",
            "rank_math_description": "台南會議茶點外燴適合研討會、學校講座、企業會議與內部訓練，MAPLAB Kitchen 協助規劃好拿取、不中斷交流的餐點與飲品。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:meeting START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">台南會議茶點外燴：研討會、講座與企業會議怎麼準備？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>會議茶點更在意準時、份量清楚、好拿取與不中斷流程。比起完整餐宴，這類活動通常需要的是能穩定支援交流、休息與講座節奏的餐點配置。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item --><li>研討會與講座：以單手可拿、方便補給的甜點與鹹食為主。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li>企業會議：可依會議時間搭配飲品、午間輕食或下午茶點。</li><!-- /wp:list-item -->
<!-- wp:list-item --><li>學校活動：可依報到、休息與交流時間分段安排取餐位置。</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>若是公司茶會、品牌接待或開幕活動，可以延伸閱讀 <a href="https://www.maplabkitchen.com/corporate-catering-tainan/">台南企業外燴</a>、<a href="https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/">台南開幕茶會外燴</a> 與 <a href="https://www.maplabkitchen.com/brand-esg-catering-service/">台南品牌活動外燴</a>。</p>
<!-- /wp:paragraph -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:meeting END -->
""",
    },
    "week_one": {
        "type": "posts",
        "id": 498,
        "object_type": "post",
        "title": None,
        "rank_math": {
            "rank_math_focus_keyword": "台南週歲派對外燴",
            "rank_math_title": "台南週歲派對外燴推薦｜菜單、場地、費用完整懶人包 2026",
            "rank_math_description": "整理台南週歲派對外燴、抓周餐點、家庭派對菜單與場地準備重點，協助你把家人聚會、取餐動線與餐桌畫面安排得更穩。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:week_one START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">週歲之外，也常見的家庭派對外燴場景</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>如果這場聚會同時包含生日、抓周、性別揭曉或親友小型派對，可以先從活動時間、人數與取餐動線來判斷餐點形式。更多派對與到府活動，也可以參考 <a href="https://www.maplabkitchen.com/gender-reveal-party-tips/">性別揭曉派對外燴</a> 與 <a href="https://www.maplabkitchen.com/tainan-catering-guide/">台南到府外燴全攻略</a>。</p>
<!-- /wp:paragraph -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:week_one END -->
""",
    },
    "gender": {
        "type": "posts",
        "id": 332,
        "object_type": "post",
        "title": "性別揭曉派對外燴｜Gender Reveal 餐點與甜點桌規劃｜MAPLAB",
        "rank_math": {
            "rank_math_focus_keyword": "性別揭曉派對, Gender Reveal Party",
            "rank_math_title": "性別揭曉派對外燴｜Gender Reveal 餐點與甜點桌規劃｜MAPLAB",
            "rank_math_description": "性別揭曉派對外燴可依家庭聚會人數、拍照流程與甜點桌需求規劃餐點。MAPLAB Kitchen 協助整理 Gender Reveal Party 的餐桌與取餐節奏。",
        },
        "block": """
<!-- MAPLAB-A2-KEYWORD-RECOVERY:gender START -->
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">性別揭曉派對外燴可以和週歲、生日派對一起規劃</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Gender Reveal Party 通常很重視拍照瞬間、甜點桌畫面與親友互動。如果同時在籌備寶寶生日、抓周或家庭聚會，可以延伸參考 <a href="https://www.maplabkitchen.com/catering-one-year-old-party-tainan/">台南週歲派對外燴</a> 與 <a href="https://www.maplabkitchen.com/tainan-catering-guide/">台南派對外燴規劃</a>。</p>
<!-- /wp:paragraph -->
<!-- MAPLAB-A2-KEYWORD-RECOVERY:gender END -->
""",
    },
}


STALE_LINK_REWRITES = {
    "/catering-corporate-tainan/": "/corporate-catering-tainan/",
    "/catering-birthday-party-tainan/": "/catering-one-year-old-party-tainan/",
    "/catering-wedding-tainan/": "/tainan-catering-guide/",
    "/opening-event-catering-tainan/": "/tainan-corporate-opening-tea-catering/",
    "/meeting-refreshment-catering-tainan/": "/corporate-tea-party-desserts/",
    "/brand-event-catering/": "/brand-esg-catering-service/",
}


def auth_header() -> str:
    username = os.environ.get("WP_USERNAME")
    password = os.environ.get("WP_APP_PASSWORD")
    if not username or not password:
        raise SystemExit("Missing WP_USERNAME or WP_APP_PASSWORD")
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"


def request_json(method: str, path: str, auth: str | None = None, payload: Any | None = None) -> Any:
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = auth
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} failed: HTTP {exc.code} {body[:500]}") from exc


def fetch_item(spec: dict[str, Any], auth: str) -> dict[str, Any]:
    return request_json("GET", f"/wp-json/wp/v2/{spec['type']}/{spec['id']}?context=edit", auth=auth)


def replace_marked_block(content: str, key: str, block: str) -> str:
    start = f"<!-- MAPLAB-A2-KEYWORD-RECOVERY:{key} START -->"
    end = f"<!-- MAPLAB-A2-KEYWORD-RECOVERY:{key} END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    block = block.strip() + "\n"
    if pattern.search(content):
        return pattern.sub(block, content)
    return content.rstrip() + "\n\n" + block


def rewrite_stale_links(content: str) -> str:
    updated = content
    for old, new in STALE_LINK_REWRITES.items():
        updated = updated.replace(f'href="{old}"', f'href="{new}"')
        updated = updated.replace(f"href='{old}'", f"href='{new}'")
        updated = updated.replace(f'href="{BASE_URL}{old}"', f'href="{BASE_URL}{new}"')
        updated = updated.replace(f"href='{BASE_URL}{old}'", f"href='{BASE_URL}{new}'")
    return updated


def fix_known_markup_breaks(content: str) -> str:
    # Existing gender-reveal content had a dangling closing tag (`</section`)
    # that prevented appended blocks from rendering on the frontend.
    return content.replace("</section\n", "</section>\n")


def live_fetch(path: str) -> str:
    req = urllib.request.Request(BASE_URL + path, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode(errors="replace")


def extract_head(html: str) -> dict[str, Any]:
    title = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S | re.I)
    canon = re.search(r'<link rel="canonical" href="(.*?)"', html, re.S | re.I)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    return {
        "title": re.sub("<.*?>", "", title.group(1)).strip() if title else None,
        "description": desc.group(1).strip() if desc else None,
        "canonical": canon.group(1).strip() if canon else None,
        "h1": re.sub("<.*?>", "", h1.group(1)).strip() if h1 else None,
        "has_rank_math": "Rank Math" in html,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write live WordPress/Rank Math changes.")
    parser.add_argument("--job", default=f"JOB-A2-RANKMATH-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    args = parser.parse_args()

    auth = auth_header()
    job_dir = REVIEWS_DIR / args.job
    before_dir = job_dir / "before"
    after_dir = job_dir / "after"
    job_dir.mkdir(parents=True, exist_ok=True)

    execution: dict[str, Any] = {
        "job_id": args.job,
        "started_at": now_iso(),
        "apply": args.apply,
        "targets": [],
        "rankmath_results": [],
        "wp_update_results": [],
        "errors": [],
    }
    diffs: list[str] = []

    for key, spec in TARGETS.items():
        item = fetch_item(spec, auth)
        raw = item.get("content", {}).get("raw", "") or ""
        link = item.get("link")
        before_snapshot = {
            "key": key,
            "id": spec["id"],
            "type": spec["type"],
            "link": link,
            "status": item.get("status"),
            "title": item.get("title", {}).get("raw"),
            "slug": item.get("slug"),
            "rank_math_payload": spec["rank_math"],
            "content_raw": raw,
        }
        write_json(before_dir / f"{key}.json", before_snapshot)

        new_raw = fix_known_markup_breaks(rewrite_stale_links(raw))
        if spec.get("block"):
            new_raw = replace_marked_block(new_raw, key, spec["block"])

        update_payload: dict[str, Any] = {}
        if spec.get("title"):
            update_payload["title"] = spec["title"]
        if new_raw != raw:
            update_payload["content"] = new_raw
            diff = "\n".join(
                difflib.unified_diff(
                    raw.splitlines(),
                    new_raw.splitlines(),
                    fromfile=f"{key}:before",
                    tofile=f"{key}:after",
                    lineterm="",
                )
            )
            diffs.append(f"\n## {key}\n\n```diff\n{diff}\n```\n")

        execution["targets"].append(
            {
                "key": key,
                "id": spec["id"],
                "type": spec["type"],
                "link": link,
                "title_update": bool(spec.get("title")),
                "content_update": new_raw != raw,
                "rank_math": spec["rank_math"],
            }
        )

        if args.apply:
            try:
                rm = request_json(
                    "POST",
                    "/wp-json/rankmath/v1/updateMeta",
                    auth=auth,
                    payload={
                        "objectID": spec["id"],
                        "objectType": spec.get("object_type", "post"),
                        "meta": spec["rank_math"],
                    },
                )
                execution["rankmath_results"].append({"key": key, "ok": True, "response": rm})
            except Exception as exc:  # fallback through WP REST meta
                execution["rankmath_results"].append({"key": key, "ok": False, "error": str(exc)})
                update_payload.setdefault("meta", {}).update(spec["rank_math"])

            if update_payload:
                try:
                    wp = request_json(
                        "POST",
                        f"/wp-json/wp/v2/{spec['type']}/{spec['id']}",
                        auth=auth,
                        payload=update_payload,
                    )
                    execution["wp_update_results"].append(
                        {"key": key, "ok": True, "id": wp.get("id"), "modified": wp.get("modified"), "link": wp.get("link")}
                    )
                except Exception as exc:
                    execution["wp_update_results"].append({"key": key, "ok": False, "error": str(exc)})
                    execution["errors"].append({"key": key, "stage": "wp_update", "error": str(exc)})

    (job_dir / "diff.md").write_text("\n".join(diffs) if diffs else "No content diffs.\n")

    # Verify live heads and expected anchors after writes. Sleep briefly for cache/plugin writes.
    if args.apply:
        time.sleep(2)
    verification: dict[str, Any] = {"job_id": args.job, "verified_at": now_iso(), "targets": []}
    for key, spec in TARGETS.items():
        item = fetch_item(spec, auth)
        write_json(after_dir / f"{key}.json", {
            "key": key,
            "id": spec["id"],
            "type": spec["type"],
            "link": item.get("link"),
            "status": item.get("status"),
            "title": item.get("title", {}).get("raw"),
            "slug": item.get("slug"),
            "content_raw": item.get("content", {}).get("raw", "") or "",
        })
        parsed = urllib.parse.urlparse(item.get("link") or "")
        html = live_fetch(parsed.path or "/")
        head = extract_head(html)
        expected_focus = [x.strip() for x in spec["rank_math"]["rank_math_focus_keyword"].split(",")]
        expected_links = re.findall(r'https://www\.maplabkitchen\.com/[^"\']+/', spec.get("block") or "")
        target_result = {
            "key": key,
            "link": item.get("link"),
            "head": head,
            "expected_focus_terms_present": {term: term in html for term in expected_focus if term},
            "expected_links_present": {url: url in html for url in expected_links},
            "content_marker_present": (not spec.get("block")) or (f"MAPLAB-A2-KEYWORD-RECOVERY:{key}" in (item.get("content", {}).get("raw", "") or "")),
        }
        verification["targets"].append(target_result)

    execution["finished_at"] = now_iso()
    write_json(job_dir / "execution_log.json", execution)
    write_json(job_dir / "verification_log.json", verification)
    write_json(job_dir / "output_manifest.json", {
        "job_id": args.job,
        "files": [
            "execution_log.json",
            "verification_log.json",
            "output_manifest.json",
            "diff.md",
            "before/*.json",
            "after/*.json",
            "review_request.md",
        ],
        "live_targets": [t["link"] for t in execution["targets"]],
    })
    (job_dir / "review_request.md").write_text(
        f"""# Review Request: {args.job}

status: waiting_for_review
owner_agent: A2
reviewer: A1 / Owner
created_at: {now_iso()}

## Scope

- Rank Math focus keyword / title / description updated through REST when accepted.
- Existing live owner posts/pages updated with small marked support blocks.
- No new pages, no generated images, no deletes, no redirects.

## Verify

1. Check `verification_log.json`.
2. Open each live URL and confirm title/description/anchors.
3. Confirm Rank Math panel in wp-admin shows expected focus keyword and title.

"""
    )
    print(json.dumps({"job_id": args.job, "review_bundle": str(job_dir), "apply": args.apply, "errors": execution["errors"]}, ensure_ascii=False))
    return 1 if execution["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
