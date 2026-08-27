import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maplab_margin_join_first_shadow.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "maplab_margin_join_first_shadow_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FakeReadProvider:
    def __init__(self):
        self.api_read_calls = 0
        self.oauth_refresh_calls = 0
        self.orders = []
        self.charges = []
        for index in range(8):
            order_id = f"PRIVATE-ORDER-{index}"
            self.orders.append(
                {
                    "order_id": order_id,
                    "event_date": f"2026-03-{index + 1:02d}",
                    "company_name": f"私密企業{index}",
                    "contact_person": f"私密聯絡人{index}",
                    "event_name": f"私密專案{index}",
                    "client_sheet_url": (
                        "https://docs.google.com/spreadsheets/d/"
                        f"PRIVATE-SHEET-ID-LONG-{index:02d}-FOR-TESTS/edit"
                    ),
                }
            )
            self.charges.append(
                {
                    "order_id": order_id,
                    "description": f"私密費用{index}",
                    "charge_type": f"私密類型{index}",
                    "amount": str(1000 + index),
                }
            )
        self.orders.append(
            {
                "order_id": "PRIVATE-ORDER-2025",
                "event_date": "2025-12-31",
                "company_name": "私密舊案",
                "contact_person": "私密舊聯絡人",
                "event_name": "私密舊專案",
                "client_sheet_url": "https://private.invalid/2025",
            }
        )

    def read_named_columns(self, sheet_id, tab, fields):
        self.api_read_calls += 2
        return self.orders if tab == "Orders" else self.charges


def write_line_csv(path, *, sender, date_value, text):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metadata"])
        writer.writerow(["傳送者類型", "傳送者", "日期", "時間", "訊息"])
        writer.writerow(["User", sender, date_value, "10:00", text])


class MarginJoinFirstShadowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.raw = self.root / "raw"
        self.raw.mkdir(mode=0o700)
        self.prior = self.root / "prior.json"
        self.prior.write_text(
            json.dumps(
                {
                    "schema_version": MODULE.PRIOR_BRIDGE_SCHEMA_VERSION,
                    "data_class": "private-local-google-read-receipt",
                    "method_contract": {
                        "fingerprint": MODULE.PRIOR_BRIDGE_FINGERPRINT
                    },
                    "stable_identity_joins": 0,
                    "privacy": {
                        "contains_raw_text": False,
                        "contains_customer_identifiers": False,
                        "contains_source_conversation_ids": False,
                        "contains_customer_bearing_paths": False,
                        "contains_raw_google_ids": False,
                        "new_third_party_private_data_egress": False,
                        "oauth_token_writes": False,
                        "model_calls": False,
                        "customer_send": False,
                        "google_writes": False,
                        "live_price_write": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        self.prior.chmod(0o600)
        self.prior_sha = hashlib.sha256(self.prior.read_bytes()).hexdigest()

    def tearDown(self):
        self.temp.cleanup()

    def _write_selected_matches(self, provider, *, unmatched_last=False):
        selected, _ = MODULE._select_orders(provider.orders, provider.charges)
        for index, order in enumerate(selected):
            if unmatched_last and index == len(selected) - 1:
                continue
            sheet_id = order["quote_id"]
            write_line_csv(
                self.raw / f"{index:04d}_20260101_20260331_私密檔名{index}.csv",
                sender=order["contact_person"],
                date_value=order["event_date"],
                text=(
                    f"{order['company_name']} 日期 {order['event_date']} "
                    f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
                ),
            )
        return selected

    def test_fixed_five_uses_two_anchors_and_emits_no_private_values(self):
        provider = FakeReadProvider()
        selected = self._write_selected_matches(provider, unmatched_last=True)
        payload = MODULE.build_join_first_receipt(
            self.prior,
            self.raw,
            provider,
            expected_prior_sha256=self.prior_sha,
        )
        self.assertEqual(payload["sample_count"], 5)
        self.assertEqual(payload["unique_order_refs"], 5)
        self.assertEqual(payload["stable_identity_joins"], 4)
        self.assertFalse(payload["all_five_lack_unique_two_anchor_link"])
        self.assertEqual(payload["orders_with_no_two_anchor_candidates"], 1)
        self.assertEqual(payload["confirmed_leakage_amount"], 0)
        self.assertEqual(payload["privacy"]["google_writes"], 0)
        self.assertEqual(payload["privacy"]["model_calls"], 0)
        self.assertGreater(payload["privacy"]["private_values_checked"], 0)
        for sample in payload["samples"][:4]:
            self.assertTrue(sample["identity_chain_verified"])
            self.assertGreaterEqual(sample["anchor_count"], 2)

        serialised = json.dumps(payload, ensure_ascii=False)
        forbidden = []
        for order in selected:
            forbidden.extend(
                [
                    order["order_id"],
                    order["company_name"],
                    order["contact_person"],
                    order["event_name"],
                    order["client_sheet_url"],
                    order["quote_id"],
                ]
            )
        for value in forbidden:
            self.assertNotIn(value, serialised)

    def test_ambiguous_links_fail_closed_and_writer_is_private(self):
        provider = FakeReadProvider()
        selected = self._write_selected_matches(provider)
        order = selected[0]
        write_line_csv(
            self.raw / "9999_20260101_20260331_私密重複檔.csv",
            sender=order["contact_person"],
            date_value=order["event_date"],
            text=f"{order['company_name']} {order['event_date']}",
        )
        payload = MODULE.build_join_first_receipt(
            self.prior,
            self.raw,
            provider,
            expected_prior_sha256=self.prior_sha,
        )
        self.assertEqual(payload["stable_identity_joins"], 4)
        self.assertEqual(
            payload["missing_evidence_code_counts"][
                "AMBIGUOUS_TWO_ANCHOR_LINE_LINK"
            ],
            1,
        )
        output = self.root / "receipt" / "shadow.json"
        MODULE.write_private_json(output, payload)
        self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)

        with self.assertRaisesRegex(
            MODULE.JoinFirstShadowError, "prior_bridge_sha256_mismatch"
        ):
            MODULE.build_join_first_receipt(
                self.prior,
                self.raw,
                FakeReadProvider(),
                expected_prior_sha256="0" * 64,
            )

    def test_wrong_year_and_low_entropy_identity_do_not_form_two_anchors(self):
        provider = FakeReadProvider()
        selected, _ = MODULE._select_orders(provider.orders, provider.charges)
        order = selected[0]
        order["contact_person"] = "2026"
        order["company_name"] = "活動"
        order["event_name"] = "外燴"
        wrong_year = order["event_date"].replace("2026", "2025")
        write_line_csv(
            self.raw / "0000_20250101_20251231_wrong-year.csv",
            sender="2026",
            date_value=wrong_year,
            text=f"2026 {wrong_year}",
        )
        matches, _, _, _ = MODULE._scan_line_archive(selected, self.raw)
        self.assertEqual(matches[order["order_id"]], [])

        for low_entropy in ("客戶1", "活動A", "公司01"):
            row = {
                "company_name": low_entropy,
                "contact_person": "",
                "event_name": "",
                "event_date": "2026-01-01",
                "client_sheet_url": "",
            }
            self.assertEqual(MODULE._identity_tokens(row), [])

        self.assertEqual(
            MODULE._parse_sheet_id(
                "https://docs.google.com/spreadsheets/d/short/edit"
            ),
            "",
        )

    def test_archive_manifest_hashes_content_not_only_name_and_size(self):
        provider = FakeReadProvider()
        selected, _ = MODULE._select_orders(provider.orders, provider.charges)
        path = self.raw / "0000_20260101_20261231_manifest.csv"
        write_line_csv(path, sender="甲方", date_value="2026-01-01", text="AAAA")
        _, _, first_manifest, _ = MODULE._scan_line_archive(selected, self.raw)
        original_size = path.stat().st_size
        write_line_csv(path, sender="乙方", date_value="2026-01-01", text="BBBB")
        self.assertEqual(path.stat().st_size, original_size)
        _, _, second_manifest, _ = MODULE._scan_line_archive(selected, self.raw)
        self.assertNotEqual(first_manifest, second_manifest)

    def test_prior_schema_and_privacy_fail_closed(self):
        provider = FakeReadProvider()
        prior_payload = json.loads(self.prior.read_text(encoding="utf-8"))
        prior_payload["schema_version"] = "wrong.schema"
        self.prior.write_text(json.dumps(prior_payload), encoding="utf-8")
        self.prior.chmod(0o600)
        bad_schema_sha = hashlib.sha256(self.prior.read_bytes()).hexdigest()
        with self.assertRaisesRegex(
            MODULE.JoinFirstShadowError, "expected_zero_join_prior_bridge_required"
        ):
            MODULE.build_join_first_receipt(
                self.prior,
                self.raw,
                provider,
                expected_prior_sha256=bad_schema_sha,
            )

        prior_payload["schema_version"] = MODULE.PRIOR_BRIDGE_SCHEMA_VERSION
        prior_payload["privacy"]["google_writes"] = 1
        self.prior.write_text(json.dumps(prior_payload), encoding="utf-8")
        self.prior.chmod(0o600)
        bad_privacy_sha = hashlib.sha256(self.prior.read_bytes()).hexdigest()
        with self.assertRaisesRegex(
            MODULE.JoinFirstShadowError, "prior_bridge_privacy_assertions_invalid"
        ):
            MODULE.build_join_first_receipt(
                self.prior,
                self.raw,
                FakeReadProvider(),
                expected_prior_sha256=bad_privacy_sha,
            )

    def test_all_ambiguous_is_not_reported_as_no_candidates(self):
        provider = FakeReadProvider()
        selected = self._write_selected_matches(provider)
        for index, order in enumerate(selected):
            write_line_csv(
                self.raw / f"duplicate-{index}.csv",
                sender=order["contact_person"],
                date_value=order["event_date"],
                text=f"{order['company_name']} {order['event_date']}",
            )
        payload = MODULE.build_join_first_receipt(
            self.prior,
            self.raw,
            provider,
            expected_prior_sha256=self.prior_sha,
        )
        self.assertEqual(payload["stable_identity_joins"], 0)
        self.assertEqual(payload["orders_with_no_two_anchor_candidates"], 0)
        self.assertEqual(payload["orders_with_ambiguous_two_anchor_candidates"], 5)
        self.assertFalse(payload["all_five_lack_two_anchor_candidates"])
        self.assertTrue(payload["all_five_lack_unique_two_anchor_link"])
        self.assertEqual(payload["next_repair_point"], "intake_time_case_id_capture")

    def test_cli_pins_canonical_prior_and_stdout_is_opaque(self):
        output = self.root / "customer-bearing-output-name.json"
        payload = {
            "sample_count": 5,
            "stable_identity_joins": 0,
            "all_five_lack_unique_two_anchor_link": True,
        }
        stdout = io.StringIO()
        with (
            mock.patch.object(
                MODULE, "build_join_first_receipt", return_value=payload
            ) as build,
            mock.patch.object(MODULE, "GoogleReadProvider", return_value=FakeReadProvider()),
            mock.patch.object(MODULE, "write_private_json"),
            mock.patch.object(MODULE, "sha256_file", return_value="a" * 64),
            contextlib.redirect_stdout(stdout),
        ):
            result = MODULE.main(
                [
                    "--prior-bridge",
                    str(self.prior),
                    "--raw-source-dir",
                    str(self.raw),
                    "--google-token",
                    str(self.root / "token.json"),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            build.call_args.kwargs["expected_prior_sha256"],
            MODULE.CANONICAL_PRIOR_BRIDGE_SHA256,
        )
        emitted = stdout.getvalue()
        self.assertNotIn(str(output), emitted)
        self.assertNotIn("customer-bearing-output-name", emitted)


if __name__ == "__main__":
    unittest.main()
