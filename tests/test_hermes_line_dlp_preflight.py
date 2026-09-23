from __future__ import annotations

import ast
import contextlib
import copy
import importlib.util
import io
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_dlp_preflight.py"
MANIFEST_SCHEMA_PATH = (
    ROOT / "config" / "schemas" / "hermes-line-dlp-rights-manifest-v1.schema.json"
)
RECEIPT_SCHEMA_PATH = (
    ROOT / "config" / "schemas" / "hermes-line-dlp-preflight-receipt-v1.schema.json"
)
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "hermes_line_dlp"
SAFE_DATASET = FIXTURE_ROOT / "safe.jsonl"
UNSAFE_DATASET = FIXTURE_ROOT / "unsafe-identifiers.jsonl"
APPROVED_MANIFEST = FIXTURE_ROOT / "rights-approved-safe.json"

SPEC = importlib.util.spec_from_file_location("hermes_line_dlp_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HermesLineDlpPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.private_root = Path(self.temp_dir.name) / "private"
        self.private_root.mkdir(mode=0o700)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _load(path: Path) -> dict[str, object]:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(value, dict)
        return value

    @staticmethod
    def _rehash_receipt(receipt: dict[str, object]) -> None:
        body = dict(receipt)
        body.pop("body_sha256", None)
        receipt["body_sha256"] = MODULE.sha256_text(MODULE.canonical_json(body))

    def _safe_receipt(self) -> dict[str, object]:
        manifest = self._load(APPROVED_MANIFEST)
        scan = MODULE.aggregate_scan(
            [MODULE.scan_jsonl(SAFE_DATASET, "safe", private=False)]
        )
        return MODULE.build_receipt(
            manifest=manifest,
            manifest_sha256=MODULE.sha256_file(APPROVED_MANIFEST),
            scan=scan,
            source_paths=[SAFE_DATASET],
            created_at="2026-09-01T06:00:00Z",
            scanner_sha256=MODULE.sha256_file(MODULE_PATH),
        )

    def _private_copy(self, source: Path, name: str, mode: int = 0o600) -> Path:
        destination = self.private_root / name
        destination.write_bytes(source.read_bytes())
        destination.chmod(mode)
        return destination

    def test_safe_synthetic_cli_pass_is_private_and_aggregate_only(self) -> None:
        receipt_path = self.private_root / "receipt.json"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = MODULE.main(
                [
                    "scan",
                    "--dataset",
                    f"safe={SAFE_DATASET}",
                    "--rights-manifest",
                    str(APPROVED_MANIFEST),
                    "--receipt-output",
                    str(receipt_path),
                    "--allow-public-synthetic-fixtures",
                    "--quiet",
                ]
            )
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)

        receipt = self._load(receipt_path)
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["eligible_for_offline_training"])
        self.assertEqual(receipt["reason_codes"], [])
        self.assertEqual(receipt["scan"]["high_confidence_findings"], 0)
        self.assertEqual(receipt["scan"]["review_required_findings"], 0)
        serialized = MODULE.canonical_json(receipt)
        for forbidden in (
            str(SAFE_DATASET),
            "/Users/",
            ".jsonl",
            "客戶詢問大型活動流程",
            "有素食需求",
        ):
            self.assertNotIn(forbidden, serialized)
        MODULE.validate_receipt(receipt)

    def test_private_init_creates_pending_manifest_and_blocked_receipt(self) -> None:
        dataset_path = self._private_copy(SAFE_DATASET, "private-line.jsonl")
        manifest_path = self.private_root / "rights.json"
        receipt_path = self.private_root / "receipt.json"

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            init_exit = MODULE.main(
                [
                    "init",
                    "--dataset",
                    f"train={dataset_path}",
                    "--dataset-id",
                    "hermes-line-private-snapshot",
                    "--manifest-output",
                    str(manifest_path),
                    "--quiet",
                ]
            )
            scan_exit = MODULE.main(
                [
                    "scan",
                    "--dataset",
                    f"train={dataset_path}",
                    "--rights-manifest",
                    str(manifest_path),
                    "--receipt-output",
                    str(receipt_path),
                    "--quiet",
                ]
            )

        self.assertEqual(init_exit, 0)
        self.assertEqual(scan_exit, 3)
        self.assertEqual(stat.S_IMODE(manifest_path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o600)
        manifest = self._load(manifest_path)
        receipt = self._load(receipt_path)
        self.assertEqual(manifest["authority"]["status"], "PENDING")
        self.assertEqual(receipt["status"], "BLOCKED")
        self.assertFalse(receipt["eligible_for_offline_training"])
        self.assertIn("RIGHTS_AUTHORITY_NOT_APPROVED", receipt["reason_codes"])
        self.assertEqual(receipt["execution"]["training_runs_started"], 0)

    def test_synthetic_identifier_fixture_is_detected_without_values(self) -> None:
        scan = MODULE.scan_jsonl(UNSAFE_DATASET, "unsafe", private=False)
        self.assertGreater(scan["high_confidence_findings"], 0)
        self.assertGreater(scan["review_required_findings"], 0)
        for category in (
            "direct_name_field",
            "email_address",
            "taiwan_mobile_phone",
            "line_account",
            "person_name_with_honorific",
        ):
            self.assertGreater(scan["findings_by_category"].get(category, 0), 0)
        serialized = MODULE.canonical_json(scan)
        for forbidden in ("fake@example.test", "0912-345-678", "synthetic_user"):
            self.assertNotIn(forbidden, serialized)

    def test_machine_hash_fields_do_not_trigger_identifier_rules(self) -> None:
        scan = MODULE.scan_jsonl(SAFE_DATASET, "safe", private=False)
        self.assertEqual(scan["high_confidence_findings"], 0)
        self.assertEqual(scan["review_required_findings"], 0)
        self.assertEqual(scan["findings_by_category"], {})

    def test_manifest_contract_rejects_renamed_rights_field(self) -> None:
        manifest = self._load(APPROVED_MANIFEST)
        rights = manifest["data_subject_rights"]
        rights["contact_route"] = rights.pop("contact_route_id")
        with self.assertRaisesRegex(
            MODULE.DLPPreflightError, "MANIFEST_RIGHTS_FIELDS_INVALID"
        ):
            MODULE.validate_manifest_shape(manifest)

    def test_receipt_rejects_nested_injection_even_with_recomputed_hash(self) -> None:
        receipt = self._safe_receipt()
        receipt["scan"]["files"][0]["source_path"] = "/private/source.jsonl"
        self._rehash_receipt(receipt)
        with self.assertRaisesRegex(
            MODULE.DLPPreflightError, "RECEIPT_SCAN_FILE_FIELDS_INVALID"
        ):
            MODULE.validate_receipt(receipt)

    def test_receipt_rejects_aggregate_mismatch_even_with_recomputed_hash(self) -> None:
        receipt = self._safe_receipt()
        receipt["scan"]["record_count"] += 1
        self._rehash_receipt(receipt)
        with self.assertRaisesRegex(
            MODULE.DLPPreflightError, "RECEIPT_SCAN_AGGREGATE_MISMATCH"
        ):
            MODULE.validate_receipt(receipt)

    def test_private_mode_rejects_group_or_world_readable_source(self) -> None:
        dataset_path = self._private_copy(SAFE_DATASET, "not-private.jsonl", mode=0o644)
        with self.assertRaisesRegex(
            MODULE.DLPPreflightError, "DATASET_PERMISSIONS_NOT_PRIVATE"
        ):
            MODULE.scan_jsonl(dataset_path, "train", private=True)

    def test_cli_error_is_sanitized_and_does_not_echo_source_path(self) -> None:
        missing_path = self.private_root / "secret-customer-data.jsonl"
        stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            exit_code = MODULE.main(
                [
                    "init",
                    "--dataset",
                    f"train={missing_path}",
                    "--dataset-id",
                    "private-line-snapshot",
                    "--manifest-output",
                    str(self.private_root / "manifest.json"),
                    "--quiet",
                ]
            )
        self.assertEqual(exit_code, 2)
        self.assertNotIn(str(missing_path), stderr.getvalue())
        self.assertEqual(
            json.loads(stderr.getvalue()),
            {"status": "ERROR", "reason_code": "DATASET_FILE_INVALID"},
        )

    def test_scanner_has_no_network_process_or_model_runtime_imports(self) -> None:
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertTrue(
            imported_roots.isdisjoint(
                {
                    "aiohttp",
                    "httpx",
                    "mlx",
                    "ollama",
                    "requests",
                    "socket",
                    "subprocess",
                    "torch",
                    "urllib",
                }
            )
        )

    def test_json_schemas_accept_approved_manifest_and_pass_receipt(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        manifest_schema = self._load(MANIFEST_SCHEMA_PATH)
        receipt_schema = self._load(RECEIPT_SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(manifest_schema)
        jsonschema.Draft202012Validator.check_schema(receipt_schema)
        jsonschema.Draft202012Validator(manifest_schema).validate(
            self._load(APPROVED_MANIFEST)
        )
        jsonschema.Draft202012Validator(receipt_schema).validate(self._safe_receipt())


if __name__ == "__main__":
    unittest.main()
