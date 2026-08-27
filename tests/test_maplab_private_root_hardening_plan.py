import copy
import importlib.util
import json
import secrets
import stat
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_private_root_hardening_plan.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_private_root_hardening_plan_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
CREATED_AT = MODULE.EXPECTED_CREATED_AT


class CurrentDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MODULE.build_receipt(ROOT, CREATED_AT)

    def test_design_inventory_is_validated_but_runtime_and_live_adoption_hold(self):
        decision = self.receipt["decision"]
        self.assertEqual(decision["status"], "STATIC_DESIGN_INVENTORY_VALIDATED")
        self.assertEqual(decision["adoption_status"], "HOLD")
        self.assertTrue(decision["design_inventory_validated"])
        self.assertFalse(decision["resolver_copy_ledger_runtime_validated"])
        self.assertFalse(decision["eligible_for_live_change"])
        self.assertFalse(decision["live_migration_performed"])
        self.assertFalse(decision["current_quote_deployed_truth_resolved"])
        self.assertFalse(decision["current_line_deployed_truth_resolved"])
        self.assertFalse(decision["orders_writer_resolved"])
        self.assertFalse(decision["header_capable_line_ingress_proven"])

    def test_consumer_graph_includes_google_and_installed_launchagent_files(self):
        self.assertEqual(len(self.receipt["consumer_inventory"]), 62)
        self.assertTrue(
            all(row["status"] == "MATCH" for row in self.receipt["consumer_inventory"])
        )
        google = self.receipt["google_credential_consumers"]
        self.assertEqual(google["repo_reference_count"], 19)
        self.assertEqual(google["external_reference_count"], 4)
        self.assertEqual(google["total_known_consumer_count"], 23)
        self.assertTrue(google["repo_manifest_complete"])
        self.assertTrue(google["repo_consumers_all_source_pinned"])
        self.assertTrue(set(MODULE.GOOGLE_TOKEN_CONSUMERS) <= set(MODULE.PINNED_SOURCE_SHA256))
        self.assertTrue(all(item.path in MODULE.PINNED_SOURCE_SHA256 for item in MODULE.CONSUMERS))
        self.assertEqual(google["safe_external_source_verified_count"], 3)
        self.assertEqual(google["secret_config_metadata_only_count"], 1)
        self.assertFalse(google["external_payload_current_verified"])
        self.assertFalse(google["live_cutover_consumer_truth_complete"])
        runtime = self.receipt["external_runtime_consumers"]
        self.assertEqual(len(runtime), 4)
        self.assertTrue(all(row["matches_pinned"] for row in runtime))
        self.assertTrue(all(not row["runtime_binding_readback"] for row in runtime))

    def test_google_scan_is_git_index_only_and_does_not_read_private_files(self):
        with mock.patch.object(Path, "read_text", side_effect=AssertionError("payload read")):
            found = MODULE.scan_google_token_references(ROOT)
        self.assertEqual(found, set(MODULE.GOOGLE_TOKEN_CONSUMERS))

    def test_private_env_reference_scan_is_tracked_source_only_and_exact(self):
        with mock.patch.object(Path, "read_text", side_effect=AssertionError("payload read")):
            found = MODULE.scan_private_env_references(ROOT)
        self.assertEqual(found, set(MODULE.PRIVATE_ENV_REFERENCE_CONSUMERS))
        inventory = self.receipt["private_env_reference_consumers"]
        self.assertEqual(inventory["repo_reference_count"], 10)
        self.assertTrue(inventory["repo_manifest_complete"])
        self.assertTrue(inventory["repo_consumers_all_source_pinned"])
        self.assertEqual(inventory["private_payload_reads"], 0)

    def test_secret_config_unread_and_safe_external_sources_hash_only(self):
        rows = {
            row["alias"]: row
            for row in self.receipt["google_credential_consumers"]["external_manifest"]
        }
        self.assertEqual(rows["mcp_config"]["current_read_mode"], "NONE")
        self.assertIsNone(rows["mcp_config"]["current_sha256"])
        self.assertIsNone(rows["mcp_config"]["matches_pinned"])
        for alias in ("drive_smoke", "gsc_pull", "reauth"):
            self.assertEqual(rows[alias]["current_read_mode"], "HASH_ONLY_SOURCE_CODE")
            self.assertTrue(rows[alias]["matches_pinned"])

    def test_private_surfaces_and_backup_copy_classes_fail_closed(self):
        modes = self.receipt["current_modes"]
        self.assertEqual(modes["case_store"]["directory_mode"], 0o755)
        self.assertEqual(modes["case_store"]["database_mode"], 0o644)
        self.assertEqual(modes["bot_env"]["file_mode"], 0o644)
        review = modes["openclaw_review"]
        self.assertEqual(review["adapter_bundle_count"], 44)
        self.assertEqual(review["adapter_artifact_file_count"], 352)
        self.assertEqual(review["legacy_manifest_mismatch_count"], 116)
        self.assertEqual(review["legacy_manifest_untrusted_bundle_count"], 44)
        self.assertEqual(review["terminal_unsealed_bundle_count"], 44)
        self.assertEqual(review["routing_unsealed_bundle_count"], 44)
        self.assertEqual(review["adapter_artifact_hardlink_count"], 0)
        self.assertEqual(modes["openclaw_dispatch"]["file_count"], 83)
        self.assertFalse(modes["openclaw_temp_clipboard"]["file_present"])
        backup = modes["backup_propagation"]
        self.assertEqual(backup["generation_count"], 8)
        self.assertEqual(backup["environment_copy_count"], 48)
        self.assertEqual(backup["case_store_copy_count"], 16)
        self.assertEqual(backup["adapter_bundle_copy_count"], 352)
        self.assertEqual(backup["adapter_artifact_copy_count"], 2816)
        self.assertEqual(backup["dispatch_file_copy_count"], 600)
        self.assertEqual(backup["backup_index_copy_count"], 8)
        self.assertEqual(backup["classified_private_copy_count"], 3912)
        self.assertEqual(backup["stale_worktree_copy_count"], 2)
        self.assertFalse(modes["provider_credential"]["owner_only"])
        self.assertEqual(modes["provider_credential"]["source_parent_mode"], 0o755)
        self.assertFalse(modes["hermes_line_training"]["owner_only"])
        self.assertEqual(modes["hermes_line_training"]["file_count"], 38)
        self.assertEqual(modes["hermes_line_training"]["file_mode_histogram"], {"0600": 38})
        self.assertTrue(all(not value["owner_only"] for value in modes.values()))

    def test_target_ownership_and_version_bound_get_only_contracts(self):
        non_adapter = self.receipt["target_contracts"]["shared_review_non_adapter"]
        self.assertEqual(non_adapter["root_symbol"], "MAPLAB_PRIVATE_SHARED_REVIEW_ROOT")
        self.assertIn("fifty-three-current-non-adapter", non_adapter["readback"])
        self.assertIn("future-classified-writes-external-only", non_adapter["readback"])
        self.assertIn("never-write-private-bytes-back-to-shared-repo", non_adapter["rollback"])
        non_adapter_consumers = {
            row["path"]
            for row in self.receipt["consumer_inventory"]
            if row["surface"] == "shared_review_non_adapter"
        }
        self.assertEqual(
            non_adapter_consumers,
            {"tools/wp_rankmath_recovery.py", "tools/google_reindex_submit.py"},
        )
        for contract in self.receipt["target_contracts"].values():
            self.assertEqual(contract["path_class"], "OWNER_HOME_EXTERNAL_TO_REPO")
            self.assertEqual(contract["directory_mode"], 0o700)
            self.assertEqual(contract["file_mode"], 0o600)
            self.assertFalse(contract["symlink_allowed"])
            self.assertEqual(contract["owner_uid"], "effective-user")
            self.assertTrue(contract["parent_chain_owner_uid_required"])
            self.assertTrue(contract["regular_files_only"])
            self.assertFalse(contract["hardlink_allowed"])
            self.assertFalse(contract["acl_entries_allowed"])
        plan = self.receipt["deployed_readback_plan"]
        self.assertFalse(plan["reuse_shared_google_credential"])
        self.assertEqual(sorted(plan["required_scopes"]), sorted(MODULE.APPS_SCRIPT_READONLY_SCOPES))
        self.assertEqual(plan["versioned_content_method"], "projects.getContent(versionNumber)")
        self.assertEqual(plan["per_target_planned_read_calls"], 3)
        self.assertTrue(plan["deployment_metadata_double_read_required"])
        self.assertFalse(plan["head_only_is_deployed_truth"])
        self.assertEqual(plan["transport_methods_allowed"], ["GET"])
        self.assertTrue(plan["transport_get_only"])
        self.assertEqual(plan["write_methods_allowed"], [])
        self.assertFalse(plan["clasp_allowed"])
        self.assertFalse(plan["shared_mcp_allowed"])

    def test_all_thirty_nine_policy_fixtures_pass_without_runtime_overclaim(self):
        rows = self.receipt["synthetic_fixtures"]
        self.assertEqual(len(rows), 39)
        self.assertTrue(all(row["result"] == "PASS" for row in rows))
        by_name = {row["name"]: row["actual"] for row in rows}
        expected = {
            "backup_still_copying": "REJECT_BACKUP_PROPAGATION",
            "trust_stale_manifest": "REJECT_LEGACY_MANIFEST_TRUST",
            "wrong_owner_uid": "REJECT_OWNER_UID",
            "hardlink_alias": "REJECT_HARDLINK",
            "acl_entry": "REJECT_ACL",
            "head_only": "REJECT_HEAD_ONLY",
            "deployment_changed_midread": "REJECT_TOCTOU",
            "wrong_read_call_count": "REJECT_READ_CALL_COUNT",
        }
        for name, result in expected.items():
            self.assertEqual(by_name[name], result)

    def test_safety_accounts_for_reads_and_receipt_only_writes(self):
        safety = self.receipt["safety"]
        expected_reads = {
            "private_artifact_hash_reads": 264,
            "private_manifest_metadata_reads": 44,
            "private_review_request_text_reads": 44,
            "source_file_hash_reads": 67,
            "source_anchor_text_reads": 62,
            "credential_file_metadata_reads": 4,
            "provider_credential_metadata_reads": 2,
            "training_root_metadata_reads": 43,
            "external_safe_source_hash_reads": 3,
            "external_runtime_config_file_hash_reads": 4,
        }
        for key, expected in expected_reads.items():
            self.assertEqual(safety[key], expected)
        self.assertEqual(safety["credential_payload_reads"], 0)
        self.assertEqual(safety["environment_payload_reads"], 0)
        for key in (
            "network_calls", "apps_script_api_calls", "live_target_chmod_operations",
            "live_target_copy_operations", "live_target_move_operations",
            "live_target_restart_operations", "deployment_writes",
            "credential_writes", "google_writes",
        ):
            self.assertEqual(safety[key], 0)
        self.assertEqual(safety["receipt_artifact_replace_operations"], 1)
        self.assertEqual(safety["receipt_permission_operations"], 1)
        self.assertEqual(safety["receipt_fsync_operations"], 2)
        self.assertEqual(safety["receipt_post_write_readbacks"], 1)
        self.assertEqual(safety["receipt_validation_passes"], 3)

    def test_receipt_emits_no_actual_binding_secret_or_private_path(self):
        binding = json.loads(
            (ROOT / "scripts" / "apps-script" / ".clasp.json").read_text(encoding="utf-8")
        )["scriptId"]
        serialized = json.dumps(self.receipt, ensure_ascii=False, sort_keys=True)
        self.assertNotIn(binding, serialized)
        self.assertNotIn("/Users/", serialized)
        self.assertNotIn("/tmp/", serialized)
        self.assertNotIn("file://", serialized.lower())
        for forbidden in ('"access_token"', '"refresh_token"', '"client_secret"'):
            self.assertNotIn(forbidden, serialized)


class BoundaryTests(unittest.TestCase):
    def test_source_drift_and_method_manifest_changes_are_detected(self):
        relative = "bot_a6/case_store.py"
        changed = (ROOT / relative).read_bytes() + b"\n# synthetic drift\n"
        row = next(
            item for item in MODULE.inspect_source_pins(ROOT, {relative: changed})
            if item["path"] == relative
        )
        self.assertFalse(row["matches_pinned"])
        baseline = MODULE.method_fingerprint()
        original_pin = MODULE.PINNED_SOURCE_SHA256[relative]
        original_consumers = MODULE.CONSUMERS
        try:
            MODULE.PINNED_SOURCE_SHA256[relative] = "0" * 64
            self.assertNotEqual(MODULE.method_fingerprint(), baseline)
            MODULE.PINNED_SOURCE_SHA256[relative] = original_pin
            first = original_consumers[0]
            MODULE.CONSUMERS = (
                MODULE.Consumer(first.surface, first.path, first.role, first.anchors + ("new-anchor",)),
            ) + original_consumers[1:]
            self.assertNotEqual(MODULE.method_fingerprint(), baseline)
        finally:
            MODULE.PINNED_SOURCE_SHA256[relative] = original_pin
            MODULE.CONSUMERS = original_consumers

    @staticmethod
    def migration_state():
        return {
            "source_snapshot_pinned": True, "target_external_to_repo": True,
            "target_dir_mode": 0o700, "target_file_mode": 0o600,
            "target_symlink_free": True, "target_owner_uid_matches": True,
            "target_regular_types": True, "target_hardlink_free": True,
            "parent_chain_owner_uid_matches": True, "target_acl_free": True,
            "consumer_manifest_complete": True, "copy_digest_matches": True,
            "readback_matches": True, "cutover_cas_matches": True,
            "rollback_snapshot_preserved": True, "backup_propagation_stopped": True,
            "actual_byte_ledger_complete": True, "legacy_manifest_used_as_truth": False,
            "new_writes_external_only": True, "physical_paths_redacted": True,
            "active_writer_quiesced": True,
        }

    def test_migration_gate_rejects_alias_owner_type_hardlink_acl_and_manifest(self):
        cases = (
            ({"target_file_mode": True}, "REJECT_FILE_MODE"),
            ({"target_owner_uid_matches": False}, "REJECT_OWNER_UID"),
            ({"target_regular_types": False}, "REJECT_NON_REGULAR_TYPE"),
            ({"target_hardlink_free": False}, "REJECT_HARDLINK"),
            ({"parent_chain_owner_uid_matches": False}, "REJECT_PARENT_OWNER_UID"),
            ({"target_acl_free": False}, "REJECT_ACL"),
            ({"legacy_manifest_used_as_truth": True}, "REJECT_LEGACY_MANIFEST_TRUST"),
        )
        for mutation, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    MODULE.evaluate_migration_precheck(dict(self.migration_state(), **mutation)), expected
                )

    @staticmethod
    def readback_state():
        return {
            "dedicated_credential": True, "credential_owner_only": True,
            "credential_symlink_free": True, "scopes": list(MODULE.APPS_SCRIPT_READONLY_SCOPES),
            "deployment_version_bound": True, "versioned_content_used": True,
            "raw_source_persisted": False, "raw_identifiers_persisted": False,
            "write_methods": [], "direct_gas_line_authority": False,
            "deployment_double_read_stable": True, "target_binding_current_verified": True,
            "transport_get_only": True, "planned_get_calls": 3,
        }

    def test_readback_gate_rejects_scope_head_raw_write_transport_and_call_count(self):
        cases = (
            ({"scopes": ["https://www.googleapis.com/auth/script.projects"]}, "REJECT_SCOPE_SET"),
            ({"versioned_content_used": False}, "REJECT_HEAD_ONLY"),
            ({"raw_source_persisted": True}, "REJECT_RAW_SOURCE_PERSISTENCE"),
            ({"write_methods": ["projects.updateContent"]}, "REJECT_WRITE_METHOD"),
            ({"direct_gas_line_authority": True}, "REJECT_DIRECT_GAS_LINE_AUTHORITY"),
            ({"transport_get_only": False}, "REJECT_TRANSPORT_METHOD"),
            ({"planned_get_calls": 2}, "REJECT_READ_CALL_COUNT"),
        )
        for mutation, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    MODULE.evaluate_readback_precheck(dict(self.readback_state(), **mutation)), expected
                )


class ReceiptValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MODULE.build_receipt(ROOT, CREATED_AT)

    @staticmethod
    def rehash(receipt):
        body = {
            key: value for key, value in receipt.items()
            if key not in {"schema_version", "deterministic_body_sha256"}
        }
        receipt["deterministic_body_sha256"] = MODULE._sha256_bytes(MODULE._canonical_json(body))

    def assert_rejected(self, mutation, code):
        changed = copy.deepcopy(self.receipt)
        mutation(changed)
        self.rehash(changed)
        with self.assertRaisesRegex(MODULE.HardeningPlanError, code):
            MODULE.validate_receipt(changed)

    def test_manifest_provenance_and_get_only_poison_are_rejected(self):
        self.assert_rejected(
            lambda value: value["consumer_inventory"][0].__setitem__("role", "invented"),
            "CONSUMER_MANIFEST",
        )
        self.assert_rejected(
            lambda value: value["implementation_provenance"][0].__setitem__("sha256", "0" * 64),
            "IMPLEMENTATION_PROVENANCE",
        )
        self.assert_rejected(
            lambda value: value["deployed_readback_plan"].__setitem__(
                "transport_methods_allowed", ["GET", "POST"]
            ),
            "READBACK_PLAN",
        )

    def test_bool_data_class_raw_id_source_secret_and_decision_poison_are_rejected(self):
        mutations = (
            (lambda value: value["safety"].__setitem__("network_calls", False), "SAFETY_ZERO_TYPE_OR_VALUE"),
            (lambda value: value["current_modes"]["openclaw_review"].__setitem__("generic_fixed_basename_symlink_count", False), "OPENCLAW_MODE_BOUNDARY"),
            (lambda value: value.__setitem__("data_class", "/Users/synthetic/private.json"), "DATA_CLASS"),
            (lambda value: value["current_modes"]["case_store"].__setitem__("raw_identifier", "synthetic-raw-id"), "CASE_MODE_BOUNDARY"),
            (lambda value: value["method_contract"].__setitem__("stop_loss", "function doPost secret-value"), "METHOD_CONTRACT"),
            (lambda value: value["decision"].__setitem__("eligible_for_live_change", True), "DECISION_BOUNDARY"),
        )
        for mutation, code in mutations:
            with self.subTest(code=code):
                self.assert_rejected(mutation, code)

    def test_writer_is_root_bounded_owner_only_and_symlink_safe(self):
        root = MODULE.PRIVATE_RECEIPT_ROOT
        token = secrets.token_hex(8)
        receipt_path = root / f"test-private-plan-{token}.json"
        target = root / f"test-target-{token}"
        link = root / f"test-link-{token}.json"
        broken = root / f"test-broken-{token}.json"
        try:
            MODULE.write_private_receipt(receipt_path, self.receipt)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)
            MODULE.validate_receipt(json.loads(receipt_path.read_text(encoding="utf-8")))
            target.write_text("not a receipt", encoding="utf-8")
            link.symlink_to(target)
            with self.assertRaisesRegex(MODULE.HardeningPlanError, "RECEIPT_SYMLINK"):
                MODULE.write_private_receipt(link, self.receipt)
            broken.symlink_to(root / f"missing-{token}")
            with self.assertRaisesRegex(MODULE.HardeningPlanError, "RECEIPT_SYMLINK"):
                MODULE.write_private_receipt(broken, self.receipt)
            with self.assertRaisesRegex(MODULE.HardeningPlanError, "RECEIPT_PATH_NOT_ABSOLUTE"):
                MODULE.write_private_receipt(Path("relative.json"), self.receipt)
            with self.assertRaisesRegex(MODULE.HardeningPlanError, "RECEIPT_PATH_OUTSIDE_PRIVATE_ROOT"):
                MODULE.write_private_receipt(ROOT / f"outside-{token}.json", self.receipt)
        finally:
            for path in (receipt_path, link, broken, target):
                if path.is_symlink() or path.exists():
                    path.unlink()

    def test_cli_summary_and_outside_path_rejection(self):
        token = secrets.token_hex(8)
        receipt_path = MODULE.PRIVATE_RECEIPT_ROOT / f"test-cli-{token}.json"
        outside = ROOT / f"should-not-write-{token}.json"
        try:
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--repo-root", str(ROOT),
                 "--receipt", str(receipt_path), "--created-at", CREATED_AT],
                check=True, capture_output=True, text=True,
            )
            summary = json.loads(result.stdout)
            self.assertEqual(summary["status"], "STATIC_DESIGN_INVENTORY_VALIDATED")
            self.assertEqual(summary["consumer_anchors"], 62)
            self.assertEqual(summary["shared_credential_references"], 23)
            self.assertEqual(summary["fixture_passed"], 39)
            self.assertFalse(summary["live_change"])
            self.assertNotIn("scriptId", result.stdout)
            self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)
            rejected = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--repo-root", str(ROOT),
                 "--receipt", str(outside), "--created-at", CREATED_AT],
                capture_output=True, text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(outside.exists())
        finally:
            if receipt_path.exists():
                receipt_path.unlink()


if __name__ == "__main__":
    unittest.main()
