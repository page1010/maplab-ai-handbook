#!/usr/bin/env python3
"""Public-only MAPLAB SEO baseline probe; JSON is written to stdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


PROBE_VERSION = "maplab-public-seo-probe-v1"
USER_AGENT = "MAPLAB-SEO-Coach/1.0 (+public-read-only)"


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_title = False
        self._in_h1 = False
        self._in_schema = False
        self.title_parts: list[str] = []
        self.h1: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.schema_blocks = 0
        self.schema_texts: list[str] = []
        self.images = 0
        self.images_missing_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
            self.h1.append("")
        elif tag == "meta":
            key = (values.get("name") or values.get("property") or "").lower()
            if key and values.get("content"):
                self.meta[key] = values["content"]
        elif tag == "link" and "canonical" in values.get("rel", "").lower():
            self.canonical = values.get("href") or None
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_schema = True
            self.schema_blocks += 1
            self.schema_texts.append("")
        elif tag == "img":
            self.images += 1
            if not values.get("alt", "").strip():
                self.images_missing_alt += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "script":
            self._in_schema = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_h1 and self.h1:
            self.h1[-1] += data
        if self._in_schema and self.schema_texts:
            self.schema_texts[-1] += data


def clean(value: str | None) -> str | None:
    return " ".join(value.split()) if value else None


def request(url: str, timeout: float) -> tuple[int, str, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return (
                int(response.status),
                response.geturl(),
                {key.lower(): value for key, value in response.headers.items()},
                response.read(),
            )
    except urllib.error.HTTPError as exc:
        return (
            int(exc.code),
            exc.geturl(),
            {key.lower(): value for key, value in exc.headers.items()},
            exc.read(),
        )


def page_record(url: str, timeout: float) -> dict[str, Any]:
    try:
        status, final_url, headers, body = request(url, timeout)
    except Exception as exc:  # Network failures are evidence, not script crashes.
        return {"url": url, "error": type(exc).__name__, "detail": str(exc)}

    parser = HeadParser()
    parser.feed(body.decode("utf-8", "replace"))
    robots = clean(parser.meta.get("robots"))
    canonical = parser.canonical
    normalized_final = final_url.rstrip("/") + "/"
    normalized_canonical = canonical.rstrip("/") + "/" if canonical else None
    findings: list[str] = []
    if status != 200:
        findings.append("non_200")
    if robots and "noindex" in robots.lower():
        findings.append("noindex")
    if not clean("".join(parser.title_parts)):
        findings.append("missing_title")
    if not clean(parser.meta.get("description")):
        findings.append("missing_description")
    if not canonical:
        findings.append("missing_canonical")
    elif normalized_canonical != normalized_final:
        findings.append("canonical_not_self")
    if len(parser.h1) != 1:
        findings.append("h1_count_not_one")
    if parser.schema_blocks == 0:
        findings.append("missing_json_ld")
    schema_errors: list[str] = []
    for index, schema_text in enumerate(parser.schema_texts):
        try:
            json.loads(schema_text)
        except json.JSONDecodeError as exc:
            schema_errors.append(f"block_{index + 1}:{exc.msg}@{exc.pos}")
    if schema_errors:
        findings.append("invalid_json_ld")
    if parser.images_missing_alt:
        findings.append("images_missing_alt")

    return {
        "url": url,
        "status": status,
        "final_url": final_url,
        "content_type": headers.get("content-type"),
        "title": clean("".join(parser.title_parts)),
        "description": clean(parser.meta.get("description")),
        "robots": robots,
        "canonical": canonical,
        "h1": [clean(item) for item in parser.h1],
        "schema_blocks": parser.schema_blocks,
        "schema_valid_blocks": parser.schema_blocks - len(schema_errors),
        "schema_invalid_blocks": len(schema_errors),
        "schema_errors": schema_errors,
        "images": parser.images,
        "images_missing_alt": parser.images_missing_alt,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "findings": findings,
    }


def text_record(url: str, timeout: float) -> dict[str, Any]:
    try:
        status, final_url, headers, body = request(url, timeout)
        return {
            "url": url,
            "status": status,
            "final_url": final_url,
            "content_type": headers.get("content-type"),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "text": body.decode("utf-8", "replace"),
        }
    except Exception as exc:
        return {"url": url, "error": type(exc).__name__, "detail": str(exc)}


def wp_count(site: str, kind: str, timeout: float) -> dict[str, Any]:
    endpoint = urllib.parse.urljoin(site, f"wp-json/wp/v2/{kind}?status=publish&per_page=1")
    try:
        status, final_url, headers, body = request(endpoint, timeout)
        return {
            "url": endpoint,
            "status": status,
            "final_url": final_url,
            "total": int(headers["x-wp-total"]) if headers.get("x-wp-total") else None,
            "total_pages": int(headers["x-wp-totalpages"]) if headers.get("x-wp-totalpages") else None,
            "body_sha256": hashlib.sha256(body).hexdigest(),
        }
    except Exception as exc:
        return {"url": endpoint, "error": type(exc).__name__, "detail": str(exc)}


def sitemap_summary(record: dict[str, Any]) -> dict[str, Any]:
    text = record.pop("text", "")
    record["child_sitemaps"] = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", text)
    record["lastmods"] = re.findall(r"<lastmod>\s*([^<]+?)\s*</lastmod>", text)
    return record


def sitemap_tree(site: str, timeout: float) -> dict[str, Any]:
    index = sitemap_summary(
        text_record(urllib.parse.urljoin(site, "sitemap_index.xml"), timeout)
    )
    children: list[dict[str, Any]] = []
    for child_url in index.get("child_sitemaps", []):
        child = sitemap_summary(text_record(child_url, timeout))
        urls = child.pop("child_sitemaps", [])
        lastmods = child.pop("lastmods", [])
        child.update(
            {
                "url_count": len(urls),
                "latest_lastmod": max(lastmods) if lastmods else None,
                "urls_sha256": hashlib.sha256(
                    json.dumps(urls, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ).hexdigest(),
            }
        )
        children.append(child)
    return {"index": index, "children": children}


def page_material(record: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "url",
        "status",
        "final_url",
        "title",
        "description",
        "robots",
        "canonical",
        "h1",
        "schema_blocks",
        "schema_valid_blocks",
        "schema_invalid_blocks",
        "schema_errors",
        "images_missing_alt",
        "findings",
        "error",
    )
    return {field: record.get(field) for field in fields}


def comparable(payload: dict[str, Any]) -> dict[str, Any]:
    robots = payload.get("robots", {})
    sitemap = payload.get("sitemap", {})
    wordpress = payload.get("wordpress", {})
    return {
        "method_fingerprint": payload.get("method_fingerprint"),
        "robots": {
            "status": robots.get("status"),
            "final_url": robots.get("final_url"),
            "body_sha256": robots.get("body_sha256"),
            "error": robots.get("error"),
        },
        "sitemap": {
            "index_status": sitemap.get("index", {}).get("status"),
            "index_children": sitemap.get("index", {}).get("child_sitemaps"),
            "children": [
                {
                    "url": item.get("url"),
                    "status": item.get("status"),
                    "url_count": item.get("url_count"),
                    "latest_lastmod": item.get("latest_lastmod"),
                    "urls_sha256": item.get("urls_sha256"),
                    "error": item.get("error"),
                }
                for item in sitemap.get("children", [])
            ],
        },
        "wordpress": {
            kind: {
                "status": wordpress.get(kind, {}).get("status"),
                "total": wordpress.get(kind, {}).get("total"),
                "error": wordpress.get(kind, {}).get("error"),
            }
            for kind in ("posts", "pages")
        },
        "pages": [page_material(item) for item in payload.get("pages", [])],
    }


def load_previous(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="https://www.maplabkitchen.com/")
    parser.add_argument("--url", action="append", dest="urls", default=[])
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()

    site = args.site.rstrip("/") + "/"
    urls = args.urls or [site]
    method_fields = {
        "probe_version": PROBE_VERSION,
        "worker": "stdlib-public-http",
        "model": "none",
        "sampling": "none",
        "evaluator": "deterministic-field-checks-v1",
        "acceptance": "http-index-canonical-title-description-h1-schema-alt-v1",
        "urls": urls,
        "timeout_seconds": args.timeout,
    }
    fingerprint = hashlib.sha256(
        json.dumps(method_fields, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "public-read-only",
        "site": site,
        "method_fields": method_fields,
        "method_fingerprint": fingerprint,
        "robots": text_record(urllib.parse.urljoin(site, "robots.txt"), args.timeout),
        "sitemap": sitemap_tree(site, args.timeout),
        "wordpress": {
            "posts": wp_count(site, "posts", args.timeout),
            "pages": wp_count(site, "pages", args.timeout),
        },
        "pages": [page_record(url, args.timeout) for url in urls],
    }
    previous = load_previous(args.previous)
    if previous is not None:
        verified_delta = comparable(previous) != comparable(payload)
        payload["comparison"] = {
            "previous_path": str(args.previous),
            "verified_delta": verified_delta,
            "previous_method_fingerprint": previous.get("method_fingerprint"),
            "decision": "MATERIAL_DELTA" if verified_delta else "NO_DELTA_NO_DISPATCH",
        }
    else:
        payload["comparison"] = {
            "previous_path": None,
            "verified_delta": None,
            "previous_method_fingerprint": None,
            "decision": "BASELINE_CREATED",
        }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
