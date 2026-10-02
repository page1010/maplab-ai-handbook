from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "bot_a6" / "case_store.py"
SPEC = importlib.util.spec_from_file_location("line_oa_case_store_for_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CASE_STORE_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CASE_STORE_MODULE
SPEC.loader.exec_module(CASE_STORE_MODULE)
CaseStore = CASE_STORE_MODULE.CaseStore


class LineOASettingsImportTest(unittest.TestCase):
    def test_import_is_immutable_local_snapshot_with_human_review_gate(self) -> None:
        payload = {
            "account_ref": "@example",
            "source": "line_chat_settings_read_only",
            "observed_at": "2026-10-02T20:00:00+08:00",
            "tags": [
                {"label": "外燴", "chat_count": 10},
                {"label": "外帶自取", "chat_count": 4},
            ],
            "saved_replies": [
                {"title": "什麼類型活動", "message": "請問是哪一類型的活動呢？"},
                {"title": "匯款資訊", "message": "請由 Mina 核對後提供匯款資訊。"},
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            store = CaseStore(Path(temp_dir) / "a6.sqlite3")
            first = store.import_line_oa_settings(payload)
            second = store.import_line_oa_settings(payload)

            self.assertTrue(first.created)
            self.assertFalse(second.created)
            self.assertEqual(first.snapshot_id, second.snapshot_id)
            self.assertEqual(first.tag_count, 2)
            self.assertEqual(first.saved_reply_count, 2)

            summary = store.latest_line_oa_settings_summary()
            self.assertIsNotNone(summary)
            self.assertEqual(summary["auto_send_count"], 0)
            self.assertEqual(summary["human_review_count"], 2)
            self.assertEqual(summary["financial_count"], 1)

            with sqlite3.connect(store.db_path) as conn:
                rows = conn.execute(
                    """
                    SELECT title, usage_scenario, policy_status,
                           allowed_for_auto_send, requires_human_review
                    FROM line_oa_saved_replies
                    ORDER BY ordinal
                    """
                ).fetchall()
            self.assertEqual(rows[0][0], rows[0][1])
            self.assertEqual(rows[0][2], "HISTORICAL_REFERENCE_REQUIRES_MINA_REVIEW")
            self.assertEqual(rows[0][3:], (0, 1))

    def test_rejects_duplicate_titles(self) -> None:
        payload = {
            "account_ref": "@example",
            "source": "line_chat_settings_read_only",
            "observed_at": "2026-10-02T20:00:00+08:00",
            "tags": [],
            "saved_replies": [
                {"title": "重複", "message": "一"},
                {"title": "重複", "message": "二"},
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            store = CaseStore(Path(temp_dir) / "a6.sqlite3")
            with self.assertRaisesRegex(ValueError, "invalid_or_duplicate"):
                store.import_line_oa_settings(payload)


if __name__ == "__main__":
    unittest.main()
