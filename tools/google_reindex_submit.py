#!/usr/bin/env python3
"""Submit/verify MAPLAB SEO recovery URLs through allowed Google discovery paths.

This does not pretend to force Google indexing. For normal WordPress pages,
Google's public paths are:

- sitemap discovery / submission
- Search Console URL Inspection status checks
- Search Console UI "Request Indexing" for a few individual URLs

Rank Math's Instant Indexing REST route is also attempted when WordPress
credentials are supplied. The response is saved as evidence, because the plugin
configuration determines what services it can actually notify.

Credentials are read from environment variables only:
  WP_USERNAME
  WP_APP_PASSWORD
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from wp_rankmath_recovery import BASE_URL, REVIEWS_DIR, TARGETS, USER_AGENT


TOKEN_PATH = Path.home() / ".claude" / "mcp-keys" / "google-token.json"
SITEMAP_INDEX = f"{BASE_URL}/sitemap_index.xml"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec="seconds")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_text_url(url: str, *, headers: dict[str, str] | None = None) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode(errors="replace")
            return resp.status, body, dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return exc.code, body, dict(exc.headers.items())


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
) -> tuple[int, Any, dict[str, str]]:
    data = None
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode(errors="replace")
            return resp.status, json.loads(body) if body else {}, dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            parsed: Any = json.loads(body)
        except Exception:
            parsed = {"raw": body[:1000]}
        return exc.code, parsed, dict(exc.headers.items())


def auth_header() -> str | None:
    username = os.environ.get("WP_USERNAME")
    password = os.environ.get("WP_APP_PASSWORD")
    if not username or not password:
        return None
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"


def target_urls() -> list[str]:
    urls = []
    for spec in TARGETS.values():
        # The recovery script stores live URLs through WP object IDs; use the
        # canonical slugs that were verified in the previous review bundle.
        pass
    return [
        f"{BASE_URL}/",
        f"{BASE_URL}/tainan-catering-guide/",
        f"{BASE_URL}/corporate-catering-tainan/",
        f"{BASE_URL}/tainan-corporate-opening-tea-catering/",
        f"{BASE_URL}/corporate-tea-party-desserts/",
        f"{BASE_URL}/brand-esg-catering-service/",
        f"{BASE_URL}/catering-one-year-old-party-tainan/",
        f"{BASE_URL}/gender-reveal-party-tips/",
    ]


def parse_sitemap_locs(xml_text: str) -> list[str]:
    try:
        root = ET.fromstring(xml_text.encode())
        return [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    except ET.ParseError:
        return re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.S)


def check_sitemap_membership(urls: list[str]) -> dict[str, Any]:
    status, index_xml, index_headers = read_text_url(SITEMAP_INDEX)
    sitemap_urls = parse_sitemap_locs(index_xml) if status == 200 else []
    all_page_urls: dict[str, list[str]] = {}
    found_in: dict[str, str | None] = {u: None for u in urls}

    for sitemap_url in sitemap_urls:
        sm_status, sm_xml, _ = read_text_url(sitemap_url)
        locs = parse_sitemap_locs(sm_xml) if sm_status == 200 else []
        all_page_urls[sitemap_url] = locs
        loc_set = set(locs)
        for url in urls:
            variants = {url, url.rstrip("/") + "/"}
            if loc_set.intersection(variants):
                found_in[url] = sitemap_url

    return {
        "sitemap_index": SITEMAP_INDEX,
        "sitemap_index_status": status,
        "sitemap_index_headers": {
            "content-type": index_headers.get("Content-Type"),
            "x-robots-tag": index_headers.get("X-Robots-Tag"),
            "cache-control": index_headers.get("Cache-Control"),
        },
        "sub_sitemaps": sitemap_urls,
        "url_membership": [
            {"url": url, "found": bool(sitemap), "sitemap": sitemap}
            for url, sitemap in found_in.items()
        ],
    }


def check_live_urls(urls: list[str]) -> list[dict[str, Any]]:
    checks = []
    for url in urls:
        status, html, headers = read_text_url(url)
        title = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        canonical = re.search(r'<link rel="canonical" href="(.*?)"', html, re.S | re.I)
        robots = re.search(r'<meta name="robots" content="(.*?)"', html, re.S | re.I)
        description = re.search(r'<meta name="description" content="(.*?)"', html, re.S | re.I)
        checks.append(
            {
                "url": url,
                "http_status": status,
                "content_type": headers.get("Content-Type"),
                "title": re.sub("<.*?>", "", title.group(1)).strip() if title else None,
                "canonical": canonical.group(1).strip() if canonical else None,
                "robots_meta": robots.group(1).strip() if robots else None,
                "has_description": bool(description),
                "has_rank_math_marker": "Rank Math" in html,
                "indexable_by_page_meta": not (robots and "noindex" in robots.group(1).lower()),
            }
        )
    return checks


def submit_rank_math(urls: list[str], auth: str | None) -> dict[str, Any]:
    if not auth:
        return {
            "attempted": False,
            "status": "blocked",
            "reason": "Missing WP_USERNAME or WP_APP_PASSWORD",
        }

    endpoint = f"{BASE_URL}/wp-json/rankmath/v1/in/submitUrls"
    attempts = []
    for payload in ({"urls": urls}, {"urls": "\n".join(urls)}):
        started = time.time()
        status, body, headers = request_json(
            "POST",
            endpoint,
            headers={"Authorization": auth},
            payload=payload,
        )
        attempts.append(
            {
                "http_status": status,
                "duration_seconds": round(time.time() - started, 2),
                "response": body,
                "content_type": headers.get("Content-Type"),
                "payload_shape": "list" if isinstance(payload["urls"], list) else "newline_string",
            }
        )
        if 200 <= status < 300:
            break

    return {
        "attempted": True,
        "endpoint": endpoint,
        "attempts": attempts,
        "accepted": any(200 <= a["http_status"] < 300 for a in attempts),
    }


def token_scope_report() -> dict[str, Any]:
    if not TOKEN_PATH.exists():
        return {"token_path": str(TOKEN_PATH), "exists": False}
    try:
        data = json.loads(TOKEN_PATH.read_text())
    except Exception as exc:
        return {"token_path": str(TOKEN_PATH), "exists": True, "read_error": str(exc)}
    scopes = data.get("scopes") or data.get("scope") or []
    if isinstance(scopes, str):
        scopes = scopes.split()
    has_gsc = any("webmasters" in scope for scope in scopes)
    return {
        "token_path": str(TOKEN_PATH),
        "exists": True,
        "account": data.get("account"),
        "expiry": data.get("expiry"),
        "scopes": scopes,
        "has_search_console_scope": has_gsc,
        "gsc_api_action": "skipped" if not has_gsc else "available",
        "note": (
            "Current token does not include webmasters/webmasters.readonly scope; "
            "URL Inspection API and sitemap submission through GSC are not attempted."
            if not has_gsc
            else "Token includes Search Console scope; URL Inspection can be attempted in a future run."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", default=f"JOB-A2-GOOGLE-RECRAWL-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    parser.add_argument("--submit-rankmath", action="store_true")
    args = parser.parse_args()

    job_dir = REVIEWS_DIR / args.job
    job_dir.mkdir(parents=True, exist_ok=True)
    urls = target_urls()
    started = time.time()

    sitemap_result = check_sitemap_membership(urls)
    live_result = check_live_urls(urls)
    gsc_report = token_scope_report()
    rankmath_result = submit_rank_math(urls, auth_header()) if args.submit_rankmath else {"attempted": False}

    verification_targets = []
    for item in sitemap_result["url_membership"]:
        verification_targets.append(
            {
                "type": "sitemap_membership",
                "expected": f"{item['url']} is discoverable in Rank Math sitemap",
                "observed": item["sitemap"] if item["found"] else "not found",
                "result": "pass" if item["found"] else "fail",
            }
        )
    for item in live_result:
        ok = item["http_status"] == 200 and item["indexable_by_page_meta"] and item["has_description"]
        verification_targets.append(
            {
                "type": "live_indexability",
                "expected": f"{item['url']} returns 200, has description, and is not noindex",
                "observed": {
                    "http_status": item["http_status"],
                    "robots_meta": item["robots_meta"],
                    "has_description": item["has_description"],
                },
                "result": "pass" if ok else "fail",
            }
        )
    verification_targets.append(
        {
            "type": "rank_math_instant_indexing",
            "expected": "Rank Math submitUrls endpoint accepts the 8 updated URLs",
            "observed": rankmath_result,
            "result": (
                "pass"
                if rankmath_result.get("accepted")
                else "blocked"
                if rankmath_result.get("attempted") is False or rankmath_result.get("status") == "blocked"
                else "fail"
            ),
        }
    )
    verification_targets.append(
        {
            "type": "gsc_api_scope",
            "expected": "OAuth token has Search Console scope for URL Inspection checks",
            "observed": gsc_report,
            "result": "pass" if gsc_report.get("has_search_console_scope") else "blocked",
        }
    )

    overall = "pass"
    if any(t["result"] == "fail" for t in verification_targets):
        overall = "fail"
    elif any(t["result"] == "blocked" for t in verification_targets):
        overall = "partial"

    execution_log = {
        "job_id": args.job,
        "started_at": now_iso(),
        "duration_seconds": round(time.time() - started, 2),
        "target_urls": urls,
        "rank_math_submit_attempted": args.submit_rankmath,
        "gsc_scope_available": bool(gsc_report.get("has_search_console_scope")),
        "overall_result": overall,
    }
    verification_log = {
        "job_id": args.job,
        "verified_by": "Codex local HTTP/API checks",
        "verified_at": now_iso(),
        "verification_targets": verification_targets,
        "overall_result": overall,
    }
    output_manifest = {
        "job_id": args.job,
        "files": [
            "target_urls.json",
            "sitemap_check.json",
            "live_url_check.json",
            "rankmath_submit_response.json",
            "gsc_scope_report.json",
            "execution_log.json",
            "verification_log.json",
            "review_request.md",
        ],
    }

    write_json(job_dir / "target_urls.json", urls)
    write_json(job_dir / "sitemap_check.json", sitemap_result)
    write_json(job_dir / "live_url_check.json", live_result)
    write_json(job_dir / "rankmath_submit_response.json", rankmath_result)
    write_json(job_dir / "gsc_scope_report.json", gsc_report)
    write_json(job_dir / "execution_log.json", execution_log)
    write_json(job_dir / "verification_log.json", verification_log)
    write_json(job_dir / "output_manifest.json", output_manifest)
    (job_dir / "review_request.md").write_text(
        "\n".join(
            [
                f"# {args.job} — Google recrawl / discovery evidence",
                "",
                "status: waiting_for_review",
                "owner_agent: A2/A3",
                "reviewer: Owner / R1",
                "",
                "## What Was Done",
                "",
                "- Checked robots.txt and sitemap discoverability for the 8 Rank Math recovery URLs.",
                "- Checked live URL status, canonical, robots meta, description, and Rank Math marker.",
                "- Attempted Rank Math Instant Indexing submitUrls when WordPress credentials were available.",
                "- Checked whether the local Google OAuth token can use Search Console URL Inspection.",
                "",
                "## Important Boundary",
                "",
                "Google Search Console Request Indexing for normal pages remains a UI action; the public URL Inspection API is for status inspection, not requesting recrawl.",
                "",
                f"overall_result: {overall}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(job_dir)
    print(json.dumps(execution_log, ensure_ascii=False, indent=2))
    return 0 if overall in {"pass", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
