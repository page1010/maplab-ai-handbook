import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "report", Path(__file__).resolve().parents[1] / "scripts/prelayout_collection_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class CollectionReportTests(unittest.TestCase):
    def test_unknown_year_not_promoted(self):
        self.assertIn("年份待核", report.capture_label({"source_year_bucket": "2025"}))
        self.assertNotIn("EXIF：", report.capture_label({"source_year_bucket": "2025"}))

    def test_album_date_not_exif(self):
        label = report.capture_label({"date_evidence": {
            "google_photos_displayed_datetime": "2026-09-15T12:28:32+08:00"}})
        self.assertIn("非已下載原檔 EXIF", label)

    def test_link_keeps_external_scheme_and_fragment(self):
        url = "https://docs.google.com/spreadsheets/d/example/edit#gid=0"
        self.assertEqual(report.link(url, "來源"), f"[來源]({url})")

    def test_path_cannot_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                report.inside(Path(tmp), "../external.jpg")

    def test_atomic_output_is_private_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            report.atomic_text(path, "測試\n")
            before = path.stat().st_mtime_ns
            report.atomic_text(path, "測試\n")
            self.assertEqual(before, path.stat().st_mtime_ns)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_missing_photo_or_mismatched_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "photo.jpg"
            path.write_bytes(b"test")
            path.chmod(0o600)
            row = {"id": "T1", "local_relative_path": "photo.jpg",
                   "sha256": "not-correct", "byte_size": 4, "source_path": str(path)}
            with self.assertRaises(ValueError):
                report.verify_photos(root, [row])
            row["sha256"] = report.sha(path)
            self.assertEqual(report.verify_photos(root, [row]), 1)
            with self.assertRaises(ValueError):
                report.verify_photos(root, [row, row])


if __name__ == "__main__":
    unittest.main()
