import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_leak_calibrate.py"
SPEC = importlib.util.spec_from_file_location("maplab_margin_leak_calibrate_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MarginLeakCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.source = self.root / "train.jsonl"
        rows = [
            ("conv-custom", "請幫我做企業 Logo 插旗"),
            ("conv-vendor", "場地在台南市區"),
            ("conv-included", "這個方案已包含桌巾嗎"),
            ("conv-rework", "你們弄錯了，請重做並改成原本版本"),
            ("conv-dietary", "其中一位朋友吃全素"),
        ]
        with self.source.open("w", encoding="utf-8") as handle:
            for index, (conversation_id, customer) in enumerate(rows):
                handle.write(
                    json.dumps(
                        {
                            "id": f"row-{index}",
                            "conversation_id": conversation_id,
                            "customer": customer,
                            "target": "private reply",
                            "stage": "S_PENDING",
                            "context": [],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        self.source.chmod(0o600)

    def tearDown(self):
        self.temp.cleanup()

    def test_calibration_emits_hashes_and_expected_triage_labels(self):
        payload = MODULE.calibrate(
            [self.source],
            quotas={
                "custom_scope": 1,
                "third_party_turnkey": 1,
                "equipment_consumables": 1,
                "revision_change_order": 1,
                "dietary_separation": 1,
            },
        )
        labels = {sample["category"]: sample["label"] for sample in payload["samples"]}
        self.assertEqual(labels["custom_scope"], "true_candidate")
        self.assertEqual(labels["third_party_turnkey"], "false_positive")
        self.assertEqual(labels["equipment_consumables"], "included")
        self.assertEqual(labels["revision_change_order"], "our_rework")
        self.assertEqual(labels["dietary_separation"], "insufficient_evidence")
        self.assertEqual(payload["sample_count"], 5)
        self.assertEqual(payload["unique_candidate_hashes"], 5)
        self.assertEqual(payload["privacy"]["network_calls"], 0)

        serialized = json.dumps(payload, ensure_ascii=False)
        for forbidden in (
            "conv-custom",
            "conv-vendor",
            "請幫我做企業 Logo 插旗",
            "場地在台南市區",
            "private reply",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_private_writer_and_sampling_are_deterministic(self):
        quotas = {"custom_scope": 1}
        first = MODULE.calibrate([self.source], quotas=quotas)
        second = MODULE.calibrate([self.source], quotas=quotas)
        self.assertEqual(first["samples"], second["samples"])
        self.assertEqual(
            first["method_contract"]["fingerprint"],
            second["method_contract"]["fingerprint"],
        )

        output = self.root / "receipts" / "calibration.json"
        MODULE.write_private_json(output, first)
        self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
