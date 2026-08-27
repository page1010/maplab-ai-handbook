import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from maplab_case_first_gate import validate_case, validate_registry


BASE_CASE = {
    "case_id": "CASE-001",
    "source_kind": "drive_case",
    "internal_label": "0717真實活動",
    "event_date": "2026-07-17",
    "drive_folder_id": "folder_123",
    "drive_folder_url": "https://drive.google.com/drive/folders/folder_123",
    "asset_inventory": {"images": 4, "videos": 1, "total": 5},
    "source_integrity": {"inventory": "verified_connector_inventory"},
    "identity_status": "folder_label_only",
    "public_name_status": "withheld",
    "seo": {
        "cluster": "family_event",
        "delivery_route": "existing_pillar_proof",
        "primary_keyword": "台南活動外燴案例",
        "keyword_status": "candidate_not_final",
        "collision_check": "pending",
    },
}


class CaseFirstGateTests(unittest.TestCase):
    def test_real_drive_case_passes_intake(self):
        self.assertEqual(validate_case(BASE_CASE, "intake"), [])

    def test_service_page_is_not_a_case(self):
        case = copy.deepcopy(BASE_CASE)
        case["source_kind"] = "wp_category"
        errors = validate_case(case, "intake")
        self.assertTrue(any("source_kind must be drive_case" in error for error in errors))

    def test_media_inventory_is_required(self):
        case = copy.deepcopy(BASE_CASE)
        case["asset_inventory"] = {"images": 0, "videos": 0, "total": 0}
        errors = validate_case(case, "intake")
        self.assertTrue(any("at least one image or video" in error for error in errors))

    def test_final_keyword_requires_identity_and_collision_proof(self):
        case = copy.deepcopy(BASE_CASE)
        case["seo"]["keyword_status"] = "final_verified"
        errors = validate_case(case, "intake")
        self.assertTrue(any("verified case identity" in error for error in errors))
        self.assertTrue(any("live collision check" in error for error in errors))

    def test_private_document_contamination_must_be_excluded(self):
        case = copy.deepcopy(BASE_CASE)
        case["source_integrity"]["unrelated_private_document_detected"] = True
        errors = validate_case(case, "intake")
        self.assertTrue(any("explicitly excluded" in error for error in errors))

    def test_wp_stage_needs_full_fact_chain(self):
        errors = validate_case(BASE_CASE, "wp")
        self.assertTrue(any("WP stage requires verified case identity" in error for error in errors))
        self.assertTrue(any("WP stage requires visual_qa proof" in error for error in errors))

    def test_duplicate_case_id_fails_registry(self):
        payload = {"cases": [BASE_CASE, copy.deepcopy(BASE_CASE)]}
        errors = validate_registry(payload, "intake")
        self.assertTrue(any("duplicate case_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
