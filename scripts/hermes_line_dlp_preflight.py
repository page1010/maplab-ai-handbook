#!/usr/bin/env python3
"""Offline, aggregate-only DLP and data-rights preflight for Hermes LINE data.

The scanner reads local JSONL files, never calls a model or network surface,
never starts training, and never emits source paths, source text, matched
values, or value hashes.  Only an owner-only aggregate receipt may be written.

`init` creates a fail-closed PENDING rights manifest bound to exact dataset
bytes.  A named human must deliberately complete that manifest before `scan`
can return PASS.  `scan` still reports aggregate DLP counts while rights are
pending so the remediation boundary is observable without exposing records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA_VERSION = "maplab.hermes.line-dlp-rights-manifest.v1"
RECEIPT_SCHEMA_VERSION = "maplab.hermes.line-dlp-preflight-receipt.v1"
MANIFEST_SCHEMA_PATH = (
    ROOT / "config" / "schemas" / "hermes-line-dlp-rights-manifest-v1.schema.json"
)
RECEIPT_SCHEMA_PATH = (
    ROOT / "config" / "schemas" / "hermes-line-dlp-preflight-receipt-v1.schema.json"
)
PRIVATE_DLP_ROOT = Path.home() / ".maplab" / "a6-hermes-training" / "dlp"
DEFAULT_MANIFEST_PATH = PRIVATE_DLP_ROOT / "data-rights-manifest-v1.json"
DEFAULT_RECEIPT_PATH = PRIVATE_DLP_ROOT / "preflight-receipt-v1.json"

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
LOGICAL_NAME_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
REASON_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
CATEGORY_RE = re.compile(r"^[a-z][a-z0-9_]{0,127}$")
MACHINE_HASH_FIELD_RE = re.compile(r"(?:^|_)(?:hash|sha256)$")
MAX_DATASET_BYTES = 512 * 1024 * 1024
MAX_LINE_BYTES = 2 * 1024 * 1024
MAX_RECORD_NODES = 4096
MAX_DEPTH = 24
MAX_STRING_CHARS = 200_000

REQUIRED_ALLOWED_USES = {"offline_training", "offline_evaluation"}
REQUIRED_PROHIBITED_USES = {
    "external_model_egress",
    "third_party_sharing",
    "customer_auto_send",
    "sale_or_ad_targeting",
    "production_inference",
}
RIGHTS_BOOLEAN_FIELDS = (
    "access_export",
    "correction",
    "deletion",
    "withdrawal_or_objection",
)


class DLPPreflightError(RuntimeError):
    """Fail-closed error whose message is always a non-sensitive reason code."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value: object, reason_code: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise DLPPreflightError(reason_code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise DLPPreflightError(reason_code) from error
    if parsed.tzinfo is None:
        raise DLPPreflightError(reason_code)
    return parsed.astimezone(timezone.utc)


def absolute_path(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return Path(os.path.abspath(path))


def validate_regular_file(path: Path, *, private: bool, reason_prefix: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.exists():
        raise DLPPreflightError(f"{reason_prefix}_FILE_INVALID")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise DLPPreflightError(f"{reason_prefix}_FILE_INVALID")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise DLPPreflightError(f"{reason_prefix}_OWNER_INVALID")
    if private and stat.S_IMODE(info.st_mode) & 0o077:
        raise DLPPreflightError(f"{reason_prefix}_PERMISSIONS_NOT_PRIVATE")
    if info.st_size > MAX_DATASET_BYTES:
        raise DLPPreflightError(f"{reason_prefix}_FILE_TOO_LARGE")


def load_json(path: Path, *, private: bool, reason_prefix: str) -> dict[str, Any]:
    validate_regular_file(path, private=private, reason_prefix=reason_prefix)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DLPPreflightError(f"{reason_prefix}_JSON_INVALID") from error
    if not isinstance(payload, dict):
        raise DLPPreflightError(f"{reason_prefix}_JSON_NOT_OBJECT")
    return payload


def _exact_keys(value: object, expected: set[str], reason_code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise DLPPreflightError(reason_code)
    return value


def validate_manifest_shape(manifest: dict[str, Any]) -> None:
    top = _exact_keys(
        manifest,
        {
            "schema_version",
            "manifest_id",
            "created_at",
            "dataset",
            "authority",
            "data_subject_rights",
            "retention",
            "storage",
            "egress",
            "review",
        },
        "MANIFEST_FIELDS_INVALID",
    )
    if top.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise DLPPreflightError("MANIFEST_SCHEMA_INVALID")
    if not isinstance(top.get("manifest_id"), str) or not SAFE_ID_RE.fullmatch(top["manifest_id"]):
        raise DLPPreflightError("MANIFEST_ID_INVALID")
    parse_datetime(top.get("created_at"), "MANIFEST_CREATED_AT_INVALID")

    dataset = _exact_keys(
        top.get("dataset"),
        {"dataset_id", "data_class", "source_kind", "contains_raw_customer_text", "files"},
        "MANIFEST_DATASET_FIELDS_INVALID",
    )
    if not isinstance(dataset.get("dataset_id"), str) or not SAFE_ID_RE.fullmatch(dataset["dataset_id"]):
        raise DLPPreflightError("MANIFEST_DATASET_ID_INVALID")
    if dataset.get("data_class") not in {"private_line_derived", "synthetic"}:
        raise DLPPreflightError("MANIFEST_DATA_CLASS_INVALID")
    if dataset.get("source_kind") not in {"line_oa_export", "synthetic"}:
        raise DLPPreflightError("MANIFEST_SOURCE_KIND_INVALID")
    if not isinstance(dataset.get("contains_raw_customer_text"), bool):
        raise DLPPreflightError("MANIFEST_RAW_TEXT_FLAG_INVALID")
    files = dataset.get("files")
    if not isinstance(files, list) or not files:
        raise DLPPreflightError("MANIFEST_FILES_INVALID")
    logical_names: set[str] = set()
    for item in files:
        file_item = _exact_keys(
            item,
            {"logical_name", "sha256", "record_count", "byte_count"},
            "MANIFEST_FILE_FIELDS_INVALID",
        )
        name = file_item.get("logical_name")
        if not isinstance(name, str) or not LOGICAL_NAME_RE.fullmatch(name) or name in logical_names:
            raise DLPPreflightError("MANIFEST_LOGICAL_NAME_INVALID")
        logical_names.add(name)
        if not isinstance(file_item.get("sha256"), str) or not HASH_RE.fullmatch(file_item["sha256"]):
            raise DLPPreflightError("MANIFEST_FILE_SHA_INVALID")
        for key in ("record_count", "byte_count"):
            if type(file_item.get(key)) is not int or file_item[key] < 0:
                raise DLPPreflightError("MANIFEST_FILE_COUNT_INVALID")

    authority = _exact_keys(
        top.get("authority"),
        {"status", "controller_id", "attested_by", "attested_at", "allowed_uses", "prohibited_uses"},
        "MANIFEST_AUTHORITY_FIELDS_INVALID",
    )
    if authority.get("status") not in {"PENDING", "APPROVED", "REVOKED", "EXPIRED"}:
        raise DLPPreflightError("MANIFEST_AUTHORITY_STATUS_INVALID")
    if not isinstance(authority.get("controller_id"), str) or len(authority["controller_id"]) < 3:
        raise DLPPreflightError("MANIFEST_CONTROLLER_INVALID")
    if authority.get("attested_by") is not None and not isinstance(authority["attested_by"], str):
        raise DLPPreflightError("MANIFEST_ATTESTATION_INVALID")
    if authority.get("attested_at") is not None:
        parse_datetime(authority["attested_at"], "MANIFEST_ATTESTATION_INVALID")
    for key in ("allowed_uses", "prohibited_uses"):
        values = authority.get(key)
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise DLPPreflightError("MANIFEST_USE_POLICY_INVALID")
        if len(values) != len(set(values)):
            raise DLPPreflightError("MANIFEST_USE_POLICY_INVALID")

    rights = _exact_keys(
        top.get("data_subject_rights"),
        set(RIGHTS_BOOLEAN_FIELDS) | {"contact_route_id"},
        "MANIFEST_RIGHTS_FIELDS_INVALID",
    )
    if any(not isinstance(rights.get(key), bool) for key in RIGHTS_BOOLEAN_FIELDS):
        raise DLPPreflightError("MANIFEST_RIGHTS_VALUE_INVALID")
    if not isinstance(rights.get("contact_route_id"), str) or len(rights["contact_route_id"]) < 3:
        raise DLPPreflightError("MANIFEST_CONTACT_ROUTE_INVALID")

    retention = _exact_keys(
        top.get("retention"),
        {"status", "policy_id", "expires_at", "deletion_sla_days"},
        "MANIFEST_RETENTION_FIELDS_INVALID",
    )
    if retention.get("status") not in {"PENDING", "ACTIVE", "EXPIRED"}:
        raise DLPPreflightError("MANIFEST_RETENTION_STATUS_INVALID")
    if not isinstance(retention.get("policy_id"), str) or len(retention["policy_id"]) < 3:
        raise DLPPreflightError("MANIFEST_RETENTION_POLICY_INVALID")
    if retention.get("expires_at") is not None:
        parse_datetime(retention["expires_at"], "MANIFEST_RETENTION_EXPIRY_INVALID")
    if type(retention.get("deletion_sla_days")) is not int or not (1 <= retention["deletion_sla_days"] <= 365):
        raise DLPPreflightError("MANIFEST_DELETION_SLA_INVALID")

    storage = _exact_keys(
        top.get("storage"),
        {"owner_only", "allowed_root_fingerprint"},
        "MANIFEST_STORAGE_FIELDS_INVALID",
    )
    if not isinstance(storage.get("owner_only"), bool):
        raise DLPPreflightError("MANIFEST_STORAGE_POLICY_INVALID")
    if not isinstance(storage.get("allowed_root_fingerprint"), str) or not HASH_RE.fullmatch(
        storage["allowed_root_fingerprint"]
    ):
        raise DLPPreflightError("MANIFEST_STORAGE_FINGERPRINT_INVALID")

    egress = _exact_keys(
        top.get("egress"),
        {"network_allowed", "third_party_allowed", "customer_send_allowed"},
        "MANIFEST_EGRESS_FIELDS_INVALID",
    )
    if any(not isinstance(egress.get(key), bool) for key in egress):
        raise DLPPreflightError("MANIFEST_EGRESS_POLICY_INVALID")

    review = _exact_keys(
        top.get("review"),
        {
            "free_text_review_status",
            "reviewed_by",
            "reviewed_at",
            "method",
            "known_identifier_dictionary_sha256",
        },
        "MANIFEST_REVIEW_FIELDS_INVALID",
    )
    if review.get("free_text_review_status") not in {"PENDING", "APPROVED", "REJECTED"}:
        raise DLPPreflightError("MANIFEST_REVIEW_STATUS_INVALID")
    if review.get("reviewed_by") is not None and not isinstance(review["reviewed_by"], str):
        raise DLPPreflightError("MANIFEST_REVIEW_ATTESTATION_INVALID")
    if review.get("reviewed_at") is not None:
        parse_datetime(review["reviewed_at"], "MANIFEST_REVIEW_ATTESTATION_INVALID")
    if review.get("method") not in {"deterministic_plus_named_human", "synthetic_fixture"}:
        raise DLPPreflightError("MANIFEST_REVIEW_METHOD_INVALID")
    dictionary_sha = review.get("known_identifier_dictionary_sha256")
    if dictionary_sha is not None and (not isinstance(dictionary_sha, str) or not HASH_RE.fullmatch(dictionary_sha)):
        raise DLPPreflightError("MANIFEST_DICTIONARY_SHA_INVALID")


FIELD_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "direct_name_field",
        re.compile(
            r"^(?:customer_name|sender_name|display_name|full_name|real_name|contact_name|姓名|客戶姓名|聯絡人)$",
            re.IGNORECASE,
        ),
    ),
    (
        "direct_phone_field",
        re.compile(r"^(?:phone|mobile|telephone|tel|phone_number|手機|電話|聯絡電話)$", re.IGNORECASE),
    ),
    (
        "direct_email_field",
        re.compile(r"^(?:email|e_mail|email_address|電子郵件|信箱)$", re.IGNORECASE),
    ),
    (
        "direct_address_field",
        re.compile(r"^(?:address|street_address|delivery_address|地址|住址|配送地址)$", re.IGNORECASE),
    ),
    (
        "direct_account_field",
        re.compile(
            r"^(?:line_user_id|line_id|telegram_user_id|chat_id|account_id|bank_account|帳號|銀行帳號|line帳號)$",
            re.IGNORECASE,
        ),
    ),
    (
        "direct_identity_field",
        re.compile(r"^(?:national_id|identity_number|id_number|身分證|統一編號)$", re.IGNORECASE),
    ),
)

TEXT_RULES: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "high",
        "email_address",
        re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE),
    ),
    (
        "high",
        "taiwan_mobile_phone",
        re.compile(r"(?<!\d)(?:\+?886[-\s]?)?0?9\d{2}[-\s]?\d{3}[-\s]?\d{3}(?!\d)"),
    ),
    (
        "high",
        "taiwan_landline_phone",
        re.compile(r"(?<!\d)0(?:2|3|4|5|6|7|8)[-\s]?\d{6,8}(?!\d)"),
    ),
    (
        "high",
        "taiwan_national_id",
        re.compile(r"(?<![A-Z0-9])[A-Z][12]\d{8}(?![A-Z0-9])", re.IGNORECASE),
    ),
    (
        "high",
        "line_account",
        re.compile(r"(?:LINE\s*(?:ID|帳號)|賴(?:ID|帳號))\s*[:：]?\s*[A-Z0-9._-]{4,}", re.IGNORECASE),
    ),
    (
        "high",
        "bank_account",
        re.compile(r"(?:銀行帳號|銀行帳戶|匯款帳號|匯款帳戶)\D{0,12}\d{8,16}"),
    ),
    (
        "high",
        "taiwan_postal_address",
        re.compile(
            r"(?:台|臺|新北|桃園|台中|臺中|台南|臺南|高雄|基隆|新竹|嘉義|苗栗|彰化|南投|雲林|屏東|宜蘭|花蓮|台東|臺東|澎湖|金門|連江)(?:市|縣).{0,20}(?:區|鄉|鎮|市).{0,24}(?:路|街|大道|巷|弄).{0,12}(?:號|樓)"
        ),
    ),
    (
        "review",
        "person_name_with_honorific",
        re.compile(r"[\u4e00-\u9fff]{2,4}(?:先生|小姐|女士|太太|經理|老師)"),
    ),
    (
        "review",
        "social_handle",
        re.compile(r"(?<![\w@])@[A-Z0-9_]{5,}(?![\w@])", re.IGNORECASE),
    ),
    (
        "review",
        "long_numeric_identifier",
        re.compile(r"(?<!\d)\d{9,18}(?!\d)"),
    ),
)


def normalize_field_name(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff]+", "_", value.strip()).strip("_").lower()


def iter_record_fields(record: dict[str, Any]) -> Iterator[tuple[str, object, int]]:
    stack: list[tuple[str, object, int]] = [("root", record, 0)]
    visited = 0
    while stack:
        field_name, value, depth = stack.pop()
        visited += 1
        if visited > MAX_RECORD_NODES:
            raise DLPPreflightError("RECORD_NODE_LIMIT_EXCEEDED")
        if depth > MAX_DEPTH:
            raise DLPPreflightError("RECORD_DEPTH_LIMIT_EXCEEDED")
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise DLPPreflightError("RECORD_FIELD_NAME_INVALID")
                yield key, child, depth + 1
                stack.append((key, child, depth + 1))
        elif isinstance(value, list):
            for child in value:
                stack.append((field_name, child, depth + 1))


def _increment(counter: Counter[str], category: str, amount: int = 1) -> None:
    if amount > 0:
        counter[category] += amount


def inspect_record(record: dict[str, Any]) -> tuple[Counter[str], int, int]:
    categories: Counter[str] = Counter()
    high = 0
    review = 0
    for raw_field, value, _depth in iter_record_fields(record):
        field = normalize_field_name(raw_field)
        is_machine_hash = bool(MACHINE_HASH_FIELD_RE.search(field))
        if not is_machine_hash:
            for category, pattern in FIELD_RULES:
                if pattern.fullmatch(field):
                    _increment(categories, category)
                    high += 1
        if not isinstance(value, str) or is_machine_hash:
            continue
        if len(value) > MAX_STRING_CHARS:
            raise DLPPreflightError("RECORD_STRING_LIMIT_EXCEEDED")
        for severity, category, pattern in TEXT_RULES:
            count = sum(1 for _ in pattern.finditer(value))
            if not count:
                continue
            _increment(categories, category, count)
            if severity == "high":
                high += count
            else:
                review += count
    return categories, high, review


def scan_jsonl(path: Path, logical_name: str, *, private: bool) -> dict[str, Any]:
    validate_regular_file(path, private=private, reason_prefix="DATASET")
    digest = hashlib.sha256()
    categories: Counter[str] = Counter()
    record_count = 0
    invalid_json_records = 0
    non_object_records = 0
    scan_errors = 0
    high_confidence_findings = 0
    review_required_findings = 0
    byte_count = 0

    with path.open("rb") as handle:
        for raw_line in handle:
            record_count += 1
            byte_count += len(raw_line)
            digest.update(raw_line)
            if len(raw_line) > MAX_LINE_BYTES:
                scan_errors += 1
                continue
            try:
                line = raw_line.decode("utf-8")
                record = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                invalid_json_records += 1
                continue
            if not isinstance(record, dict):
                non_object_records += 1
                continue
            try:
                found, high, review = inspect_record(record)
            except DLPPreflightError:
                scan_errors += 1
                continue
            categories.update(found)
            high_confidence_findings += high
            review_required_findings += review

    if byte_count != path.stat().st_size:
        raise DLPPreflightError("DATASET_SIZE_CHANGED_DURING_SCAN")
    return {
        "logical_name": logical_name,
        "sha256": digest.hexdigest(),
        "record_count": record_count,
        "byte_count": byte_count,
        "invalid_json_records": invalid_json_records,
        "non_object_records": non_object_records,
        "scan_errors": scan_errors,
        "high_confidence_findings": high_confidence_findings,
        "review_required_findings": review_required_findings,
        "findings_by_category": dict(sorted(categories.items())),
    }


def aggregate_scan(files: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(files)
    categories: Counter[str] = Counter()
    for item in items:
        categories.update(item["findings_by_category"])
    return {
        "dataset_file_count": len(items),
        "record_count": sum(item["record_count"] for item in items),
        "byte_count": sum(item["byte_count"] for item in items),
        "invalid_json_records": sum(item["invalid_json_records"] for item in items),
        "non_object_records": sum(item["non_object_records"] for item in items),
        "scan_errors": sum(item["scan_errors"] for item in items),
        "high_confidence_findings": sum(item["high_confidence_findings"] for item in items),
        "review_required_findings": sum(item["review_required_findings"] for item in items),
        "findings_by_category": dict(sorted(categories.items())),
        "files": [
            {key: value for key, value in item.items() if key != "findings_by_category"}
            for item in items
        ],
    }


def parse_dataset_specs(raw_specs: list[str]) -> list[tuple[str, Path]]:
    parsed: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for raw in raw_specs:
        if "=" not in raw:
            raise DLPPreflightError("DATASET_ARGUMENT_INVALID")
        logical_name, raw_path = raw.split("=", 1)
        if not LOGICAL_NAME_RE.fullmatch(logical_name) or logical_name in seen or not raw_path:
            raise DLPPreflightError("DATASET_ARGUMENT_INVALID")
        seen.add(logical_name)
        parsed.append((logical_name, absolute_path(raw_path)))
    if not parsed:
        raise DLPPreflightError("DATASET_ARGUMENT_MISSING")
    return parsed


def common_root_fingerprint(paths: Iterable[Path]) -> str:
    parents = [str(path.parent) for path in paths]
    try:
        common = os.path.commonpath(parents)
    except ValueError as error:
        raise DLPPreflightError("DATASET_COMMON_ROOT_INVALID") from error
    return sha256_text("maplab-owner-root-v1\0" + common)


def manifest_file_projection(scan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "logical_name": item["logical_name"],
            "sha256": item["sha256"],
            "record_count": item["record_count"],
            "byte_count": item["byte_count"],
        }
        for item in scan["files"]
    ]


def build_pending_manifest(
    *,
    dataset_id: str,
    scan: dict[str, Any],
    source_paths: Iterable[Path],
    created_at: str,
    synthetic: bool,
) -> dict[str, Any]:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": f"{dataset_id}-rights-v1",
        "created_at": created_at,
        "dataset": {
            "dataset_id": dataset_id,
            "data_class": "synthetic" if synthetic else "private_line_derived",
            "source_kind": "synthetic" if synthetic else "line_oa_export",
            "contains_raw_customer_text": not synthetic,
            "files": manifest_file_projection(scan),
        },
        "authority": {
            "status": "PENDING",
            "controller_id": "PENDING_NAMED_HUMAN_CONFIRMATION",
            "attested_by": None,
            "attested_at": None,
            "allowed_uses": [],
            "prohibited_uses": sorted(REQUIRED_PROHIBITED_USES),
        },
        "data_subject_rights": {
            "access_export": False,
            "correction": False,
            "deletion": False,
            "withdrawal_or_objection": False,
            "contact_route_id": "PENDING_OWNER_DEFINED_ROUTE",
        },
        "retention": {
            "status": "PENDING",
            "policy_id": "PENDING_OWNER_RETENTION_POLICY",
            "expires_at": None,
            "deletion_sla_days": 30,
        },
        "storage": {
            "owner_only": True,
            "allowed_root_fingerprint": common_root_fingerprint(source_paths),
        },
        "egress": {
            "network_allowed": False,
            "third_party_allowed": False,
            "customer_send_allowed": False,
        },
        "review": {
            "free_text_review_status": "PENDING",
            "reviewed_by": None,
            "reviewed_at": None,
            "method": "synthetic_fixture" if synthetic else "deterministic_plus_named_human",
            "known_identifier_dictionary_sha256": None,
        },
    }
    validate_manifest_shape(manifest)
    return manifest


def dataset_binding_reasons(manifest: dict[str, Any], scan: dict[str, Any]) -> list[str]:
    expected = sorted(manifest["dataset"]["files"], key=lambda item: item["logical_name"])
    actual = sorted(manifest_file_projection(scan), key=lambda item: item["logical_name"])
    return [] if expected == actual else ["DATASET_BINDING_MISMATCH"]


def rights_reasons(
    manifest: dict[str, Any], *, source_paths: Iterable[Path], now: datetime
) -> list[str]:
    reasons: list[str] = []
    authority = manifest["authority"]
    if authority["status"] != "APPROVED":
        reasons.append("RIGHTS_AUTHORITY_NOT_APPROVED")
    if not authority["attested_by"] or authority["attested_at"] is None:
        reasons.append("RIGHTS_ATTESTATION_MISSING")
    else:
        attested_at = parse_datetime(authority["attested_at"], "MANIFEST_ATTESTATION_INVALID")
        if attested_at > now + timedelta(minutes=5):
            reasons.append("RIGHTS_ATTESTATION_TIME_INVALID")
    if not REQUIRED_ALLOWED_USES.issubset(set(authority["allowed_uses"])):
        reasons.append("RIGHTS_REQUIRED_PURPOSE_MISSING")
    if not REQUIRED_PROHIBITED_USES.issubset(set(authority["prohibited_uses"])):
        reasons.append("RIGHTS_PROHIBITIONS_INCOMPLETE")

    rights = manifest["data_subject_rights"]
    if any(rights[key] is not True for key in RIGHTS_BOOLEAN_FIELDS):
        reasons.append("DATA_SUBJECT_RIGHTS_INCOMPLETE")
    if rights["contact_route_id"].startswith("PENDING_"):
        reasons.append("DATA_SUBJECT_CONTACT_ROUTE_PENDING")

    retention = manifest["retention"]
    if retention["status"] != "ACTIVE":
        reasons.append("RETENTION_NOT_ACTIVE")
    if retention["expires_at"] is None:
        reasons.append("RETENTION_EXPIRY_MISSING")
    elif parse_datetime(retention["expires_at"], "MANIFEST_RETENTION_EXPIRY_INVALID") <= now:
        reasons.append("RETENTION_EXPIRED")
    if retention["policy_id"].startswith("PENDING_"):
        reasons.append("RETENTION_POLICY_PENDING")

    storage = manifest["storage"]
    if storage["owner_only"] is not True:
        reasons.append("OWNER_ONLY_STORAGE_NOT_REQUIRED")
    if storage["allowed_root_fingerprint"] != common_root_fingerprint(source_paths):
        reasons.append("STORAGE_ROOT_BINDING_MISMATCH")

    egress = manifest["egress"]
    if any(egress[key] is not False for key in egress):
        reasons.append("ZERO_EGRESS_POLICY_NOT_ENFORCED")

    review = manifest["review"]
    if review["free_text_review_status"] != "APPROVED":
        reasons.append("FREE_TEXT_REVIEW_NOT_APPROVED")
    if not review["reviewed_by"] or review["reviewed_at"] is None:
        reasons.append("FREE_TEXT_REVIEW_ATTESTATION_MISSING")
    elif parse_datetime(review["reviewed_at"], "MANIFEST_REVIEW_ATTESTATION_INVALID") > now + timedelta(minutes=5):
        reasons.append("FREE_TEXT_REVIEW_TIME_INVALID")
    return reasons


def scan_reasons(scan: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if scan["invalid_json_records"]:
        reasons.append("INVALID_JSON_RECORDS")
    if scan["non_object_records"]:
        reasons.append("NON_OBJECT_RECORDS")
    if scan["scan_errors"]:
        reasons.append("SCAN_ERRORS")
    if scan["high_confidence_findings"]:
        reasons.append("HIGH_CONFIDENCE_IDENTIFIERS_DETECTED")
    if scan["review_required_findings"]:
        reasons.append("REVIEW_REQUIRED_IDENTIFIERS_DETECTED")
    return reasons


def build_receipt(
    *,
    manifest: dict[str, Any],
    manifest_sha256: str,
    scan: dict[str, Any],
    source_paths: Iterable[Path],
    created_at: str,
    scanner_sha256: str,
) -> dict[str, Any]:
    now = parse_datetime(created_at, "RECEIPT_CREATED_AT_INVALID")
    reasons = sorted(
        set(
            dataset_binding_reasons(manifest, scan)
            + rights_reasons(manifest, source_paths=source_paths, now=now)
            + scan_reasons(scan)
        )
    )
    eligible = not reasons
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "created_at": created_at,
        "status": "PASS" if eligible else "BLOCKED",
        "eligible_for_offline_training": eligible,
        "reason_codes": reasons,
        "manifest": {
            "schema_version": manifest["schema_version"],
            "sha256": manifest_sha256,
            "dataset_id": manifest["dataset"]["dataset_id"],
            "authority_status": manifest["authority"]["status"],
            "retention_status": manifest["retention"]["status"],
            "free_text_review_status": manifest["review"]["free_text_review_status"],
            "rights_controls_complete": not rights_reasons(
                manifest, source_paths=source_paths, now=now
            ),
        },
        "scan": scan,
        "privacy": {
            "raw_text_emitted": False,
            "matched_values_emitted": False,
            "source_paths_emitted": False,
            "aggregate_counts_only": True,
        },
        "execution": {
            "network_calls": 0,
            "model_calls": 0,
            "local_model_calls": 0,
            "training_runs_started": 0,
            "customer_sends": 0,
        },
        "provenance": {
            "scanner_sha256": scanner_sha256,
            "manifest_sha256": manifest_sha256,
            "schema_sha256": sha256_file(RECEIPT_SCHEMA_PATH),
        },
    }
    receipt["body_sha256"] = sha256_text(canonical_json(receipt))
    validate_receipt(receipt)
    return receipt


def validate_receipt(receipt: dict[str, Any]) -> None:
    expected_top = {
        "schema_version",
        "created_at",
        "status",
        "eligible_for_offline_training",
        "reason_codes",
        "manifest",
        "scan",
        "privacy",
        "execution",
        "provenance",
        "body_sha256",
    }
    _exact_keys(receipt, expected_top, "RECEIPT_FIELDS_INVALID")
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise DLPPreflightError("RECEIPT_SCHEMA_INVALID")
    parse_datetime(receipt.get("created_at"), "RECEIPT_CREATED_AT_INVALID")
    reasons = receipt.get("reason_codes")
    if (
        not isinstance(reasons, list)
        or reasons != sorted(set(reasons))
        or any(
            not isinstance(item, str) or not REASON_CODE_RE.fullmatch(item)
            for item in reasons
        )
    ):
        raise DLPPreflightError("RECEIPT_REASON_CODES_INVALID")
    eligible = receipt.get("eligible_for_offline_training")
    if type(eligible) is not bool or receipt.get("status") != (
        "PASS" if eligible else "BLOCKED"
    ):
        raise DLPPreflightError("RECEIPT_STATUS_INVALID")
    if eligible != (not reasons):
        raise DLPPreflightError("RECEIPT_ELIGIBILITY_INVALID")

    manifest = _exact_keys(
        receipt.get("manifest"),
        {
            "schema_version",
            "sha256",
            "dataset_id",
            "authority_status",
            "retention_status",
            "free_text_review_status",
            "rights_controls_complete",
        },
        "RECEIPT_MANIFEST_FIELDS_INVALID",
    )
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise DLPPreflightError("RECEIPT_MANIFEST_SCHEMA_INVALID")
    if not isinstance(manifest.get("sha256"), str) or not HASH_RE.fullmatch(
        manifest["sha256"]
    ):
        raise DLPPreflightError("RECEIPT_MANIFEST_SHA_INVALID")
    if not isinstance(manifest.get("dataset_id"), str) or not SAFE_ID_RE.fullmatch(
        manifest["dataset_id"]
    ):
        raise DLPPreflightError("RECEIPT_DATASET_ID_INVALID")
    if manifest.get("authority_status") not in {
        "PENDING",
        "APPROVED",
        "REVOKED",
        "EXPIRED",
    }:
        raise DLPPreflightError("RECEIPT_AUTHORITY_STATUS_INVALID")
    if manifest.get("retention_status") not in {"PENDING", "ACTIVE", "EXPIRED"}:
        raise DLPPreflightError("RECEIPT_RETENTION_STATUS_INVALID")
    if manifest.get("free_text_review_status") not in {
        "PENDING",
        "APPROVED",
        "REJECTED",
    }:
        raise DLPPreflightError("RECEIPT_REVIEW_STATUS_INVALID")
    if type(manifest.get("rights_controls_complete")) is not bool:
        raise DLPPreflightError("RECEIPT_RIGHTS_COMPLETE_INVALID")
    if eligible and manifest["rights_controls_complete"] is not True:
        raise DLPPreflightError("RECEIPT_RIGHTS_ELIGIBILITY_INVALID")

    scan = _exact_keys(
        receipt.get("scan"),
        {
            "dataset_file_count",
            "record_count",
            "byte_count",
            "invalid_json_records",
            "non_object_records",
            "scan_errors",
            "high_confidence_findings",
            "review_required_findings",
            "findings_by_category",
            "files",
        },
        "RECEIPT_SCAN_FIELDS_INVALID",
    )
    count_fields = (
        "record_count",
        "byte_count",
        "invalid_json_records",
        "non_object_records",
        "scan_errors",
        "high_confidence_findings",
        "review_required_findings",
    )
    if type(scan.get("dataset_file_count")) is not int or scan["dataset_file_count"] < 1:
        raise DLPPreflightError("RECEIPT_SCAN_COUNT_INVALID")
    if any(type(scan.get(key)) is not int or scan[key] < 0 for key in count_fields):
        raise DLPPreflightError("RECEIPT_SCAN_COUNT_INVALID")
    categories = scan.get("findings_by_category")
    if not isinstance(categories, dict) or any(
        not isinstance(key, str)
        or not CATEGORY_RE.fullmatch(key)
        or type(value) is not int
        or value <= 0
        for key, value in categories.items()
    ):
        raise DLPPreflightError("RECEIPT_SCAN_CATEGORIES_INVALID")
    if sum(categories.values()) != (
        scan["high_confidence_findings"] + scan["review_required_findings"]
    ):
        raise DLPPreflightError("RECEIPT_SCAN_CATEGORY_TOTAL_INVALID")
    files = scan.get("files")
    if not isinstance(files, list) or len(files) != scan["dataset_file_count"] or not files:
        raise DLPPreflightError("RECEIPT_SCAN_FILES_INVALID")
    logical_names: set[str] = set()
    expected_file_keys = {"logical_name", "sha256", *count_fields}
    for item in files:
        file_item = _exact_keys(
            item, expected_file_keys, "RECEIPT_SCAN_FILE_FIELDS_INVALID"
        )
        logical_name = file_item.get("logical_name")
        if (
            not isinstance(logical_name, str)
            or not LOGICAL_NAME_RE.fullmatch(logical_name)
            or logical_name in logical_names
        ):
            raise DLPPreflightError("RECEIPT_SCAN_LOGICAL_NAME_INVALID")
        logical_names.add(logical_name)
        if not isinstance(file_item.get("sha256"), str) or not HASH_RE.fullmatch(
            file_item["sha256"]
        ):
            raise DLPPreflightError("RECEIPT_SCAN_FILE_SHA_INVALID")
        if any(
            type(file_item.get(key)) is not int or file_item[key] < 0
            for key in count_fields
        ):
            raise DLPPreflightError("RECEIPT_SCAN_FILE_COUNT_INVALID")
    if any(scan[key] != sum(item[key] for item in files) for key in count_fields):
        raise DLPPreflightError("RECEIPT_SCAN_AGGREGATE_MISMATCH")

    if receipt.get("privacy") != {
        "raw_text_emitted": False,
        "matched_values_emitted": False,
        "source_paths_emitted": False,
        "aggregate_counts_only": True,
    }:
        raise DLPPreflightError("RECEIPT_PRIVACY_BOUNDARY_INVALID")
    if receipt.get("execution") != {
        "network_calls": 0,
        "model_calls": 0,
        "local_model_calls": 0,
        "training_runs_started": 0,
        "customer_sends": 0,
    }:
        raise DLPPreflightError("RECEIPT_EXECUTION_BOUNDARY_INVALID")
    provenance = _exact_keys(
        receipt.get("provenance"),
        {"scanner_sha256", "manifest_sha256", "schema_sha256"},
        "RECEIPT_PROVENANCE_FIELDS_INVALID",
    )
    if any(
        not isinstance(provenance.get(key), str) or not HASH_RE.fullmatch(provenance[key])
        for key in provenance
    ):
        raise DLPPreflightError("RECEIPT_PROVENANCE_SHA_INVALID")
    if provenance["manifest_sha256"] != manifest["sha256"]:
        raise DLPPreflightError("RECEIPT_MANIFEST_PROVENANCE_MISMATCH")

    serialized = canonical_json(receipt)
    for forbidden in ("/Users/", "/Volumes/", "file://", "http://", "https://"):
        if forbidden in serialized:
            raise DLPPreflightError("RECEIPT_PATH_OR_URL_LEAK")
    body = dict(receipt)
    expected_hash = body.pop("body_sha256", None)
    if not isinstance(expected_hash, str) or expected_hash != sha256_text(
        canonical_json(body)
    ):
        raise DLPPreflightError("RECEIPT_BODY_SHA_INVALID")


def write_private_json(path: Path, payload: dict[str, Any]) -> bool:
    if not path.is_absolute() or path.is_symlink():
        raise DLPPreflightError("PRIVATE_OUTPUT_PATH_INVALID")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink():
        raise DLPPreflightError("PRIVATE_OUTPUT_PARENT_INVALID")
    parent_info = path.parent.stat()
    if hasattr(os, "getuid") and parent_info.st_uid != os.getuid():
        raise DLPPreflightError("PRIVATE_OUTPUT_PARENT_OWNER_INVALID")
    path.parent.chmod(0o700)
    if path.exists():
        existing = load_json(path, private=True, reason_prefix="PRIVATE_OUTPUT")
        if canonical_json(existing) == canonical_json(payload):
            return False
        raise DLPPreflightError("PRIVATE_OUTPUT_CONFLICT")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(0o600)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise
    return True


def _scan_specs(
    specs: list[tuple[str, Path]], *, private: bool
) -> tuple[dict[str, Any], list[Path]]:
    results = [
        scan_jsonl(path, logical_name, private=private)
        for logical_name, path in specs
    ]
    return aggregate_scan(results), [path for _logical_name, path in specs]


def command_init(args: argparse.Namespace) -> int:
    specs = parse_dataset_specs(args.dataset)
    synthetic = bool(args.allow_public_synthetic_fixtures)
    scan, paths = _scan_specs(specs, private=not synthetic)
    manifest = build_pending_manifest(
        dataset_id=args.dataset_id,
        scan=scan,
        source_paths=paths,
        created_at=utc_now(),
        synthetic=synthetic,
    )
    output = absolute_path(args.manifest_output)
    write_private_json(output, manifest)
    if not args.quiet:
        print(
            canonical_json(
                {
                    "status": "PENDING_RIGHTS_REVIEW",
                    "dataset_file_count": scan["dataset_file_count"],
                    "record_count": scan["record_count"],
                    "manifest_sha256": sha256_file(output),
                }
            )
        )
    return 0


def command_scan(args: argparse.Namespace) -> int:
    specs = parse_dataset_specs(args.dataset)
    manifest_path = absolute_path(args.rights_manifest)
    allow_public = bool(args.allow_public_synthetic_fixtures)
    manifest = load_json(manifest_path, private=not allow_public, reason_prefix="MANIFEST")
    validate_manifest_shape(manifest)
    if allow_public and manifest["dataset"]["data_class"] != "synthetic":
        raise DLPPreflightError("PUBLIC_FIXTURE_MODE_REQUIRES_SYNTHETIC_MANIFEST")
    if not allow_public and manifest["dataset"]["data_class"] != "private_line_derived":
        raise DLPPreflightError("PRIVATE_MODE_REQUIRES_PRIVATE_DATA_CLASS")
    scan, paths = _scan_specs(specs, private=not allow_public)
    receipt = build_receipt(
        manifest=manifest,
        manifest_sha256=sha256_file(manifest_path),
        scan=scan,
        source_paths=paths,
        created_at=utc_now(),
        scanner_sha256=sha256_file(Path(__file__).resolve()),
    )
    output = absolute_path(args.receipt_output)
    write_private_json(output, receipt)
    if not args.quiet:
        print(
            canonical_json(
                {
                    "status": receipt["status"],
                    "eligible_for_offline_training": receipt["eligible_for_offline_training"],
                    "reason_codes": receipt["reason_codes"],
                    "record_count": receipt["scan"]["record_count"],
                    "high_confidence_findings": receipt["scan"]["high_confidence_findings"],
                    "review_required_findings": receipt["scan"]["review_required_findings"],
                    "receipt_sha256": sha256_file(output),
                }
            )
        )
    return 0 if receipt["eligible_for_offline_training"] else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a PENDING rights manifest")
    init_parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        metavar="LOGICAL_NAME=ABSOLUTE_PATH",
    )
    init_parser.add_argument("--dataset-id", required=True)
    init_parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST_PATH))
    init_parser.add_argument("--allow-public-synthetic-fixtures", action="store_true")
    init_parser.add_argument("--quiet", action="store_true")
    init_parser.set_defaults(handler=command_init)

    scan_parser = subparsers.add_parser("scan", help="run aggregate-only DLP preflight")
    scan_parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        metavar="LOGICAL_NAME=ABSOLUTE_PATH",
    )
    scan_parser.add_argument("--rights-manifest", default=str(DEFAULT_MANIFEST_PATH))
    scan_parser.add_argument("--receipt-output", default=str(DEFAULT_RECEIPT_PATH))
    scan_parser.add_argument("--allow-public-synthetic-fixtures", action="store_true")
    scan_parser.add_argument("--quiet", action="store_true")
    scan_parser.set_defaults(handler=command_scan)
    return parser


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    try:
        args = build_parser().parse_args(argv)
        return int(args.handler(args))
    except DLPPreflightError as error:
        print(canonical_json({"status": "ERROR", "reason_code": str(error)}), file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print(
            canonical_json({"status": "ERROR", "reason_code": "LOCAL_IO_FAILURE"}),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
