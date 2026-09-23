import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_case_id_capture_contract.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_case_id_capture_contract_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


GOOD_ID = "case_11111111-1111-4111-8111-111111111111"
OTHER_ID = "case_99999999-9999-4999-8999-999999999999"
THIRD_ID = "case_33333333-3333-4333-8333-333333333333"
AUDIT_KEY = b"unit-test-local-audit-key"


def ref(kind, value):
    return MODULE.make_stage_event_ref(kind, value, AUDIT_KEY)


def fp(value):
    return MODULE.payload_fingerprint(value)


class SequenceFactory:
    def __init__(self, *values):
        self.values = iter(values)
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self):
        with self.lock:
            self.calls += 1
            return next(self.values)


def make_intake(registry, *, serial="1", case_id=GOOD_ID):
    intake_ref = ref("intake", f"event-{serial}")
    actual, created = registry.intake_new_case(
        stage_event_ref=intake_ref,
        payload_fingerprint_value=fp(f"payload-{serial}"),
    )
    assert actual == case_id
    assert created
    return intake_ref


def make_case_store(registry, intake_ref, *, serial="1", case_id=GOOD_ID):
    case_ref = ref("case_store", f"case-{serial}")
    registry.link_case_store(
        stage_event_ref=case_ref,
        parent_ref=intake_ref,
        case_id=case_id,
        payload_fingerprint_value=fp(f"case-{serial}"),
    )
    return case_ref


def make_sales_intake(registry, intake_ref, *, serial="1", case_id=GOOD_ID):
    sales_ref = ref("sales_intake", f"sales-{serial}")
    registry.link_sales_intake(
        stage_event_ref=sales_ref,
        parent_ref=intake_ref,
        case_id=case_id,
        payload_fingerprint_value=fp(f"sales-{serial}"),
    )
    return sales_ref


def make_case_pair(registry, intake_ref, *, serial="1", case_id=GOOD_ID):
    return (
        make_case_store(registry, intake_ref, serial=serial, case_id=case_id),
        make_sales_intake(registry, intake_ref, serial=serial, case_id=case_id),
    )


def make_quote(registry, sales_ref, *, serial="1", case_id=GOOD_ID):
    quote_ref = ref("quote", f"quote-{serial}")
    registry.link_quote(
        stage_event_ref=quote_ref,
        parent_ref=sales_ref,
        case_id=case_id,
        payload_fingerprint_value=fp(f"quote-{serial}"),
    )
    return quote_ref


def make_order(registry, quote_ref, *, serial="1", case_id=GOOD_ID):
    order_ref = ref("order", f"order-{serial}")
    registry.link_order(
        stage_event_ref=order_ref,
        parent_ref=quote_ref,
        case_id=case_id,
        payload_fingerprint_value=fp(f"order-{serial}"),
    )
    return order_ref


class CaseIdCaptureContractTests(unittest.TestCase):
    def test_new_intake_mints_canonical_uuid4_once(self):
        factory = SequenceFactory(GOOD_ID)
        registry = MODULE.CaseIdCaptureContract(factory)
        case_id, created = registry.intake_new_case(
            stage_event_ref=ref("intake", "event-1"),
            payload_fingerprint_value=fp("payload-1"),
        )
        self.assertTrue(created)
        self.assertEqual(case_id, GOOD_ID)
        MODULE.validate_case_id(case_id)
        self.assertEqual(factory.calls, 1)
        self.assertNotIn("event-1", case_id)

    def test_same_intake_replay_is_idempotent(self):
        factory = SequenceFactory(GOOD_ID, OTHER_ID)
        registry = MODULE.CaseIdCaptureContract(factory)
        event_ref = ref("intake", "same-event")
        first = registry.intake_new_case(
            stage_event_ref=event_ref,
            payload_fingerprint_value=fp("same-payload"),
        )
        second = registry.intake_new_case(
            stage_event_ref=event_ref,
            payload_fingerprint_value=fp("same-payload"),
        )
        self.assertEqual(first, (GOOD_ID, True))
        self.assertEqual(second, (GOOD_ID, False))
        self.assertEqual(factory.calls, 1)
        self.assertEqual(registry.node_count, 1)

    def test_same_event_changed_payload_is_replay_conflict(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID, OTHER_ID))
        event_ref = ref("intake", "changed-event")
        registry.intake_new_case(
            stage_event_ref=event_ref,
            payload_fingerprint_value=fp("first-payload"),
        )
        with self.assertRaisesRegex(MODULE.CaseIdContractError, "REPLAY_CONFLICT"):
            registry.intake_new_case(
                stage_event_ref=event_ref,
                payload_fingerprint_value=fp("changed-payload"),
            )
        self.assertEqual(registry.node_count, 1)

    def test_five_stage_chain_preserves_exact_id_with_multiple_children(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry)
        _, sales_ref = make_case_pair(registry, intake_ref)
        quote_ref = make_quote(registry, sales_ref)
        order_ref = make_order(registry, quote_ref)
        for serial in ("1", "2"):
            registry.link_order_charge(
                stage_event_ref=ref("charge", serial),
                parent_ref=order_ref,
                case_id=GOOD_ID,
                payload_fingerprint_value=fp(f"charge-{serial}"),
            )
            registry.link_asset(
                stage_event_ref=ref("asset", serial),
                parent_ref=order_ref,
                case_id=GOOD_ID,
                payload_fingerprint_value=fp(f"asset-{serial}"),
            )
        registry.assert_complete_five_stage_chain(GOOD_ID)
        self.assertEqual(sum(registry.stage_coverage(GOOD_ID).values()), 5)
        self.assertEqual(registry.node_count, 9)

    def test_case_store_and_sales_intake_require_independent_acknowledgements(self):
        missing_store = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(missing_store, serial="missing-store")
        sales_ref = make_sales_intake(
            missing_store, intake_ref, serial="missing-store"
        )
        with self.assertRaisesRegex(
            MODULE.CaseIdContractError, "CASE_STAGE_INCOMPLETE"
        ):
            make_quote(missing_store, sales_ref, serial="missing-store")
        self.assertFalse(missing_store.stage_coverage(GOOD_ID)[MODULE.CASE_STAGE])
        self.assertEqual(missing_store.node_count, 2)

        missing_sales = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(missing_sales, serial="missing-sales")
        make_case_store(missing_sales, intake_ref, serial="missing-sales")
        with self.assertRaisesRegex(MODULE.CaseIdContractError, "MISSING_PARENT"):
            missing_sales.link_quote(
                stage_event_ref=ref("quote", "missing-sales"),
                parent_ref=ref("sales_intake", "missing-sales"),
                case_id=GOOD_ID,
                payload_fingerprint_value=fp("quote"),
            )

        mismatch = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(mismatch, serial="mismatch")
        make_case_store(mismatch, intake_ref, serial="mismatch")
        with self.assertRaisesRegex(
            MODULE.CaseIdContractError, "CASE_ID_MISMATCH"
        ):
            make_sales_intake(
                mismatch, intake_ref, serial="mismatch", case_id=OTHER_ID
            )

    def test_quote_gate_and_destination_ack_are_atomic_under_interleaving(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry, serial="atomic-gate")
        _, sales_ref = make_case_pair(registry, intake_ref, serial="atomic-gate")
        original_link_child = registry._link_child
        quote_gate_entered = threading.Event()
        allow_quote_insert = threading.Event()

        def gated_link_child(**kwargs):
            if kwargs.get("stage") == MODULE.QUOTE_STAGE:
                quote_gate_entered.set()
                if not allow_quote_insert.wait(timeout=2):
                    raise AssertionError("quote gate test timed out")
            return original_link_child(**kwargs)

        registry._link_child = gated_link_child
        quote_results = []
        duplicate_errors = []

        def create_quote():
            quote_results.append(
                registry.link_quote(
                    stage_event_ref=ref("quote", "atomic-gate"),
                    parent_ref=sales_ref,
                    case_id=GOOD_ID,
                    payload_fingerprint_value=fp("quote"),
                )
            )

        def add_late_case_store_ack():
            try:
                registry.link_case_store(
                    stage_event_ref=ref("case_store", "late-duplicate"),
                    parent_ref=intake_ref,
                    case_id=GOOD_ID,
                    payload_fingerprint_value=fp("late-duplicate"),
                )
            except MODULE.CaseIdContractError as exc:
                duplicate_errors.append(exc.code)

        quote_thread = threading.Thread(target=create_quote)
        duplicate_thread = threading.Thread(target=add_late_case_store_ack)
        quote_thread.start()
        self.assertTrue(quote_gate_entered.wait(timeout=2))
        duplicate_thread.start()
        allow_quote_insert.set()
        quote_thread.join(timeout=2)
        duplicate_thread.join(timeout=2)
        self.assertFalse(quote_thread.is_alive())
        self.assertFalse(duplicate_thread.is_alive())
        self.assertEqual(quote_results, [True])
        self.assertEqual(duplicate_errors, ["DUPLICATE_DESTINATION_ACK"])
        self.assertEqual(registry.node_count, 4)

    def test_distinct_new_case_events_in_same_conversation_get_distinct_ids(self):
        factory = SequenceFactory(GOOD_ID, OTHER_ID)
        registry = MODULE.CaseIdCaptureContract(factory)
        first, _ = registry.intake_new_case(
            stage_event_ref=ref("intake", "conversation-1-new-case-a"),
            payload_fingerprint_value=fp("payload-a"),
        )
        second, _ = registry.intake_new_case(
            stage_event_ref=ref("intake", "conversation-1-new-case-b"),
            payload_fingerprint_value=fp("payload-b"),
        )
        self.assertEqual({first, second}, {GOOD_ID, OTHER_ID})
        self.assertEqual(factory.calls, 2)

    def test_missing_or_invalid_case_id_is_rejected_downstream(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry)
        invalid_values = [
            "",
            " ",
            "Q20260828010101",
            "case_11111111-1111-1111-8111-111111111111",
            "case_11111111-1111-4111-7111-111111111111",
            GOOD_ID.upper(),
            "case_１１１１１１１１-1111-4111-8111-111111111111",
        ]
        for index, invalid in enumerate(invalid_values):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(
                    MODULE.CaseIdContractError, "INVALID_CASE_ID"
                ):
                    registry.link_case_store(
                        stage_event_ref=ref("case", f"invalid-{index}"),
                        parent_ref=intake_ref,
                        case_id=invalid,
                        payload_fingerprint_value=fp("payload"),
                    )
        self.assertEqual(registry.node_count, 1)

    def test_handoff_mismatch_stops_each_chain_edge(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry)
        _, sales_ref = make_case_pair(registry, intake_ref)
        quote_ref = make_quote(registry, sales_ref)
        order_ref = make_order(registry, quote_ref)
        calls = [
            lambda: registry.link_quote(
                stage_event_ref=ref("quote", "wrong"),
                parent_ref=sales_ref,
                case_id=OTHER_ID,
                payload_fingerprint_value=fp("wrong"),
            ),
            lambda: registry.link_order(
                stage_event_ref=ref("order", "wrong"),
                parent_ref=quote_ref,
                case_id=OTHER_ID,
                payload_fingerprint_value=fp("wrong"),
            ),
            lambda: registry.link_order_charge(
                stage_event_ref=ref("charge", "wrong"),
                parent_ref=order_ref,
                case_id=OTHER_ID,
                payload_fingerprint_value=fp("wrong"),
            ),
            lambda: registry.link_asset(
                stage_event_ref=ref("asset", "wrong"),
                parent_ref=order_ref,
                case_id=OTHER_ID,
                payload_fingerprint_value=fp("wrong"),
            ),
        ]
        baseline = registry.node_count
        for call in calls:
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError, "CASE_ID_MISMATCH"
            ):
                call()
        self.assertEqual(registry.node_count, baseline)

    def test_child_duplicate_semantics_are_idempotent_or_conflict(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry)
        case_ref = ref("case_store", "duplicate")
        kwargs = {
            "stage_event_ref": case_ref,
            "parent_ref": intake_ref,
            "case_id": GOOD_ID,
            "payload_fingerprint_value": fp("same"),
        }
        self.assertTrue(registry.link_case_store(**kwargs))
        self.assertFalse(registry.link_case_store(**kwargs))
        with self.assertRaisesRegex(
            MODULE.CaseIdContractError, "CHILD_BINDING_CONFLICT"
        ):
            registry.link_case_store(
                **{**kwargs, "payload_fingerprint_value": fp("changed")}
            )
        self.assertEqual(registry.node_count, 2)

    def test_out_of_order_or_wrong_parent_kind_is_rejected(self):
        registry = MODULE.CaseIdCaptureContract(SequenceFactory(GOOD_ID))
        intake_ref = make_intake(registry)
        with self.assertRaisesRegex(MODULE.CaseIdContractError, "MISSING_PARENT"):
            registry.link_quote(
                stage_event_ref=ref("quote", "missing"),
                parent_ref=ref("case", "missing"),
                case_id=GOOD_ID,
                payload_fingerprint_value=fp("quote"),
            )
        _, sales_ref = make_case_pair(registry, intake_ref)
        quote_ref = make_quote(registry, sales_ref)
        order_ref = make_order(registry, quote_ref)
        charge_ref = ref("charge", "parent-is-a-charge")
        registry.link_order_charge(
            stage_event_ref=charge_ref,
            parent_ref=order_ref,
            case_id=GOOD_ID,
            payload_fingerprint_value=fp("first-charge"),
        )
        with self.assertRaisesRegex(
            MODULE.CaseIdContractError, "INVALID_PARENT_KIND"
        ):
            registry.link_order_charge(
                stage_event_ref=ref("charge", "wrong-parent-kind"),
                parent_ref=charge_ref,
                case_id=GOOD_ID,
                payload_fingerprint_value=fp("charge"),
            )
        self.assertEqual(registry.node_count, 6)

    def test_durable_reservation_survives_restart_and_two_connections(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "private"
            path = root / "ledger.sqlite3"
            first_factory = SequenceFactory(GOOD_ID)
            first = MODULE.SQLiteIntakeLedger(path, first_factory)
            event_ref = ref("intake", "restart-event")
            self.assertEqual(
                first.reserve(
                    stage_event_ref=event_ref,
                    payload_fingerprint_value=fp("same-payload"),
                ),
                (GOOD_ID, True),
            )
            restarted_factory = SequenceFactory(OTHER_ID)
            restarted = MODULE.SQLiteIntakeLedger(path, restarted_factory)
            self.assertEqual(
                restarted.reserve(
                    stage_event_ref=event_ref,
                    payload_fingerprint_value=fp("same-payload"),
                ),
                (GOOD_ID, False),
            )
            self.assertEqual(first_factory.calls, 1)
            self.assertEqual(restarted_factory.calls, 0)
            self.assertEqual(restarted.row_count(), 1)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

            race_path = root / "race.sqlite3"
            left_factory = SequenceFactory(GOOD_ID)
            right_factory = SequenceFactory(OTHER_ID)
            left = MODULE.SQLiteIntakeLedger(race_path, left_factory)
            right = MODULE.SQLiteIntakeLedger(race_path, right_factory)
            race_ref = ref("intake", "two-connection-event")
            barrier = threading.Barrier(2)
            results = []
            errors = []

            def worker(ledger):
                try:
                    barrier.wait()
                    results.append(
                        ledger.reserve(
                            stage_event_ref=race_ref,
                            payload_fingerprint_value=fp("same-payload"),
                        )
                    )
                except Exception as exc:  # pragma: no cover - assertion reports it
                    errors.append(exc)

            threads = [
                threading.Thread(target=worker, args=(left,)),
                threading.Thread(target=worker, args=(right,)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(errors, [])
            self.assertEqual(len({item[0] for item in results}), 1)
            self.assertEqual(sum(1 for _, created in results if created), 1)
            self.assertEqual(left.row_count(), 1)
            self.assertEqual(left_factory.calls + right_factory.calls, 1)

    def test_legacy_backfill_boundary_fails_closed(self):
        self.assertEqual(
            MODULE.classify_migration_row(
                pre_cutover=True, case_id=None, link_basis=None
            ),
            "LEGACY_UNLINKED",
        )
        self.assertEqual(
            MODULE.classify_migration_row(
                pre_cutover=False, case_id=None, link_basis=None
            ),
            "CONTRACT_VIOLATION",
        )
        self.assertEqual(
            MODULE.classify_migration_row(
                pre_cutover=True,
                case_id=GOOD_ID,
                link_basis="owner_verified_evidence",
            ),
            "HISTORICAL_VERIFIED",
        )
        with self.assertRaisesRegex(
            MODULE.CaseIdContractError, "PROSPECTIVE_PROVENANCE_REQUIRED"
        ):
            MODULE.classify_migration_row(
                pre_cutover=False, case_id=GOOD_ID, link_basis=None
            )
        with tempfile.TemporaryDirectory() as temp:
            ledger = MODULE.SQLiteIntakeLedger(
                Path(temp).resolve() / "private" / "intake.sqlite3",
                SequenceFactory(GOOD_ID),
            )
            event_ref = ref("intake", "migration-proof")
            ledger.reserve(
                stage_event_ref=event_ref,
                payload_fingerprint_value=fp("migration-proof"),
            )
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError, "PROSPECTIVE_PROVENANCE_REQUIRED"
            ):
                MODULE.classify_migration_row(
                    pre_cutover=False,
                    case_id=GOOD_ID,
                    link_basis="prospective_intake",
                    intake_ledger=None,
                    stage_event_ref=event_ref,
                )
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError, "PROSPECTIVE_PROVENANCE_REQUIRED"
            ):
                MODULE.classify_migration_row(
                    pre_cutover=False,
                    case_id=OTHER_ID,
                    link_basis="prospective_intake",
                    intake_ledger=ledger,
                    stage_event_ref=event_ref,
                )
            self.assertEqual(
                MODULE.classify_migration_row(
                    pre_cutover=False,
                    case_id=GOOD_ID,
                    link_basis="prospective_intake",
                    intake_ledger=ledger,
                    stage_event_ref=event_ref,
                ),
                "PROSPECTIVE_LINKED",
            )
        for basis in ("name", "date", "content_hash", "fuzzy"):
            with self.subTest(basis=basis):
                with self.assertRaisesRegex(
                    MODULE.CaseIdContractError, "LEGACY_AUTO_LINK_FORBIDDEN"
                ):
                    MODULE.classify_migration_row(
                        pre_cutover=True, case_id=None, link_basis=basis
                    )

    def test_receipt_is_private_allowlisted_and_writer_is_atomic(self):
        canaries = [
            "客戶秘密姓名",
            "0912-345-678",
            "台南市秘密地址",
            "/private/customer/path",
            GOOD_ID,
            "raw-google-sheet-id",
        ]
        receipt = MODULE.build_contract_receipt(
            generated_at="2026-08-27T19:49:04.146000+00:00"
        )
        serialised = json.dumps(receipt, ensure_ascii=False)
        for canary in canaries:
            self.assertNotIn(canary, serialised)
            self.assertNotIn(canary.encode().hex(), serialised)
            self.assertNotIn(
                hashlib.sha256(canary.encode()).hexdigest(), serialised
            )
        self.assertEqual(receipt["privacy"]["external_network_calls"], 0)
        self.assertEqual(receipt["privacy"]["model_calls"], 0)
        self.assertEqual(receipt["privacy"]["google_writes"], 0)
        self.assertEqual(receipt["confirmed_leakage_amount"], 0)
        self.assertTrue(receipt["contract_ready_for_proposal"])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            root.chmod(0o755)
            output = root / "private" / "receipt.json"
            MODULE.write_private_json(output.resolve(), receipt)
            self.assertEqual(stat.S_IMODE(output.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertEqual(json.loads(output.read_text()), receipt)
            self.assertEqual(list(output.parent.glob("*.tmp")), [])
            tainted = {**receipt, "customer_payload": "客戶秘密姓名"}
            rejected_output = root / "rejected" / "receipt.json"
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError,
                "RECEIPT_TOP_LEVEL_ALLOWLIST_VIOLATION",
            ):
                MODULE.write_private_json(rejected_output.resolve(), tainted)
            self.assertFalse(rejected_output.exists())

            nested_taint = deepcopy(receipt)
            nested_taint["privacy"]["unexpected_private_field"] = (
                "SYNTHETIC_PRIVATE_SENTINEL"
            )
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError, "RECEIPT_PRIVACY_ASSERTION_FAILED"
            ):
                MODULE.write_private_json(
                    (root / "nested" / "receipt.json").resolve(), nested_taint
                )

            timestamp_taint = deepcopy(receipt)
            timestamp_taint["generated_at"] = "SYNTHETIC_PRIVATE_SENTINEL"
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError, "RECEIPT_TIMESTAMP_INVALID"
            ):
                MODULE.write_private_json(
                    (root / "timestamp" / "receipt.json").resolve(),
                    timestamp_taint,
                )

            nested_value_taint = deepcopy(receipt)
            target = next(
                row
                for row in nested_value_taint["scenario_results"]
                if row["scenario"] == "asset_case_id_mismatch"
            )
            target["observed"] = "ARBITRARY_NESTED_SECRET_SENTINEL"
            target["passed"] = False
            nested_value_taint["passed_expected"] = 9
            nested_value_taint["failed_expectations"] = [
                "asset_case_id_mismatch"
            ]
            nested_value_taint["contract_ready_for_proposal"] = False
            nested_value_taint["adoption_status"] = "HOLD"
            nested_value_taint["eligible_for_separate_live_review"] = False
            nested_value_taint["next_repair_point"] = "repair_case_id_contract"
            body = dict(nested_value_taint)
            body.pop("generated_at")
            body.pop("deterministic_body_sha256")
            nested_value_taint["deterministic_body_sha256"] = (
                MODULE.sha256_json(body)
            )
            with self.assertRaisesRegex(
                MODULE.CaseIdContractError,
                "RECEIPT_SCENARIO_VALUE_MISMATCH",
            ):
                MODULE.write_private_json(
                    (root / "nested-value" / "receipt.json").resolve(),
                    nested_value_taint,
                )

    def test_manifest_is_deterministic_and_stop_loss_is_strict(self):
        first = MODULE.build_contract_receipt(
            generated_at="2026-08-27T19:49:04.146000+00:00"
        )
        second = MODULE.build_contract_receipt(
            generated_at="2026-08-27T19:49:05.146000+00:00"
        )
        self.assertEqual(
            first["deterministic_body_sha256"],
            second["deterministic_body_sha256"],
        )
        self.assertEqual(
            first["fixture_manifest_sha256"], second["fixture_manifest_sha256"]
        )
        self.assertEqual(first["scenario_count"], 10)
        self.assertEqual(first["passed_expected"], 10)
        self.assertEqual(first["failed_expectations"], [])
        self.assertEqual(first["adoption_status"], "PROPOSAL_ONLY")
        self.assertFalse(first["live_adoption"])
        self.assertEqual(first["method_contract"]["model"], "none")
        self.assertEqual(len(first["method_contract"]["fingerprint"]), 64)

        with mock.patch.dict(
            MODULE.EXPECTED_SCENARIO_OUTCOMES,
            {"asset_case_id_mismatch": "ACCEPTED"},
        ):
            failed = MODULE.build_contract_receipt(
                generated_at="2026-08-27T19:49:06.146000+00:00"
            )
        self.assertFalse(failed["contract_ready_for_proposal"])
        self.assertEqual(failed["adoption_status"], "HOLD")
        self.assertFalse(failed["eligible_for_separate_live_review"])
        self.assertEqual(
            failed["failed_expectations"], ["asset_case_id_mismatch"]
        )
        self.assertEqual(failed["next_repair_point"], "repair_case_id_contract")

    def test_cli_emits_only_opaque_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp).resolve() / "private" / "customer-canary-name.json"
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)
            self.assertEqual(summary["passed_expected"], 10)
            self.assertTrue(summary["five_stage_chain_preserved"])
            self.assertNotIn("customer-canary-name", result.stdout)
            self.assertEqual(result.stderr, "")
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
