import copy
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_case_id_integration_plan.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_case_id_integration_plan_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SourceInventoryTests(unittest.TestCase):
    def test_current_repo_matches_pinned_source_and_plan_contract(self):
        anchors = MODULE.inspect_source_anchors(ROOT)
        self.assertGreaterEqual(len(anchors), 16)
        self.assertTrue(all(row["status"] == "PRESENT" for row in anchors))
        self.assertTrue(all(row["pinned_sha256_matches"] for row in anchors))
        plan = MODULE.inspect_plan_contract(ROOT)
        self.assertEqual(plan["status"], "PRESENT")
        self.assertTrue(plan["pinned_sha256_matches"])
        self.assertEqual(plan["missing_heading_ids"], ())
        self.assertEqual(plan["missing_gate_ids"], ())

    def test_single_source_change_fails_pinned_digest_even_if_fragments_remain(self):
        relative = "scripts/apps-script/LineWebhook.gs"
        changed = (ROOT / relative).read_text(encoding="utf-8") + "\n// drift\n"
        anchors = MODULE.inspect_source_anchors(ROOT, {relative: changed})
        affected = [row for row in anchors if row["path"] == relative]
        self.assertTrue(affected)
        self.assertTrue(all(row["status"] == "DRIFT" for row in affected))
        self.assertTrue(all(not row["pinned_sha256_matches"] for row in affected))

    def test_symlinked_source_is_not_trusted(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            root = Path(temp_dir)
            target = root / "outside.gs"
            target.write_text("function handleLineWebhook_(e) {}", encoding="utf-8")
            source_dir = root / "scripts" / "apps-script"
            source_dir.mkdir(parents=True)
            (source_dir / "LineWebhook.gs").symlink_to(target)
            anchors = MODULE.inspect_source_anchors(root)
            line = next(row for row in anchors if row["anchor_id"] == "line_blank_case_id")
            self.assertEqual(line["status"], "DRIFT")

    def test_orders_writer_remains_unresolved_not_guessed(self):
        inventory = MODULE.orders_writer_inventory(ROOT)
        self.assertGreater(inventory["scanned_file_count"], 0)
        self.assertEqual(inventory["matching_file_count"], 0)
        self.assertEqual(inventory["status"], "AUTHORITATIVE_WRITER_UNRESOLVED")

    def test_declared_line_project_symlink_is_layout_change_not_missing(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            root = Path(temp_dir)
            app_dir = root / "scripts" / "apps-script"
            app_dir.mkdir(parents=True)
            (app_dir / ".claspignore").write_text("LineWebhook.gs\n", encoding="utf-8")
            target = root / "external-line-project"
            target.mkdir()
            (root / "scripts" / "apps-script-line").symlink_to(target)
            inventory = MODULE.deployment_source_inventory(root)
            self.assertTrue(inventory["declared_line_project_exists_or_symlink"])
            self.assertFalse(inventory["declared_line_project_trusted_directory"])
            self.assertEqual(
                inventory["status"], "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED"
            )


class HeaderAndCellFixtureTests(unittest.TestCase):
    def test_named_headers_accept_reorder_extra_and_nfkc(self):
        required = MODULE.TARGET_HEADERS["SALES_INTAKE"]
        fullwidth_case_id = "ｃａｓｅ＿ｉｄ"
        actual = ("notes",) + tuple(reversed(required[1:])) + (fullwidth_case_id,)
        accepted, codes = MODULE.validate_named_headers(actual, required)
        self.assertTrue(accepted)
        self.assertEqual(codes, ())

    def test_named_headers_reject_all_fail_closed_shapes(self):
        required = MODULE.TARGET_HEADERS["SALES_INTAKE"]
        cases = (
            ((), "HEADER_EMPTY"),
            (("case_id", "case_id") + required[1:], "HEADER_DUPLICATE"),
            (required + ("",), "HEADER_BLANK"),
            (required + ("1234",), "HEADER_NUMERIC"),
            ((object(),) + required, "HEADER_NON_STRING"),
            (required[:-1], "REQUIRED_HEADER_MISSING"),
        )
        for actual, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                accepted, codes = MODULE.validate_named_headers(actual, required)
                self.assertFalse(accepted)
                self.assertIn(expected_code, codes)

        accepted, codes = MODULE.validate_named_headers(
            required,
            required,
            schema_version="legacy",
            expected_schema_version="case-id-linkage-v1",
        )
        self.assertFalse(accepted)
        self.assertIn("SCHEMA_VERSION_MISMATCH", codes)

    def test_formula_injection_is_rejected_but_controlled_formula_is_explicit(self):
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "UNTRUSTED_FORMULA"):
            MODULE.validate_sheet_cell('=IMPORTXML("private","//x")')
        self.assertEqual(
            MODULE.validate_sheet_cell('=IFERROR(1,"pending")', controlled_formula=True),
            "CONTROLLED_FORMULA",
        )
        self.assertEqual(MODULE.validate_sheet_cell("customer text"), "LITERAL_VALUE")


class PrivacyAndOutboxFixtureTests(unittest.TestCase):
    def private_route(self, **overrides):
        values = {
            "data_class": "private-local-only",
            "provider": "local-domain-worker",
            "contains_raw_context": True,
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
        values.update(overrides)
        return MODULE.route_private_quote(**values)

    def test_private_route_accepts_only_owner_only_loopback_local_worker(self):
        self.assertEqual(self.private_route(), "LOCAL_ONLY_RAW_CONTEXT_CONTAINED")
        rejection_cases = (
            ({"provider": "cloud-a5"}, "PRIVATE_PROVIDER_FORBIDDEN"),
            ({"endpoint": "remote.internal"}, "PRIVATE_ENDPOINT_NOT_LOOPBACK"),
            ({"artifact_dir_mode": 0o755}, "PRIVATE_ARTIFACT_MODE_UNSAFE"),
            ({"artifact_file_mode": 0o644}, "PRIVATE_ARTIFACT_MODE_UNSAFE"),
            ({"cloud_credentials_present": True}, "PRIVATE_ROUTE_CLOUD_ENV_PRESENT"),
            ({"proxy_present": True}, "PRIVATE_ROUTE_PROXY_PRESENT"),
            ({"provider_override_present": True}, "PRIVATE_ROUTE_PROVIDER_OVERRIDE_PRESENT"),
            ({"model_override_present": True}, "PRIVATE_ROUTE_MODEL_OVERRIDE_PRESENT"),
            ({"artifact_root_outside_repo": False}, "PRIVATE_ARTIFACT_ROOT_IN_REPO"),
            ({"allow_cloud": True}, "PRIVATE_ROUTE_CLOUD_ALLOWED"),
            ({"allow_live_write": True}, "PRIVATE_ROUTE_LIVE_WRITE_FORBIDDEN"),
        )
        for overrides, code in rejection_cases:
            with self.subTest(code=code), self.assertRaisesRegex(
                MODULE.IntegrationPlanError, code
            ):
                self.private_route(**overrides)

        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "UNKNOWN_DATA_CLASS"):
            self.private_route(
                data_class="private-local-onyl",
                provider="cloud-a5",
                contains_raw_context=False,
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

    def test_conceptual_outbox_requires_exact_readback_and_rejects_replay_drift(self):
        outbox = MODULE.SyntheticOutbox()
        self.assertEqual(outbox.stage("event-a", "fp-a"), "PENDING")
        self.assertEqual(outbox.verify("event-a", None), "PENDING")
        self.assertEqual(outbox.verify("event-a", "fp-a"), "COMMITTED")
        self.assertEqual(outbox.stage("event-a", "fp-a"), "COMMITTED")
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "OUTBOX_REPLAY_CONFLICT"):
            outbox.stage("event-a", "changed")

        outbox.stage("event-b", "fp-b")
        self.assertEqual(outbox.verify("event-b", "wrong"), "CONFLICT")

    def test_fixed_fixture_matrix_matches_every_expected_outcome(self):
        results = MODULE.run_fixture_matrix()
        self.assertEqual(
            tuple(row["fixture_id"] for row in results), MODULE.FIXTURE_IDS
        )
        self.assertEqual(len({row["fixture_id"] for row in results}), len(results))
        self.assertTrue(all(row["expected"] == row["observed"] for row in results))

    def test_full_live_header_fixtures_match_prior_read_only_hashes(self):
        results = MODULE.live_header_fixture_inventory()
        self.assertEqual({row["table"] for row in results}, set(MODULE.PINNED_LIVE_HEADER_SHA256))
        self.assertTrue(all(row["matches_pinned"] for row in results))
        orders = next(row for row in results if row["table"] == "Orders")
        self.assertEqual(orders["field_count"], 29)


class ReceiptTests(unittest.TestCase):
    def build(self):
        return MODULE.build_receipt(ROOT, "2026-08-28T04:25:04+00:00")

    @staticmethod
    def rehash(receipt):
        body = {
            key: value
            for key, value in receipt.items()
            if key
            not in {
                "schema_version",
                "created_at",
                "deterministic_body_sha256",
            }
        }
        receipt["deterministic_body_sha256"] = MODULE._sha256_bytes(
            MODULE._canonical_json(body)
        )
        return receipt

    def test_receipt_is_static_plan_only_and_explicitly_not_live_ready(self):
        receipt = self.build()
        self.assertEqual(receipt["decision"]["status"], "STATIC_PLAN_VALIDATED")
        self.assertEqual(receipt["decision"]["adoption_status"], "PROPOSAL_ONLY")
        self.assertFalse(receipt["decision"]["eligible_for_live_change"])
        self.assertFalse(receipt["decision"]["durable_outbox_runtime_validated"])
        self.assertEqual(receipt["decision"]["confirmed_leakage_amount"], 0)
        self.assertEqual(
            receipt["deployed_source_truth"]["status"],
            "INCOMPLETE_OWNER_REVIEW_BOUNDARY",
        )
        self.assertEqual(receipt["safety"]["external_network_calls"], 0)
        self.assertEqual(receipt["safety"]["google_reads"], 0)
        self.assertEqual(receipt["safety"]["google_writes"], 0)
        self.assertEqual(receipt["safety"]["model_calls"], 0)

    def test_nested_allowlist_and_forbidden_values_fail_closed(self):
        receipt = self.build()
        poisoned = copy.deepcopy(receipt)
        poisoned["safety"]["raw_customer_text"] = "secret"
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "NESTED_ALLOWLIST"):
            MODULE._assert_receipt_safe(poisoned)

        poisoned = copy.deepcopy(receipt)
        poisoned["decision"]["note"] = "https://example.invalid"
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "FORBIDDEN_VALUE"):
            MODULE._assert_receipt_safe(poisoned)

        poisoned = copy.deepcopy(receipt)
        poisoned["fixture_results"][0]["code"] = "customer_name Alice phone 0912345678"
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "FIXTURE_VALUE_ALLOWLIST"):
            MODULE.validate_receipt(poisoned)

        poison_cases = (
            ("safety", "contains_raw_text", True, "SAFETY_VALUE_ALLOWLIST"),
            ("safety", "google_writes", 99, "SAFETY_VALUE_ALLOWLIST"),
            ("decision", "adoption_status", "LIVE", "DECISION_VALUE_ALLOWLIST"),
            ("decision", "confirmed_leakage_amount", 999, "DECISION_VALUE_ALLOWLIST"),
            ("decision", "durable_outbox_runtime_validated", True, "DECISION_VALUE_ALLOWLIST"),
        )
        for section, key, value, code in poison_cases:
            with self.subTest(key=key):
                poisoned = copy.deepcopy(receipt)
                poisoned[section][key] = value
                with self.assertRaisesRegex(MODULE.IntegrationPlanError, code):
                    MODULE.validate_receipt(poisoned)

        poisoned = copy.deepcopy(receipt)
        poisoned["deterministic_body_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.IntegrationPlanError, "BODY_SHA256"):
            MODULE.validate_receipt(poisoned)

    def test_plateau_review_values_fail_closed_even_with_valid_body_hash(self):
        receipt = self.build()
        poison_cases = (
            ("same_method_repeated", True),
            ("historical_fuzzy_backfill_reopened", True),
            ("new_repair_point", "customer Alice phone 0912345678"),
        )
        for key, value in poison_cases:
            with self.subTest(key=key):
                poisoned = copy.deepcopy(receipt)
                poisoned["plateau_review"][key] = value
                self.rehash(poisoned)
                with self.assertRaisesRegex(
                    MODULE.IntegrationPlanError,
                    "RECEIPT_PLATEAU_REVIEW_VALUE_ALLOWLIST",
                ):
                    MODULE.validate_receipt(poisoned)

    def test_numeric_receipt_fields_reject_booleans_with_valid_body_hash(self):
        receipt = self.build()
        poison_cases = (
            (
                lambda value: value["orders_writer_inventory"].__setitem__(
                    "scanned_file_count", True
                ),
                "RECEIPT_WRITER_SCAN_COUNT",
            ),
            (
                lambda value: value["orders_writer_inventory"].__setitem__(
                    "matching_file_count", False
                ),
                "RECEIPT_WRITER_MATCH_COUNT",
            ),
            (
                lambda value: value["decision"].__setitem__(
                    "confirmed_leakage_amount", False
                ),
                "RECEIPT_DECISION_VALUE_ALLOWLIST",
            ),
            (
                lambda value: value["orders_writer_inventory"].__setitem__(
                    "scanned_file_count",
                    value["orders_writer_inventory"]["scanned_file_count"] + 1,
                ),
                "RECEIPT_WRITER_VALUE_ALLOWLIST",
            ),
        )
        for mutate, code in poison_cases:
            with self.subTest(code=code):
                poisoned = copy.deepcopy(receipt)
                mutate(poisoned)
                self.rehash(poisoned)
                with self.assertRaisesRegex(MODULE.IntegrationPlanError, code):
                    MODULE.validate_receipt(poisoned)

    def test_source_drift_sets_both_decision_and_adoption_hold(self):
        relative = "scripts/apps-script/LineWebhook.gs"
        changed = (ROOT / relative).read_text(encoding="utf-8") + "\n// drift\n"
        receipt = MODULE.build_receipt(
            ROOT,
            "2026-08-28T04:25:04+00:00",
            source_overrides={relative: changed},
        )
        self.assertEqual(receipt["decision"]["status"], "HOLD")
        self.assertEqual(receipt["decision"]["adoption_status"], "HOLD")

    def test_writer_revalidates_payload_and_rejects_symlink_target(self):
        receipt = self.build()
        tampered = copy.deepcopy(receipt)
        tampered["safety"]["google_writes"] = 1
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(MODULE.IntegrationPlanError, "SAFETY_VALUE_ALLOWLIST"):
                MODULE.write_private_receipt(root / "tampered.json", tampered)

            actual = root / "actual.json"
            actual.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(actual)
            with self.assertRaisesRegex(MODULE.IntegrationPlanError, "SYMLINK_FORBIDDEN"):
                MODULE.write_private_receipt(link, receipt)

    def test_private_receipt_write_is_atomic_owner_only_and_readable(self):
        receipt = self.build()
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            parent = Path(temp_dir) / "private"
            path = parent / "receipt.json"
            MODULE.write_private_receipt(path, receipt)
            self.assertEqual(stat.S_IMODE(parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                json.loads(json.dumps(receipt)),
            )
            self.assertEqual(list(parent.glob(".receipt.json.*")), [])

    def test_cli_summary_is_aggregate_only(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            path = Path(temp_dir) / "receipt.json"
            process = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--repo-root",
                    str(ROOT),
                    "--receipt",
                    str(path),
                    "--created-at",
                    "2026-08-28T04:25:04+00:00",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            summary = json.loads(process.stdout)
            self.assertEqual(summary["decision"], "STATIC_PLAN_VALIDATED")
            self.assertNotIn("case_", process.stdout)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
