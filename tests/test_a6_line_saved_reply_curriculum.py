from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CASE_STORE = load_module("curriculum_case_store", REPO_ROOT / "bot_a6" / "case_store.py")
CURRICULUM = load_module(
    "a6_line_saved_reply_curriculum",
    REPO_ROOT / "scripts" / "a6_line_saved_reply_curriculum.py",
)


class A6LineSavedReplyCurriculumTest(unittest.TestCase):
    def test_materializes_private_hash_only_development_fixtures(self) -> None:
        secret_marker = "LOCAL-ONLY-SECRET-MARKER"
        replies = []
        for index, title in enumerate(CURRICULUM.ROUTE_BY_TITLE, start=1):
            message = f"歷史內容 {index}"
            if title == "匯款資訊":
                message = f"匯款帳號 {secret_marker}"
            replies.append({"title": title, "message": message})
        payload = {
            "account_ref": "@example",
            "source": "test",
            "observed_at": "2026-10-02T00:00:00Z",
            "tags": [{"label": "外燴", "chat_count": 1}],
            "saved_replies": replies,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "a6.sqlite3"
            store = CASE_STORE.CaseStore(db_path)
            store.import_line_oa_settings(payload)
            db_path.chmod(0o600)
            output_root = root / "private"

            receipt = CURRICULUM.materialize(db_path, output_root)
            fixture_text = (output_root / "development_fixtures.jsonl").read_text(
                encoding="utf-8"
            )
            fixtures = [json.loads(line) for line in fixture_text.splitlines()]

            self.assertEqual(receipt["fixture_count"], 28)
            self.assertEqual(receipt["approved_pattern_violation_count"], 0)
            self.assertEqual(receipt["provider_attempts"], 0)
            self.assertEqual(receipt["optimizer_steps"], 0)
            self.assertFalse(receipt["weight_delta_created"])
            self.assertNotIn(secret_marker, fixture_text)
            self.assertTrue(all(not item["eligible_for_sft"] for item in fixtures))
            self.assertTrue(all(not item["eligible_for_auto_send"] for item in fixtures))
            self.assertEqual((output_root / "receipt.json").stat().st_mode & 0o777, 0o600)
            self.assertEqual(output_root.stat().st_mode & 0o777, 0o700)

    def test_inventory_drift_fails_closed(self) -> None:
        snapshot = {"saved_reply_count": 1, "snapshot_id": 1, "payload_digest": "x"}
        replies = [
            {
                "ordinal": 1,
                "title": "未知情境",
                "message": "測試",
                "sensitivity": "business_internal",
                "policy_status": "HISTORICAL_REFERENCE_REQUIRES_MINA_REVIEW",
            }
        ]
        with self.assertRaisesRegex(ValueError, "scenario_inventory_drift"):
            CURRICULUM.build_curriculum(snapshot, replies, CURRICULUM.load_contract())


if __name__ == "__main__":
    unittest.main()
