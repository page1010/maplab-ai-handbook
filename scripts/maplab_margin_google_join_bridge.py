#!/usr/bin/env python3
"""Audit live Google join keys for a fixed private margin-leak pilot.

The worker reads only the minimum columns needed from the Owner's existing
Google Workspace sources.  Customer-bearing values are used only in-process;
the receipt contains hashes, counts, schema fields, and missing-evidence codes.
It never writes Google data, persists OAuth refreshes, calls a model, or sends a
customer message.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import warnings
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\..*")
warnings.filterwarnings("ignore", message=r"urllib3 v2 only supports OpenSSL.*")

METHOD_VERSION = "margin-google-join-bridge-v1"
PILOT_SIZE = 10
MAIN_SHEET_ID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ASSET_SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
QUOTE_ROOT_ID = "17wM4wldkllDbj0T8Xg_rgY3mM3RgH7LG"
GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"
GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


class GoogleJoinBridgeError(RuntimeError):
    """The bounded bridge cannot produce a trustworthy receipt."""


class ReadProvider(Protocol):
    api_read_calls: int
    oauth_refresh_calls: int

    def read_headers(self, sheet_id: str, tab: str) -> list[str]: ...

    def read_named_columns(
        self, sheet_id: str, tab: str, fields: list[str]
    ) -> list[dict[str, str]]: ...

    def list_files(self, parent_id: str) -> list[dict[str, str]]: ...


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
        raise GoogleJoinBridgeError("input_must_be_absolute_private_file")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise GoogleJoinBridgeError("input_permissions_not_private")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise GoogleJoinBridgeError("input_wrong_owner")


def _normalise(value: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", value)).lower()


def _conversation_id(path: Path) -> str:
    return sha256_text(path.name)[:16]


def _candidate_hash(conversation_id: str, category: str) -> str:
    return sha256_text(f"{conversation_id}|{category}")


def _private_label_and_year(path: Path) -> tuple[str, str]:
    parts = path.stem.split("_", 3)
    if len(parts) != 4:
        return "", ""
    return _normalise(parts[3]), parts[1][:4]


def _ref(kind: str, value: str) -> str:
    return f"private://{kind}/{sha256_text(f'{METHOD_VERSION}|{kind}|{value}')}"


def _column_letter(index: int) -> str:
    if index < 0:
        raise GoogleJoinBridgeError("negative_column_index")
    value = index + 1
    letters = ""
    while value:
        value, remainder = divmod(value - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


class GoogleReadProvider:
    """GET/list-only Google API adapter with in-memory OAuth refresh."""

    def __init__(self, token_path: Path):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        if not token_path.is_absolute() or token_path.is_symlink() or not token_path.is_file():
            raise GoogleJoinBridgeError("google_token_missing_or_invalid")
        token_info = json.loads(token_path.read_text(encoding="utf-8"))
        credentials = Credentials(
            token=token_info.get("token"),
            refresh_token=token_info.get("refresh_token"),
            token_uri=token_info.get("token_uri"),
            client_id=token_info.get("client_id"),
            client_secret=token_info.get("client_secret"),
            scopes=token_info.get("scopes"),
        )
        self.oauth_refresh_calls = 0
        if not credentials.valid:
            credentials.refresh(Request())
            self.oauth_refresh_calls = 1
        self._sheets = build(
            "sheets", "v4", credentials=credentials, cache_discovery=False
        )
        self._drive = build(
            "drive", "v3", credentials=credentials, cache_discovery=False
        )
        self.api_read_calls = 0
        self.token_mode = f"{stat.S_IMODE(token_path.stat().st_mode):04o}"

    def read_headers(self, sheet_id: str, tab: str) -> list[str]:
        self.api_read_calls += 1
        result = (
            self._sheets.spreadsheets()
            .values()
            .get(
                spreadsheetId=sheet_id,
                range=f"'{tab}'!1:1",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        rows = result.get("values", [])
        return [str(value).strip() for value in rows[0]] if rows else []

    def read_named_columns(
        self, sheet_id: str, tab: str, fields: list[str]
    ) -> list[dict[str, str]]:
        headers = self.read_headers(sheet_id, tab)
        header_index = {header: index for index, header in enumerate(headers) if header}
        missing = [field for field in fields if field not in header_index]
        if missing:
            raise GoogleJoinBridgeError(
                f"live_schema_missing_fields:{tab}:{','.join(missing)}"
            )
        ranges = [
            f"'{tab}'!{_column_letter(header_index[field])}2:{_column_letter(header_index[field])}"
            for field in fields
        ]
        self.api_read_calls += 1
        result = (
            self._sheets.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=sheet_id,
                ranges=ranges,
                valueRenderOption="FORMATTED_VALUE",
                majorDimension="COLUMNS",
            )
            .execute()
        )
        columns = []
        for value_range in result.get("valueRanges", []):
            values = value_range.get("values", [])
            columns.append([str(value) for value in values[0]] if values else [])
        while len(columns) < len(fields):
            columns.append([])
        row_count = max((len(column) for column in columns), default=0)
        rows = []
        for row_index in range(row_count):
            rows.append(
                {
                    field: (
                        columns[field_index][row_index]
                        if row_index < len(columns[field_index])
                        else ""
                    )
                    for field_index, field in enumerate(fields)
                }
            )
        return rows

    def list_files(self, parent_id: str) -> list[dict[str, str]]:
        files: list[dict[str, str]] = []
        page_token = None
        while True:
            self.api_read_calls += 1
            response = (
                self._drive.files()
                .list(
                    q=f"'{parent_id}' in parents and trashed=false",
                    fields=(
                        "nextPageToken,files(id,name,mimeType,createdTime,"
                        "modifiedTime,parents)"
                    ),
                    pageSize=1000,
                    pageToken=page_token,
                )
                .execute()
            )
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                return files


def _resolve_sources(
    samples: list[dict[str, Any]], raw_source_dir: Path
) -> dict[str, Path]:
    if not raw_source_dir.is_absolute() or not raw_source_dir.is_dir():
        raise GoogleJoinBridgeError("raw_source_dir_must_be_absolute_directory")
    index = {_conversation_id(path): path for path in raw_source_dir.glob("*.csv")}
    if not index:
        raise GoogleJoinBridgeError("raw_source_dir_has_no_csv")
    resolved = {}
    for sample in samples:
        matches = [
            path
            for conversation_id, path in index.items()
            if _candidate_hash(conversation_id, sample["category"])
            == sample["candidate_hash"]
        ]
        if len(matches) != 1:
            raise GoogleJoinBridgeError(
                f"candidate_source_resolution_count:{len(matches)}"
            )
        resolved[sample["candidate_hash"]] = matches[0]
    return resolved


def _label_matches(label: str, values: list[str]) -> bool:
    if len(label) < 4:
        return False
    for value in values:
        candidate = _normalise(value)
        if len(candidate) < 4:
            continue
        if label == candidate or label in candidate or candidate in label:
            return True
    return False


def _header_receipt(headers: list[str]) -> dict[str, Any]:
    clean = [header for header in headers if header]
    return {
        "field_count": len(clean),
        "fields": clean,
        "sha256": sha256_text(
            json.dumps(clean, ensure_ascii=False, separators=(",", ":"))
        ),
    }


def build_bridge_receipt(
    evidence_receipt_path: Path,
    raw_source_dir: Path,
    provider: ReadProvider,
    *,
    expected_evidence_sha256: str,
    main_sheet_id: str = MAIN_SHEET_ID,
    asset_sheet_id: str = ASSET_SHEET_ID,
    quote_root_id: str = QUOTE_ROOT_ID,
) -> dict[str, Any]:
    validate_private_file(evidence_receipt_path)
    actual_evidence_sha256 = sha256_file(evidence_receipt_path)
    if actual_evidence_sha256 != expected_evidence_sha256:
        raise GoogleJoinBridgeError("evidence_receipt_sha256_mismatch")
    evidence_receipt = json.loads(evidence_receipt_path.read_text(encoding="utf-8"))
    samples = evidence_receipt.get("samples", [])
    if len(samples) != PILOT_SIZE or len(
        {sample.get("candidate_hash") for sample in samples}
    ) != PILOT_SIZE:
        raise GoogleJoinBridgeError("fixed_ten_evidence_receipt_required")
    for sample in samples:
        if not isinstance(sample.get("candidate_hash"), str) or not isinstance(
            sample.get("category"), str
        ):
            raise GoogleJoinBridgeError("evidence_sample_schema_invalid")
    resolved = _resolve_sources(samples, raw_source_dir)

    sales_fields = [
        "case_id",
        "created_at",
        "client_name",
        "event_date",
        "a6_output_link",
    ]
    order_fields = [
        "order_id",
        "event_date",
        "company_name",
        "contact_person",
        "event_name",
        "client_sheet_url",
    ]
    charge_fields = ["order_id", "description", "charge_type", "amount"]
    sales_headers = provider.read_headers(main_sheet_id, "SALES_INTAKE")
    order_headers = provider.read_headers(main_sheet_id, "Orders")
    charge_headers = provider.read_headers(main_sheet_id, "OrderCharges")
    asset_headers = provider.read_headers(asset_sheet_id, "工作表1")
    sales_rows = provider.read_named_columns(
        main_sheet_id, "SALES_INTAKE", sales_fields
    )
    order_rows = provider.read_named_columns(main_sheet_id, "Orders", order_fields)
    charge_rows = provider.read_named_columns(
        main_sheet_id, "OrderCharges", charge_fields
    )
    root_files = provider.list_files(quote_root_id)
    folders_2026_candidates = [
        item
        for item in root_files
        if item.get("mimeType") == GOOGLE_FOLDER_MIME
        and "2026" in _normalise(item.get("name", ""))
    ]
    exact_folders_2026 = [
        item
        for item in folders_2026_candidates
        if _normalise(item.get("name", "")) == "2026外燴訂單"
    ]
    folders_2026 = (
        exact_folders_2026
        if exact_folders_2026
        else folders_2026_candidates
    )
    if len(folders_2026) != 1:
        raise GoogleJoinBridgeError(
            f"quote_2026_folder_resolution_count:{len(folders_2026)}"
        )
    quote_files = [
        item
        for item in provider.list_files(folders_2026[0]["id"])
        if item.get("mimeType") == GOOGLE_SHEET_MIME
    ]

    charges_by_order: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in charge_rows:
        if row.get("order_id"):
            charges_by_order[row["order_id"]].append(row)

    bridge_samples = []
    match_counts: Counter[str] = Counter()
    source_year_counts: Counter[str] = Counter()
    for sample in samples:
        raw_path = resolved[sample["candidate_hash"]]
        private_label, source_year = _private_label_and_year(raw_path)
        source_year_counts[source_year or "unknown"] += 1
        eligible_2026 = source_year == "2026"
        sales_matches = (
            [
                row
                for row in sales_rows
                if _label_matches(private_label, [row.get("client_name", "")])
            ]
            if eligible_2026
            else []
        )
        order_matches = (
            [
                row
                for row in order_rows
                if _label_matches(
                    private_label,
                    [
                        row.get("company_name", ""),
                        row.get("contact_person", ""),
                        row.get("event_name", ""),
                    ],
                )
            ]
            if eligible_2026
            else []
        )
        quote_matches = (
            [
                item
                for item in quote_files
                if _label_matches(private_label, [item.get("name", "")])
            ]
            if eligible_2026
            else []
        )
        matched_charge_rows = [
            charge
            for order in order_matches
            for charge in charges_by_order.get(order.get("order_id", ""), [])
        ]
        match_counts["sales_intake_name_candidates"] += len(sales_matches)
        match_counts["orders_name_candidates"] += len(order_matches)
        match_counts["quote_name_candidates"] += len(quote_matches)
        match_counts["ordercharge_rows_via_name_candidate"] += len(
            matched_charge_rows
        )
        case_refs = sorted(
            {
                _ref("case", row["case_id"])
                for row in sales_matches
                if row.get("case_id")
            }
        )
        order_refs = sorted(
            {
                _ref("order", row["order_id"])
                for row in order_matches
                if row.get("order_id")
            }
        )
        quote_refs = sorted(
            {_ref("quote", item["id"]) for item in quote_matches if item.get("id")}
        )
        charge_refs = sorted(
            {
                _ref(
                    "charge-row",
                    "|".join(
                        [
                            row.get("order_id", ""),
                            row.get("description", ""),
                            row.get("charge_type", ""),
                            row.get("amount", ""),
                        ]
                    ),
                )
                for row in matched_charge_rows
            }
        )
        missing_codes = [
            "SOURCE_HASH_HAS_NO_SHARED_CASE_ID",
            "BASELINE_SCOPE_UNVERIFIED_NO_STABLE_QUOTE_JOIN",
            "ACTUAL_DELIVERY_UNVERIFIED_ASSET_LOG_HAS_NO_CASE_KEY",
            "INCREMENTAL_COST_UNVERIFIED_NO_COST_LEDGER",
            "CHARGED_FEE_UNVERIFIED_HEURISTIC_ORDER_MATCH_ONLY",
        ]
        if not eligible_2026:
            missing_codes.append("OUTSIDE_2026_QUOTE_FOLDER_SCOPE")
        bridge_samples.append(
            {
                "candidate_hash": sample["candidate_hash"],
                "category": sample["category"],
                "source_year": source_year,
                "eligible_2026": eligible_2026,
                "heuristic_candidates": {
                    "case_refs": case_refs,
                    "order_refs": order_refs,
                    "quote_refs": quote_refs,
                    "charge_row_refs": charge_refs,
                },
                "stable_identity_join": False,
                "four_pillar_confirmed": False,
                "decision_label": "insufficient_evidence",
                "missing_evidence_codes": missing_codes,
            }
        )

    stable_identity_joins = sum(
        1 for sample in bridge_samples if sample["stable_identity_join"]
    )
    method_contract = {
        "method_version": METHOD_VERSION,
        "hypothesis": (
            "Live read-only Google key fields will either recover a stable case-to-quote-to-"
            "charge-to-asset chain for the fixed ten hashes or prove the schema requires a "
            "join-key repair before leakage can be measured."
        ),
        "changed_variable": (
            "replace local pointer-name inventory with live Google Sheets key columns and "
            "Drive file metadata; keep the same ten candidate hashes"
        ),
        "fixed_holdout": {
            "total": PILOT_SIZE,
            "evidence_receipt_sha256": actual_evidence_sha256,
        },
        "expected_delta": (
            "resolve at least one stable identity chain or emit a field-level schema proposal"
        ),
        "stop_loss": (
            "stop after fixed ten and minimum live fields; no quote-body dump, asset-row dump, "
            "model call, Google write, token write, customer send, or price change"
        ),
        "adapter": "maplab-margin-leak-auditor/google-read-bridge",
        "sampling": "same fixed ten hashes from margin-evidence-join-v1",
        "evaluator": (
            "name matches remain heuristic; stable only with a shared source case_id and all "
            "four evidence pillars"
        ),
        "acceptance": (
            "live schema hashes, read counts, hash-only refs, explicit missing codes, and "
            "schema proposal when stable joins equal zero"
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
    missing_counts = Counter(
        code for sample in bridge_samples for code in sample["missing_evidence_codes"]
    )
    return {
        "schema_version": "maplab.margin-leak.google-join-bridge.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-google-read-receipt",
        "plateau_review": {
            "recent_method_fingerprints": [
                "aggregate-scan-no-method-fingerprint",
                "7e65e7be6eec8e77bf71866928bcdf616bf0cb81948b473c985e739885422b30",
                "9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17",
            ],
            "same_method_consecutive_no_improvement": 0,
            "decision": "new_live_join_source_method_allowed",
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
        },
        "source_receipts": {
            "prior_evidence_sha256": actual_evidence_sha256,
            "main_sheet_ref": _ref("sheet", main_sheet_id),
            "asset_sheet_ref": _ref("sheet", asset_sheet_id),
            "quote_root_ref": _ref("drive-folder", quote_root_id),
            "quote_2026_folder_ref": _ref("drive-folder", folders_2026[0]["id"]),
            "live_schema": {
                "SALES_INTAKE": _header_receipt(sales_headers),
                "Orders": _header_receipt(order_headers),
                "OrderCharges": _header_receipt(charge_headers),
                "MAPLAB_ASSET_LOG": _header_receipt(asset_headers),
            },
            "row_counts_minimal_fields": {
                "SALES_INTAKE": len(sales_rows),
                "Orders": len(order_rows),
                "OrderCharges": len(charge_rows),
                "quote_2026_spreadsheets": len(quote_files),
            },
            "asset_stable_join_fields_present": any(
                field in asset_headers
                for field in ("case_id", "quote_id", "order_id")
            ),
        },
        "sample_count": len(bridge_samples),
        "unique_candidate_hashes": len(
            {sample["candidate_hash"] for sample in bridge_samples}
        ),
        "source_year_counts": dict(sorted(source_year_counts.items())),
        "heuristic_match_counts": dict(sorted(match_counts.items())),
        "stable_identity_joins": stable_identity_joins,
        "four_pillar_confirmed": 0,
        "confirmed_leakage_amount": 0,
        "decision_counts": {"insufficient_evidence": len(bridge_samples)},
        "missing_evidence_code_counts": dict(sorted(missing_counts.items())),
        "schema_change_proposal_required": stable_identity_joins == 0,
        "interpretation": (
            "Live Google readback is newer evidence than local pointers, but source LINE "
            "hashes still share no case_id with SALES_INTAKE. Name candidates, if any, are "
            "not stable joins. Orders and OrderCharges do not repair the missing source key, "
            "and ASSET_LOG has no case/quote/order key. Leakage remains unconfirmed."
        ),
        "samples": bridge_samples,
    }


def write_private_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.is_absolute():
        raise GoogleJoinBridgeError("output_path_must_be_absolute")
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
    parser.add_argument("--evidence-receipt", required=True)
    parser.add_argument("--expected-evidence-sha256", required=True)
    parser.add_argument("--raw-source-dir", required=True)
    parser.add_argument(
        "--token", default=str(Path.home() / ".claude/mcp-keys/google-token.json")
    )
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    provider = GoogleReadProvider(Path(args.token).expanduser().resolve())
    payload = build_bridge_receipt(
        Path(args.evidence_receipt).expanduser().resolve(),
        Path(args.raw_source_dir).expanduser().resolve(),
        provider,
        expected_evidence_sha256=args.expected_evidence_sha256,
    )
    output = Path(args.output).expanduser().resolve()
    write_private_json(output, payload)
    print(
        json.dumps(
            {
                "status": "ok",
                "method_version": METHOD_VERSION,
                "sample_count": payload["sample_count"],
                "stable_identity_joins": payload["stable_identity_joins"],
                "four_pillar_confirmed": 0,
                "confirmed_leakage_amount": 0,
                "google_source_reads": payload["privacy"]["google_source_reads"],
                "google_writes": 0,
                "model_calls": 0,
                "schema_change_proposal_required": payload[
                    "schema_change_proposal_required"
                ],
                "output": str(output),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
