#!/usr/bin/env python3
"""Fail-closed intake gate for MAPLAB case-led WordPress/music work.

The gate prevents a service/category page from being mistaken for a real case.
It is intentionally deterministic and does not call Drive, WordPress, or AI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DRIVE_FOLDER_RE = re.compile(r"^https://drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)$")
DATE_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}$")
VERIFIED_IDENTITY = {
    "verified_existing_receipt",
    "verified_a2_triangulation",
    "verified_private_event_anchor",
}
VERIFIED_OR_SAFE_PUBLIC_NAME = {"verified_public", "public_safe_anonymous"}
VERIFIED_FACT_STATUS = {"verified", "verified_existing_receipt", "waived_private_family"}


def _media_count(case: dict[str, Any]) -> int:
    inventory = case.get("asset_inventory") or {}
    return int(inventory.get("images", 0)) + int(inventory.get("videos", 0))


def validate_case(case: dict[str, Any], level: str) -> list[str]:
    case_id = str(case.get("case_id") or "<missing-case-id>")
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{case_id}: {message}")

    require(case.get("source_kind") == "drive_case", "source_kind must be drive_case")
    require(bool(case.get("internal_label")), "internal_label is required")
    require(bool(DATE_RE.match(str(case.get("event_date") or ""))), "event_date must be YYYY-MM-DD")

    folder_id = str(case.get("drive_folder_id") or "")
    folder_url = str(case.get("drive_folder_url") or "")
    match = DRIVE_FOLDER_RE.match(folder_url)
    require(bool(folder_id), "drive_folder_id is required")
    require(bool(match), "drive_folder_url must be a canonical Drive folder URL")
    if match:
        require(match.group(1) == folder_id, "Drive URL id must equal drive_folder_id")
    require(_media_count(case) > 0, "at least one image or video is required")

    integrity = case.get("source_integrity") or {}
    require(integrity.get("inventory") == "verified_connector_inventory", "connector inventory proof is required")
    if integrity.get("unrelated_private_document_detected"):
        require(
            integrity.get("contamination_action") == "excluded_from_case_facts",
            "unrelated private documents must be explicitly excluded from case facts",
        )

    seo = case.get("seo") or {}
    require(bool(seo.get("cluster")), "SEO cluster is required")
    require(bool(seo.get("delivery_route")), "SEO delivery_route is required")
    require(
        seo.get("keyword_status") in {"final_verified", "candidate_not_final", "withheld_until_identity"},
        "keyword_status must be final_verified, candidate_not_final, or withheld_until_identity",
    )
    if seo.get("keyword_status") == "final_verified":
        require(bool(seo.get("primary_keyword")), "final keyword requires primary_keyword")
        require(case.get("identity_status") in VERIFIED_IDENTITY, "final keyword requires verified case identity")
        require(seo.get("collision_check") == "verified", "final keyword requires live collision check")

    if level == "wp":
        fact_chain = case.get("fact_chain") or {}
        require(case.get("identity_status") in VERIFIED_IDENTITY, "WP stage requires verified case identity")
        require(
            case.get("public_name_status") in VERIFIED_OR_SAFE_PUBLIC_NAME,
            "WP stage requires verified or anonymous public naming",
        )
        for field in ("event_anchor", "quote_or_equivalent", "asset_log", "visual_qa"):
            require(fact_chain.get(field) in VERIFIED_FACT_STATUS, f"WP stage requires {field} proof")
        require(seo.get("collision_check") == "verified", "WP stage requires live SEO collision check")
        require(bool(seo.get("primary_keyword")), "WP stage requires a primary keyword")
        require(bool(case.get("public_safe_title")), "WP stage requires public_safe_title")

    return errors


def validate_registry(payload: dict[str, Any], level: str, case_id: str | None = None) -> list[str]:
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return ["registry: cases must be a non-empty list"]
    selected = [case for case in cases if not case_id or case.get("case_id") == case_id]
    if case_id and not selected:
        return [f"registry: unknown case_id {case_id}"]
    errors: list[str] = []
    seen: set[str] = set()
    for case in selected:
        cid = str(case.get("case_id") or "")
        if cid in seen:
            errors.append(f"{cid}: duplicate case_id")
        seen.add(cid)
        errors.extend(validate_case(case, level))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--level", choices=("intake", "wp"), default="intake")
    parser.add_argument("--case-id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.registry.read_text(encoding="utf-8"))
    errors = validate_registry(payload, args.level, args.case_id)
    report = {
        "ok": not errors,
        "level": args.level,
        "case_id": args.case_id,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print("CASE_FIRST_GATE=FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print("CASE_FIRST_GATE=PASS")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
