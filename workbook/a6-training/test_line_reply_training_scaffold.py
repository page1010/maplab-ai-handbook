#!/usr/bin/env python3
"""Tests for the A6 LINE reply training scaffold."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("line_reply_training_scaffold.py")
SPEC = importlib.util.spec_from_file_location("line_reply_training_scaffold", MODULE_PATH)
assert SPEC and SPEC.loader
scaffold = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scaffold
SPEC.loader.exec_module(scaffold)


class LineReplyTrainingScaffoldTests(unittest.TestCase):
    def test_build_dataset_masks_pii_and_keeps_only_user_to_account_targets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            booking_path = root / "line_booking_pairs.csv"
            qa_path = root / "qa.json"
            raw_path = root / "raw.json"
            out_dir = root / "out"

            with booking_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "filename",
                        "index",
                        "contact_name",
                        "start_date",
                        "end_date",
                        "confirmed",
                        "likely_true_positive",
                        "match_timetree_date",
                        "match_timetree_events",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "filename": "王小明_0900123456.csv",
                        "index": "1",
                        "contact_name": "王小明",
                        "start_date": "2026-06-23",
                        "end_date": "2026-06-23",
                        "confirmed": "1",
                        "likely_true_positive": "1",
                        "match_timetree_date": "2026-06-23",
                        "match_timetree_events": "測試活動",
                    }
                )

            raw_path.write_text(
                json.dumps(
                    {
                        "total": 2,
                        "pairs": [
                            {
                                "conv_id": "conv-1",
                                "stage": "S2_DATA",
                                "role": "User",
                                "msg": "王小明 0900-123-456 想問 6/23 台南中西區測試路10號外燴",
                                "response_role": "Account",
                                "response": "您好王小明，請問大約幾位賓客？",
                            },
                            {
                                "conv_id": "conv-2",
                                "stage": "S0_OPENING",
                                "role": "Account",
                                "msg": "您好",
                                "response_role": "User",
                                "response": "我想詢價",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            qa_path.write_text(
                json.dumps(
                    {
                        "total": 1,
                        "examples": [
                            {
                                "id": "qa-1",
                                "conv_id": "qa-conv",
                                "stage": "S1_INQUIRY",
                                "customer": "王小明 想詢問開幕茶會",
                                "business": "您好，想先了解活動日期與人數。",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            samples, manifest, mask_tokens = scaffold.build_dataset(
                booking_pairs=booking_path,
                qa_json=qa_path,
                raw_pairs_json=raw_path,
            )
            self.assertEqual(len(samples), 2)
            self.assertEqual(manifest["sample_counts"]["with_account_target"], 2)
            self.assertEqual(manifest["answer_side_gap"]["current_booking_pairs_have_answer_text"], False)
            self.assertTrue(all(sample["target"]["role"] == "business" for sample in samples))
            self.assertNotIn("S0_OPENING", [sample["stage"] for sample in samples])

            scaffold.write_outputs(out_dir, samples, manifest, mask_tokens)
            combined = (out_dir / "training_samples.jsonl").read_text(encoding="utf-8")
            combined += (out_dir / "manifest.json").read_text(encoding="utf-8")

            self.assertNotIn("王小明", combined)
            self.assertNotIn("0900", combined)
            self.assertNotIn("王小明_0900123456.csv", combined)
            self.assertIn("[姓名]", combined)
            self.assertIn("[電話]", combined)

    def test_mask_pii_handles_common_patterns(self) -> None:
        masked = scaffold.mask_pii(
            "王小明 email a@example.com 電話 0912-345-678 2026-06-23 台南測試路10號",
            ["王小明"],
        )
        self.assertIn("[姓名]", masked)
        self.assertIn("[email]", masked)
        self.assertIn("[電話]", masked)
        self.assertIn("[日期]", masked)
        self.assertIn("[地址]", masked)


if __name__ == "__main__":
    unittest.main()
