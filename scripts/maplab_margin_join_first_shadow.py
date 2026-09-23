#!/usr/bin/env python3
"""Run a bounded join-first shadow pilot for MAPLAB margin-leak evidence.

The worker starts from five deterministic 2026 Orders that already have a
quotation pointer and at least one OrderCharges row.  It then searches the
private local LINE archive using independent date, identity, and exact quote
link anchors.  Only opaque references, anchor counts, evidence status, and
missing codes leave the process.  It never writes Google data, calls a model,
sends a customer message, or emits a leakage amount.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from maplab_margin_google_join_bridge import (  # noqa: E402
    GoogleReadProvider,
    MAIN_SHEET_ID,
)


METHOD_VERSION = "margin-join-first-shadow-v1"
PILOT_SIZE = 5
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
PRIOR_BRIDGE_FINGERPRINT = (
    "8c96645e45090a62ab6d3a19c3b945fb1f24459d6920e5741edee2e04fdf4ff1"
)
CANONICAL_PRIOR_BRIDGE_SHA256 = (
    "c757d2c055b678ee05ba931002ff8732b7f0d5134e041c53eb50b30785e15c4a"
)
PRIOR_BRIDGE_SCHEMA_VERSION = "maplab.margin-leak.google-join-bridge.v1"
RECENT_METHOD_FINGERPRINTS = [
    "7e65e7be6eec8e77bf71866928bcdf616bf0cb81948b473c985e739885422b30",
    "9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17",
    PRIOR_BRIDGE_FINGERPRINT,
]


class JoinFirstShadowError(RuntimeError):
    """The fixed shadow pilot cannot produce a trustworthy receipt."""


class ReadProvider(Protocol):
    api_read_calls: int
    oauth_refresh_calls: int

    def read_named_columns(
        self, sheet_id: str, tab: str, fields: list[str]
    ) -> list[dict[str, str]]: ...


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_private_file(path: Path) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise JoinFirstShadowError("prior_receipt_must_be_absolute_private_file")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise JoinFirstShadowError("prior_receipt_permissions_not_private")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise JoinFirstShadowError("prior_receipt_wrong_owner")


def validate_private_dir(path: Path) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise JoinFirstShadowError("line_archive_must_be_absolute_directory")
    info = path.stat()
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise JoinFirstShadowError("line_archive_permissions_not_private")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise JoinFirstShadowError("line_archive_wrong_owner")


def _normalise(value: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", value)).lower()


def _ref(kind: str, value: str) -> str:
    return f"private://{kind}/{sha256_text(f'{METHOD_VERSION}|{kind}|{value}')}"


def _parse_event_date(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"(20\d{2})\D{0,3}(\d{1,2})\D{0,3}(\d{1,2})", value)
    if not match:
        return None
    year, month, day = (int(item) for item in match.groups())
    try:
        datetime(year, month, day)
    except ValueError:
        return None
    return year, month, day


def _date_variants(value: str) -> set[str]:
    parsed = _parse_event_date(value)
    if not parsed:
        return set()
    year, month, day = parsed
    return {
        f"{year}-{month:02d}-{day:02d}",
        f"{year}/{month:02d}/{day:02d}",
        f"{year}/{month}/{day}",
        f"{year}年{month}月{day}日",
    }


def _parse_sheet_id(value: str) -> str:
    for pattern in (
        r"/spreadsheets/d/([A-Za-z0-9_-]{20,})",
        r"[?&]id=([A-Za-z0-9_-]{20,})",
    ):
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    return ""


GENERIC_IDENTITY_VALUES = {
    _normalise(value)
    for value in (
        "外燴",
        "活動",
        "企業",
        "公司",
        "茶會",
        "餐會",
        "婚禮",
        "生日",
        "派對",
        "開幕",
        "週歲",
        "抓周",
        "先生",
        "小姐",
        "客戶",
    )
}


def _identity_tokens(row: dict[str, str]) -> list[str]:
    tokens: set[str] = set()
    for field in ("company_name", "contact_person", "event_name"):
        raw = str(row.get(field, "")).strip()
        token = _normalise(raw)
        if not token:
            continue
        for suffix in ("股份有限公司", "有限公司", "公司", "先生", "小姐"):
            normal_suffix = _normalise(suffix)
            if token.endswith(normal_suffix) and len(token) > len(normal_suffix):
                token = token[: -len(normal_suffix)]
                break
        generic_base = re.sub(r"[a-z0-9]+$", "", token)
        if (
            token in GENERIC_IDENTITY_VALUES
            or generic_base in GENERIC_IDENTITY_VALUES
            or token.isdigit()
        ):
            continue
        quote_id = _parse_sheet_id(str(row.get("client_sheet_url", "")))
        forbidden_tokens = {_normalise(quote_id)} if quote_id else set()
        parsed_date = _parse_event_date(str(row.get("event_date", "")))
        if parsed_date:
            year, month, day = parsed_date
            forbidden_tokens.add(f"{year:04d}{month:02d}{day:02d}")
        if token in forbidden_tokens:
            continue
        chinese_count = len(re.findall(r"[\u4e00-\u9fff]", token))
        alphanumeric_count = len(re.findall(r"[a-z0-9]", token))
        if chinese_count >= 2 or alphanumeric_count >= 4:
            tokens.add(token)
    return sorted(tokens)


def _select_orders(
    order_rows: list[dict[str, str]],
    charge_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    charges_by_order: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in charge_rows:
        order_id = str(row.get("order_id", "")).strip()
        if order_id:
            charges_by_order[order_id].append(row)

    eligible_by_order: dict[str, dict[str, Any]] = {}
    for row in order_rows:
        order_id = str(row.get("order_id", "")).strip()
        client_sheet_url = str(row.get("client_sheet_url", "")).strip()
        event_date = str(row.get("event_date", "")).strip()
        parsed_date = _parse_event_date(event_date)
        if (
            not order_id
            or not client_sheet_url
            or not parsed_date
            or parsed_date[0] != 2026
            or not charges_by_order.get(order_id)
        ):
            continue
        eligible_by_order.setdefault(
            order_id,
            {
                "order_id": order_id,
                "event_date": event_date,
                "company_name": str(row.get("company_name", "")),
                "contact_person": str(row.get("contact_person", "")),
                "event_name": str(row.get("event_name", "")),
                "client_sheet_url": client_sheet_url,
                "quote_id": _parse_sheet_id(client_sheet_url),
                "charges": charges_by_order[order_id],
            },
        )
    ordered = sorted(
        eligible_by_order.values(),
        key=lambda row: sha256_text(f"{METHOD_VERSION}|{row['order_id']}"),
    )
    if len(ordered) < PILOT_SIZE:
        raise JoinFirstShadowError("insufficient_evidence_rich_2026_orders")
    return ordered[:PILOT_SIZE], len(ordered)


def _read_line_search_document(path: Path) -> tuple[str, str]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        rows = list(csv.reader(handle))
    header_index = next(
        (index for index, row in enumerate(rows) if row and row[0] == "傳送者類型"),
        None,
    )
    if header_index is None:
        return "", ""
    private_parts = [path.stem.split("_", 3)[-1]]
    for row in rows[header_index + 1 :]:
        if len(row) < 5 or row[0] not in {"User", "Account"}:
            continue
        private_parts.extend((row[1], row[2], row[3], row[4]))
    raw_haystack = "\n".join(private_parts).lower()
    return raw_haystack, _normalise(raw_haystack)


def _scan_line_archive(
    selected_orders: list[dict[str, Any]], raw_source_dir: Path
) -> tuple[dict[str, list[dict[str, Any]]], int, str, list[str]]:
    validate_private_dir(raw_source_dir)
    paths = sorted(raw_source_dir.glob("*.csv"))
    if not paths:
        raise JoinFirstShadowError("line_archive_has_no_csv")
    matches: dict[str, list[dict[str, Any]]] = {
        order["order_id"]: [] for order in selected_orders
    }
    manifest_rows = []
    private_filenames = []
    for path in paths:
        manifest_rows.append(f"{sha256_text(path.name)}|{sha256_file(path)}")
        raw_haystack, normalised_haystack = _read_line_search_document(path)
        if not raw_haystack:
            continue
        for order in selected_orders:
            anchor_types = []
            if any(
                variant.lower() in raw_haystack
                for variant in _date_variants(order["event_date"])
            ):
                anchor_types.append("event_date_exact")
            if any(
                token in normalised_haystack for token in _identity_tokens(order)
            ):
                anchor_types.append("identity_exact")
            quote_id = order.get("quote_id", "")
            if quote_id and quote_id.lower() in raw_haystack:
                anchor_types.append("quote_link_exact")
            if len(anchor_types) < 2:
                continue
            private_filenames.append(path.name)
            matches[order["order_id"]].append(
                {
                    "conversation_ref": _ref("line-conversation", path.name),
                    "anchor_count": len(anchor_types),
                    "anchor_types": sorted(anchor_types),
                }
            )
    return (
        matches,
        len(paths),
        sha256_text("\n".join(manifest_rows)),
        private_filenames,
    )


def _private_values(selected_orders: list[dict[str, Any]]) -> list[str]:
    values = []
    for order in selected_orders:
        for field in (
            "order_id",
            "event_date",
            "company_name",
            "contact_person",
            "event_name",
            "client_sheet_url",
            "quote_id",
        ):
            value = str(order.get(field, "")).strip()
            if value:
                values.append(value)
        for row in order["charges"]:
            for field in ("order_id", "description", "charge_type", "amount"):
                value = str(row.get(field, "")).strip()
                if value:
                    values.append(value)
    return values


def _assert_no_private_values(
    payload: dict[str, Any], private_values: list[str], private_filenames: list[str]
) -> int:
    serialised = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    checked = 0
    for value in private_values + private_filenames:
        candidate = value.strip()
        if len(candidate) < 2 or candidate.isdigit():
            continue
        checked += 1
        if candidate in serialised:
            raise JoinFirstShadowError("private_value_leak_detected")
    return checked


def build_join_first_receipt(
    prior_bridge_path: Path,
    raw_source_dir: Path,
    provider: ReadProvider,
    *,
    expected_prior_sha256: str,
    main_sheet_id: str = MAIN_SHEET_ID,
) -> dict[str, Any]:
    validate_private_file(prior_bridge_path)
    actual_prior_sha256 = sha256_file(prior_bridge_path)
    if actual_prior_sha256 != expected_prior_sha256:
        raise JoinFirstShadowError("prior_bridge_sha256_mismatch")
    prior = json.loads(prior_bridge_path.read_text(encoding="utf-8"))
    if (
        prior.get("schema_version") != PRIOR_BRIDGE_SCHEMA_VERSION
        or prior.get("data_class") != "private-local-google-read-receipt"
        or prior.get("method_contract", {}).get("fingerprint")
        != PRIOR_BRIDGE_FINGERPRINT
        or prior.get("stable_identity_joins") != 0
    ):
        raise JoinFirstShadowError("expected_zero_join_prior_bridge_required")
    prior_privacy = prior.get("privacy", {})
    required_false_privacy = (
        "contains_raw_text",
        "contains_customer_identifiers",
        "contains_source_conversation_ids",
        "contains_customer_bearing_paths",
        "contains_raw_google_ids",
        "new_third_party_private_data_egress",
        "oauth_token_writes",
        "model_calls",
        "customer_send",
        "google_writes",
        "live_price_write",
    )
    if any(prior_privacy.get(field) not in (False, 0) for field in required_false_privacy):
        raise JoinFirstShadowError("prior_bridge_privacy_assertions_invalid")

    order_fields = [
        "order_id",
        "event_date",
        "company_name",
        "contact_person",
        "event_name",
        "client_sheet_url",
    ]
    charge_fields = ["order_id", "description", "charge_type", "amount"]
    order_rows = provider.read_named_columns(main_sheet_id, "Orders", order_fields)
    charge_rows = provider.read_named_columns(
        main_sheet_id, "OrderCharges", charge_fields
    )
    selected_orders, eligible_order_count = _select_orders(order_rows, charge_rows)
    (
        matches_by_order,
        archive_file_count,
        archive_manifest_sha256,
        private_filenames,
    ) = _scan_line_archive(selected_orders, raw_source_dir)

    samples = []
    missing_counts: Counter[str] = Counter()
    stable_identity_joins = 0
    no_candidate_count = 0
    ambiguous_candidate_count = 0
    for order in selected_orders:
        matches = matches_by_order[order["order_id"]]
        stable_match = matches[0] if len(matches) == 1 else None
        identity_chain_verified = stable_match is not None
        if identity_chain_verified:
            stable_identity_joins += 1
        missing_codes = [
            "BASELINE_SCOPE_UNVERIFIED_QUOTE_POINTER_NOT_SCOPE_CONTENT",
            "ACTUAL_DELIVERY_UNVERIFIED_NO_ASSET_JOIN",
            "INCREMENTAL_COST_UNVERIFIED_NO_COST_LEDGER",
            "CHARGED_FEE_UNVERIFIED_CHARGES_NOT_REQUEST_SCOPE_MAPPED",
        ]
        if not matches:
            no_candidate_count += 1
            missing_codes.append("NO_TWO_ANCHOR_LINE_LINK")
        elif len(matches) > 1:
            ambiguous_candidate_count += 1
            missing_codes.append("AMBIGUOUS_TWO_ANCHOR_LINE_LINK")
        missing_counts.update(missing_codes)
        charge_refs = sorted(
            {
                _ref(
                    "charge-row",
                    "|".join(
                        str(row.get(field, ""))
                        for field in (
                            "order_id",
                            "description",
                            "charge_type",
                            "amount",
                        )
                    ),
                )
                for row in order["charges"]
            }
        )
        samples.append(
            {
                "order_ref": _ref("order", order["order_id"]),
                "quote_ref": _ref(
                    "quote", order.get("quote_id") or order["client_sheet_url"]
                ),
                "charge_row_refs": charge_refs,
                "charge_row_count": len(order["charges"]),
                "identity_token_count": len(_identity_tokens(order)),
                "quote_id_parseable": bool(order.get("quote_id")),
                "two_anchor_candidate_count": len(matches),
                "identity_chain_verified": identity_chain_verified,
                "line_conversation_ref": (
                    stable_match["conversation_ref"] if stable_match else None
                ),
                "anchor_count": stable_match["anchor_count"] if stable_match else 0,
                "anchor_types": stable_match["anchor_types"] if stable_match else [],
                "evidence_pillars": {
                    "baseline_scope": "unverified",
                    "actual_delivery": "unverified",
                    "incremental_cost": "unverified",
                    "charged_fee": "unverified",
                },
                "four_pillar_confirmed": False,
                "decision_label": "insufficient_evidence",
                "missing_evidence_codes": missing_codes,
            }
        )

    method_contract = {
        "method_version": METHOD_VERSION,
        "hypothesis": (
            "Starting from 2026 orders that already have quote and charge references will "
            "recover at least one unique LINE link using two independent anchors, or "
            "falsify archive backfill as the repair point."
        ),
        "changed_variable": (
            "reverse join direction from random LINE candidates to evidence-rich Orders; "
            "use exact date, identity, and quote-link anchors only"
        ),
        "fixed_holdout": {
            "total": PILOT_SIZE,
            "selection": "first five by sha256(method_version|order_id) from eligible 2026 orders",
            "prior_bridge_sha256": actual_prior_sha256,
        },
        "expected_delta": (
            "at least one unique order-to-LINE-to-quote-to-charge identity chain, or a "
            "verified stop and move to intake-time case_id capture"
        ),
        "stop_loss": (
            "stop after five orders; require at least two independent exact anchors; do "
            "not widen fuzzy matching; no model, Google write, token write, customer send, "
            "raw identifier output, price change, or leakage amount"
        ),
        "adapter": "maplab-margin-leak-auditor/join-first-local-shadow",
        "sampling": "deterministic evidence-rich 2026 Orders holdout",
        "evaluator": (
            "stable only when exactly one LINE conversation has at least two of exact "
            "event-date, identity, or quote-link anchors"
        ),
        "acceptance": (
            "five opaque samples, explicit anchor and missing-evidence status, zero raw "
            "identifiers, and a deterministic next repair point"
        ),
    }
    method_contract["fingerprint"] = sha256_text(
        json.dumps(
            method_contract,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    selection_refs = sorted(sample["order_ref"] for sample in samples)
    payload = {
        "schema_version": "maplab.margin-leak.join-first-shadow.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-shadow-receipt",
        "plateau_review": {
            "recent_method_fingerprints": RECENT_METHOD_FINGERPRINTS,
            "same_method_consecutive_no_improvement": 0,
            "decision": "new_join_direction_single_variable_method_allowed",
        },
        "method_contract": method_contract,
        "privacy": {
            "contains_raw_text": False,
            "contains_customer_identifiers": False,
            "contains_source_conversation_ids": False,
            "contains_customer_bearing_paths": False,
            "contains_raw_google_ids": False,
            "new_third_party_private_data_egress": False,
            "google_source_reads": provider.api_read_calls,
            "oauth_refresh_calls_in_memory": provider.oauth_refresh_calls,
            "oauth_token_writes": 0,
            "model_calls": 0,
            "customer_send": False,
            "google_writes": 0,
            "live_price_write": False,
            "private_value_leak_count": 0,
        },
        "source_receipts": {
            "prior_bridge_sha256": actual_prior_sha256,
            "main_sheet_ref": _ref("sheet", main_sheet_id),
            "live_minimal_row_counts": {
                "Orders": len(order_rows),
                "OrderCharges": len(charge_rows),
                "eligible_2026_orders": eligible_order_count,
            },
            "line_archive_ref": _ref("line-archive", str(raw_source_dir)),
            "line_archive_file_count": archive_file_count,
            "line_archive_manifest_sha256": archive_manifest_sha256,
            "selection_manifest_sha256": sha256_text("\n".join(selection_refs)),
        },
        "sample_count": len(samples),
        "unique_order_refs": len({sample["order_ref"] for sample in samples}),
        "stable_identity_joins": stable_identity_joins,
        "orders_with_no_two_anchor_candidates": no_candidate_count,
        "orders_with_ambiguous_two_anchor_candidates": ambiguous_candidate_count,
        "all_five_lack_two_anchor_candidates": no_candidate_count == PILOT_SIZE,
        "all_five_lack_unique_two_anchor_link": stable_identity_joins == 0,
        "four_pillar_confirmed": 0,
        "confirmed_leakage_amount": 0,
        "decision_counts": {"insufficient_evidence": len(samples)},
        "missing_evidence_code_counts": dict(sorted(missing_counts.items())),
        "next_repair_point": (
            "intake_time_case_id_capture"
            if stable_identity_joins == 0
            else "delivery_and_incremental_cost_evidence_for_stable_chains"
        ),
        "interpretation": (
            "The pilot proves identity linkage only. Quote and charge references do not "
            "prove baseline scope, delivery, incremental cost, or an omitted fee. "
            "Confirmed leakage remains zero."
        ),
        "samples": samples,
    }
    checked_count = _assert_no_private_values(
        payload, _private_values(selected_orders), private_filenames
    )
    payload["privacy"]["private_values_checked"] = checked_count
    return payload


def write_private_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.is_absolute():
        raise JoinFirstShadowError("output_path_must_be_absolute")
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(PRIVATE_FILE_MODE)
    os.replace(temporary, path)
    path.chmod(PRIVATE_FILE_MODE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-bridge", required=True)
    parser.add_argument("--raw-source-dir", required=True)
    parser.add_argument("--google-token", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prior_bridge = Path(args.prior_bridge).expanduser().resolve()
    raw_source_dir = Path(args.raw_source_dir).expanduser().resolve()
    google_token = Path(args.google_token).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    provider = GoogleReadProvider(google_token)
    payload = build_join_first_receipt(
        prior_bridge,
        raw_source_dir,
        provider,
        expected_prior_sha256=CANONICAL_PRIOR_BRIDGE_SHA256,
    )
    write_private_json(output, payload)
    artifact_sha256 = sha256_file(output)
    print(
        json.dumps(
            {
                "status": "ok",
                "sample_count": payload["sample_count"],
                "stable_identity_joins": payload["stable_identity_joins"],
                "all_five_lack_unique_two_anchor_link": payload[
                    "all_five_lack_unique_two_anchor_link"
                ],
                "confirmed_leakage_amount": 0,
                "google_writes": 0,
                "customer_send": False,
                "artifact_sha256": artifact_sha256,
                "output_ref": _ref("shadow-receipt", str(output)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
