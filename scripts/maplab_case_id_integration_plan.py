#!/usr/bin/env python3
"""Validate the proposal-only MAPLAB case-id integration plan.

This module never contacts Google, LINE, a model, or a customer-facing system.
It performs three bounded checks only:

1. fail closed when the repo source anchors used by the plan drift;
2. exercise synthetic named-header, outbox, and privacy-route fixtures; and
3. write an aggregate-only private receipt with hashes and status codes.

It is deliberately not a production adapter.  Passing this validator does not
authorize a GAS deployment, a Sheet schema change, a message, or a history
rewrite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "maplab.margin.case-id-integration-plan-receipt.v1"
METHOD_VERSION = "margin-case-id-integration-plan-v1"
DATA_CLASS = "synthetic-local-integration-plan-receipt"
PLAN_PATH = Path("docs/margin-leak-case-id-integration-plan.md")
PINNED_PLAN_SHA256 = "e93da7d1c480112118d1e803fc1809faa1129db7101a52b9454cda33bbeb2695"
REQUIRED_PLAN_HEADINGS = (
    "## Exact current-source map",
    "## Target identity envelope",
    "## Named-header targets",
    "## Durable outbox and readback gate",
    "## Ordered migration and rollback",
    "## Fixture compatibility matrix",
    "## Private-local-only quote routing",
    "## Deployed-source truth boundary",
)
REQUIRED_PLAN_TERMS = {
    "case_open_authority": "case-open authority",
    "quote_registry_cardinality": "QUOTE_REGISTRY",
    "owner_only_modes": "0700/0600",
    "endpoint_auth": "authenticated",
    "header_capable_ingress": "header-capable ingress",
    "orphan_recovery": "orphan",
    "post_cutover_freeze": "freeze new quote writes",
}
PINNED_SOURCE_SHA256 = {
    "scripts/apps-script/LineWebhook.gs": "e508571af06fc887dcd016947c5f02aab7cbbbc65dbb070425e4220858131184",
    "scripts/apps-script/.claspignore": "165d9c88aeaca43de6dccff90eaa0320ccde8de469ce31eb41bd1763c9f715f2",
    "scripts/apps-script/README.md": "0fbccbebeab481a10b75df82bcf9ee6c12cdb0e8426a5fa631dd7d9d115c2cf9",
    "bot_a6/case_store.py": "5e1e934d3adb1f7d918d72eeef0ef6cc5632d7c52a0d9c52a7138a4772f35007",
    "bot_a6/a5_quote_engine.py": "91b2092713b2c2952fc110171a1e06a2ba33aafd7167ea50d64f6486303668a4",
    "bot_a6/bot_a6.py": "0ad1bba2aa94267427276663695cfabbc8f75e75f06878a8fa46cdeed0cc6774",
    "scripts/apps-script/Code.gs": "f7dcb4d4b673e3a74a97d00b15621a427451795e6295cd95bcf29fe379c2fbc3",
    "scripts/apps-script/ApiEndpoint.gs": "bffd474cb10aa1d39115ac01ffc8445177d628b795c285486ac93cfcdfc87754",
    "scripts/a4_s11_2024_resume_classifier.py": "14786afe66696a8c7977d2d7703fb786201c60b7f84d2024dfe81999f2bb09b8",
    "tools/ai_workbook/openclaw_adapter.py": "e02ccbd0db33fa277640924171f81c5bb336afe715acf1f48cc46f5de0808aa4",
    "tools/ai_workbook/paths.py": "ed2663e28fe3530f5c5151d30173dd942254b001d0b4443c4b3d4952314b9a2a",
}


@dataclass(frozen=True)
class SourceAnchor:
    anchor_id: str
    path: str
    function: str
    required_fragments: tuple[str, ...]
    current_risk_code: str


SOURCE_ANCHORS = (
    SourceAnchor(
        "line_blank_case_id",
        "scripts/apps-script/LineWebhook.gs",
        "handleLineWebhook_",
        (
            "function handleLineWebhook_(e)",
            "Utilities.getUuid()",
            "// B: case_id（業務填入）",
            "processed_line_msg_ids",
        ),
        "CASE_ID_BLANK_AT_INGRESS",
    ),
    SourceAnchor(
        "line_deploy_source_boundary",
        "scripts/apps-script/.claspignore",
        "clasp source selection",
        ("LineWebhook.gs",),
        "REPO_LINE_SOURCE_EXCLUDED_FROM_CLASP",
    ),
    SourceAnchor(
        "line_declared_project_boundary",
        "scripts/apps-script/README.md",
        "declared LINE GAS checkout",
        ("scripts/apps-script-line/",),
        "DECLARED_LINE_PROJECT_PATH_MISSING",
    ),
    SourceAnchor(
        "line_webhook_signature_boundary",
        "scripts/apps-script/LineWebhook.gs",
        "getConfig_ / handleLineWebhook_",
        (
            "channelSecret: props.getProperty('LINE_CHANNEL_SECRET')",
            "function handleLineWebhook_(e)",
            "const body = JSON.parse(e.postData.contents)",
        ),
        "LINE_WEBHOOK_SIGNATURE_UNVERIFIED",
    ),
    SourceAnchor(
        "case_store_sliding_window",
        "bot_a6/case_store.py",
        "fetch_conversation_log_rows",
        (
            "def fetch_conversation_log_rows(max_rows: int = 600)",
            "start_index = max(0, len(data_rows) - max_rows)",
        ),
        "SLIDING_WINDOW_IDENTITY_DRIFT",
    ),
    SourceAnchor(
        "case_store_derived_key",
        "bot_a6/case_store.py",
        "_case_from_cluster",
        (
            "def _case_from_cluster(",
            'f"LINE-{date_key}-{_line_hash(line_user_id)}-{first.row_number}"',
        ),
        "DERIVED_CASE_ID_NOT_CANONICAL",
    ),
    SourceAnchor(
        "a5_payload_case_key",
        "bot_a6/a5_quote_engine.py",
        "_build_basic_high_margin_quote_payload",
        (
            "def build_sheet_quote_payload(",
            '"caseId": tracking["case_id"]',
            "def _extract_quote_tracking_fields(",
        ),
        "CASE_KEY_IS_OPTIONAL_TEXT_EXTRACTION",
    ),
    SourceAnchor(
        "casequote_private_context",
        "bot_a6/bot_a6.py",
        "casequote_cmd",
        (
            "async def casequote_cmd(",
            "store.build_quote_context(query)",
            'f"/localquote {context_text}"',
        ),
        "PRIVATE_GUARD_IMPLICIT_PREFIX_ONLY",
    ),
    SourceAnchor(
        "a5_general_cloud_branch",
        "bot_a6/bot_a6.py",
        "_run_a5_quote_background",
        (
            "async def _run_a5_quote_background(",
            'force_local = user_message.strip().startswith("/localquote")',
            "cloud_answer = await a5_cloud_quote_ask(",
        ),
        "PRIVATE_ROUTE_RELIES_ON_COMMAND_PREFIX_NOT_DATA_CLASS",
    ),
    SourceAnchor(
        "quote_regenerates_case_key",
        "scripts/apps-script/Code.gs",
        "createQuote",
        (
            "function createQuote(formData)",
            "var caseId = 'Q' + Utilities.formatDate(",
            "writeToIntake_(ss, caseId, formData, newUrl, now)",
        ),
        "QUOTE_REPLACES_PARENT_CASE_KEY",
    ),
    SourceAnchor(
        "quote_copy_precedes_intake_ack",
        "scripts/apps-script/Code.gs",
        "createQuote",
        (
            "var newFile = sourceFile.makeCopy(newFileName, yearFolder)",
            "writeToIntake_(ss, caseId, formData, newUrl, now)",
        ),
        "COPY_BEFORE_INTAKE_CAN_ORPHAN_ON_RESPONSE_LOSS",
    ),
    SourceAnchor(
        "quote_variants_repeat_create",
        "scripts/apps-script/Code.gs",
        "createQuoteVariants_",
        (
            "function createQuoteVariants_(body)",
            "var created = createQuote(formData)",
            "caseId: created.caseId",
        ),
        "VARIANTS_CAN_SPLIT_OR_COLLIDE_CASE_ID",
    ),
    SourceAnchor(
        "sales_intake_positional_writer",
        "scripts/apps-script/Code.gs",
        "writeToIntake_",
        (
            "function writeToIntake_(ss, caseId, formData, sheetUrl, now)",
            "intakeSheet.getRange(lastRow, 1, 1, row.length).setValues([row])",
        ),
        "POSITIONAL_WRITE_HEADER_DRIFT",
    ),
    SourceAnchor(
        "quote_http_entry_drops_parent_key",
        "scripts/apps-script/Code.gs",
        "handleQuoteRequest_",
        (
            "function handleQuoteRequest_(params)",
            "var formData = {",
            "var result = createQuote(formData)",
        ),
        "HTTP_ENTRY_DOES_NOT_COPY_CASE_ID",
    ),
    SourceAnchor(
        "quote_http_auth_idempotency_boundary",
        "scripts/apps-script/ApiEndpoint.gs",
        "doPost",
        (
            "function doPost(e)",
            "var body = JSON.parse(e.postData.contents)",
            "return handleQuoteRequest_(body)",
            "var variantsResult = createQuoteVariants_(body)",
        ),
        "HTTP_ENTRY_HAS_NO_VISIBLE_AUTH_OR_IDEMPOTENCY_GATE",
    ),
    SourceAnchor(
        "quote_http_client_auth_boundary",
        "bot_a6/bot_a6.py",
        "_trigger_gas_quote_sync",
        (
            "def _trigger_gas_quote_sync(form_data: dict)",
            'headers={"Content-Type": "application/json"}',
            "urllib.request.urlopen(req, timeout=60)",
        ),
        "HTTP_CLIENT_SENDS_NO_VISIBLE_SIGNATURE_OR_IDEMPOTENCY_HEADER",
    ),
    SourceAnchor(
        "case_store_private_file_boundary",
        "bot_a6/case_store.py",
        "CaseStore.__init__ / from_env",
        (
            "self.db_path.parent.mkdir(parents=True, exist_ok=True)",
            'repo / "data" / "case-store" / "a6_case_store.sqlite3"',
        ),
        "CASE_STORE_OWNER_ONLY_MODE_NOT_ENFORCED",
    ),
    SourceAnchor(
        "a5_review_bundle_raw_context",
        "tools/ai_workbook/openclaw_adapter.py",
        "OpenClawAdapter.run_local_task",
        (
            "bundle_dir = REVIEWS_DIR / job_id",
            "bundle_dir.mkdir(parents=True, exist_ok=True)",
            "task_request_path.write_text(",
            "output_json_path.write_text(",
            "terminal_log.write_text(",
        ),
        "RAW_PRIVATE_CONTEXT_CAN_LAND_IN_REPO_REVIEW_BUNDLE",
    ),
    SourceAnchor(
        "a5_review_bundle_repo_root",
        "tools/ai_workbook/paths.py",
        "REVIEWS_DIR",
        (
            'WORKBOOK_DIR = ROOT / "workbook"',
            'REVIEWS_DIR = WORKBOOK_DIR / "reviews"',
        ),
        "PRIVATE_ARTIFACT_ROOT_IS_INSIDE_REPO",
    ),
    SourceAnchor(
        "asset_log_append_writer",
        "scripts/a4_s11_2024_resume_classifier.py",
        "sheet_append_rows / _flush_pending",
        (
            "def sheet_append_rows(rows: list[list[str]])",
            'f"{SHEET_TAB}!A:G"',
            "insertDataOption=INSERT_ROWS",
            "def _flush_pending(",
        ),
        "ASSET_APPEND_RETRY_CAN_DUPLICATE",
    ),
)


TARGET_HEADERS = {
    "SALES_INTAKE": (
        "case_id",
        "drive_case_folder_id",
        "scope_version",
        "scope_confirmed_at",
        "contract_version",
        "payload_fingerprint",
        "idempotency_key",
    ),
    "QUOTE_REGISTRY": (
        "quote_id",
        "quote_group_id",
        "case_id",
        "quote_spreadsheet_id",
        "variant_label",
        "idempotency_key",
        "contract_version",
        "payload_fingerprint",
    ),
    "Orders": (
        "order_id",
        "case_id",
        "quote_id",
        "scope_version",
        "scope_confirmed_at",
        "drive_case_folder_id",
        "contract_version",
        "payload_fingerprint",
        "idempotency_key",
    ),
    "OrderCharges": (
        "charge_id",
        "order_id",
        "case_id",
        "quote_id",
        "idempotency_key",
        "source_evidence_hash",
        "contract_version",
        "payload_fingerprint",
    ),
    "MAPLAB_ASSET_LOG": (
        "file_id",
        "origin_case_id",
        "quote_id",
        "order_id",
        "delivery_type",
        "delivered_at",
        "delivery_verified_by",
        "contract_version",
        "payload_fingerprint",
        "idempotency_key",
    ),
}


CURRENT_SAFE_HEADER_FIXTURES = {
    "SALES_INTAKE": (
        "case_id",
        "created_at",
        "source",
        "client_name",
        "client_phone",
        "event_type",
        "event_date",
        "pax",
        "budget",
        "location",
        "raw_request",
        "status",
        "assigned_to",
        "a6_output_link",
        "notes",
    ),
    "QUOTE_REGISTRY": (),
    "Orders": (
        "order_id",
        "event_date",
        "time_start",
        "time_end",
        "company_name",
        "tax_id",
        "contact_person",
        "contact_phone",
        "event_name",
        "venue",
        "address",
        "headcount",
        "project_owner",
        "deal_status",
        "quote_stage",
        "base_food_amount",
        "service_fee_amount",
        "rental_amount",
        "extra_amount",
        "discount_amount",
        "tax_amount",
        "total_amount",
        "deposit_amount",
        "paid_amount",
        "balance_amount",
        "payment_status",
        "invoice_status",
        "client_sheet_url",
        "internal_note",
    ),
    "OrderCharges": ("order_id", "description", "charge_type", "amount"),
    "MAPLAB_ASSET_LOG": (
        "file_id",
        "original_name",
        "seo_name",
        "category",
        "keywords",
        "alt_text",
        "drive_url",
        "8549",
        "year",
        "file_type",
        "daily_sub",
        "status",
        "error",
        "40292",
    ),
}


PINNED_LIVE_HEADER_SHA256 = {
    "SALES_INTAKE": "b1ac8e43777ffe23e17dc4e0303b07b9d0cc1cbe7de46de03786865c7b3245fd",
    "Orders": "672d0fa668a436d57a5f8593339839e22c347aabfa2600d00ac59e0bfa2b363e",
    "OrderCharges": "2b34bd9c0b10b6ff00111ac9724d2e72b2567366491b487bf58dc53114fae949",
    "MAPLAB_ASSET_LOG": "8ce84e88737b3d906ea1b789a2964a05d499cd3909d46b0906ecc3f7705ff9c9",
}


FIXTURE_IDS = (
    "current_sales_intake_headers",
    "current_quote_registry_headers",
    "current_orders_headers",
    "current_ordercharges_headers",
    "current_maplab_asset_log_headers",
    "reordered_target_headers",
    "nfkc_target_headers",
    "duplicate_case_header",
    "wrong_schema_version_headers",
    "private_cloud_route",
    "private_local_route",
    "private_non_loopback_route",
    "private_unsafe_artifact_mode",
    "private_cloud_environment",
    "private_proxy_environment",
    "private_provider_override",
    "private_model_override",
    "private_repo_artifact_root",
    "private_allow_cloud_flag",
    "unknown_data_class",
    "customer_formula_injection",
    "controlled_status_formula",
    "outbox_readback_commit",
    "outbox_missing_readback",
    "outbox_payload_conflict",
)


METHOD_CONTRACT = {
    "hypothesis": (
        "an exact repo-anchor map plus synthetic compatibility gates can expose "
        "the safe migration boundary without touching live systems"
    ),
    "changed_variable": "integration_surface_mapping_not_identity_inference",
    "fixed_holdout": FIXTURE_IDS,
    "expected_delta": (
        "all source anchors mapped; current incompatible schemas and unsafe "
        "routes rejected; safe synthetic fixtures accepted"
    ),
    "stop_loss": (
        "any missing source anchor, unsafe fixture accepted, safe fixture "
        "rejected, or receipt allowlist failure sets adoption_status HOLD"
    ),
    "model": "none",
    "sampling": "none",
    "evaluator": "deterministic_source_and_fixture_validator_v1",
    "acceptance": "all_anchors_and_all_expected_fixture_outcomes",
}


DEPLOYED_BOUNDARY_CODES = (
    "REPO_LINE_SOURCE_EXCLUDED_FROM_CLASP",
    "DECLARED_LINE_PROJECT_PATH_MISSING",
    "LINE_WEBHOOK_SIGNATURE_UNVERIFIED",
    "GAS_WEB_APP_HEADER_UNAVAILABLE_FOR_LINE_SIGNATURE",
    "QUOTE_ENDPOINT_AUTH_IDEMPOTENCY_UNVERIFIED",
    "PRIVATE_REPO_ARTIFACT_SINK_UNSAFE",
    "ORDERS_WRITER_NOT_FOUND_IN_INSPECTED_PATHS",
    "LIVE_HEADERS_FROM_PRIOR_READ_ONLY_RECEIPT_ONLY",
    "NO_DEPLOYMENT_OR_LIVE_WRITE_READBACK_PERFORMED",
)


SAFE_SAFETY = {
    "contains_raw_text": False,
    "contains_customer_identifiers": False,
    "contains_source_conversation_ids": False,
    "contains_customer_bearing_paths": False,
    "contains_raw_case_ids": False,
    "contains_raw_google_ids": False,
    "external_network_calls": 0,
    "model_calls": 0,
    "google_reads": 0,
    "google_writes": 0,
    "customer_send": False,
    "price_system_write": False,
    "historical_mutations": 0,
    "new_third_party_private_data_egress": False,
}


PLATEAU_REVIEW = {
    "prior_method_fingerprints": (
        "9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17",
        "8c96645e45090a62ab6d3a19c3b945fb1f24459d6920e5741edee2e04fdf4ff1",
        "cfe227ba61206a7a1825aa9a960054fe8f9ca6858ac8152819a4ab6c36e09ae0",
        "a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123",
    ),
    "same_method_repeated": False,
    "historical_fuzzy_backfill_reopened": False,
    "new_repair_point": "exact_source_to_adapter_integration_plan",
}


class IntegrationPlanError(RuntimeError):
    """Fail-closed validation error with a stable machine code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}" if detail else code)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _header_sha256(headers: Iterable[str]) -> str:
    clean = [header for header in headers if header]
    payload = json.dumps(clean, ensure_ascii=False, separators=(",", ":"))
    return _sha256_bytes(payload.encode("utf-8"))


def live_header_fixture_inventory() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for table, pinned in PINNED_LIVE_HEADER_SHA256.items():
        headers = CURRENT_SAFE_HEADER_FIXTURES[table]
        actual = _header_sha256(headers)
        results.append(
            {
                "table": table,
                "field_count": len([value for value in headers if value]),
                "sha256": actual,
                "pinned_sha256": pinned,
                "matches_pinned": actual == pinned,
            }
        )
    return results


def deployment_source_inventory(repo_root: Path) -> dict[str, Any]:
    declared = repo_root / "scripts" / "apps-script-line"
    ignore = repo_root / "scripts" / "apps-script" / ".claspignore"
    ignored_text = ignore.read_text(encoding="utf-8") if ignore.is_file() else ""
    declared_exists_or_symlink = declared.exists() or declared.is_symlink()
    declared_trusted_directory = declared.is_dir() and not declared.is_symlink()
    line_excluded = "LineWebhook.gs" in {
        line.strip() for line in ignored_text.splitlines() if line.strip()
    }
    return {
        "declared_line_project_path": "scripts/apps-script-line",
        "declared_line_project_exists_or_symlink": declared_exists_or_symlink,
        "declared_line_project_trusted_directory": declared_trusted_directory,
        "quote_clasp_excludes_line_webhook": line_excluded,
        "status": (
            "EXPECTED_UNRESOLVED_BOUNDARY"
            if not declared_exists_or_symlink and line_excluded
            else "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED"
        ),
    }


def method_fingerprint() -> str:
    return _sha256_bytes(
        _canonical_json(
            {
                "method_version": METHOD_VERSION,
                "method_contract": METHOD_CONTRACT,
                "anchor_ids": [anchor.anchor_id for anchor in SOURCE_ANCHORS],
                "pinned_source_sha256": PINNED_SOURCE_SHA256,
                "pinned_live_header_sha256": PINNED_LIVE_HEADER_SHA256,
                "required_plan_headings": REQUIRED_PLAN_HEADINGS,
                "pinned_plan_sha256": PINNED_PLAN_SHA256,
                "target_headers": TARGET_HEADERS,
            }
        )
    )


def validate_named_headers(
    actual: Iterable[object],
    required: Iterable[str],
    *,
    schema_version: str = "case-id-linkage-v1",
    expected_schema_version: str = "case-id-linkage-v1",
) -> tuple[bool, tuple[str, ...]]:
    values = list(actual)
    codes: list[str] = []
    if not values:
        return False, ("HEADER_EMPTY",)

    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str):
            codes.append("HEADER_NON_STRING")
            continue
        clean = unicodedata.normalize("NFKC", value).strip()
        if not clean:
            codes.append("HEADER_BLANK")
        elif clean.isdigit():
            codes.append("HEADER_NUMERIC")
        normalized.append(clean)

    seen: set[str] = set()
    for value in normalized:
        folded = value.casefold()
        if folded in seen:
            codes.append("HEADER_DUPLICATE")
        seen.add(folded)

    present = {value.casefold() for value in normalized}
    if any(field.casefold() not in present for field in required):
        codes.append("REQUIRED_HEADER_MISSING")
    if schema_version != expected_schema_version:
        codes.append("SCHEMA_VERSION_MISMATCH")
    return not codes, tuple(sorted(set(codes)))


def validate_sheet_cell(value: object, *, controlled_formula: bool = False) -> str:
    if not isinstance(value, str):
        return "LITERAL_VALUE"
    normalized = unicodedata.normalize("NFKC", value).lstrip()
    if normalized.startswith(("=", "+", "-", "@")) and not controlled_formula:
        raise IntegrationPlanError("UNTRUSTED_FORMULA_FORBIDDEN")
    return "CONTROLLED_FORMULA" if controlled_formula else "LITERAL_VALUE"


def inspect_plan_contract(repo_root: Path) -> dict[str, Any]:
    raw_path = repo_root / PLAN_PATH
    path = raw_path.resolve()
    root = repo_root.resolve()
    safe_path = not raw_path.is_symlink() and path.is_relative_to(root)
    content = path.read_text(encoding="utf-8") if safe_path and path.is_file() else ""
    missing_headings = [heading for heading in REQUIRED_PLAN_HEADINGS if heading not in content]
    missing_terms = [
        gate_id for gate_id, term in REQUIRED_PLAN_TERMS.items() if term not in content
    ]
    plan_sha = _sha256_bytes(content.encode("utf-8")) if content else None
    pinned_matches = bool(plan_sha and plan_sha == PINNED_PLAN_SHA256)
    return {
        "path": str(PLAN_PATH),
        "present": bool(content),
        "sha256": plan_sha,
        "pinned_sha256": PINNED_PLAN_SHA256,
        "pinned_sha256_matches": pinned_matches,
        "required_heading_count": len(REQUIRED_PLAN_HEADINGS),
        "missing_heading_ids": tuple(missing_headings),
            "required_gate_count": len(REQUIRED_PLAN_TERMS),
        "missing_gate_ids": tuple(missing_terms),
        "status": (
            "PRESENT"
            if content and pinned_matches and not missing_headings and not missing_terms
            else "DRIFT"
        ),
    }


class SyntheticOutbox:
    """Tiny fixture-only state machine for write/readback semantics."""

    def __init__(self) -> None:
        self._rows: dict[str, tuple[str, str]] = {}

    def stage(self, key: str, payload_fingerprint: str) -> str:
        prior = self._rows.get(key)
        if prior:
            if prior[0] != payload_fingerprint:
                raise IntegrationPlanError("OUTBOX_REPLAY_CONFLICT")
            return prior[1]
        self._rows[key] = (payload_fingerprint, "PENDING")
        return "PENDING"

    def verify(self, key: str, readback_fingerprint: str | None) -> str:
        if key not in self._rows:
            raise IntegrationPlanError("OUTBOX_EVENT_MISSING")
        expected, _state = self._rows[key]
        if readback_fingerprint is None:
            return "PENDING"
        if readback_fingerprint != expected:
            self._rows[key] = (expected, "CONFLICT")
            return "CONFLICT"
        self._rows[key] = (expected, "COMMITTED")
        return "COMMITTED"


def route_private_quote(
    data_class: str,
    provider: str,
    contains_raw_context: bool,
    *,
    endpoint: str,
    artifact_dir_mode: int,
    artifact_file_mode: int,
    cloud_credentials_present: bool,
    proxy_present: bool,
    provider_override_present: bool,
    model_override_present: bool,
    artifact_root_outside_repo: bool,
    allow_cloud: bool,
    allow_live_write: bool,
) -> str:
    if data_class == "private-local-only":
        if provider != "local-domain-worker":
            raise IntegrationPlanError("PRIVATE_PROVIDER_FORBIDDEN")
        if endpoint not in {"127.0.0.1", "::1", "localhost"}:
            raise IntegrationPlanError("PRIVATE_ENDPOINT_NOT_LOOPBACK")
        if artifact_dir_mode != 0o700 or artifact_file_mode != 0o600:
            raise IntegrationPlanError("PRIVATE_ARTIFACT_MODE_UNSAFE")
        if not artifact_root_outside_repo:
            raise IntegrationPlanError("PRIVATE_ARTIFACT_ROOT_IN_REPO")
        if cloud_credentials_present:
            raise IntegrationPlanError("PRIVATE_ROUTE_CLOUD_ENV_PRESENT")
        if proxy_present:
            raise IntegrationPlanError("PRIVATE_ROUTE_PROXY_PRESENT")
        if provider_override_present:
            raise IntegrationPlanError("PRIVATE_ROUTE_PROVIDER_OVERRIDE_PRESENT")
        if model_override_present:
            raise IntegrationPlanError("PRIVATE_ROUTE_MODEL_OVERRIDE_PRESENT")
        if allow_cloud:
            raise IntegrationPlanError("PRIVATE_ROUTE_CLOUD_ALLOWED")
        if allow_live_write:
            raise IntegrationPlanError("PRIVATE_ROUTE_LIVE_WRITE_FORBIDDEN")
        if not contains_raw_context:
            return "LOCAL_ONLY"
        return "LOCAL_ONLY_RAW_CONTEXT_CONTAINED"
    if data_class != "public-synthetic-only":
        raise IntegrationPlanError("UNKNOWN_DATA_CLASS")
    if contains_raw_context:
        raise IntegrationPlanError("RAW_CONTEXT_REQUIRES_PRIVATE_CLASS")
    return "PUBLIC_SYNTHETIC_ALLOWED"


def inspect_source_anchors(
    repo_root: Path, source_overrides: dict[str, str] | None = None
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    root = repo_root.resolve()
    for anchor in SOURCE_ANCHORS:
        path = root / anchor.path
        safe_path = (
            not path.is_symlink()
            and path.resolve().is_relative_to(root)
        )
        exists = safe_path and path.is_file()
        if source_overrides and anchor.path in source_overrides:
            content = source_overrides[anchor.path] if safe_path else ""
            exists = safe_path
        else:
            content = path.read_text(encoding="utf-8") if exists else ""
        source_sha = _sha256_bytes(content.encode("utf-8")) if exists else None
        expected_sha = PINNED_SOURCE_SHA256.get(anchor.path)
        missing_count = sum(
            1 for fragment in anchor.required_fragments if fragment not in content
        )
        hash_matches = bool(source_sha and source_sha == expected_sha)
        results.append(
            {
                "anchor_id": anchor.anchor_id,
                "path": anchor.path,
                "function": anchor.function,
                "source_sha256": source_sha,
                "pinned_sha256": expected_sha,
                "pinned_sha256_matches": hash_matches,
                "required_fragment_count": len(anchor.required_fragments),
                "missing_fragment_count": missing_count,
                "status": (
                    "PRESENT"
                    if exists and missing_count == 0 and hash_matches
                    else "DRIFT"
                ),
                "current_risk_code": anchor.current_risk_code,
            }
        )
    return results


def orders_writer_inventory(repo_root: Path) -> dict[str, Any]:
    candidates = tuple(sorted((repo_root / "scripts" / "apps-script").glob("*.gs"))) + tuple(
        sorted((repo_root / "bot_a6").glob("*.py"))
    )
    identity_tokens = ("OrderCharges", "charge_id", "order_id")
    write_tokens = ("appendRow", "setValues", "batchUpdate", "values().append", "INSERT INTO")
    matching_paths: list[str] = []
    for path in candidates:
        content = path.read_text(encoding="utf-8")
        if any(token in content for token in identity_tokens) and any(
            token in content for token in write_tokens
        ):
            matching_paths.append(str(path.relative_to(repo_root)))
    return {
        "scanned_file_count": len(candidates),
        "matching_file_count": len(matching_paths),
        "status": "AUTHORITATIVE_WRITER_UNRESOLVED" if not matching_paths else "REVIEW_REQUIRED",
    }


def run_fixture_matrix() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    for table, actual in CURRENT_SAFE_HEADER_FIXTURES.items():
        accepted, codes = validate_named_headers(actual, TARGET_HEADERS[table])
        results.append(
            {
                "fixture_id": f"current_{table.lower()}_headers",
                "expected": "REJECT",
                "observed": "ACCEPT" if accepted else "REJECT",
                "code": "OK" if accepted else "+".join(codes),
            }
        )

    reordered = tuple(reversed(TARGET_HEADERS["SALES_INTAKE"])) + ("notes",)
    accepted, codes = validate_named_headers(reordered, TARGET_HEADERS["SALES_INTAKE"])
    results.append(
        {
            "fixture_id": "reordered_target_headers",
            "expected": "ACCEPT",
            "observed": "ACCEPT" if accepted else "REJECT",
            "code": "OK" if accepted else "+".join(codes),
        }
    )

    nfkc = tuple(
        "ｃａｓｅ＿ｉｄ" if value == "case_id" else value
        for value in TARGET_HEADERS["SALES_INTAKE"]
    )
    accepted, codes = validate_named_headers(nfkc, TARGET_HEADERS["SALES_INTAKE"])
    results.append(
        {
            "fixture_id": "nfkc_target_headers",
            "expected": "ACCEPT",
            "observed": "ACCEPT" if accepted else "REJECT",
            "code": "OK" if accepted else "+".join(codes),
        }
    )

    duplicate = TARGET_HEADERS["SALES_INTAKE"] + ("case_id",)
    accepted, codes = validate_named_headers(duplicate, TARGET_HEADERS["SALES_INTAKE"])
    results.append(
        {
            "fixture_id": "duplicate_case_header",
            "expected": "REJECT",
            "observed": "ACCEPT" if accepted else "REJECT",
            "code": "OK" if accepted else "+".join(codes),
        }
    )

    accepted, codes = validate_named_headers(
        TARGET_HEADERS["SALES_INTAKE"],
        TARGET_HEADERS["SALES_INTAKE"],
        schema_version="legacy",
    )
    results.append(
        {
            "fixture_id": "wrong_schema_version_headers",
            "expected": "REJECT",
            "observed": "ACCEPT" if accepted else "REJECT",
            "code": "OK" if accepted else "+".join(codes),
        }
    )

    for fixture_id, provider, expected in (
        ("private_cloud_route", "cloud-a5", "REJECT"),
        ("private_local_route", "local-domain-worker", "ACCEPT"),
    ):
        try:
            route_private_quote(
                "private-local-only",
                provider,
                True,
                endpoint="127.0.0.1",
                artifact_dir_mode=0o700,
                artifact_file_mode=0o600,
                cloud_credentials_present=False,
                proxy_present=False,
                provider_override_present=False,
                model_override_present=False,
                artifact_root_outside_repo=True,
                allow_cloud=False,
                allow_live_write=False,
            )
            observed, code = "ACCEPT", "OK"
        except IntegrationPlanError as exc:
            observed, code = "REJECT", exc.code
        results.append(
            {
                "fixture_id": fixture_id,
                "expected": expected,
                "observed": observed,
                "code": code,
            }
        )

    private_route_cases = (
        ("private_non_loopback_route", {"endpoint": "remote.internal"}),
        ("private_unsafe_artifact_mode", {"artifact_dir_mode": 0o755, "artifact_file_mode": 0o644}),
        ("private_cloud_environment", {"cloud_credentials_present": True}),
        ("private_proxy_environment", {"proxy_present": True}),
        ("private_provider_override", {"provider_override_present": True}),
        ("private_model_override", {"model_override_present": True}),
        ("private_repo_artifact_root", {"artifact_root_outside_repo": False}),
        ("private_allow_cloud_flag", {"allow_cloud": True}),
    )
    for fixture_id, overrides in private_route_cases:
        config = {
            "endpoint": "127.0.0.1",
            "artifact_dir_mode": 0o700,
            "artifact_file_mode": 0o600,
            "cloud_credentials_present": False,
            "proxy_present": False,
            "provider_override_present": False,
            "model_override_present": False,
            "artifact_root_outside_repo": True,
            "allow_cloud": False,
            "allow_live_write": False,
        }
        config.update(overrides)
        try:
            route_private_quote(
                "private-local-only",
                "local-domain-worker",
                True,
                **config,
            )
            observed, code = "ACCEPT", "OK"
        except IntegrationPlanError as exc:
            observed, code = "REJECT", exc.code
        results.append(
            {
                "fixture_id": fixture_id,
                "expected": "REJECT",
                "observed": observed,
                "code": code,
            }
        )

    try:
        route_private_quote(
            "private-local-onyl",
            "cloud-a5",
            False,
            endpoint="remote.internal",
            artifact_dir_mode=0o777,
            artifact_file_mode=0o666,
            cloud_credentials_present=True,
            proxy_present=True,
            provider_override_present=True,
            model_override_present=True,
            artifact_root_outside_repo=False,
            allow_cloud=True,
            allow_live_write=True,
        )
        observed, code = "ACCEPT", "OK"
    except IntegrationPlanError as exc:
        observed, code = "REJECT", exc.code
    results.append(
        {
            "fixture_id": "unknown_data_class",
            "expected": "REJECT",
            "observed": observed,
            "code": code,
        }
    )

    for fixture_id, value, controlled, expected in (
        ("customer_formula_injection", '=IMPORTXML("private","//x")', False, "REJECT"),
        ("controlled_status_formula", '=IFERROR(1,"pending")', True, "ACCEPT"),
    ):
        try:
            validate_sheet_cell(value, controlled_formula=controlled)
            observed, code = "ACCEPT", "OK"
        except IntegrationPlanError as exc:
            observed, code = "REJECT", exc.code
        results.append(
            {
                "fixture_id": fixture_id,
                "expected": expected,
                "observed": observed,
                "code": code,
            }
        )

    outbox = SyntheticOutbox()
    outbox.stage("event-a", "fp-a")
    results.append(
        {
            "fixture_id": "outbox_readback_commit",
            "expected": "COMMITTED",
            "observed": outbox.verify("event-a", "fp-a"),
            "code": "OK",
        }
    )
    outbox.stage("event-b", "fp-b")
    results.append(
        {
            "fixture_id": "outbox_missing_readback",
            "expected": "PENDING",
            "observed": outbox.verify("event-b", None),
            "code": "LIVE_READBACK_REQUIRED",
        }
    )
    outbox.stage("event-c", "fp-c")
    results.append(
        {
            "fixture_id": "outbox_payload_conflict",
            "expected": "CONFLICT",
            "observed": outbox.verify("event-c", "fp-other"),
            "code": "READBACK_MISMATCH",
        }
    )
    if tuple(row["fixture_id"] for row in results) != FIXTURE_IDS:
        raise IntegrationPlanError("FIXTURE_MANIFEST_DRIFT")
    return results


def validate_receipt(receipt: dict[str, Any]) -> None:
    serialized = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
    forbidden_patterns = (
        re.compile(r"case_[0-9a-f]{8}-[0-9a-f-]{27}"),
        re.compile(r"https?://"),
        re.compile(r"private://"),
    )
    if any(pattern.search(serialized) for pattern in forbidden_patterns):
        raise IntegrationPlanError("RECEIPT_FORBIDDEN_VALUE")
    allowed_top_level = {
        "schema_version",
        "created_at",
        "data_class",
        "method_contract",
        "method_version",
        "method_fingerprint",
        "plateau_review",
        "source_anchor_results",
        "live_header_fixtures",
        "deployment_source_inventory",
        "orders_writer_inventory",
        "fixture_results",
        "plan_artifact",
        "deployed_source_truth",
        "decision",
        "safety",
        "deterministic_body_sha256",
    }
    if set(receipt) != allowed_top_level:
        raise IntegrationPlanError("RECEIPT_TOP_LEVEL_ALLOWLIST")

    exact_nested_keys = {
        "method_contract": {
            "hypothesis",
            "changed_variable",
            "fixed_holdout",
            "expected_delta",
            "stop_loss",
            "model",
            "sampling",
            "evaluator",
            "acceptance",
        },
        "plateau_review": {
            "prior_method_fingerprints",
            "same_method_repeated",
            "historical_fuzzy_backfill_reopened",
            "new_repair_point",
        },
        "orders_writer_inventory": {
            "scanned_file_count",
            "matching_file_count",
            "status",
        },
        "deployment_source_inventory": {
            "declared_line_project_path",
            "declared_line_project_exists_or_symlink",
            "declared_line_project_trusted_directory",
            "quote_clasp_excludes_line_webhook",
            "status",
        },
        "plan_artifact": {
            "path",
            "present",
            "sha256",
            "pinned_sha256",
            "pinned_sha256_matches",
            "required_heading_count",
            "missing_heading_ids",
            "required_gate_count",
            "missing_gate_ids",
            "status",
        },
        "deployed_source_truth": {"status", "codes", "live_adoption"},
        "decision": {
            "status",
            "adoption_status",
            "eligible_for_live_change",
            "confirmed_leakage_amount",
            "durable_outbox_runtime_validated",
        },
        "safety": {
            "contains_raw_text",
            "contains_customer_identifiers",
            "contains_source_conversation_ids",
            "contains_customer_bearing_paths",
            "contains_raw_case_ids",
            "contains_raw_google_ids",
            "external_network_calls",
            "model_calls",
            "google_reads",
            "google_writes",
            "customer_send",
            "price_system_write",
            "historical_mutations",
            "new_third_party_private_data_egress",
        },
    }
    for key, expected in exact_nested_keys.items():
        if not isinstance(receipt.get(key), dict) or set(receipt[key]) != expected:
            raise IntegrationPlanError(f"RECEIPT_NESTED_ALLOWLIST_{key.upper()}")

    anchor_keys = {
        "anchor_id",
        "path",
        "function",
        "source_sha256",
        "pinned_sha256",
        "pinned_sha256_matches",
        "required_fragment_count",
        "missing_fragment_count",
        "status",
        "current_risk_code",
    }
    fixture_keys = {"fixture_id", "expected", "observed", "code"}
    live_header_keys = {
        "table",
        "field_count",
        "sha256",
        "pinned_sha256",
        "matches_pinned",
    }
    if any(set(row) != anchor_keys for row in receipt["source_anchor_results"]):
        raise IntegrationPlanError("RECEIPT_ANCHOR_ALLOWLIST")
    if any(set(row) != fixture_keys for row in receipt["fixture_results"]):
        raise IntegrationPlanError("RECEIPT_FIXTURE_ALLOWLIST")
    if any(set(row) != live_header_keys for row in receipt["live_header_fixtures"]):
        raise IntegrationPlanError("RECEIPT_LIVE_HEADER_ALLOWLIST")

    if receipt["schema_version"] != SCHEMA_VERSION:
        raise IntegrationPlanError("RECEIPT_SCHEMA_VERSION")
    if receipt["data_class"] != DATA_CLASS:
        raise IntegrationPlanError("RECEIPT_DATA_CLASS")
    if receipt["method_version"] != METHOD_VERSION:
        raise IntegrationPlanError("RECEIPT_METHOD_VERSION")
    if _canonical_json(receipt["method_contract"]) != _canonical_json(METHOD_CONTRACT):
        raise IntegrationPlanError("RECEIPT_METHOD_CONTRACT")
    if receipt["method_fingerprint"] != method_fingerprint():
        raise IntegrationPlanError("RECEIPT_METHOD_FINGERPRINT")
    if _canonical_json(receipt["plateau_review"]) != _canonical_json(PLATEAU_REVIEW):
        raise IntegrationPlanError("RECEIPT_PLATEAU_REVIEW_VALUE_ALLOWLIST")

    try:
        created = datetime.fromisoformat(str(receipt["created_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntegrationPlanError("RECEIPT_TIMESTAMP_INVALID") from exc
    if created.tzinfo is None:
        raise IntegrationPlanError("RECEIPT_TIMESTAMP_NOT_OFFSET_AWARE")

    if _canonical_json(receipt["fixture_results"]) != _canonical_json(run_fixture_matrix()):
        raise IntegrationPlanError("RECEIPT_FIXTURE_VALUE_ALLOWLIST")
    if _canonical_json(receipt["live_header_fixtures"]) != _canonical_json(
        live_header_fixture_inventory()
    ):
        raise IntegrationPlanError("RECEIPT_LIVE_HEADER_VALUE_ALLOWLIST")

    anchor_by_id = {anchor.anchor_id: anchor for anchor in SOURCE_ANCHORS}
    rows = receipt["source_anchor_results"]
    if len(rows) != len(anchor_by_id) or {row["anchor_id"] for row in rows} != set(anchor_by_id):
        raise IntegrationPlanError("RECEIPT_ANCHOR_MANIFEST")
    hex_digest = re.compile(r"^[0-9a-f]{64}$")
    for row in rows:
        anchor = anchor_by_id[row["anchor_id"]]
        if (
            row["path"] != anchor.path
            or row["function"] != anchor.function
            or row["current_risk_code"] != anchor.current_risk_code
            or row["pinned_sha256"] != PINNED_SOURCE_SHA256.get(anchor.path)
            or row["required_fragment_count"] != len(anchor.required_fragments)
        ):
            raise IntegrationPlanError("RECEIPT_ANCHOR_VALUE_ALLOWLIST")
        if row["source_sha256"] is not None and not hex_digest.fullmatch(
            str(row["source_sha256"])
        ):
            raise IntegrationPlanError("RECEIPT_ANCHOR_SHA256")
        pinned_match = bool(
            row["source_sha256"]
            and row["source_sha256"] == row["pinned_sha256"]
        )
        if row["pinned_sha256_matches"] is not pinned_match:
            raise IntegrationPlanError("RECEIPT_ANCHOR_PIN_RELATION")
        if type(row["missing_fragment_count"]) is not int or row[
            "missing_fragment_count"
        ] < 0:
            raise IntegrationPlanError("RECEIPT_ANCHOR_MISSING_COUNT")
        expected_status = (
            "PRESENT"
            if pinned_match and row["missing_fragment_count"] == 0
            else "DRIFT"
        )
        if row["status"] != expected_status:
            raise IntegrationPlanError("RECEIPT_ANCHOR_STATUS_RELATION")

    plan = receipt["plan_artifact"]
    if plan["path"] != str(PLAN_PATH) or plan["pinned_sha256"] != PINNED_PLAN_SHA256:
        raise IntegrationPlanError("RECEIPT_PLAN_VALUE_ALLOWLIST")
    if plan["required_heading_count"] != len(REQUIRED_PLAN_HEADINGS):
        raise IntegrationPlanError("RECEIPT_PLAN_HEADING_COUNT")
    if plan["required_gate_count"] != len(REQUIRED_PLAN_TERMS):
        raise IntegrationPlanError("RECEIPT_PLAN_GATE_COUNT")
    if any(value not in REQUIRED_PLAN_HEADINGS for value in plan["missing_heading_ids"]):
        raise IntegrationPlanError("RECEIPT_PLAN_MISSING_HEADING_VALUE")
    allowed_gate_ids = set(REQUIRED_PLAN_TERMS)
    if any(value not in allowed_gate_ids for value in plan["missing_gate_ids"]):
        raise IntegrationPlanError("RECEIPT_PLAN_MISSING_GATE_VALUE")
    if plan["sha256"] is not None and not hex_digest.fullmatch(str(plan["sha256"])):
        raise IntegrationPlanError("RECEIPT_PLAN_SHA256")
    plan_pin_match = bool(plan["sha256"] and plan["sha256"] == PINNED_PLAN_SHA256)
    if plan["pinned_sha256_matches"] is not plan_pin_match:
        raise IntegrationPlanError("RECEIPT_PLAN_PIN_RELATION")
    expected_plan_status = (
        "PRESENT"
        if (
            plan["present"] is True
            and plan_pin_match
            and not plan["missing_heading_ids"]
            and not plan["missing_gate_ids"]
        )
        else "DRIFT"
    )
    if plan["status"] != expected_plan_status:
        raise IntegrationPlanError("RECEIPT_PLAN_STATUS_RELATION")

    deployment = receipt["deployment_source_inventory"]
    if deployment["declared_line_project_path"] != "scripts/apps-script-line":
        raise IntegrationPlanError("RECEIPT_DEPLOYMENT_PATH")
    if (
        deployment["declared_line_project_trusted_directory"] is True
        and deployment["declared_line_project_exists_or_symlink"] is not True
    ):
        raise IntegrationPlanError("RECEIPT_DEPLOYMENT_EXISTENCE_RELATION")
    expected_deployment_status = (
        "EXPECTED_UNRESOLVED_BOUNDARY"
        if (
            deployment["declared_line_project_exists_or_symlink"] is False
            and deployment["declared_line_project_trusted_directory"] is False
            and deployment["quote_clasp_excludes_line_webhook"] is True
        )
        else "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED"
    )
    if deployment["status"] != expected_deployment_status:
        raise IntegrationPlanError("RECEIPT_DEPLOYMENT_STATUS_RELATION")

    writer = receipt["orders_writer_inventory"]
    if type(writer["scanned_file_count"]) is not int or writer["scanned_file_count"] <= 0:
        raise IntegrationPlanError("RECEIPT_WRITER_SCAN_COUNT")
    if type(writer["matching_file_count"]) is not int or writer["matching_file_count"] < 0:
        raise IntegrationPlanError("RECEIPT_WRITER_MATCH_COUNT")
    if _canonical_json(writer) != _canonical_json(
        orders_writer_inventory(Path(__file__).resolve().parents[1])
    ):
        raise IntegrationPlanError("RECEIPT_WRITER_VALUE_ALLOWLIST")
    expected_writer_status = (
        "AUTHORITATIVE_WRITER_UNRESOLVED"
        if writer["matching_file_count"] == 0
        else "REVIEW_REQUIRED"
    )
    if writer["status"] != expected_writer_status:
        raise IntegrationPlanError("RECEIPT_WRITER_STATUS_RELATION")

    if _canonical_json(receipt["safety"]) != _canonical_json(SAFE_SAFETY):
        raise IntegrationPlanError("RECEIPT_SAFETY_VALUE_ALLOWLIST")
    deployed = receipt["deployed_source_truth"]
    if (
        deployed["status"] != "INCOMPLETE_OWNER_REVIEW_BOUNDARY"
        or _canonical_json(deployed["codes"]) != _canonical_json(DEPLOYED_BOUNDARY_CODES)
        or deployed["live_adoption"] is not False
    ):
        raise IntegrationPlanError("RECEIPT_DEPLOYED_BOUNDARY_VALUE_ALLOWLIST")

    static_ready = (
        all(row["status"] == "PRESENT" for row in rows)
        and all(row["expected"] == row["observed"] for row in receipt["fixture_results"])
        and plan["status"] == "PRESENT"
        and all(row["matches_pinned"] for row in receipt["live_header_fixtures"])
        and deployment["status"] == "EXPECTED_UNRESOLVED_BOUNDARY"
        and writer["status"] == "AUTHORITATIVE_WRITER_UNRESOLVED"
    )
    expected_decision = "STATIC_PLAN_VALIDATED" if static_ready else "HOLD"
    decision = receipt["decision"]
    if (
        decision["status"] != expected_decision
        or decision["adoption_status"]
        != ("PROPOSAL_ONLY" if static_ready else "HOLD")
        or decision["eligible_for_live_change"] is not False
        or type(decision["confirmed_leakage_amount"]) is not int
        or decision["confirmed_leakage_amount"] != 0
        or decision["durable_outbox_runtime_validated"] is not False
    ):
        raise IntegrationPlanError("RECEIPT_DECISION_VALUE_ALLOWLIST")

    body = {
        key: value
        for key, value in receipt.items()
        if key not in {"schema_version", "created_at", "deterministic_body_sha256"}
    }
    expected_body_sha = _sha256_bytes(_canonical_json(body))
    if receipt["deterministic_body_sha256"] != expected_body_sha:
        raise IntegrationPlanError("RECEIPT_BODY_SHA256")


def _assert_receipt_safe(receipt: dict[str, Any]) -> None:
    validate_receipt(receipt)


def build_receipt(
    repo_root: Path,
    created_at: str,
    *,
    source_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    anchors = inspect_source_anchors(repo_root, source_overrides)
    fixtures = run_fixture_matrix()
    plan_artifact = inspect_plan_contract(repo_root)
    live_headers = live_header_fixture_inventory()
    deployment_inventory = deployment_source_inventory(repo_root)
    writer_inventory = orders_writer_inventory(repo_root)

    anchors_pass = all(result["status"] == "PRESENT" for result in anchors)
    fixtures_pass = all(
        result["expected"] == result["observed"] for result in fixtures
    )
    plan_pass = plan_artifact["status"] == "PRESENT"
    header_pass = all(row["matches_pinned"] for row in live_headers)
    deployment_pass = (
        deployment_inventory["status"] == "EXPECTED_UNRESOLVED_BOUNDARY"
    )
    writer_pass = writer_inventory["status"] == "AUTHORITATIVE_WRITER_UNRESOLVED"
    decision = (
        "STATIC_PLAN_VALIDATED"
        if (
            anchors_pass
            and fixtures_pass
            and plan_pass
            and header_pass
            and deployment_pass
            and writer_pass
        )
        else "HOLD"
    )
    body = {
        "data_class": DATA_CLASS,
        "method_contract": METHOD_CONTRACT,
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(),
        "plateau_review": dict(PLATEAU_REVIEW),
        "source_anchor_results": anchors,
        "live_header_fixtures": live_headers,
        "deployment_source_inventory": deployment_inventory,
        "orders_writer_inventory": writer_inventory,
        "fixture_results": fixtures,
        "plan_artifact": plan_artifact,
        "deployed_source_truth": {
            "status": "INCOMPLETE_OWNER_REVIEW_BOUNDARY",
            "codes": DEPLOYED_BOUNDARY_CODES,
            "live_adoption": False,
        },
        "decision": {
            "status": decision,
            "adoption_status": "PROPOSAL_ONLY" if decision == "STATIC_PLAN_VALIDATED" else "HOLD",
            "eligible_for_live_change": False,
            "confirmed_leakage_amount": 0,
            "durable_outbox_runtime_validated": False,
        },
        "safety": dict(SAFE_SAFETY),
    }
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        **body,
        "deterministic_body_sha256": _sha256_bytes(_canonical_json(body)),
    }
    validate_receipt(receipt)
    return receipt


def _reject_symlink_components(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.exists() and current.is_symlink():
            raise IntegrationPlanError("OUTPUT_PATH_SYMLINK_FORBIDDEN")
        current = current.parent


def write_private_receipt(path: Path, receipt: dict[str, Any]) -> None:
    validate_receipt(receipt)
    path = path.expanduser()
    if not path.is_absolute():
        raise IntegrationPlanError("OUTPUT_PATH_MUST_BE_ABSOLUTE")
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _reject_symlink_components(path.parent)
    os.chmod(path.parent, 0o700)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise IntegrationPlanError("OUTPUT_TARGET_MUST_BE_REGULAR_FILE")
    payload = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    if (path.stat().st_mode & 0o777) != 0o600:
        raise IntegrationPlanError("OUTPUT_PERMISSIONS_NOT_PRIVATE")
    readback = json.loads(path.read_text(encoding="utf-8"))
    validate_receipt(readback)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the proposal-only MAPLAB case-id integration plan"
    )
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--created-at")
    args = parser.parse_args()

    created_at = args.created_at or datetime.now(timezone.utc).isoformat()
    receipt = build_receipt(args.repo_root.resolve(), created_at)
    if args.receipt:
        write_private_receipt(args.receipt, receipt)
    summary = {
        "method_version": METHOD_VERSION,
        "method_fingerprint": receipt["method_fingerprint"],
        "decision": receipt["decision"]["status"],
        "anchor_count": len(receipt["source_anchor_results"]),
        "fixture_count": len(receipt["fixture_results"]),
        "external_network_calls": 0,
        "google_writes": 0,
        "model_calls": 0,
    }
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if receipt["decision"]["status"] == "STATIC_PLAN_VALIDATED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
