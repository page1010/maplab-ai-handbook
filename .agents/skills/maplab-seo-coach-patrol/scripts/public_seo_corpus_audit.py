#!/usr/bin/env python3
"""Audit MAPLAB post/page sitemap URLs and internal-link topology.

This sensor uses public HTTP GET requests only and writes one JSON receipt to
stdout. It deliberately has no model, authenticated browser, or write path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from public_seo_probe import request


AUDIT_VERSION = "maplab-public-seo-corpus-audit-v1"
DEFAULT_SITEMAPS = (
    "https://www.maplabkitchen.com/post-sitemap.xml",
    "https://www.maplabkitchen.com/page-sitemap.xml",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("href"):
            self.hrefs.append(values["href"])


def urls_from_sitemap(url: str, timeout: float) -> tuple[dict[str, Any], list[str]]:
    try:
        status, final_url, headers, body = request(url, timeout)
    except Exception as exc:
        return (
            {"url": url, "error": type(exc).__name__, "detail": str(exc)},
            [],
        )
    text = body.decode("utf-8", "replace")
    urls = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", text)
    return (
        {
            "url": url,
            "status": status,
            "final_url": final_url,
            "content_type": headers.get("content-type"),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "url_count": len(urls),
            "urls_sha256": hashlib.sha256(
                json.dumps(urls, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        },
        urls,
    )


def normalize_internal_url(base_url: str, href: str, host: str) -> str | None:
    lowered = href.strip().lower()
    if not lowered or lowered.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    absolute = urllib.parse.urljoin(base_url, href)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.hostname != host:
        return None
    path = parsed.path or "/"
    if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    return urllib.parse.urlunsplit(("https", host, path, "", ""))


def crawl_page(url: str, timeout: float, host: str) -> dict[str, Any]:
    try:
        status, final_url, headers, body = request(url, timeout)
    except Exception as exc:
        return {"url": url, "error": type(exc).__name__, "detail": str(exc)}
    parser = LinkParser()
    parser.feed(body.decode("utf-8", "replace"))
    internal_links = sorted(
        {
            normalized
            for href in parser.hrefs
            if (normalized := normalize_internal_url(final_url, href, host)) is not None
        }
    )
    return {
        "url": url,
        "status": status,
        "final_url": final_url,
        "content_type": headers.get("content-type"),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "internal_links": internal_links,
    }


def canonical_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path or "/"
    if not path.endswith("/"):
        path += "/"
    return urllib.parse.urlunsplit(("https", parsed.hostname or "", path, "", ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="https://www.maplabkitchen.com/")
    parser.add_argument("--sitemap", action="append", dest="sitemaps", default=[])
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    site = args.site.rstrip("/") + "/"
    host = urllib.parse.urlsplit(site).hostname or ""
    sitemap_urls = args.sitemaps or list(DEFAULT_SITEMAPS)
    method_fields = {
        "audit_version": AUDIT_VERSION,
        "worker": "stdlib-public-http",
        "model": "none",
        "sampling": "all-post-page-sitemap-urls",
        "evaluator": "deterministic-http-and-inbound-link-topology-v1",
        "acceptance": "all-corpus-http-200-and-replayable-inbound-map-v1",
        "sitemaps": sitemap_urls,
        "timeout_seconds": args.timeout,
        "max_workers": args.workers,
    }
    method_fingerprint = hashlib.sha256(
        json.dumps(method_fields, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    sitemap_records: list[dict[str, Any]] = []
    corpus_urls: list[str] = []
    for sitemap_url in sitemap_urls:
        record, urls = urls_from_sitemap(sitemap_url, args.timeout)
        sitemap_records.append(record)
        corpus_urls.extend(urls)
    corpus_urls = sorted({canonical_url(url) for url in corpus_urls})
    corpus_set = set(corpus_urls)

    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as pool:
        pages = list(pool.map(lambda url: crawl_page(url, args.timeout, host), corpus_urls))
    pages.sort(key=lambda item: item["url"])

    inbound_sources: dict[str, list[str]] = {url: [] for url in corpus_urls}
    for page in pages:
        source = canonical_url(page.get("final_url") or page["url"])
        for target in page.get("internal_links", []):
            target = canonical_url(target)
            if target in corpus_set and source != target:
                inbound_sources[target].append(source)
    inbound_sources = {
        target: sorted(set(sources)) for target, sources in sorted(inbound_sources.items())
    }
    zero_inbound_urls = [url for url, sources in inbound_sources.items() if not sources]
    all_http_200 = bool(pages) and all(page.get("status") == 200 for page in pages)

    payload = {
        "schema_version": "maplab.seo-corpus-audit-receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "public-read-only",
        "site": site,
        "method_fields": method_fields,
        "method_fingerprint": method_fingerprint,
        "sitemaps": sitemap_records,
        "corpus_url_count": len(corpus_urls),
        "corpus_urls_sha256": hashlib.sha256(
            json.dumps(corpus_urls, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "all_http_200": all_http_200,
        "pages": pages,
        "inbound_sources": inbound_sources,
        "zero_inbound_urls": zero_inbound_urls,
        "external_writes": 0,
        "customer_send": 0,
        "private_third_party_egress": 0,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if all_http_200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
