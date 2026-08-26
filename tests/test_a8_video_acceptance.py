import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ai_workbook" / "a8_video_acceptance.py"
SPEC = importlib.util.spec_from_file_location("a8_video_acceptance", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class A8VideoAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.files = {}
        for name in ("lyrics.txt", "audio.wav", "alignment.json", "timeline.json", "lineage.json", "output.mp4", "contact.jpg", "raw.mov"):
            path = self.root / name
            path.write_bytes((name + "\n").encode("utf-8"))
            self.files[name] = {"path": name, "sha256": digest(path)}
        self.receipt_path = self.root / "receipt.json"

    def tearDown(self):
        self.temp.cleanup()

    def valid_receipt(self):
        return {
            "schema_version": MODULE.SCHEMA_VERSION,
            "job_id": "JOB-A8-TEST",
            "state": "QA_PASS",
            "state_history": ["AUDIO_SELECTED", "TIMING_LOCKED", "EDIT_READY", "RENDERED_UNVERIFIED", "QA_PASS"],
            "approvals": {
                "lyrics": self.files["lyrics.txt"],
                "audio": {
                    **self.files["audio.wav"],
                    "qa": {
                        "actual_audio_asr_pass": True,
                        "brand_exact_tokens_pass": True,
                        "human_listen_pass": True,
                    },
                },
            },
            "timing": {
                "alignment": self.files["alignment.json"],
                "approved_lyrics_match": True,
                "cues": [{"text": "邦尼兔跳起來", "start_ms": 300, "end_ms": 1800}],
                "max_onset_error_ms": 80,
                "max_tail_error_ms": 160,
                "hook_lead_in_ms": 300,
                "starts_mid_word": False,
            },
            "sources": [{
                "raw_path": "raw.mov",
                "raw_sha256": self.files["raw.mov"]["sha256"],
                "is_proxy": False,
                "privacy_status": "APPROVED",
                "trim": {"in_ms": 200, "out_ms": 2900},
                "layout": "full_fit_brand_canvas",
                "crop_strategy": "manual_subject_safe",
            }],
            "edit": {
                "engine": "ffmpeg_one_pass",
                "timeline_receipt": self.files["timeline.json"],
                "no_intermediate_video": True,
                "lyric_and_marketing_tracks_separate": True,
            },
            "encoding": {
                "actual_lossy_video_encode_depth": 1,
                "max_lossy_video_encode_depth": 1,
                "lineage": self.files["lineage.json"],
            },
            "output": {**self.files["output.mp4"], "duration_ms": 1500},
            "visual_qa": {
                "timeline_contact_sheet": self.files["contact.jpg"],
                "full_playback": {
                    "1x": {"watched_duration_ms": 1500, "verdict": "PASS"},
                    "0.5x": {"watched_duration_ms": 1500, "verdict": "PASS"},
                },
                "target_device_pass": True,
                "blur_sidebars_absent": True,
                "blind_crop_absent": True,
            },
        }

    def verify(self, receipt):
        self.receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return MODULE.verify_receipt(receipt, self.receipt_path)

    def test_valid_receipt_passes(self):
        self.assertEqual([], self.verify(self.valid_receipt()))

    def test_current_v2_failure_modes_are_blocked(self):
        receipt = self.valid_receipt()
        receipt["timing"].pop("alignment")
        receipt["sources"][0]["raw_path"] = "approved_sources/proxy.mp4"
        receipt["sources"][0]["is_proxy"] = True
        receipt["encoding"]["actual_lossy_video_encode_depth"] = 3
        codes = {item["code"] for item in self.verify(receipt)}
        self.assertTrue({
            "LYRIC_ALIGNMENT_MISSING",
            "RAW_PROVENANCE_UNBOUND",
            "ENCODE_DEPTH_EXCEEDED",
        }.issubset(codes))

    def test_state_cannot_skip_qa(self):
        receipt = self.valid_receipt()
        receipt["state"] = "OWNER_VIDEO_GATE"
        receipt["state_history"] = ["AUDIO_SELECTED", "TIMING_LOCKED", "OWNER_VIDEO_GATE"]
        codes = {item["code"] for item in self.verify(receipt)}
        self.assertIn("STATE_TRANSITION_INVALID", codes)

    def test_audio_lyrics_mismatch_is_blocked(self):
        receipt = self.valid_receipt()
        receipt["timing"]["approved_lyrics_match"] = False
        codes = {item["code"] for item in self.verify(receipt)}
        self.assertIn("LYRICS_AUDIO_MISMATCH", codes)

    def test_capcut_requires_editable_project(self):
        receipt = self.valid_receipt()
        receipt["edit"]["engine"] = "capcut_manual"
        codes = {item["code"] for item in self.verify(receipt)}
        self.assertIn("EDITOR_PROJECT_MISSING", codes)

    def test_hash_drift_is_blocked(self):
        receipt = self.valid_receipt()
        receipt["output"]["sha256"] = "0" * 64
        codes = {item["code"] for item in self.verify(receipt)}
        self.assertIn("OUTPUT_BINDING_INVALID", codes)


if __name__ == "__main__":
    unittest.main()
