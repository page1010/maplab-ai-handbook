import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ai_workbook" / "a8_platform_formats.py"
SPEC = importlib.util.spec_from_file_location("a8_platform_formats", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class A8PlatformFormatsGuardTests(unittest.TestCase):
    def test_legacy_export_refuses_before_render_or_directory_creation(self):
        with tempfile.TemporaryDirectory() as root:
            outdir = Path(root) / "must-not-exist"
            with self.assertRaisesRegex(RuntimeError, "final export refused"):
                MODULE.export_for_platforms(
                    "audio.wav",
                    "candidate",
                    ["raw.mov"],
                    ["youtube_shorts"],
                    outdir=outdir,
                )
            self.assertFalse(outdir.exists())

    def test_review_export_is_explicitly_not_for_upload(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)

            def fake_render(_music, output, _clips, **_kwargs):
                Path(output).write_bytes(b"review video")

            with mock.patch.object(MODULE, "_review_render", side_effect=fake_render):
                manifest = MODULE.export_for_platforms(
                    "audio.wav",
                    "diagnostic",
                    ["raw.mov"],
                    ["youtube_shorts"],
                    outdir=root_path,
                    thumbs=False,
                    review_only=True,
                )

            entry = manifest["youtube_shorts"]
            self.assertEqual("REVIEW_ONLY_NOT_FOR_UPLOAD", entry["classification"])
            self.assertIn("multiple_lossy_video_encodes", entry["release_restrictions"])

    def test_cli_export_command_is_refused(self):
        with mock.patch.object(MODULE.sys, "argv", ["a8_platform_formats.py", "export"]):
            self.assertEqual(2, MODULE.main())


if __name__ == "__main__":
    unittest.main()
