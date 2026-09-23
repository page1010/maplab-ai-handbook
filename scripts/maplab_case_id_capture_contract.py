#!/usr/bin/env python3
"""Validate MAPLAB's prospective case-id propagation contract on synthetic data.

This module is deliberately proposal-only.  It models a case identifier that is
minted once at conversation intake, then copied without mutation through Case
Store/SALES_INTAKE, quote creation, Orders/OrderCharges, and ASSET_LOG.  The
synthetic evaluator fails closed on replay conflicts, missing parents, key
drift, or fuzzy historical backfill.  It never reads or writes Google data,
customer messages, live prices, or customer-bearing files.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sqlite3
import stat
import tempfile
import threading
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "maplab.margin-leak.case-id-capture-contract.v1"
METHOD_VERSION = "margin-intake-case-id-contract-v1"
CONTRACT_VERSION = "maplab.case-id.v1"
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600

CASE_ID_RE = re.compile(
    r"^case_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EVENT_REF_RE = re.compile(r"^evt_[a-z][a-z0-9_]*_[0-9a-f]{64}$")

INTAKE_STAGE = "conversation_intake"
CASE_STAGE = "case_store_sales_intake"
QUOTE_STAGE = "quote_creation"
ORDER_STAGE = "orders_ordercharges"
ASSET_STAGE = "asset_log"

STAGE_CONTRACT = [
    {
        "stage": INTAKE_STAGE,
        "node_kinds": ["new_case"],
        "required_fields": [
            "contract_version",
            "stage",
            "case_id",
            "stage_event_ref",
            "payload_fingerprint",
        ],
        "case_id_rule": "mint_once_with_csprng_uuid4_then_persist_before_ack",
        "parent_rule": "new_case_intake_has_no_parent",
    },
    {
        "stage": CASE_STAGE,
        "node_kinds": ["case_store", "sales_intake"],
        "required_fields": [
            "contract_version",
            "stage",
            "case_id",
            "stage_event_ref",
            "parent_ref",
            "payload_fingerprint",
        ],
        "case_id_rule": "both_destinations_inherit_exactly_never_regenerate",
        "parent_rule": (
            "case_store_and_sales_intake_each_acknowledge_conversation_intake; "
            "coverage_requires_both"
        ),
    },
    {
        "stage": QUOTE_STAGE,
        "node_kinds": ["quote"],
        "required_fields": [
            "contract_version",
            "stage",
            "case_id",
            "stage_event_ref",
            "parent_ref",
            "payload_fingerprint",
        ],
        "case_id_rule": "inherit_exactly_never_regenerate",
        "parent_rule": "parent_must_be_case_store_sales_intake",
    },
    {
        "stage": ORDER_STAGE,
        "node_kinds": ["order", "order_charge"],
        "required_fields": [
            "contract_version",
            "stage",
            "case_id",
            "stage_event_ref",
            "parent_ref",
            "payload_fingerprint",
        ],
        "case_id_rule": "inherit_exactly_and_enforce_charge_equals_order",
        "parent_rule": "order_parent_is_quote_and_charge_parent_is_order",
    },
    {
        "stage": ASSET_STAGE,
        "node_kinds": ["case_specific_asset"],
        "required_fields": [
            "contract_version",
            "stage",
            "case_id",
            "stage_event_ref",
            "parent_ref",
            "payload_fingerprint",
        ],
        "case_id_rule": "inherit_exactly_never_regenerate",
        "parent_rule": "parent_must_be_order_and_asset_must_be_case_specific",
    },
]

RECENT_METHOD_FINGERPRINTS = [
    "9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17",
    "8c96645e45090a62ab6d3a19c3b945fb1f24459d6920e5741edee2e04fdf4ff1",
    "cfe227ba61206a7a1825aa9a960054fe8f9ca6858ac8152819a4ab6c36e09ae0",
]

FIXED_HOLDOUT = [
    "valid_five_stage_chain",
    "missing_case_store_ack",
    "missing_sales_intake_ack",
    "case_store_sales_intake_mismatch",
    "quote_case_id_mismatch",
    "order_charge_case_id_mismatch",
    "asset_case_id_mismatch",
    "changed_payload_replay_conflict",
    "historical_fuzzy_auto_backfill",
    "durable_restart_and_two_connection_replay",
]

PLATEAU_REVIEW = {
    "recent_method_fingerprints": RECENT_METHOD_FINGERPRINTS,
    "verified_improvement_in_last_two": False,
    "decision": (
        "change_repair_point_from_historical_join_inference_to_"
        "prospective_intake_key_capture"
    ),
    "same_method_rerun": False,
}

MIGRATION_BOUNDARY = {
    "cutover_basis": "ingestion_cursor_or_migration_snapshot_not_event_date",
    "prospective": (
        "durable local intake ledger persists one case_id before "
        "acknowledgement; downstream stages only inherit and read back"
    ),
    "historical_verified": (
        "existing key may be attached only from owner-reviewed deterministic evidence"
    ),
    "historical_unresolved": (
        "remain LEGACY_UNLINKED or INSUFFICIENT_EVIDENCE; never name/date/"
        "content-hash/fuzzy auto-link"
    ),
    "post_cutover_missing_key": "CONTRACT_VIOLATION",
}

PRIVACY_ASSERTIONS = {
    "contains_raw_text": False,
    "contains_customer_identifiers": False,
    "contains_source_conversation_ids": False,
    "contains_customer_bearing_paths": False,
    "contains_raw_case_ids": False,
    "contains_raw_google_ids": False,
    "external_network_calls": 0,
    "model_calls": 0,
    "customer_send": False,
    "google_writes": 0,
    "price_system_write": False,
    "historical_mutations": 0,
    "new_third_party_private_data_egress": False,
}


class CaseIdContractError(RuntimeError):
    """A stable, non-sensitive contract failure code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def payload_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_stage_event_ref(kind: str, raw_event_id: str, audit_key: bytes) -> str:
    """Return a local keyed reference without exposing a raw source identifier."""

    safe_kind = re.sub(r"[^a-z0-9_]+", "_", kind.lower()).strip("_")
    if not safe_kind or not audit_key:
        raise CaseIdContractError("INVALID_EVENT_REF_INPUT")
    digest = hmac.new(
        audit_key,
        f"{CONTRACT_VERSION}|{safe_kind}|{raw_event_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"evt_{safe_kind}_{digest}"


def mint_case_id() -> str:
    """Mint a production-shape opaque ID with the operating-system CSPRNG."""

    return f"case_{uuid.uuid4()}"


def validate_case_id(case_id: str) -> None:
    if not isinstance(case_id, str) or not CASE_ID_RE.fullmatch(case_id):
        raise CaseIdContractError("INVALID_CASE_ID")
    try:
        parsed = uuid.UUID(case_id.removeprefix("case_"))
    except (ValueError, AttributeError) as exc:
        raise CaseIdContractError("INVALID_CASE_ID") from exc
    if parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise CaseIdContractError("INVALID_CASE_ID")


def _validate_event_ref(event_ref: str) -> None:
    if not isinstance(event_ref, str) or not EVENT_REF_RE.fullmatch(event_ref):
        raise CaseIdContractError("INVALID_EVENT_REF")


def _validate_payload_fingerprint(fingerprint: str) -> None:
    if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
        raise CaseIdContractError("INVALID_PAYLOAD_FINGERPRINT")


@dataclass(frozen=True)
class ContractNode:
    contract_version: str
    stage: str
    node_kind: str
    case_id: str
    stage_event_ref: str
    parent_ref: str | None
    payload_fingerprint: str


class SQLiteIntakeLedger:
    """Durable synthetic reference for mint-once intake reservations.

    Each call opens its own SQLite connection and takes an IMMEDIATE
    transaction.  The source-event reference is the primary key and case_id is
    unique, so restart and two-worker retries converge on one persisted value.
    This is a local reference adapter, not a live LINE or Google writer.
    """

    def __init__(self, path: Path, id_factory: Callable[[], str] = mint_case_id):
        if not path.is_absolute():
            raise CaseIdContractError("LEDGER_PATH_MUST_BE_ABSOLUTE")
        _reject_symlink_components(path)
        path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
        _reject_symlink_components(path.parent)
        path.parent.chmod(PRIVATE_DIR_MODE)
        if path.exists() and (path.is_symlink() or not path.is_file()):
            raise CaseIdContractError("LEDGER_TARGET_MUST_BE_REGULAR_FILE")
        self.path = path
        self._id_factory = id_factory
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.execute("PRAGMA busy_timeout = 10000")
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS intake_identity (
                    stage_event_ref TEXT PRIMARY KEY,
                    payload_fingerprint TEXT NOT NULL,
                    case_id TEXT NOT NULL UNIQUE,
                    contract_version TEXT NOT NULL,
                    CHECK (contract_version = 'maplab.case-id.v1')
                )
                """
            )
            connection.commit()
        self.path.chmod(PRIVATE_FILE_MODE)

    def reserve(
        self,
        *,
        stage_event_ref: str,
        payload_fingerprint_value: str,
    ) -> tuple[str, bool]:
        _validate_event_ref(stage_event_ref)
        _validate_payload_fingerprint(payload_fingerprint_value)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            prior = connection.execute(
                """
                SELECT payload_fingerprint, case_id
                FROM intake_identity
                WHERE stage_event_ref = ?
                """,
                (stage_event_ref,),
            ).fetchone()
            if prior is not None:
                if prior[0] != payload_fingerprint_value:
                    connection.rollback()
                    raise CaseIdContractError("REPLAY_CONFLICT")
                validate_case_id(prior[1])
                connection.commit()
                return prior[1], False

            case_id = self._id_factory()
            validate_case_id(case_id)
            try:
                connection.execute(
                    """
                    INSERT INTO intake_identity (
                        stage_event_ref,
                        payload_fingerprint,
                        case_id,
                        contract_version
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        stage_event_ref,
                        payload_fingerprint_value,
                        case_id,
                        CONTRACT_VERSION,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                raise CaseIdContractError("CASE_ID_COLLISION") from exc
            connection.commit()
            self.path.chmod(PRIVATE_FILE_MODE)
            return case_id, True
        finally:
            connection.close()

    def row_count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM intake_identity"
            ).fetchone()
        return int(row[0])

    def lookup_case_id(self, stage_event_ref: str) -> str | None:
        _validate_event_ref(stage_event_ref)
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT case_id
                FROM intake_identity
                WHERE stage_event_ref = ?
                """,
                (stage_event_ref,),
            ).fetchone()
        if row is None:
            return None
        validate_case_id(row[0])
        return str(row[0])


class CaseIdCaptureContract:
    """In-memory reference model for the proposal-only propagation contract."""

    def __init__(self, id_factory: Callable[[], str] = mint_case_id):
        self._id_factory = id_factory
        self._nodes: dict[tuple[str, str], ContractNode] = {}
        self._intake_by_event: dict[str, ContractNode] = {}
        self._case_ids: set[str] = set()
        self._lock = threading.RLock()

    def _find_node(self, stage: str, event_ref: str) -> ContractNode:
        node = self._nodes.get((stage, event_ref))
        if node is None:
            raise CaseIdContractError("MISSING_PARENT")
        return node

    def intake_new_case(
        self,
        *,
        stage_event_ref: str,
        payload_fingerprint_value: str,
    ) -> tuple[str, bool]:
        _validate_event_ref(stage_event_ref)
        _validate_payload_fingerprint(payload_fingerprint_value)
        with self._lock:
            prior = self._intake_by_event.get(stage_event_ref)
            if prior is not None:
                if prior.payload_fingerprint != payload_fingerprint_value:
                    raise CaseIdContractError("REPLAY_CONFLICT")
                return prior.case_id, False

            case_id = self._id_factory()
            validate_case_id(case_id)
            if case_id in self._case_ids:
                raise CaseIdContractError("CASE_ID_COLLISION")
            node = ContractNode(
                contract_version=CONTRACT_VERSION,
                stage=INTAKE_STAGE,
                node_kind="new_case",
                case_id=case_id,
                stage_event_ref=stage_event_ref,
                parent_ref=None,
                payload_fingerprint=payload_fingerprint_value,
            )
            self._nodes[(INTAKE_STAGE, stage_event_ref)] = node
            self._intake_by_event[stage_event_ref] = node
            self._case_ids.add(case_id)
            return case_id, True

    def _link_child(
        self,
        *,
        stage: str,
        node_kind: str,
        stage_event_ref: str,
        parent_stage: str,
        parent_ref: str,
        case_id: str,
        payload_fingerprint_value: str,
        required_parent_kind: str | None = None,
    ) -> bool:
        _validate_event_ref(stage_event_ref)
        _validate_event_ref(parent_ref)
        _validate_payload_fingerprint(payload_fingerprint_value)
        validate_case_id(case_id)
        with self._lock:
            parent = self._find_node(parent_stage, parent_ref)
            if required_parent_kind and parent.node_kind != required_parent_kind:
                raise CaseIdContractError("INVALID_PARENT_KIND")
            if parent.case_id != case_id:
                raise CaseIdContractError("CASE_ID_MISMATCH")

            key = (stage, stage_event_ref)
            proposed = ContractNode(
                contract_version=CONTRACT_VERSION,
                stage=stage,
                node_kind=node_kind,
                case_id=case_id,
                stage_event_ref=stage_event_ref,
                parent_ref=parent_ref,
                payload_fingerprint=payload_fingerprint_value,
            )
            prior = self._nodes.get(key)
            if prior is not None:
                if prior != proposed:
                    raise CaseIdContractError("CHILD_BINDING_CONFLICT")
                return False
            self._nodes[key] = proposed
            return True

    def _link_case_destination(
        self,
        *,
        node_kind: str,
        stage_event_ref: str,
        parent_ref: str,
        case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        """Allow one durable acknowledgement per intake and destination."""

        with self._lock:
            existing = [
                node
                for node in self._nodes.values()
                if node.stage == CASE_STAGE
                and node.node_kind == node_kind
                and node.parent_ref == parent_ref
            ]
            if existing and all(
                node.stage_event_ref != stage_event_ref for node in existing
            ):
                raise CaseIdContractError("DUPLICATE_DESTINATION_ACK")
            return self._link_child(
                stage=CASE_STAGE,
                node_kind=node_kind,
                stage_event_ref=stage_event_ref,
                parent_stage=INTAKE_STAGE,
                parent_ref=parent_ref,
                case_id=case_id,
                payload_fingerprint_value=payload_fingerprint_value,
                required_parent_kind="new_case",
            )

    def link_case_store(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        return self._link_case_destination(
            node_kind="case_store",
            stage_event_ref=stage_event_ref,
            parent_ref=parent_ref,
            case_id=case_id,
            payload_fingerprint_value=payload_fingerprint_value,
        )

    def link_sales_intake(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        return self._link_case_destination(
            node_kind="sales_intake",
            stage_event_ref=stage_event_ref,
            parent_ref=parent_ref,
            case_id=case_id,
            payload_fingerprint_value=payload_fingerprint_value,
        )

    def link_quote(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        validate_case_id(case_id)
        with self._lock:
            sales_intake = self._find_node(CASE_STAGE, parent_ref)
            if sales_intake.node_kind != "sales_intake":
                raise CaseIdContractError("INVALID_PARENT_KIND")
            if sales_intake.case_id != case_id:
                raise CaseIdContractError("CASE_ID_MISMATCH")
            case_store_acks = [
                node
                for node in self._nodes.values()
                if node.stage == CASE_STAGE
                and node.node_kind == "case_store"
                and node.parent_ref == sales_intake.parent_ref
                and node.case_id == case_id
            ]
            if len(case_store_acks) != 1:
                raise CaseIdContractError("CASE_STAGE_INCOMPLETE")
            return self._link_child(
                stage=QUOTE_STAGE,
                node_kind="quote",
                stage_event_ref=stage_event_ref,
                parent_stage=CASE_STAGE,
                parent_ref=parent_ref,
                case_id=case_id,
                payload_fingerprint_value=payload_fingerprint_value,
                required_parent_kind="sales_intake",
            )

    def link_order(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        return self._link_child(
            stage=ORDER_STAGE,
            node_kind="order",
            stage_event_ref=stage_event_ref,
            parent_stage=QUOTE_STAGE,
            parent_ref=parent_ref,
            case_id=case_id,
            payload_fingerprint_value=payload_fingerprint_value,
            required_parent_kind="quote",
        )

    def link_order_charge(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        return self._link_child(
            stage=ORDER_STAGE,
            node_kind="order_charge",
            stage_event_ref=stage_event_ref,
            parent_stage=ORDER_STAGE,
            parent_ref=parent_ref,
            case_id=case_id,
            payload_fingerprint_value=payload_fingerprint_value,
            required_parent_kind="order",
        )

    def link_asset(
        self, *, stage_event_ref: str, parent_ref: str, case_id: str,
        payload_fingerprint_value: str,
    ) -> bool:
        return self._link_child(
            stage=ASSET_STAGE,
            node_kind="case_specific_asset",
            stage_event_ref=stage_event_ref,
            parent_stage=ORDER_STAGE,
            parent_ref=parent_ref,
            case_id=case_id,
            payload_fingerprint_value=payload_fingerprint_value,
            required_parent_kind="order",
        )

    def stage_coverage(self, case_id: str) -> dict[str, bool]:
        validate_case_id(case_id)
        nodes = [node for node in self._nodes.values() if node.case_id == case_id]
        kinds = {(node.stage, node.node_kind) for node in nodes}
        return {
            INTAKE_STAGE: (INTAKE_STAGE, "new_case") in kinds,
            CASE_STAGE: (
                (CASE_STAGE, "case_store") in kinds
                and (CASE_STAGE, "sales_intake") in kinds
            ),
            QUOTE_STAGE: (QUOTE_STAGE, "quote") in kinds,
            ORDER_STAGE: (
                (ORDER_STAGE, "order") in kinds
                and (ORDER_STAGE, "order_charge") in kinds
            ),
            ASSET_STAGE: (ASSET_STAGE, "case_specific_asset") in kinds,
        }

    def assert_complete_five_stage_chain(self, case_id: str) -> None:
        if not all(self.stage_coverage(case_id).values()):
            raise CaseIdContractError("INCOMPLETE_FIVE_STAGE_CHAIN")

    @property
    def node_count(self) -> int:
        return len(self._nodes)


def classify_migration_row(
    *,
    pre_cutover: bool,
    case_id: str | None,
    link_basis: str | None,
    intake_ledger: SQLiteIntakeLedger | None = None,
    stage_event_ref: str | None = None,
) -> str:
    """Classify a migration row without guessing or minting a historical key."""

    if link_basis in {"name", "date", "content_hash", "fuzzy", "customer_identity"}:
        raise CaseIdContractError("LEGACY_AUTO_LINK_FORBIDDEN")
    if not case_id:
        return "LEGACY_UNLINKED" if pre_cutover else "CONTRACT_VIOLATION"
    validate_case_id(case_id)
    if pre_cutover:
        if link_basis != "owner_verified_evidence":
            raise CaseIdContractError("LEGACY_VERIFICATION_REQUIRED")
        return "HISTORICAL_VERIFIED"
    if (
        link_basis != "prospective_intake"
        or intake_ledger is None
        or stage_event_ref is None
        or intake_ledger.lookup_case_id(stage_event_ref) != case_id
    ):
        raise CaseIdContractError("PROSPECTIVE_PROVENANCE_REQUIRED")
    return "PROSPECTIVE_LINKED"


def _fixed_ref(kind: str, serial: str) -> str:
    return make_stage_event_ref(kind, serial, b"synthetic-fixed-audit-key-v1")


def _fixed_id_factory(case_id: str) -> Callable[[], str]:
    calls = 0

    def factory() -> str:
        nonlocal calls
        calls += 1
        if calls > 1:
            raise CaseIdContractError("UNEXPECTED_SECOND_MINT")
        return case_id

    return factory


def _build_valid_chain(
    *,
    case_id: str = "case_11111111-1111-4111-8111-111111111111",
) -> tuple[CaseIdCaptureContract, dict[str, str]]:
    registry = CaseIdCaptureContract(_fixed_id_factory(case_id))
    refs = {
        "intake": _fixed_ref("intake", "synthetic-intake-1"),
        "case_store": _fixed_ref("case_store", "synthetic-case-store-1"),
        "sales_intake": _fixed_ref("sales_intake", "synthetic-sales-intake-1"),
        "quote": _fixed_ref("quote", "synthetic-quote-1"),
        "order": _fixed_ref("order", "synthetic-order-1"),
        "charge": _fixed_ref("charge", "synthetic-charge-1"),
        "asset": _fixed_ref("asset", "synthetic-asset-1"),
    }
    minted, created = registry.intake_new_case(
        stage_event_ref=refs["intake"],
        payload_fingerprint_value=payload_fingerprint("synthetic-intake-payload"),
    )
    if not created or minted != case_id:
        raise CaseIdContractError("INTAKE_MINT_ASSERTION_FAILED")
    registry.link_case_store(
        stage_event_ref=refs["case_store"],
        parent_ref=refs["intake"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint(
            "synthetic-case-store-payload"
        ),
    )
    registry.link_sales_intake(
        stage_event_ref=refs["sales_intake"],
        parent_ref=refs["intake"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint(
            "synthetic-sales-intake-payload"
        ),
    )
    registry.link_quote(
        stage_event_ref=refs["quote"],
        parent_ref=refs["sales_intake"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint("synthetic-quote-payload"),
    )
    registry.link_order(
        stage_event_ref=refs["order"],
        parent_ref=refs["quote"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint("synthetic-order-payload"),
    )
    registry.link_order_charge(
        stage_event_ref=refs["charge"],
        parent_ref=refs["order"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint("synthetic-charge-payload"),
    )
    registry.link_asset(
        stage_event_ref=refs["asset"],
        parent_ref=refs["order"],
        case_id=case_id,
        payload_fingerprint_value=payload_fingerprint("synthetic-asset-payload"),
    )
    registry.assert_complete_five_stage_chain(case_id)
    return registry, refs


def _run_scenario(name: str) -> tuple[str, int]:
    good = "case_11111111-1111-4111-8111-111111111111"
    other = "case_99999999-9999-4999-8999-999999999999"
    if name == "valid_five_stage_chain":
        registry, _ = _build_valid_chain(case_id=good)
        return "ACCEPTED", sum(registry.stage_coverage(good).values())
    if name == "missing_case_store_ack":
        registry = CaseIdCaptureContract(_fixed_id_factory(good))
        intake_ref = _fixed_ref("intake", "missing-case-store")
        sales_ref = _fixed_ref("sales_intake", "missing-case-store")
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("intake"),
        )
        registry.link_sales_intake(
            stage_event_ref=sales_ref,
            parent_ref=intake_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("sales"),
        )
        quote_ref = _fixed_ref("quote", "missing-case-store")
        registry.link_quote(
            stage_event_ref=quote_ref,
            parent_ref=sales_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("quote"),
        )
        order_ref = _fixed_ref("order", "missing-case-store")
        registry.link_order(
            stage_event_ref=order_ref,
            parent_ref=quote_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("order"),
        )
        registry.link_order_charge(
            stage_event_ref=_fixed_ref("charge", "missing-case-store"),
            parent_ref=order_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("charge"),
        )
        registry.link_asset(
            stage_event_ref=_fixed_ref("asset", "missing-case-store"),
            parent_ref=order_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("asset"),
        )
        registry.assert_complete_five_stage_chain(good)
    elif name == "missing_sales_intake_ack":
        registry = CaseIdCaptureContract(_fixed_id_factory(good))
        intake_ref = _fixed_ref("intake", "missing-sales-intake")
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("intake"),
        )
        registry.link_case_store(
            stage_event_ref=_fixed_ref("case_store", "missing-sales-intake"),
            parent_ref=intake_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("case-store"),
        )
        registry.link_quote(
            stage_event_ref=_fixed_ref("quote", "missing-sales-intake"),
            parent_ref=_fixed_ref("sales_intake", "missing-sales-intake"),
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("quote"),
        )
    elif name == "case_store_sales_intake_mismatch":
        registry = CaseIdCaptureContract(_fixed_id_factory(good))
        intake_ref = _fixed_ref("intake", "case-sales-mismatch")
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("intake"),
        )
        registry.link_case_store(
            stage_event_ref=_fixed_ref("case_store", "case-sales-mismatch"),
            parent_ref=intake_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("case-store"),
        )
        registry.link_sales_intake(
            stage_event_ref=_fixed_ref("sales_intake", "case-sales-mismatch"),
            parent_ref=intake_ref,
            case_id=other,
            payload_fingerprint_value=payload_fingerprint("sales-intake"),
        )
    elif name == "quote_case_id_mismatch":
        registry = CaseIdCaptureContract(_fixed_id_factory(good))
        intake_ref = _fixed_ref("intake", "quote-mismatch")
        sales_ref = _fixed_ref("sales_intake", "quote-mismatch")
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("intake"),
        )
        registry.link_case_store(
            stage_event_ref=_fixed_ref("case_store", "quote-mismatch"),
            parent_ref=intake_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("case-store"),
        )
        registry.link_sales_intake(
            stage_event_ref=sales_ref,
            parent_ref=intake_ref,
            case_id=good,
            payload_fingerprint_value=payload_fingerprint("sales"),
        )
        registry.link_quote(
            stage_event_ref=_fixed_ref("quote", "quote-mismatch"),
            parent_ref=sales_ref,
            case_id=other,
            payload_fingerprint_value=payload_fingerprint("quote"),
        )
    elif name == "order_charge_case_id_mismatch":
        registry, refs = _build_valid_chain(case_id=good)
        registry.link_order_charge(
            stage_event_ref=_fixed_ref("charge", "mismatch"),
            parent_ref=refs["order"],
            case_id=other,
            payload_fingerprint_value=payload_fingerprint("charge-mismatch"),
        )
    elif name == "asset_case_id_mismatch":
        registry, refs = _build_valid_chain(case_id=good)
        registry.link_asset(
            stage_event_ref=_fixed_ref("asset", "mismatch"),
            parent_ref=refs["order"],
            case_id=other,
            payload_fingerprint_value=payload_fingerprint("asset-mismatch"),
        )
    elif name == "changed_payload_replay_conflict":
        registry = CaseIdCaptureContract(_fixed_id_factory(good))
        intake_ref = _fixed_ref("intake", "replay")
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("first"),
        )
        registry.intake_new_case(
            stage_event_ref=intake_ref,
            payload_fingerprint_value=payload_fingerprint("changed"),
        )
    elif name == "historical_fuzzy_auto_backfill":
        classify_migration_row(
            pre_cutover=True,
            case_id=None,
            link_basis="fuzzy",
        )
    elif name == "durable_restart_and_two_connection_replay":
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "private"
            path = root / "intake.sqlite3"
            first_ledger = SQLiteIntakeLedger(path, _fixed_id_factory(good))
            event_ref = _fixed_ref("intake", "durable-restart")
            first = first_ledger.reserve(
                stage_event_ref=event_ref,
                payload_fingerprint_value=payload_fingerprint("same"),
            )
            restarted = SQLiteIntakeLedger(path, _fixed_id_factory(other))
            second = restarted.reserve(
                stage_event_ref=event_ref,
                payload_fingerprint_value=payload_fingerprint("same"),
            )
            if first != (good, True) or second != (good, False):
                raise CaseIdContractError("DURABLE_RESTART_ASSERTION_FAILED")

            race_path = root / "race.sqlite3"
            left = SQLiteIntakeLedger(race_path, _fixed_id_factory(good))
            right = SQLiteIntakeLedger(race_path, _fixed_id_factory(other))
            race_ref = _fixed_ref("intake", "two-connection-race")
            barrier = threading.Barrier(2)
            race_results: list[tuple[str, bool]] = []
            race_errors: list[str] = []

            def reserve(ledger: SQLiteIntakeLedger) -> None:
                try:
                    barrier.wait()
                    race_results.append(
                        ledger.reserve(
                            stage_event_ref=race_ref,
                            payload_fingerprint_value=payload_fingerprint("same"),
                        )
                    )
                except Exception as exc:  # pragma: no cover - receipt fails closed
                    race_errors.append(type(exc).__name__)

            threads = [
                threading.Thread(target=reserve, args=(left,)),
                threading.Thread(target=reserve, args=(right,)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            if (
                race_errors
                or len(race_results) != 2
                or len({row[0] for row in race_results}) != 1
                or sum(1 for _, created in race_results if created) != 1
                or left.row_count() != 1
            ):
                raise CaseIdContractError("TWO_CONNECTION_ASSERTION_FAILED")
        return "ACCEPTED_DURABLE", 0
    else:
        raise CaseIdContractError("UNKNOWN_SCENARIO")
    raise CaseIdContractError("EXPECTED_SCENARIO_REJECTION_MISSING")


EXPECTED_SCENARIO_OUTCOMES = {
    "valid_five_stage_chain": "ACCEPTED",
    "missing_case_store_ack": "CASE_STAGE_INCOMPLETE",
    "missing_sales_intake_ack": "MISSING_PARENT",
    "case_store_sales_intake_mismatch": "CASE_ID_MISMATCH",
    "quote_case_id_mismatch": "CASE_ID_MISMATCH",
    "order_charge_case_id_mismatch": "CASE_ID_MISMATCH",
    "asset_case_id_mismatch": "CASE_ID_MISMATCH",
    "changed_payload_replay_conflict": "REPLAY_CONFLICT",
    "historical_fuzzy_auto_backfill": "LEGACY_AUTO_LINK_FORBIDDEN",
    "durable_restart_and_two_connection_replay": "ACCEPTED_DURABLE",
}

CANONICAL_SCENARIO_OBSERVED = dict(EXPECTED_SCENARIO_OUTCOMES)
CANONICAL_SCENARIO_STAGE_COVERAGE = {
    name: 5 if name == "valid_five_stage_chain" else 0
    for name in FIXED_HOLDOUT
}

RECEIPT_TOP_LEVEL_KEYS = {
    "generated_at",
    "schema_version",
    "data_class",
    "plateau_review",
    "method_contract",
    "stage_contract",
    "scenario_count",
    "passed_expected",
    "failed_expectations",
    "scenario_results",
    "five_stage_chain_preserved",
    "migration_boundary",
    "privacy",
    "contract_ready_for_proposal",
    "adoption_status",
    "eligible_for_separate_live_review",
    "live_adoption",
    "confirmed_leakage_amount",
    "next_repair_point",
    "fixture_manifest_sha256",
    "deterministic_body_sha256",
}

SCENARIO_RESULT_KEYS = {
    "scenario",
    "expected",
    "observed",
    "passed",
    "stage_coverage",
}

RAW_CASE_ID_ANYWHERE_RE = re.compile(
    r"case_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}"
)


def validate_contract_receipt(payload: dict[str, Any]) -> None:
    """Enforce the receipt's static allowlist before it can be written."""

    if set(payload) != RECEIPT_TOP_LEVEL_KEYS:
        raise CaseIdContractError("RECEIPT_TOP_LEVEL_ALLOWLIST_VIOLATION")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise CaseIdContractError("RECEIPT_SCHEMA_MISMATCH")
    if payload.get("data_class") != "synthetic-local-contract-receipt":
        raise CaseIdContractError("RECEIPT_DATA_CLASS_MISMATCH")
    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str):
        raise CaseIdContractError("RECEIPT_TIMESTAMP_INVALID")
    try:
        parsed_timestamp = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CaseIdContractError("RECEIPT_TIMESTAMP_INVALID") from exc
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() is None:
        raise CaseIdContractError("RECEIPT_TIMESTAMP_INVALID")
    if payload.get("plateau_review") != PLATEAU_REVIEW:
        raise CaseIdContractError("RECEIPT_PLATEAU_REVIEW_MISMATCH")
    if payload.get("migration_boundary") != MIGRATION_BOUNDARY:
        raise CaseIdContractError("RECEIPT_MIGRATION_BOUNDARY_MISMATCH")
    if payload.get("privacy") != PRIVACY_ASSERTIONS:
        raise CaseIdContractError("RECEIPT_PRIVACY_ASSERTION_FAILED")
    results = payload.get("scenario_results")
    if not isinstance(results, list) or any(
        not isinstance(row, dict) or set(row) != SCENARIO_RESULT_KEYS
        for row in results
    ):
        raise CaseIdContractError("RECEIPT_SCENARIO_ALLOWLIST_VIOLATION")
    if [row["scenario"] for row in results] != FIXED_HOLDOUT:
        raise CaseIdContractError("RECEIPT_SCENARIO_MANIFEST_MISMATCH")
    for row in results:
        name = row["scenario"]
        expected = EXPECTED_SCENARIO_OUTCOMES[name]
        if (
            row["expected"] != expected
            or row["observed"] != CANONICAL_SCENARIO_OBSERVED[name]
            or not isinstance(row["passed"], bool)
            or row["passed"] is not (row["observed"] == expected)
            or row["stage_coverage"]
            != CANONICAL_SCENARIO_STAGE_COVERAGE[name]
        ):
            raise CaseIdContractError("RECEIPT_SCENARIO_VALUE_MISMATCH")
    if payload.get("stage_contract") != STAGE_CONTRACT:
        raise CaseIdContractError("RECEIPT_STAGE_CONTRACT_MISMATCH")
    if payload.get("method_contract") != method_contract():
        raise CaseIdContractError("RECEIPT_METHOD_CONTRACT_MISMATCH")
    serialised = canonical_json(payload)
    if RAW_CASE_ID_ANYWHERE_RE.search(serialised):
        raise CaseIdContractError("RECEIPT_RAW_CASE_ID_FORBIDDEN")
    failed = [row["scenario"] for row in results if not row["passed"]]
    valid_result = results[FIXED_HOLDOUT.index("valid_five_stage_chain")]
    contract_ready = not failed and valid_result["stage_coverage"] == 5
    scalar_relations = (
        payload.get("scenario_count") == len(results),
        payload.get("passed_expected") == len(results) - len(failed),
        payload.get("failed_expectations") == failed,
        payload.get("five_stage_chain_preserved")
        is (valid_result["stage_coverage"] == 5),
        payload.get("contract_ready_for_proposal") is contract_ready,
        payload.get("adoption_status")
        == ("PROPOSAL_ONLY" if contract_ready else "HOLD"),
        payload.get("eligible_for_separate_live_review") is contract_ready,
        payload.get("live_adoption") is False,
        payload.get("confirmed_leakage_amount") == 0,
        payload.get("next_repair_point")
        == (
            "proposal_only_integration_adapter_plan"
            if contract_ready
            else "repair_case_id_contract"
        ),
    )
    if not all(scalar_relations):
        raise CaseIdContractError("RECEIPT_RELATIONSHIP_MISMATCH")
    expected_fixture_sha = sha256_json(
        {
            "method_version": METHOD_VERSION,
            "holdout": FIXED_HOLDOUT,
            "expected": EXPECTED_SCENARIO_OUTCOMES,
            "stage_contract": STAGE_CONTRACT,
        }
    )
    if payload.get("fixture_manifest_sha256") != expected_fixture_sha:
        raise CaseIdContractError("RECEIPT_FIXTURE_MANIFEST_MISMATCH")
    deterministic_body = dict(payload)
    deterministic_body.pop("generated_at", None)
    supplied_body_sha = deterministic_body.pop("deterministic_body_sha256", None)
    if supplied_body_sha != sha256_json(deterministic_body):
        raise CaseIdContractError("RECEIPT_DETERMINISTIC_BODY_MISMATCH")


def method_contract() -> dict[str, Any]:
    body: dict[str, Any] = {
        "method_version": METHOD_VERSION,
        "adapter": "maplab-margin-leak-auditor/case-id-capture-contract",
        "model": "none",
        "prompt_or_lesson_version": "case-id-contract-v1",
        "sampling": "fixed-ten-synthetic-holdout",
        "evaluator": "deterministic-referential-integrity-validator-v1",
        "acceptance": (
            "valid chain covers 5/5 stages; every mutation, replay conflict, "
            "missing destination/parent, and fuzzy backfill scenario rejects; "
            "restart and two-connection replay converge; zero live writes"
        ),
        "hypothesis": (
            "Minting one opaque case_id at conversation intake and enforcing "
            "immutable parent-child equality through all five downstream stages "
            "prevents future ambiguous joins while failing closed on drift."
        ),
        "changed_variable": (
            "replace historical identity inference with prospective intake mint "
            "plus immutable foreign-key propagation"
        ),
        "fixed_holdout": list(FIXED_HOLDOUT),
        "expected_delta": {
            "synthetic_stage_coverage": "0_to_5_of_5",
            "false_accepts": 0,
            "privacy_leaks": 0,
            "legacy_auto_backfills": 0,
        },
        "stop_loss": (
            "if the valid chain misses any stage or any negative scenario is "
            "accepted, set HOLD and do not propose live adoption"
        ),
    }
    body["fingerprint"] = sha256_json(body)
    return body


def build_contract_receipt(*, generated_at: str | None = None) -> dict[str, Any]:
    results = []
    for name in FIXED_HOLDOUT:
        stage_coverage = 0
        try:
            observed, stage_coverage = _run_scenario(name)
        except CaseIdContractError as exc:
            observed = exc.code
        expected = EXPECTED_SCENARIO_OUTCOMES[name]
        results.append(
            {
                "scenario": name,
                "expected": expected,
                "observed": observed,
                "passed": observed == expected,
                "stage_coverage": stage_coverage,
            }
        )

    failed = [row["scenario"] for row in results if not row["passed"]]
    valid_result = next(
        row for row in results if row["scenario"] == "valid_five_stage_chain"
    )
    contract_ready = not failed and valid_result["stage_coverage"] == 5
    deterministic_body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "data_class": "synthetic-local-contract-receipt",
        "plateau_review": deepcopy(PLATEAU_REVIEW),
        "method_contract": method_contract(),
        "stage_contract": deepcopy(STAGE_CONTRACT),
        "scenario_count": len(results),
        "passed_expected": len(results) - len(failed),
        "failed_expectations": failed,
        "scenario_results": results,
        "five_stage_chain_preserved": valid_result["stage_coverage"] == 5,
        "migration_boundary": deepcopy(MIGRATION_BOUNDARY),
        "privacy": deepcopy(PRIVACY_ASSERTIONS),
        "contract_ready_for_proposal": contract_ready,
        "adoption_status": "PROPOSAL_ONLY" if contract_ready else "HOLD",
        "eligible_for_separate_live_review": contract_ready,
        "live_adoption": False,
        "confirmed_leakage_amount": 0,
        "next_repair_point": (
            "proposal_only_integration_adapter_plan"
            if contract_ready
            else "repair_case_id_contract"
        ),
    }
    deterministic_body["fixture_manifest_sha256"] = sha256_json(
        {
            "method_version": METHOD_VERSION,
            "holdout": FIXED_HOLDOUT,
            "expected": EXPECTED_SCENARIO_OUTCOMES,
            "stage_contract": STAGE_CONTRACT,
        }
    )
    deterministic_body["deterministic_body_sha256"] = sha256_json(
        deterministic_body
    )
    receipt = {"generated_at": generated_at or utc_iso(), **deterministic_body}
    validate_contract_receipt(receipt)
    return receipt


def _reject_symlink_components(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.exists() and current.is_symlink():
            raise CaseIdContractError("OUTPUT_PATH_SYMLINK_FORBIDDEN")
        current = current.parent


def write_private_json(path: Path, payload: dict[str, Any]) -> None:
    validate_contract_receipt(payload)
    if not path.is_absolute():
        raise CaseIdContractError("OUTPUT_PATH_MUST_BE_ABSOLUTE")
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    _reject_symlink_components(path.parent)
    path.parent.chmod(PRIVATE_DIR_MODE)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise CaseIdContractError("OUTPUT_TARGET_MUST_BE_REGULAR_FILE")

    descriptor, temp_name = tempfile.mkstemp(
        prefix=".case-id-contract-",
        suffix=".tmp",
        dir=path.parent,
    )
    temp_path = Path(temp_name)
    try:
        os.fchmod(descriptor, PRIVATE_FILE_MODE)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        path.chmod(PRIVATE_FILE_MODE)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode != PRIVATE_FILE_MODE:
        raise CaseIdContractError("OUTPUT_PERMISSIONS_NOT_PRIVATE")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_contract_receipt()
    if not receipt["contract_ready_for_proposal"]:
        raise CaseIdContractError("CONTRACT_STOP_LOSS_TRIGGERED")
    write_private_json(args.output, receipt)
    print(
        canonical_json(
            {
                "schema_version": receipt["schema_version"],
                "adoption_status": receipt["adoption_status"],
                "scenario_count": receipt["scenario_count"],
                "passed_expected": receipt["passed_expected"],
                "five_stage_chain_preserved": receipt[
                    "five_stage_chain_preserved"
                ],
                "confirmed_leakage_amount": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
