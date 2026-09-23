import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_leak_scan.py"
SPEC = importlib.util.spec_from_file_location("maplab_margin_leak_scan_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MarginLeakScanTests(unittest.TestCase):
    def test_scan_returns_aggregate_candidates_without_raw_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.jsonl"
            rows = [
                {
                    "id": "row-1",
                    "conversation_id": "secret-conversation-a",
                    "stage": "S2_DATA",
                    "customer": "可以再加客製 Logo 插旗，現場也要服務人員嗎？",
                },
                {
                    "id": "row-2",
                    "conversation_id": "secret-conversation-b",
                    "stage": "S4_PAYMENT",
                    "customer": "活動在三樓沒有電梯，結束後垃圾也請幫忙載走",
                },
            ]
            source.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )
            result = MODULE.scan_jsonl([source])
            rendered = json.dumps(result, ensure_ascii=False)
            self.assertEqual(result["total_rows"], 2)
            self.assertEqual(result["unique_conversations"], 2)
            self.assertFalse(result["contains_raw_text"])
            self.assertNotIn("secret-conversation", rendered)
            self.assertNotIn("可以再加", rendered)
            by_category = {item["category"]: item for item in result["categories"]}
            self.assertEqual(by_category["custom_scope"]["unique_conversations"], 1)
            self.assertEqual(by_category["onsite_service"]["unique_conversations"], 1)
            self.assertEqual(by_category["logistics_access"]["unique_conversations"], 1)
            self.assertEqual(by_category["cleanup_waste"]["unique_conversations"], 1)

    def test_private_writer_uses_0700_directory_and_0600_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "private" / "aggregate.json"
            MODULE.write_private_json(output, {"ok": True})
            self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
