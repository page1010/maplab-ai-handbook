#!/usr/bin/env python3
"""Build the fixed-three, local-only MAPLAB margin evidence packet.

The worker freezes three already-calibrated candidates, re-verifies the exact
request row and source conversation locally, and looks only for exact opaque
join anchors. It never copies message text, customer labels, source paths,
URLs, amounts, or provider identifiers into the packet. Text cues and local
Google pointer metadata are locators only; they never prove quote scope,
delivery, incremental cost, or a charged fee.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


METHOD_VERSION = "margin-fixed-three-four-pillar-packet-v1"
PILOT_SIZE = 3
EXPECTED_TRUE_CANDIDATES = 18
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
SHEET_ID_RE = re.compile(
    r"https?://docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]{20,})",
    re.IGNORECASE,
)
DRIVE_FILE_ID_RE = re.compile(
    r"https?://drive\.google\.com/(?:file/d/|open\?id=)([A-Za-z0-9_-]{20,})",
    re.IGNORECASE,
)
QUOTE_ID_RE = re.compile(r"(?<![A-Za-z0-9])Q\d{8,}(?![A-Za-z0-9])", re.I)
ORDER_ID_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:ORD|ORDER)[-_]?[A-Za-z0-9]{6,}(?![A-Za-z0-9])",
    re.I,
)
AMOUNT_RE = re.compile(r"(?<!\d)(?:NT\$|\$)?\s*\d{3,6}(?!\d)", re.I)
DELIVERY_CUE_RE = re.compile(r"照片|圖片|相片|影片|檔案|附件|已傳送", re.I)
COST_CUE_RE = re.compile(
    r"成本|工時|加班|停車費|搬運費|清潔費|垃圾|廚餘|人員費|服務費",
    re.I,
)
CHARGE_CUE_RE = re.compile(r"加價|另計|另外收|費用|報價|金額|收費", re.I)


class FixedThreeError(RuntimeError):
    """The fixed-three evidence contract could not be satisfied."""


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


def validate_private_file(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise FixedThreeError(f"{label}_must_be_absolute_regular_file")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise FixedThreeError(f"{label}_permissions_not_private")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise FixedThreeError(f"{label}_wrong_owner")


def _selection_key(candidate_hash: str) -> str:
    return sha256_text(f"{METHOD_VERSION}|{candidate_hash}")


def _eligible_set_digest(candidate_hashes: list[str]) -> str:
    # Exact serialization: lexicographic hashes, one per line, including final LF.
    return sha256_text("".join(f"{value}\n" for value in sorted(candidate_hashes)))


def select_samples(calibration: dict) -> tuple[list[dict], str]:
    if calibration.get("schema_version") != "maplab.margin-leak.calibration.v1":
        raise FixedThreeError("calibration_schema_mismatch")
    contract = calibration.get("method_contract")
    if not isinstance(contract, dict) or contract.get("method_version") != "margin-calibration-v1":
        raise FixedThreeError("calibration_method_mismatch")
    candidates = []
    for sample in calibration.get("samples", []):
        if not isinstance(sample, dict) or sample.get("label") != "true_candidate":
            continue
        candidate_hash = sample.get("candidate_hash")
        category = sample.get("category")
        if not isinstance(candidate_hash, str) or not HASH_RE.fullmatch(candidate_hash):
            raise FixedThreeError("eligible_candidate_hash_invalid")
        if not isinstance(category, str) or not category:
            raise FixedThreeError("eligible_candidate_category_invalid")
        candidates.append(sample)
    hashes = [sample["candidate_hash"] for sample in candidates]
    if len(candidates) != EXPECTED_TRUE_CANDIDATES:
        raise FixedThreeError("true_candidate_count_mismatch")
    if len(set(hashes)) != EXPECTED_TRUE_CANDIDATES:
        raise FixedThreeError("duplicate_true_candidate_hash")
    ordered = sorted(candidates, key=lambda item: _selection_key(item["candidate_hash"]))
    return ordered[:PILOT_SIZE], _eligible_set_digest(hashes)


def _parse_evidence_locator(sample: dict) -> tuple[Path, int]:
    locator = sample.get("evidence_path")
    if not isinstance(locator, str) or "#L" not in locator:
        raise FixedThreeError("request_evidence_locator_invalid")
    raw_path, raw_line = locator.rsplit("#L", 1)
    path = Path(raw_path)
    try:
        line_number = int(raw_line)
    except ValueError as error:
        raise FixedThreeError("request_evidence_line_invalid") from error
    if line_number < 1:
        raise FixedThreeError("request_evidence_line_invalid")
    return path, line_number


def _read_request_row(
    sample: dict, allowed_evidence_paths: set[Path]
) -> tuple[dict, dict]:
    path, line_number = _parse_evidence_locator(sample)
    if path not in allowed_evidence_paths:
        raise FixedThreeError("request_evidence_source_not_allowlisted")
    validate_private_file(path, "request_evidence")
    lines = path.read_text(encoding="utf-8").splitlines()
    if line_number > len(lines):
        raise FixedThreeError("request_evidence_line_missing")
    line = lines[line_number - 1]
    actual_sha256 = sha256_text(line)
    if actual_sha256 != sample.get("evidence_sha256"):
        raise FixedThreeError("request_evidence_sha256_mismatch")
    try:
        row = json.loads(line)
    except json.JSONDecodeError as error:
        raise FixedThreeError("request_evidence_json_invalid") from error
    if not isinstance(row, dict):
        raise FixedThreeError("request_evidence_row_invalid")
    conversation_id = row.get("conversation_id")
    if not isinstance(conversation_id, str) or not conversation_id:
        raise FixedThreeError("request_conversation_id_invalid")
    expected_candidate = sha256_text(f"{conversation_id}|{sample['category']}")
    if expected_candidate != sample["candidate_hash"]:
        raise FixedThreeError("request_candidate_relation_mismatch")
    reason_codes = sample.get("reason_codes")
    if not isinstance(reason_codes, list) or not {
        "direct_request_cue",
        "category_specific_cost_cue",
    }.issubset(reason_codes):
        raise FixedThreeError("request_reason_codes_invalid")
    return row, {
        "status": "VERIFIED_REQUEST_ROW_HASH",
        "evidence_row_sha256": actual_sha256,
        "evidence_file_sha256": sha256_file(path),
        "relation": "candidate_hash=sha256(conversation_id|category)",
    }


def _raw_source_index(raw_source_dir: Path) -> tuple[dict[str, list[Path]], str]:
    if not raw_source_dir.is_absolute() or raw_source_dir.is_symlink() or not raw_source_dir.is_dir():
        raise FixedThreeError("raw_source_dir_must_be_absolute_directory")
    index: dict[str, list[Path]] = {}
    manifest = []
    for path in sorted(raw_source_dir.glob("*.csv")):
        if path.is_symlink() or not path.is_file():
            raise FixedThreeError("raw_source_entry_not_regular")
        if path.stat().st_nlink != 1:
            raise FixedThreeError("raw_source_entry_hardlinked")
        conversation_id = hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:16]
        index.setdefault(conversation_id, []).append(path)
        manifest.append(f"{conversation_id}|{path.stat().st_size}")
    if not index:
        raise FixedThreeError("raw_source_dir_has_no_csv")
    return index, sha256_text("\n".join(manifest))


def _read_message_text(path: Path) -> str:
    messages = []
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) >= 5 and row[0] in {"User", "Account"}:
                messages.append(row[4])
    return "\n".join(messages)


def _pointer_index(
    roots: list[Path], wanted_ids: set[str]
) -> tuple[Counter[str], int, str | None, str]:
    ids: Counter[str] = Counter()
    manifest = []
    if not wanted_ids:
        return ids, 0, None, "NOT_REQUIRED_NO_EXACT_SHEET_ANCHOR"
    for root in roots:
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise FixedThreeError("quote_pointer_root_must_be_absolute_directory")
        for path in sorted(root.rglob("*.gsheet")):
            if path.is_symlink() or not path.is_file():
                raise FixedThreeError("quote_pointer_entry_not_regular")
            try:
                text = path.read_text(encoding="utf-8", errors="strict")
            except (OSError, UnicodeError) as error:
                raise FixedThreeError("quote_pointer_scan_incomplete") from error
            found = set(SHEET_ID_RE.findall(text))
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                doc_id = payload.get("doc_id") or payload.get("id")
                if isinstance(doc_id, str) and len(doc_id) >= 20:
                    found.add(doc_id)
            for value in found & wanted_ids:
                ids[value] += 1
            manifest.append(
                f"{sha256_text(str(path.resolve()))}|{path.stat().st_size}|{sha256_file(path)}"
            )
    return (
        ids,
        len(manifest),
        sha256_text("\n".join(manifest)) if manifest else None,
        "COMPLETE_EXACT_ID_LOOKUP",
    )


def _opaque_counts(text: str, pointer_ids: Counter[str]) -> dict[str, int]:
    sheet_ids = SHEET_ID_RE.findall(text)
    quote_ids = QUOTE_ID_RE.findall(text)
    asset_ids = DRIVE_FILE_ID_RE.findall(text)
    order_ids = ORDER_ID_RE.findall(text)
    return {
        "exact_sheet_anchor_count": len(set(sheet_ids)),
        "unique_local_pointer_match_count": sum(
            1 for value in set(sheet_ids) if pointer_ids.get(value) == 1
        ),
        "ambiguous_local_pointer_match_count": sum(
            1 for value in set(sheet_ids) if pointer_ids.get(value, 0) > 1
        ),
        "exact_quote_id_count": len(set(quote_ids)),
        "exact_asset_anchor_count": len(set(asset_ids)),
        "exact_order_anchor_count": len(set(order_ids)),
        "delivery_cue_count": len(DELIVERY_CUE_RE.findall(text)),
        "cost_cue_count": len(COST_CUE_RE.findall(text)),
        "charge_cue_count": len(CHARGE_CUE_RE.findall(text)),
        "amount_token_count": len(AMOUNT_RE.findall(text)),
    }


def _build_sample(
    sample: dict,
    row: dict,
    request_receipt: dict,
    raw_index: dict[str, list[Path]],
    pointer_ids: Counter[str],
) -> dict:
    conversation_id = row["conversation_id"]
    raw_matches = raw_index.get(conversation_id, [])
    raw_path = raw_matches[0] if len(raw_matches) == 1 else None
    text = _read_message_text(raw_path) if raw_path is not None else ""
    counts = _opaque_counts(text, pointer_ids)
    missing = [
        "BASELINE_SCOPE_UNVERIFIED_NO_EXACT_QUOTE_CONTENT_JOIN",
        "ACTUAL_DELIVERY_UNVERIFIED_NO_STABLE_ASSET_JOIN",
        "INCREMENTAL_COST_UNVERIFIED_NO_COST_LEDGER_JOIN",
        "CHARGED_FEE_UNVERIFIED_NO_EXACT_ORDER_JOIN",
        "CHARGED_FEE_UNVERIFIED_ORDERCHARGES_SEMANTICS",
        "NO_STABLE_CASE_QUOTE_CHARGE_ASSET_JOIN_KEY",
    ]
    if raw_path is None:
        missing.insert(0, "SOURCE_CONVERSATION_UNVERIFIED_RESOLUTION_COUNT")
        source_receipt = {
            "status": "UNVERIFIED_SOURCE_RESOLUTION_COUNT",
            "resolution_count": len(raw_matches),
            "source_file_sha256": None,
            "source_ref": None,
        }
    else:
        source_sha256 = sha256_file(raw_path)
        source_receipt = {
            "status": "VERIFIED_LOCAL_SOURCE_HASH",
            "resolution_count": 1,
            "source_file_sha256": source_sha256,
            "source_ref": sha256_text(
                f"{METHOD_VERSION}|{sample['candidate_hash']}|{source_sha256}"
            ),
        }
    return {
        "candidate_hash": sample["candidate_hash"],
        "category": sample["category"],
        "selection_key": _selection_key(sample["candidate_hash"]),
        "request": request_receipt,
        "source_conversation": source_receipt,
        "baseline_scope": {
            "status": "UNVERIFIED",
            "exact_sheet_anchor_count": counts["exact_sheet_anchor_count"],
            "exact_quote_id_count": counts["exact_quote_id_count"],
            "unique_local_pointer_match_count": counts[
                "unique_local_pointer_match_count"
            ],
            "ambiguous_local_pointer_match_count": counts[
                "ambiguous_local_pointer_match_count"
            ],
            "note_code": "POINTER_OR_TEXT_IS_NOT_QUOTE_CONTENT",
        },
        "actual_delivery": {
            "status": "UNVERIFIED",
            "exact_asset_anchor_count": counts["exact_asset_anchor_count"],
            "delivery_cue_count": counts["delivery_cue_count"],
            "note_code": "MESSAGE_CUE_IS_NOT_ASSET_READBACK",
        },
        "incremental_cost": {
            "status": "UNVERIFIED",
            "cost_cue_count": counts["cost_cue_count"],
            "amount_token_count": counts["amount_token_count"],
            "note_code": "TEXT_AMOUNT_IS_NOT_INCREMENTAL_COST_LEDGER",
        },
        "charged_fee": {
            "status": "UNVERIFIED",
            "exact_order_anchor_count": counts["exact_order_anchor_count"],
            "charge_cue_count": counts["charge_cue_count"],
            "note_code": "ORDERCHARGES_ROW_REQUIRES_AUTHORITATIVE_SEMANTICS",
        },
        "four_pillar_verified": False,
        "decision_label": "INSUFFICIENT_EVIDENCE",
        "missing_evidence_codes": missing,
    }


def _validate_calibration_contract(
    calibration: dict, expected_fingerprint: str
) -> tuple[set[Path], str]:
    if not HASH_RE.fullmatch(expected_fingerprint):
        raise FixedThreeError("expected_calibration_fingerprint_invalid")
    contract = calibration.get("method_contract")
    if not isinstance(contract, dict):
        raise FixedThreeError("calibration_method_contract_invalid")
    actual_fingerprint = contract.get("fingerprint")
    body = dict(contract)
    body.pop("fingerprint", None)
    recomputed = sha256_text(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    if actual_fingerprint != expected_fingerprint or recomputed != expected_fingerprint:
        raise FixedThreeError("calibration_fingerprint_mismatch")
    samples = calibration.get("samples")
    if not isinstance(samples, list) or len(samples) != 50:
        raise FixedThreeError("calibration_sample_count_mismatch")
    all_hashes = [sample.get("candidate_hash") for sample in samples if isinstance(sample, dict)]
    if len(all_hashes) != 50 or len(set(all_hashes)) != 50:
        raise FixedThreeError("calibration_all_candidate_hashes_invalid")
    if calibration.get("sample_count") != 50 or calibration.get("unique_candidate_hashes") != 50:
        raise FixedThreeError("calibration_summary_count_mismatch")

    source_receipts = calibration.get("source_receipts")
    if not isinstance(source_receipts, list) or len(source_receipts) != 2:
        raise FixedThreeError("calibration_source_receipts_invalid")
    allowed_paths: set[Path] = set()
    source_manifest = []
    for item in source_receipts:
        if not isinstance(item, dict):
            raise FixedThreeError("calibration_source_receipt_invalid")
        path_value = item.get("path")
        expected_sha = item.get("sha256")
        if not isinstance(path_value, str) or not isinstance(expected_sha, str) or not HASH_RE.fullmatch(expected_sha):
            raise FixedThreeError("calibration_source_receipt_invalid")
        path = Path(path_value)
        validate_private_file(path, "calibration_source")
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            raise FixedThreeError("calibration_source_sha256_mismatch")
        allowed_paths.add(path)
        source_manifest.append(expected_sha)
    return allowed_paths, sha256_text("\n".join(sorted(source_manifest)))


def build_packet(
    calibration_path: Path,
    raw_source_dir: Path,
    *,
    expected_calibration_sha256: str,
    expected_calibration_fingerprint: str,
    quote_pointer_roots: list[Path] | None = None,
    attempt_before: int,
) -> dict:
    validate_private_file(calibration_path, "calibration")
    if not HASH_RE.fullmatch(expected_calibration_sha256):
        raise FixedThreeError("expected_calibration_sha256_invalid")
    actual_calibration_sha256 = sha256_file(calibration_path)
    if actual_calibration_sha256 != expected_calibration_sha256:
        raise FixedThreeError("calibration_sha256_mismatch")
    if not isinstance(attempt_before, int) or isinstance(attempt_before, bool) or attempt_before < 0:
        raise FixedThreeError("attempt_before_invalid")

    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    allowed_evidence_paths, calibration_source_manifest_sha256 = (
        _validate_calibration_contract(calibration, expected_calibration_fingerprint)
    )
    selected, eligible_digest = select_samples(calibration)
    raw_index, raw_manifest_sha256 = _raw_source_index(raw_source_dir)

    wanted_sheet_ids: set[str] = set()
    for sample in selected:
        path, line_number = _parse_evidence_locator(sample)
        line = path.read_text(encoding="utf-8").splitlines()[line_number - 1]
        row = json.loads(line)
        matches = raw_index.get(row.get("conversation_id"), [])
        if len(matches) == 1:
            wanted_sheet_ids.update(SHEET_ID_RE.findall(_read_message_text(matches[0])))
    (
        pointer_ids,
        pointer_files_read,
        pointer_manifest_sha256,
        pointer_scan_status,
    ) = _pointer_index(quote_pointer_roots or [], wanted_sheet_ids)

    packets = []
    for sample in selected:
        row, request_receipt = _read_request_row(sample, allowed_evidence_paths)
        packets.append(
            _build_sample(sample, row, request_receipt, raw_index, pointer_ids)
        )

    method_contract = {
        "method_version": METHOD_VERSION,
        "hypothesis": (
            "Candidate-specific exact anchors may recover at least one complete historical "
            "request-to-quote-to-delivery-to-cost-to-charge chain."
        ),
        "changed_variable": (
            "freeze three candidates, re-read exact request/source hashes, and accept only "
            "opaque exact joins; no name, date, keyword, or fuzzy identity inference"
        ),
        "fixed_holdout": {
            "eligible_count": EXPECTED_TRUE_CANDIDATES,
            "selected_count": PILOT_SIZE,
            "eligible_set_digest_serialization": "sorted candidate hashes, LF after every hash",
            "eligible_set_digest": eligible_digest,
            "selected_candidate_hashes": [item["candidate_hash"] for item in packets],
        },
        "expected_delta": "at least one owner-reviewable four-pillar case packet",
        "stop_loss": (
            "stop after exactly three; if zero verify, stop historical joining and route "
            "prospective case-id live capture to Owner review"
        ),
        "adapter": "maplab-margin-fixed-three-local-worker",
        "sampling": "sha256(method_version|candidate_hash), ascending",
        "evaluator": (
            "request row plus baseline quote content, delivery asset, incremental cost, "
            "and authoritative charged-fee evidence; every join exact and unique"
        ),
        "acceptance": (
            "three frozen candidates, exact source readback, explicit missing codes, no "
            "private path/text output, and no inferred leakage without all gates"
        ),
    }
    method_contract["fingerprint"] = sha256_text(
        json.dumps(method_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )

    verified = sum(bool(item["four_pillar_verified"]) for item in packets)
    missing_counts = Counter(
        code for item in packets for code in item["missing_evidence_codes"]
    )
    decision = (
        "STOP_HISTORICAL_JOIN__OWNER_REVIEW_PROSPECTIVE_CAPTURE"
        if verified == 0
        else "OWNER_REVIEW_CONFIRMED_CASE_PACKET"
    )
    payload = {
        "schema_version": "maplab.margin-leak.fixed-three-packet.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-evidence-packet",
        "method_contract": method_contract,
        "source_receipts": {
            "calibration_sha256": actual_calibration_sha256,
            "calibration_fingerprint": expected_calibration_fingerprint,
            "calibration_source_manifest_sha256": calibration_source_manifest_sha256,
            "raw_source_file_count": len(raw_index),
            "raw_source_manifest_sha256": raw_manifest_sha256,
            "local_quote_pointer_files_read": pointer_files_read,
            "local_quote_pointer_manifest_sha256": pointer_manifest_sha256,
            "local_quote_pointer_scan_status": pointer_scan_status,
            "ordercharges_authoritative_writer": "UNRESOLVED",
            "ordercharges_semantics": "UNRESOLVED_MIXED_CHARGE_COST_DISCOUNT_NOTE",
        },
        "privacy": {
            "contains_raw_text": False,
            "contains_customer_identifiers": False,
            "contains_source_conversation_ids": False,
            "contains_customer_bearing_paths": False,
            "contains_raw_urls_or_provider_ids": False,
            "network_calls": 0,
            "model_calls": 0,
            "third_party_private_egress": 0,
            "customer_send": False,
            "google_write": False,
            "live_price_write": False,
            "backup_or_permission_write": False,
        },
        "attempt_before": attempt_before,
        "attempt_after": attempt_before + 1,
        "attempt_consumed": True,
        "objective_metrics_before": {
            "four_pillar_verified_count": 0,
            "confirmed_leakage_amount": 0,
            "owner_reviewable_case_packet_count": 0,
        },
        "objective_metrics_after": {
            "four_pillar_verified_count": verified,
            "confirmed_leakage_amount": 0,
            "owner_reviewable_case_packet_count": verified,
        },
        "owner_acceptance_delta": verified,
        "supporting_delta": "fixed historical hypothesis closed at three-case stop-loss",
        "business_artifact_created": verified > 0,
        "unlocked_next_action": (
            "Owner decision on prospective case-id live-capture pilot"
            if verified == 0
            else "Owner review of confirmed historical case packet"
        ),
        "sample_count": len(packets),
        "unique_candidate_hashes": len({item["candidate_hash"] for item in packets}),
        "samples": packets,
        "evidence_summary": {
            "request_rows_verified": sum(
                item["request"]["status"] == "VERIFIED_REQUEST_ROW_HASH"
                for item in packets
            ),
            "baseline_scope_verified": 0,
            "actual_delivery_verified": 0,
            "incremental_cost_verified": 0,
            "charged_fee_verified": 0,
            "four_pillar_verified_count": verified,
            "decision_counts": {"INSUFFICIENT_EVIDENCE": len(packets) - verified},
            "missing_evidence_code_counts": dict(sorted(missing_counts.items())),
        },
        "confirmed_leakage_amount": 0,
        "decision": decision,
        "interpretation": (
            "Request/source hashes are verified for the three frozen cases. Conversation "
            "cues, pointer metadata, and amount text are not quote, delivery, cost, or "
            "charged-fee evidence. No historical leakage amount may be inferred."
        ),
    }
    validate_packet(payload)
    serialized = json.dumps(payload, ensure_ascii=False)
    forbidden = [str(calibration_path), str(raw_source_dir), "/Users/", "/Volumes/", "http://", "https://"]
    if any(value and value in serialized for value in forbidden):
        raise FixedThreeError("private_path_or_url_leaked_to_packet")
    return payload


def build_sanitized_receipt(
    private_packet_path: Path, expected_private_packet_sha256: str
) -> dict:
    validate_private_file(private_packet_path, "private_packet")
    if not HASH_RE.fullmatch(expected_private_packet_sha256):
        raise FixedThreeError("private_packet_sha256_invalid")
    private_packet_sha256 = sha256_file(private_packet_path)
    if private_packet_sha256 != expected_private_packet_sha256:
        raise FixedThreeError("private_packet_sha256_mismatch")
    try:
        private_payload = json.loads(private_packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise FixedThreeError("private_packet_json_invalid") from error
    validate_packet(private_payload)
    samples = []
    for item in private_payload["samples"]:
        samples.append({
            "candidate_hash": item["candidate_hash"],
            "category": item["category"],
            "selection_key": item["selection_key"],
            "request_status": item["request"]["status"],
            "request_row_sha256": item["request"]["evidence_row_sha256"],
            "source_file_sha256": item["source_conversation"]["source_file_sha256"],
            "baseline_scope_status": item["baseline_scope"]["status"],
            "actual_delivery_status": item["actual_delivery"]["status"],
            "incremental_cost_status": item["incremental_cost"]["status"],
            "charged_fee_status": item["charged_fee"]["status"],
            "four_pillar_verified": item["four_pillar_verified"],
            "decision_label": item["decision_label"],
            "missing_evidence_codes": item["missing_evidence_codes"],
        })
    receipt = {
        "schema_version": "maplab.margin-leak.fixed-three.sanitized.v1",
        "created_at": private_payload["created_at"],
        "method_contract": private_payload["method_contract"],
        "private_packet_sha256": private_packet_sha256,
        "attempt_before": private_payload["attempt_before"],
        "attempt_after": private_payload["attempt_after"],
        "attempt_consumed": private_payload["attempt_consumed"],
        "objective_metrics_before": private_payload["objective_metrics_before"],
        "objective_metrics_after": private_payload["objective_metrics_after"],
        "owner_acceptance_delta": private_payload["owner_acceptance_delta"],
        "supporting_delta": private_payload["supporting_delta"],
        "business_artifact_created": private_payload["business_artifact_created"],
        "unlocked_next_action": private_payload["unlocked_next_action"],
        "source_receipts": {
            "calibration_sha256": private_payload["source_receipts"]["calibration_sha256"],
            "calibration_fingerprint": private_payload["source_receipts"]["calibration_fingerprint"],
            "calibration_source_manifest_sha256": private_payload["source_receipts"]["calibration_source_manifest_sha256"],
            "raw_source_manifest_sha256": private_payload["source_receipts"]["raw_source_manifest_sha256"],
            "local_quote_pointer_manifest_sha256": private_payload["source_receipts"]["local_quote_pointer_manifest_sha256"],
            "local_quote_pointer_scan_status": private_payload["source_receipts"]["local_quote_pointer_scan_status"],
            "ordercharges_authoritative_writer": private_payload["source_receipts"]["ordercharges_authoritative_writer"],
            "ordercharges_semantics": private_payload["source_receipts"]["ordercharges_semantics"],
        },
        "privacy": private_payload["privacy"],
        "sample_count": private_payload["sample_count"],
        "unique_candidate_hashes": private_payload["unique_candidate_hashes"],
        "samples": samples,
        "evidence_summary": private_payload["evidence_summary"],
        "confirmed_leakage_amount": private_payload["confirmed_leakage_amount"],
        "decision": private_payload["decision"],
    }
    receipt["body_sha256"] = sha256_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    serialized = json.dumps(receipt, ensure_ascii=False)
    if any(token in serialized for token in ("/Users/", "/Volumes/", "http://", "https://", "evidence_path")):
        raise FixedThreeError("private_value_leaked_to_sanitized_receipt")
    return receipt


def validate_packet(payload: dict) -> None:
    samples = payload.get("samples")
    if not isinstance(samples, list) or len(samples) != PILOT_SIZE:
        raise FixedThreeError("packet_sample_count_invalid")
    hashes = [sample.get("candidate_hash") for sample in samples]
    if len(set(hashes)) != PILOT_SIZE or any(not isinstance(value, str) or not HASH_RE.fullmatch(value) for value in hashes):
        raise FixedThreeError("packet_candidate_hashes_invalid")
    if hashes != sorted(hashes, key=_selection_key):
        raise FixedThreeError("packet_selection_order_invalid")
    if payload.get("attempt_consumed") is not True:
        raise FixedThreeError("packet_attempt_accounting_invalid")
    if payload.get("attempt_after") != payload.get("attempt_before") + 1:
        raise FixedThreeError("packet_attempt_accounting_invalid")
    for sample in samples:
        if sample.get("request", {}).get("status") != "VERIFIED_REQUEST_ROW_HASH":
            raise FixedThreeError("packet_request_gate_invalid")
        for pillar in ("baseline_scope", "actual_delivery", "incremental_cost", "charged_fee"):
            if sample.get(pillar, {}).get("status") not in {"VERIFIED", "UNVERIFIED"}:
                raise FixedThreeError("packet_pillar_status_invalid")
        expected = all(sample[pillar]["status"] == "VERIFIED" for pillar in (
            "baseline_scope", "actual_delivery", "incremental_cost", "charged_fee"
        ))
        if sample.get("four_pillar_verified") is not expected:
            raise FixedThreeError("packet_four_pillar_relation_invalid")


def _packet_identity(payload: dict) -> dict:
    return {
        "schema_version": payload.get("schema_version"),
        "method_fingerprint": payload.get("method_contract", {}).get("fingerprint"),
        "attempt_before": payload.get("attempt_before"),
        "attempt_after": payload.get("attempt_after"),
        "selected_candidate_hashes": payload.get("method_contract", {})
        .get("fixed_holdout", {})
        .get("selected_candidate_hashes"),
        "calibration_sha256": payload.get("source_receipts", {}).get("calibration_sha256"),
        "raw_source_manifest_sha256": payload.get("source_receipts", {}).get("raw_source_manifest_sha256"),
        "decision": payload.get("decision"),
    }


def write_private_json(path: Path, payload: dict) -> bool:
    if not path.is_absolute():
        raise FixedThreeError("output_path_must_be_absolute")
    if path.exists():
        validate_private_file(path, "existing_output")
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise FixedThreeError("existing_output_json_invalid") from error
        validate_packet(existing)
        if _packet_identity(existing) != _packet_identity(payload):
            raise FixedThreeError("existing_output_identity_conflict")
        return False
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.chmod(PRIVATE_FILE_MODE)
    os.replace(temporary, path)
    path.chmod(PRIVATE_FILE_MODE)
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--expected-calibration-sha256", required=True)
    parser.add_argument("--expected-calibration-fingerprint", required=True)
    parser.add_argument("--raw-source-dir", required=True)
    parser.add_argument("--quote-pointer-root", action="append", default=[])
    parser.add_argument("--attempt-before", type=int, required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = build_packet(
        Path(args.calibration).expanduser().resolve(),
        Path(args.raw_source_dir).expanduser().resolve(),
        expected_calibration_sha256=args.expected_calibration_sha256,
        expected_calibration_fingerprint=args.expected_calibration_fingerprint,
        quote_pointer_roots=[Path(value).expanduser().resolve() for value in args.quote_pointer_root],
        attempt_before=args.attempt_before,
    )
    output = Path(args.output).expanduser().resolve()
    output_created = write_private_json(output, payload)
    print(json.dumps({
        "status": "ok",
        "output_created": output_created,
        "method_version": METHOD_VERSION,
        "sample_count": payload["sample_count"],
        "request_rows_verified": payload["evidence_summary"]["request_rows_verified"],
        "four_pillar_verified_count": payload["evidence_summary"]["four_pillar_verified_count"],
        "confirmed_leakage_amount": payload["confirmed_leakage_amount"],
        "attempt_after": payload["attempt_after"],
        "decision": payload["decision"],
        "network_calls": 0,
        "model_calls": 0,
        "output_sha256": sha256_file(output),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
