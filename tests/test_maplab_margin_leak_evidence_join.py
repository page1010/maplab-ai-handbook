import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_leak_evidence_join.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_margin_leak_evidence_join_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MarginLeakEvidenceJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.raw = self.root / "raw"
        self.raw.mkdir()
        self.quote = self.root / "quotes" / "2024"
        self.quote.mkdir(parents=True)
        samples = []
        self.private_labels = []
        for index in range(12):
            label = f"privatecustomer{index:02d}"
            self.private_labels.append(label)
            raw_path = self.raw / f"{index:04d}_20240101_20240102_{label}.csv"
            raw_path.write_text("sender,date,message\n", encoding="utf-8")
            conversation_id = hashlib.sha256(raw_path.name.encode()).hexdigest()[:16]
            category = "custom_scope"
            candidate_hash = hashlib.sha256(
                f"{conversation_id}|{category}".encode()
            ).hexdigest()
            samples.append(
                {
                    "candidate_hash": candidate_hash,
                    "category": category,
                    "label": "true_candidate",
                    "evidence_path": f"{self.root}/train.jsonl#L{index + 1}",
                    "evidence_sha256": hashlib.sha256(
                        f"row-{index}".encode()
                    ).hexdigest(),
                }
            )
        calibration = {
            "method_contract": {"fingerprint": "prior-fingerprint"},
            "samples": samples,
        }
        self.calibration = self.root / "calibration.json"
        self.calibration.write_text(
            json.dumps(calibration, ensure_ascii=False), encoding="utf-8"
        )
        self.calibration.chmod(0o600)

        selected = MODULE._select_samples(calibration)
        selected_hash = selected[0]["candidate_hash"]
        selected_label = None
        for raw_path in self.raw.glob("*.csv"):
            cid = hashlib.sha256(raw_path.name.encode()).hexdigest()[:16]
            if hashlib.sha256(f"{cid}|custom_scope".encode()).hexdigest() == selected_hash:
                selected_label = raw_path.stem.split("_", 3)[3]
                break
        assert selected_label
        (self.quote / f"quotation-{selected_label}.gsheet").write_text(
            "{}", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_fixed_ten_join_is_private_and_fail_closed(self):
        payload = MODULE.build_evidence_join(
            self.calibration, self.raw, quote_root=self.quote.parent
        )
        self.assertEqual(payload["sample_count"], 10)
        self.assertEqual(payload["unique_candidate_hashes"], 10)
        self.assertEqual(
            payload["evidence_summary"]["private_source_rows_resolved"], 10
        )
        self.assertEqual(payload["evidence_summary"]["quote_pointer_candidates"], 1)
        self.assertEqual(payload["evidence_summary"]["four_pillar_confirmed"], 0)
        self.assertEqual(payload["confirmed_leakage_amount"], 0)
        self.assertEqual(payload["privacy"]["network_calls"], 0)

        serialised = json.dumps(payload, ensure_ascii=False)
        for label in self.private_labels:
            self.assertNotIn(label, serialised)
        for raw_path in self.raw.glob("*.csv"):
            self.assertNotIn(raw_path.name, serialised)

    def test_private_writer_and_missing_source_fail_closed(self):
        payload = MODULE.build_evidence_join(self.calibration, self.raw)
        output = self.root / "receipts" / "join.json"
        MODULE.write_private_json(output, payload)
        self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)

        first = next(self.raw.glob("*.csv"))
        first.unlink()
        with self.assertRaisesRegex(
            MODULE.EvidenceJoinError, "candidate_source_resolution_count"
        ):
            MODULE.build_evidence_join(self.calibration, self.raw)


if __name__ == "__main__":
    unittest.main()
