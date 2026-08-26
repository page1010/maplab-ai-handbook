import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ai_workbook" / "a8_one_pass_timeline.py"
SPEC = importlib.util.spec_from_file_location("a8_one_pass_timeline", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def binding(path: Path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


class OnePassTimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.raw = self.root / "raw.mov"
        self.raw.write_bytes(b"raw")
        self.audio = self.root / "audio.wav"
        self.audio.write_bytes(b"audio")
        self.config_path = self.root / "config.json"

    def tearDown(self):
        self.temp.cleanup()

    def config(self):
        return {
            "canvas": {"width": 1080, "height": 1920, "fps": 30},
            "shots": [{
                "source": binding(self.raw),
                "is_proxy": False,
                "in_ms": 200,
                "out_ms": 1200,
                "duration_ms": 1000,
                "layout": {"mode": "fit_brand_canvas"},
            }],
            "overlays": [],
            "audio": {**binding(self.audio), "in_ms": 0, "out_ms": 1000},
            "output": {"path": "output.mp4"},
            "lineage_path": "lineage.json",
        }

    def test_builds_single_libx264_output(self):
        command = MODULE.build_command(self.config(), self.config_path, self.root / "out.mp4", False)
        self.assertEqual(1, command.count("libx264"))
        self.assertIn("-filter_complex", command)

    def test_rejects_proxy(self):
        config = self.config()
        config["shots"][0]["is_proxy"] = True
        with self.assertRaisesRegex(ValueError, "raw original"):
            MODULE.validate_config(config, self.config_path)

    def test_rejects_implicit_crop(self):
        config = self.config()
        config["shots"][0]["layout"] = {"mode": "blind_center_crop"}
        with self.assertRaisesRegex(ValueError, "forbidden"):
            MODULE.validate_config(config, self.config_path)


if __name__ == "__main__":
    unittest.main()
