import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_google_join_bridge.py"
SPEC = importlib.util.spec_from_file_location(
    "maplab_margin_google_join_bridge_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FakeReadProvider:
    def __init__(self, private_label: str):
        self.private_label = private_label
        self.api_read_calls = 0
        self.oauth_refresh_calls = 1
        self.headers = {
            "SALES_INTAKE": [
                "case_id",
                "created_at",
                "client_name",
                "event_date",
                "a6_output_link",
            ],
            "Orders": [
                "order_id",
                "event_date",
                "company_name",
                "contact_person",
                "event_name",
                "client_sheet_url",
            ],
            "OrderCharges": ["order_id", "description", "charge_type", "amount"],
            "工作表1": ["file_id", "original_name", "seo_name", "category"],
        }

    def read_headers(self, sheet_id, tab):
        self.api_read_calls += 1
        return self.headers[tab]

    def read_named_columns(self, sheet_id, tab, fields):
        self.api_read_calls += 2
        rows = {
            "SALES_INTAKE": [
                {
                    "case_id": "CASE-PRIVATE-1",
                    "created_at": "2026-01-02",
                    "client_name": self.private_label,
                    "event_date": "2026-02-03",
                    "a6_output_link": "https://private.invalid/quote",
                }
            ],
            "Orders": [
                {
                    "order_id": "ORDER-PRIVATE-1",
                    "event_date": "2026-02-03",
                    "company_name": self.private_label,
                    "contact_person": "",
                    "event_name": "",
                    "client_sheet_url": "https://private.invalid/sheet",
                }
            ],
            "OrderCharges": [
                {
                    "order_id": "ORDER-PRIVATE-1",
                    "description": "private delivery fee",
                    "charge_type": "private charge type",
                    "amount": "1234",
                }
            ],
        }
        return rows[tab]

    def list_files(self, parent_id):
        self.api_read_calls += 1
        if parent_id == MODULE.QUOTE_ROOT_ID:
            return [
                {
                    "id": "FOLDER-PRIVATE-2026-OTHER",
                    "name": "2026",
                    "mimeType": MODULE.GOOGLE_FOLDER_MIME,
                },
                {
                    "id": "FOLDER-PRIVATE-2026",
                    "name": "2026外燴訂單",
                    "mimeType": MODULE.GOOGLE_FOLDER_MIME,
                }
            ]
        return [
            {
                "id": "QUOTE-PRIVATE-1",
                "name": f"報價-{self.private_label}",
                "mimeType": MODULE.GOOGLE_SHEET_MIME,
            }
        ]


class MarginGoogleJoinBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.raw = self.root / "raw"
        self.raw.mkdir()
        samples = []
        self.private_labels = []
        for index in range(10):
            year = "2026" if index < 5 else "2025"
            label = f"privatecustomer{index:02d}"
            self.private_labels.append(label)
            raw_path = self.raw / f"{index:04d}_{year}0101_{year}0102_{label}.csv"
            raw_path.write_text("private raw content\n", encoding="utf-8")
            conversation_id = hashlib.sha256(raw_path.name.encode()).hexdigest()[:16]
            category = "custom_scope"
            samples.append(
                {
                    "candidate_hash": hashlib.sha256(
                        f"{conversation_id}|{category}".encode()
                    ).hexdigest(),
                    "category": category,
                }
            )
        self.evidence = self.root / "evidence.json"
        self.evidence.write_text(
            json.dumps({"samples": samples}, ensure_ascii=False), encoding="utf-8"
        )
        self.evidence.chmod(0o600)
        self.evidence_sha = hashlib.sha256(self.evidence.read_bytes()).hexdigest()

    def tearDown(self):
        self.temp.cleanup()

    def test_live_bridge_hashes_private_values_and_fails_closed(self):
        provider = FakeReadProvider(self.private_labels[0])
        payload = MODULE.build_bridge_receipt(
            self.evidence,
            self.raw,
            provider,
            expected_evidence_sha256=self.evidence_sha,
        )
        self.assertEqual(payload["sample_count"], 10)
        self.assertEqual(payload["source_year_counts"], {"2025": 5, "2026": 5})
        self.assertEqual(payload["stable_identity_joins"], 0)
        self.assertEqual(payload["four_pillar_confirmed"], 0)
        self.assertEqual(payload["confirmed_leakage_amount"], 0)
        self.assertTrue(payload["schema_change_proposal_required"])
        self.assertGreater(
            payload["heuristic_match_counts"]["sales_intake_name_candidates"], 0
        )
        self.assertEqual(payload["privacy"]["google_writes"], 0)
        self.assertEqual(payload["privacy"]["model_calls"], 0)

        serialised = json.dumps(payload, ensure_ascii=False)
        forbidden = self.private_labels + [
            "CASE-PRIVATE-1",
            "ORDER-PRIVATE-1",
            "QUOTE-PRIVATE-1",
            "private delivery fee",
            "private raw content",
        ]
        for value in forbidden:
            self.assertNotIn(value, serialised)

    def test_sha_mismatch_and_private_writer_fail_closed(self):
        provider = FakeReadProvider(self.private_labels[0])
        with self.assertRaisesRegex(
            MODULE.GoogleJoinBridgeError, "evidence_receipt_sha256_mismatch"
        ):
            MODULE.build_bridge_receipt(
                self.evidence,
                self.raw,
                provider,
                expected_evidence_sha256="0" * 64,
            )

        payload = MODULE.build_bridge_receipt(
            self.evidence,
            self.raw,
            provider,
            expected_evidence_sha256=self.evidence_sha,
        )
        output = self.root / "receipts" / "bridge.json"
        MODULE.write_private_json(output, payload)
        self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
