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
MODULE_PATH = ROOT / "scripts" / "maplab_deployed_source_inventory.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_deployed_source_inventory_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


HEADER_OBSERVATIONS = [
    {"table": table, "field_count": count, "sha256": digest}
    for table, (count, digest) in MODULE.PINNED_HEADER_SHA256.items()
]
CREATED_AT = "2026-08-27T21:06:04.406000+00:00"


class CurrentInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MODULE.build_receipt(
            ROOT,
            CREATED_AT,
            HEADER_OBSERVATIONS,
            connector_metadata_reads=2,
            connector_header_reads=7,
        )

    def test_current_inventory_is_complete_but_live_adoption_holds(self):
        decision = self.receipt["decision"]
        self.assertEqual(decision["status"], "READ_ONLY_INVENTORY_COMPLETE")
        self.assertEqual(decision["adoption_status"], "HOLD")
        self.assertFalse(decision["eligible_for_live_change"])
        self.assertFalse(decision["deployed_source_truth_complete"])
        self.assertFalse(decision["private_roots_owner_only"])
        self.assertFalse(decision["orders_writer_resolved"])
        self.assertFalse(decision["line_header_capable_ingress_proven"])
        self.assertEqual(decision["confirmed_leakage_amount"], 0)

    def test_local_source_and_headers_match_without_claiming_deployment(self):
        self.assertTrue(all(row["matches_pinned"] for row in self.receipt["source_pins"]))
        self.assertTrue(all(row["matches_pinned"] for row in self.receipt["live_headers"]))
        quote = self.receipt["quote_gas"]
        self.assertEqual(
            quote["status"], "LOCAL_BINDING_PRESENT_DEPLOYED_REVISION_UNRESOLVED"
        )
        self.assertIsNone(quote["deployed_revision_sha256"])
        line = self.receipt["line_gas"]
        self.assertEqual(line["status"], "DECLARED_CHECKOUT_MISSING")
        self.assertFalse(line["direct_gas_header_capable"])
        self.assertIsNone(line["deployed_revision_sha256"])

    def test_historical_fingerprints_are_pinned_but_not_current_truth(self):
        historical = self.receipt["historical_evidence"]
        self.assertEqual(historical, MODULE.HISTORICAL_EVIDENCE)
        self.assertFalse(historical["current_deployed_source_complete"])
        self.assertEqual(historical["line_last_observed_date"], "2026-05-19")

    def test_writer_authority_remains_unresolved(self):
        writer = self.receipt["orders_writer"]
        self.assertGreater(writer["current_source_file_count"], 0)
        self.assertEqual(writer["current_writer_match_count"], 0)
        self.assertEqual(writer["git_history_selector_match_count"], 0)
        self.assertFalse(writer["quote_gas_is_authoritative_writer"])
        self.assertEqual(writer["status"], "AUTHORITATIVE_WRITER_UNRESOLVED")

    def test_private_roots_and_credential_fail_closed(self):
        roots = self.receipt["private_roots"]
        self.assertTrue(roots["case_store"]["env_override_present"])
        self.assertTrue(roots["case_store"]["repo_path_override_present"])
        self.assertEqual(
            roots["case_store"]["repo_path_fingerprint"],
            MODULE.PINNED_REPO_PATH_FINGERPRINT,
        )
        self.assertTrue(roots["case_store"]["repo_path_matches_repo_root"])
        self.assertEqual(roots["case_store"]["directory_mode"], 0o755)
        self.assertEqual(roots["case_store"]["database_mode"], 0o644)
        self.assertTrue(roots["case_store"]["fallback_present"])
        self.assertEqual(roots["case_store"]["fallback_mode"], 0o644)
        self.assertFalse(roots["case_store"]["fallback_owner_only"])
        self.assertEqual(roots["case_store"]["status"], "REPO_LOCAL_UNSAFE")
        self.assertEqual(roots["openclaw"]["review_root_mode"], 0o755)
        self.assertEqual(
            roots["openclaw"]["artifact_file_count"],
            MODULE.EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT,
        )
        self.assertEqual(
            roots["openclaw"]["artifact_file_mode_histogram"],
            MODULE.EXPECTED_OPENCLAW_ARTIFACT_MODE_HISTOGRAM,
        )
        self.assertEqual(roots["openclaw"]["artifact_owner_only_file_count"], 0)
        self.assertEqual(
            roots["openclaw"]["artifact_unsafe_file_count"],
            MODULE.EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT,
        )
        self.assertEqual(roots["openclaw"]["artifact_symlink_count"], 0)
        self.assertEqual(roots["openclaw"]["status"], "REPO_LOCAL_UNSAFE")
        self.assertTrue(roots["launcher"]["runtime_umask_declared_owner_only"])
        self.assertFalse(roots["launcher"]["existing_paths_owner_only"])
        credential = self.receipt["credential_preflight"]
        self.assertEqual(credential["token_mode"], 0o644)
        self.assertFalse(credential["owner_only"])
        self.assertFalse(credential["apps_script_scope_present"])
        self.assertFalse(credential["safe_for_apps_script_readback"])

    def test_receipt_contains_no_raw_binding_or_secret_value(self):
        binding = json.loads(
            (ROOT / "scripts" / "apps-script" / ".clasp.json").read_text(
                encoding="utf-8"
            )
        )["scriptId"]
        serialized = json.dumps(self.receipt, ensure_ascii=False, sort_keys=True)
        self.assertNotIn(binding, serialized)
        self.assertNotIn("access_token", serialized)
        self.assertNotIn("refresh_token", serialized)
        self.assertNotIn("https://", serialized)

    def test_read_counts_are_honest_and_write_counts_zero(self):
        safety = self.receipt["safety"]
        self.assertEqual(safety["connector_metadata_reads"], 2)
        self.assertEqual(safety["connector_header_reads"], 7)
        self.assertEqual(safety["google_read_operations"], 9)
        self.assertEqual(safety["google_writes"], 0)
        self.assertEqual(safety["apps_script_api_calls"], 0)
        self.assertFalse(safety["customer_send"])


class HeaderTests(unittest.TestCase):
    def test_null_placeholders_are_ignored_but_literal_null_is_preserved(self):
        fields = [
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
        ]
        with_null_placeholders = fields[:4] + [None, None] + fields[4:]
        self.assertEqual(
            MODULE.header_sha256(with_null_placeholders),
            MODULE.PINNED_HEADER_SHA256["MAPLAB_ASSET_LOG"][1],
        )
        self.assertNotEqual(
            MODULE.header_sha256(fields + ["null"]),
            MODULE.PINNED_HEADER_SHA256["MAPLAB_ASSET_LOG"][1],
        )

    def test_changed_header_hash_sets_hold(self):
        changed = copy.deepcopy(HEADER_OBSERVATIONS)
        changed[0]["sha256"] = "0" * 64
        receipt = MODULE.build_receipt(
            ROOT,
            CREATED_AT,
            changed,
            connector_metadata_reads=2,
            connector_header_reads=7,
        )
        self.assertEqual(receipt["decision"]["status"], "HOLD")
        self.assertFalse(receipt["decision"]["headers_match_pinned"])

    def test_missing_duplicate_and_unknown_observations_fail_closed(self):
        with self.assertRaisesRegex(MODULE.InventoryError, "HEADER_OBSERVATION_SET_INCOMPLETE"):
            MODULE.normalize_header_observations(HEADER_OBSERVATIONS[:-1])
        with self.assertRaisesRegex(MODULE.InventoryError, "DUPLICATE_HEADER_OBSERVATION"):
            MODULE.normalize_header_observations(
                HEADER_OBSERVATIONS + [HEADER_OBSERVATIONS[0]]
            )
        with self.assertRaisesRegex(MODULE.InventoryError, "UNKNOWN_HEADER_TABLE"):
            MODULE.normalize_header_observations(
                HEADER_OBSERVATIONS
                + [{"table": "CustomerRows", "field_count": 1, "sha256": "0" * 64}]
            )


class BoundaryTests(unittest.TestCase):
    def test_single_source_drift_is_detected(self):
        relative = "bot_a6/case_store.py"
        changed = (ROOT / relative).read_bytes() + b"\n# drift\n"
        rows = MODULE.inspect_source_pins(ROOT, {relative: changed})
        row = next(value for value in rows if value["path"] == relative)
        self.assertFalse(row["matches_pinned"])
        self.assertEqual(row["status"], "DRIFT")

    def test_symlinked_line_checkout_is_not_trusted(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            root = Path(temp_dir)
            target = root / "outside"
            target.mkdir()
            declared = root / "scripts" / "apps-script-line"
            declared.parent.mkdir(parents=True)
            declared.symlink_to(target, target_is_directory=True)
            result = MODULE.inspect_line_gas(root)
            self.assertTrue(result["exists_or_symlink"])
            self.assertFalse(result["trusted_checkout"])
            self.assertEqual(result["status"], "SOURCE_LAYOUT_CHANGED_REVIEW_REQUIRED")

    def test_token_metadata_never_emits_token_values(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            path = Path(temp_dir) / "token.json"
            path.write_text(
                json.dumps(
                    {
                        "access_token": "do-not-emit-access",
                        "refresh_token": "do-not-emit-refresh",
                        "scopes": [
                            "https://www.googleapis.com/auth/script.projects.readonly"
                        ],
                    }
                ),
                encoding="utf-8",
            )
            os.chmod(path, 0o600)
            result = MODULE.inspect_credential_preflight(path)
            self.assertTrue(result["safe_for_apps_script_readback"])
            serialized = json.dumps(result)
            self.assertNotIn("do-not-emit", serialized)
            self.assertNotIn("access_token", serialized)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = MODULE.build_receipt(
            ROOT,
            CREATED_AT,
            HEADER_OBSERVATIONS,
            connector_metadata_reads=2,
            connector_header_reads=7,
        )

    @staticmethod
    def rehash(receipt):
        body = {
            key: value
            for key, value in receipt.items()
            if key not in {"schema_version", "deterministic_body_sha256"}
        }
        receipt["deterministic_body_sha256"] = MODULE._sha256_bytes(
            MODULE._canonical_json(body)
        )
        return receipt

    def test_nested_extra_key_and_unsafe_write_count_are_rejected(self):
        poisoned = copy.deepcopy(self.receipt)
        poisoned["credential_preflight"]["access_token"] = "secret"
        self.rehash(poisoned)
        with self.assertRaisesRegex(MODULE.InventoryError, "ALLOWLIST"):
            MODULE.validate_receipt(poisoned)

        poisoned = copy.deepcopy(self.receipt)
        poisoned["safety"]["google_writes"] = 1
        self.rehash(poisoned)
        with self.assertRaisesRegex(MODULE.InventoryError, "SAFETY_BOUNDARY"):
            MODULE.validate_receipt(poisoned)

    def test_raw_quote_script_id_cannot_replace_binding_fingerprint(self):
        raw_script_id = json.loads(
            (ROOT / "scripts" / "apps-script" / ".clasp.json").read_text(
                encoding="utf-8"
            )
        )["scriptId"]
        poisoned = copy.deepcopy(self.receipt)
        poisoned["quote_gas"]["binding_fingerprint"] = raw_script_id
        self.rehash(poisoned)
        with self.assertRaisesRegex(MODULE.InventoryError, "QUOTE_SHA256"):
            MODULE.validate_receipt(poisoned)

    def test_rehashed_manifest_digest_and_timestamp_poison_fail_closed(self):
        poison_cases = []

        duplicate_source = copy.deepcopy(self.receipt)
        duplicate_source["source_pins"][-1] = copy.deepcopy(
            duplicate_source["source_pins"][0]
        )
        poison_cases.append((duplicate_source, "SOURCE_MANIFEST"))

        duplicate_header = copy.deepcopy(self.receipt)
        duplicate_header["live_headers"][-1] = copy.deepcopy(
            duplicate_header["live_headers"][0]
        )
        poison_cases.append((duplicate_header, "HEADER_MANIFEST"))

        source_digest = copy.deepcopy(self.receipt)
        source_digest["source_pins"][0].update(
            {"sha256": "raw-google-id", "matches_pinned": False, "status": "DRIFT"}
        )
        source_digest["decision"]["status"] = "HOLD"
        poison_cases.append((source_digest, "SOURCE_SHA256"))

        plan_digest = copy.deepcopy(self.receipt)
        plan_digest["plan_artifact"].update(
            {"sha256": "not-a-digest", "matches_pinned": False, "status": "DRIFT"}
        )
        plan_digest["decision"]["status"] = "HOLD"
        poison_cases.append((plan_digest, "PLAN_SHA256"))

        invalid_timestamp = copy.deepcopy(self.receipt)
        invalid_timestamp["created_at"] = "yesterday"
        poison_cases.append((invalid_timestamp, "TIMESTAMP_INVALID"))

        for poisoned, code in poison_cases:
            with self.subTest(code=code):
                self.rehash(poisoned)
                with self.assertRaisesRegex(MODULE.InventoryError, code):
                    MODULE.validate_receipt(poisoned)

    def test_rehashed_derived_state_and_count_poison_fail_closed(self):
        poison_cases = []

        writer = copy.deepcopy(self.receipt)
        writer["orders_writer"]["current_writer_match_count"] = 9
        writer["orders_writer"]["git_history_selector_match_count"] = 7
        poison_cases.append((writer, "WRITER_BOUNDARY"))

        quote = copy.deepcopy(self.receipt)
        quote["quote_gas"]["binding_present"] = False
        poison_cases.append((quote, "QUOTE_BOUNDARY"))

        line = copy.deepcopy(self.receipt)
        line["line_gas"]["exists_or_symlink"] = True
        line["line_gas"]["trusted_checkout"] = True
        poison_cases.append((line, "LINE_BOUNDARY"))

        read_counts = copy.deepcopy(self.receipt)
        read_counts["safety"]["connector_metadata_reads"] = 999
        read_counts["safety"]["google_read_operations"] = 1006
        poison_cases.append((read_counts, "SAFETY_COUNT_CONTRACT"))

        boolean_zero = copy.deepcopy(self.receipt)
        boolean_zero["safety"]["google_writes"] = False
        poison_cases.append((boolean_zero, "SAFETY_ZERO_TYPE"))

        float_zero = copy.deepcopy(self.receipt)
        float_zero["safety"]["deployment_writes"] = 0.0
        poison_cases.append((float_zero, "SAFETY_ZERO_TYPE"))

        root_identity = copy.deepcopy(self.receipt)
        root_identity["private_roots"]["case_store"][
            "path_class"
        ] = "Customer Alice 0912345678"
        poison_cases.append((root_identity, "CASE_STORE_BOUNDARY"))

        repo_path = copy.deepcopy(self.receipt)
        repo_path["private_roots"]["case_store"].update(
            {
                "repo_path_fingerprint": "0" * 64,
                "repo_path_matches_repo_root": False,
            }
        )
        poison_cases.append((repo_path, "CASE_STORE_BOUNDARY"))

        fallback = copy.deepcopy(self.receipt)
        fallback["private_roots"]["case_store"].update(
            {"fallback_mode": 0o600, "fallback_owner_only": True}
        )
        poison_cases.append((fallback, "CASE_STORE_BOUNDARY"))

        openclaw = copy.deepcopy(self.receipt)
        openclaw["private_roots"]["openclaw"][
            "artifact_file_mode_histogram"
        ] = {"0600": MODULE.EXPECTED_OPENCLAW_ARTIFACT_FILE_COUNT}
        poison_cases.append((openclaw, "OPENCLAW_BOUNDARY"))

        credential = copy.deepcopy(self.receipt)
        credential["credential_preflight"].update(
            {
                "owner_only": True,
                "apps_script_scope_present": True,
                "safe_for_apps_script_readback": True,
                "status": "SAFE_READBACK_CAPABILITY_PRESENT",
            }
        )
        poison_cases.append((credential, "CREDENTIAL_RELATION"))

        future_timestamp = copy.deepcopy(self.receipt)
        future_timestamp["created_at"] = "2099-01-01T00:00:00+00:00"
        poison_cases.append((future_timestamp, "TIMESTAMP_CONTRACT"))

        for poisoned, code in poison_cases:
            with self.subTest(code=code):
                self.rehash(poisoned)
                with self.assertRaisesRegex(MODULE.InventoryError, code):
                    MODULE.validate_receipt(poisoned)

    def test_body_hash_tamper_is_rejected(self):
        poisoned = copy.deepcopy(self.receipt)
        poisoned["deterministic_body_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.InventoryError, "BODY_SHA256"):
            MODULE.validate_receipt(poisoned)

        poisoned = copy.deepcopy(self.receipt)
        poisoned["decision"]["status"] = "COMPLETE"
        self.rehash(poisoned)
        with self.assertRaisesRegex(MODULE.InventoryError, "DECISION_BOUNDARY"):
            MODULE.validate_receipt(poisoned)

    def test_private_writer_is_atomic_owner_only_and_rejects_symlink(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            parent = Path(temp_dir) / "private"
            path = parent / "receipt.json"
            MODULE.write_private_receipt(path, self.receipt)
            self.assertEqual(stat.S_IMODE(parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(
                json.loads(path.read_text()),
                json.loads(json.dumps(self.receipt)),
            )
            actual = parent / "actual.json"
            actual.write_text("{}", encoding="utf-8")
            link = parent / "link.json"
            link.symlink_to(actual)
            with self.assertRaisesRegex(MODULE.InventoryError, "SYMLINK"):
                MODULE.write_private_receipt(link, self.receipt)

    def test_cli_prints_aggregate_only_summary(self):
        with tempfile.TemporaryDirectory(dir="/Users/pagemacmini/.maplab") as temp_dir:
            path = Path(temp_dir) / "receipt.json"
            command = [
                sys.executable,
                str(MODULE_PATH),
                "--repo-root",
                str(ROOT),
                "--receipt",
                str(path),
                "--created-at",
                CREATED_AT,
                "--connector-metadata-reads",
                "2",
                "--connector-header-reads",
                "7",
            ]
            for observation in HEADER_OBSERVATIONS:
                command.extend(
                    [
                        "--header",
                        f"{observation['table']}:{observation['field_count']}:{observation['sha256']}",
                    ]
                )
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            summary = json.loads(process.stdout)
            self.assertEqual(summary["decision"], "READ_ONLY_INVENTORY_COMPLETE")
            self.assertNotIn("scriptId", process.stdout)
            self.assertNotIn("token", process.stdout)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
