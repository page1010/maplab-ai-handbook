import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_fixed_three_packet.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_margin_fixed_three_packet_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FixedThreePacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.raw = self.root / "raw"
        self.raw.mkdir(mode=0o700)
        self.pointers = self.root / "pointers"
        self.pointers.mkdir(mode=0o700)
        self.train = self.root / "train.jsonl"
        self.eval = self.root / "eval.jsonl"

        rows = {self.train: [], self.eval: []}
        samples = []
        self.private_markers = []
        for index in range(50):
            filename = f"case-{index:02d}.csv"
            conversation_id = hashlib.sha256(filename.encode()).hexdigest()[:16]
            category = ("logistics_access", "cleanup_waste", "onsite_service")[index % 3]
            row = {
                "conversation_id": conversation_id,
                "customer": f"private-marker-{index:02d} request cue",
                "stage": "S_PENDING",
            }
            target = self.train if index % 2 == 0 else self.eval
            rows[target].append(row)
            candidate_hash = hashlib.sha256(
                f"{conversation_id}|{category}".encode()
            ).hexdigest()
            samples.append(
                {
                    "candidate_hash": candidate_hash,
                    "category": category,
                    "label": "true_candidate" if index < 18 else "insufficient_evidence",
                    "reason_codes": [
                        "direct_request_cue",
                        "category_specific_cost_cue",
                    ],
                    "trigger_codes": ["synthetic"],
                    "source_split": target.stem,
                    "_target": target,
                    "_row": row,
                }
            )
            self.private_markers.append(f"private-marker-{index:02d}")

            with (self.raw / filename).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["傳送者類型", "名稱", "日期", "時間", "訊息"])
                writer.writerow(
                    [
                        "User",
                        self.private_markers[-1],
                        "2026/01/01",
                        "12:00",
                        f"{self.private_markers[-1]} 照片 費用 1200",
                    ]
                )

        line_maps = {}
        for path, source_rows in rows.items():
            lines = [json.dumps(row, ensure_ascii=False) for row in source_rows]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            path.chmod(0o600)
            line_maps[path] = {
                row["conversation_id"]: (number + 1, line)
                for number, (row, line) in enumerate(zip(source_rows, lines))
            }

        for sample in samples:
            target = sample.pop("_target")
            row = sample.pop("_row")
            line_number, line = line_maps[target][row["conversation_id"]]
            sample["evidence_path"] = f"{target}#L{line_number}"
            sample["evidence_sha256"] = hashlib.sha256(line.encode()).hexdigest()

        contract = {
            "method_version": "margin-calibration-v1",
            "hypothesis": "synthetic",
            "changed_variable": "synthetic",
            "fixed_holdout": {"total": 50},
            "expected_delta": "synthetic",
            "stop_loss": "synthetic",
            "adapter": "synthetic",
            "sampling": "synthetic",
            "evaluator": "synthetic",
            "acceptance": "synthetic",
        }
        self.fingerprint = MODULE.sha256_text(
            json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        )
        contract["fingerprint"] = self.fingerprint
        self.calibration_payload = {
            "schema_version": "maplab.margin-leak.calibration.v1",
            "method_contract": contract,
            "sample_count": 50,
            "unique_candidate_hashes": 50,
            "source_receipts": [
                {
                    "path": str(path),
                    "sha256": MODULE.sha256_file(path),
                    "mode": "0600",
                }
                for path in (self.train, self.eval)
            ],
            "samples": samples,
        }
        self.calibration = self.root / "calibration.json"
        self._write_calibration(self.calibration_payload)

    def tearDown(self):
        self.temp.cleanup()

    def _write_calibration(self, payload):
        self.calibration.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        self.calibration.chmod(0o600)

    def _build(self):
        return MODULE.build_packet(
            self.calibration,
            self.raw,
            expected_calibration_sha256=MODULE.sha256_file(self.calibration),
            expected_calibration_fingerprint=self.fingerprint,
            quote_pointer_roots=[self.pointers],
            attempt_before=9,
        )

    def test_fixed_three_packet_is_frozen_private_and_fail_closed(self):
        payload = self._build()
        expected, eligible_digest = MODULE.select_samples(self.calibration_payload)
        self.assertEqual(
            [sample["candidate_hash"] for sample in payload["samples"]],
            [sample["candidate_hash"] for sample in expected],
        )
        self.assertEqual(
            payload["method_contract"]["fixed_holdout"]["eligible_set_digest"],
            eligible_digest,
        )
        self.assertEqual(payload["evidence_summary"]["request_rows_verified"], 3)
        self.assertEqual(payload["evidence_summary"]["four_pillar_verified_count"], 0)
        self.assertEqual(payload["confirmed_leakage_amount"], 0)
        self.assertEqual(payload["attempt_before"], 9)
        self.assertEqual(payload["attempt_after"], 10)
        self.assertIs(payload["attempt_consumed"], True)
        self.assertEqual(
            payload["decision"],
            "STOP_HISTORICAL_JOIN__OWNER_REVIEW_PROSPECTIVE_CAPTURE",
        )

        serialized = json.dumps(payload, ensure_ascii=False)
        for marker in self.private_markers:
            self.assertNotIn(marker, serialized)
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn("http://", serialized)
        self.assertNotIn("https://", serialized)

    def test_sanitized_receipt_contains_only_hash_status_and_codes(self):
        payload = self._build()
        private_path = self.root / "receipt" / "private-for-sanitized.json"
        MODULE.write_private_json(private_path, payload)
        private_sha = MODULE.sha256_file(private_path)
        receipt = MODULE.build_sanitized_receipt(private_path, private_sha)
        self.assertEqual(receipt["private_packet_sha256"], private_sha)
        self.assertRegex(receipt["body_sha256"], r"^[0-9a-f]{64}$")
        serialized = json.dumps(receipt, ensure_ascii=False)
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn("evidence_path", serialized)
        for marker in self.private_markers:
            self.assertNotIn(marker, serialized)

        with self.assertRaisesRegex(MODULE.FixedThreeError, "private_packet_sha256_mismatch"):
            MODULE.build_sanitized_receipt(private_path, "0" * 64)

    def test_writer_is_owner_only_and_atomic(self):
        payload = self._build()
        output = self.root / "receipt" / "private.json"
        self.assertIs(MODULE.write_private_json(output, payload), True)
        self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(output.read_text())["attempt_after"], 10)

        original_sha = MODULE.sha256_file(output)
        replay = self._build()
        self.assertNotEqual(replay["created_at"], payload["created_at"])
        self.assertIs(MODULE.write_private_json(output, replay), False)
        self.assertEqual(MODULE.sha256_file(output), original_sha)

        conflict = json.loads(json.dumps(replay))
        conflict["attempt_after"] = 11
        conflict["attempt_before"] = 10
        with self.assertRaisesRegex(MODULE.FixedThreeError, "existing_output_identity_conflict"):
            MODULE.write_private_json(output, conflict)

    def test_calibration_sha_and_fingerprint_are_pinned(self):
        with self.assertRaisesRegex(MODULE.FixedThreeError, "calibration_sha256_mismatch"):
            MODULE.build_packet(
                self.calibration,
                self.raw,
                expected_calibration_sha256="0" * 64,
                expected_calibration_fingerprint=self.fingerprint,
                attempt_before=9,
            )
        with self.assertRaisesRegex(MODULE.FixedThreeError, "calibration_fingerprint_mismatch"):
            MODULE.build_packet(
                self.calibration,
                self.raw,
                expected_calibration_sha256=MODULE.sha256_file(self.calibration),
                expected_calibration_fingerprint="0" * 64,
                attempt_before=9,
            )

    def test_true_candidate_count_and_duplicates_cannot_replace_cases(self):
        altered = json.loads(json.dumps(self.calibration_payload))
        altered["samples"][18]["label"] = "true_candidate"
        self._write_calibration(altered)
        with self.assertRaisesRegex(MODULE.FixedThreeError, "true_candidate_count_mismatch"):
            MODULE.build_packet(
                self.calibration,
                self.raw,
                expected_calibration_sha256=MODULE.sha256_file(self.calibration),
                expected_calibration_fingerprint=self.fingerprint,
                attempt_before=9,
            )

    def test_request_row_and_source_corpus_drift_fail_closed(self):
        altered = json.loads(json.dumps(self.calibration_payload))
        selected, _ = MODULE.select_samples(altered)
        selected_hash = selected[0]["candidate_hash"]
        next(
            sample
            for sample in altered["samples"]
            if sample["candidate_hash"] == selected_hash
        )["evidence_sha256"] = "0" * 64
        self._write_calibration(altered)
        with self.assertRaisesRegex(MODULE.FixedThreeError, "request_evidence_sha256_mismatch"):
            MODULE.build_packet(
                self.calibration,
                self.raw,
                expected_calibration_sha256=MODULE.sha256_file(self.calibration),
                expected_calibration_fingerprint=self.fingerprint,
                attempt_before=9,
            )

        self._write_calibration(self.calibration_payload)
        self.train.write_text(self.train.read_text() + "{}\n", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.FixedThreeError, "calibration_source_sha256_mismatch"):
            self._build()

    def test_missing_frozen_source_does_not_select_a_fourth_case(self):
        payload = self._build()
        selected_hash = payload["samples"][0]["candidate_hash"]
        expected = next(
            sample
            for sample in self.calibration_payload["samples"]
            if sample["candidate_hash"] == selected_hash
        )
        evidence_path, line_number = expected["evidence_path"].rsplit("#L", 1)
        row = json.loads(Path(evidence_path).read_text().splitlines()[int(line_number) - 1])
        raw_path = next(
            path
            for path in self.raw.glob("*.csv")
            if hashlib.sha256(path.name.encode()).hexdigest()[:16]
            == row["conversation_id"]
        )
        raw_path.unlink()
        after = self._build()
        self.assertEqual(after["samples"][0]["candidate_hash"], selected_hash)
        self.assertEqual(
            after["samples"][0]["source_conversation"]["status"],
            "UNVERIFIED_SOURCE_RESOLUTION_COUNT",
        )
        self.assertIn(
            "SOURCE_CONVERSATION_UNVERIFIED_RESOLUTION_COUNT",
            after["samples"][0]["missing_evidence_codes"],
        )


if __name__ == "__main__":
    unittest.main()
