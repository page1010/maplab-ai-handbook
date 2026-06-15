#!/usr/bin/env python3
"""Authenticated non-secret verification for the ICC Tainan WordPress post."""

from __future__ import annotations

import base64
import json
import os
import urllib.request


POST_ID = 1829
URL = f"https://www.maplabkitchen.com/wp-json/wp/v2/posts/{POST_ID}?context=edit"


def main() -> int:
    user = os.environ["WP_USER"]
    password = os.environ["WP_APP_PASS"]
    auth = "Basic " + base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(
        URL,
        headers={
            "Authorization": auth,
            "Accept": "application/json",
            "User-Agent": "MAPLAB-A2-Verify/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        post = json.loads(resp.read().decode("utf-8"))
    raw = post.get("content", {}).get("raw", "")
    checks = {
        "published": post.get("status") == "publish",
        "case_category_170": 170 in (post.get("categories") or []),
        "featured_media_1833": post.get("featured_media") == 1833,
        "quick_nav": "maplab-quick-nav" in raw,
        "faq_block": "rank-math-faq-block" in raw,
        "line_cta": "https://lin.ee/IP8nt4n" in raw,
        "case_heading": "大臺南會展中心企業會議茶點案例" in raw,
        "image_1833": "wp-image-1833" in raw,
        "image_1834": "wp-image-1834" in raw,
        "image_1839": "wp-image-1839" in raw,
        "image_1840": "wp-image-1840" in raw,
        "image_1841": "wp-image-1841" in raw,
    }
    result = {
        "id": post.get("id"),
        "status": post.get("status"),
        "slug": post.get("slug"),
        "link": post.get("link"),
        "categories": post.get("categories"),
        "featured_media": post.get("featured_media"),
        "content_len": len(raw),
        "checks": checks,
        "ok": all(checks.values()),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
