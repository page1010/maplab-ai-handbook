import argparse
import json
import tempfile
import unittest
from pathlib import Path

from tools.ai_workbook.a8_enhanced_video_draft import (
    CATEGORY_CTA_LINES,
    list_images,
    write_metadata,
)


def _args(category: str) -> argparse.Namespace:
    return argparse.Namespace(
        case_label="邦尼兔托嬰畢業典禮・甜點桌",
        category=category,
        ending_line=CATEGORY_CTA_LINES[category],
        transition="fade",
        transition_seconds=0.35,
        no_opening=False,
        no_ending=False,
        show_counter=False,
    )


class A8EnhancedMetadataTest(unittest.TestCase):
    def test_graduation_metadata_does_not_leak_corporate_seed_copy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            write_metadata(out, _args("graduation"), [Path("c01.mov")], ["畢業典禮的甜點桌"])
            data = json.loads((out / "review_draft_platform_metadata.json").read_text())
            rendered = json.dumps(data, ensure_ascii=False)
            self.assertIn("台南畢業典禮外燴", rendered)
            self.assertNotIn("大臺南會展中心", rendered)
            self.assertNotIn("企業會議", rendered)
            self.assertNotIn("動線穩", rendered)

    def test_general_metadata_remains_case_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            write_metadata(out, _args("general"), [Path("c01.mov")], ["活動茶點"])
            rendered = (out / "review_draft_platform_metadata.md").read_text()
            self.assertIn("台南活動外燴", rendered)
            self.assertNotIn("大臺南會展中心", rendered)
            self.assertNotIn("企業會議", rendered)

    def test_asset_allowlist_excludes_unselected_private_clip(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            asset_dir = Path(raw)
            for name in ("c01.mov", "c02.mov", "c03.mov"):
                (asset_dir / name).touch()
            selected = list_images(asset_dir, 5, ["c01.mov", "c03.mov"])
            self.assertEqual([p.name for p in selected], ["c01.mov", "c03.mov"])


if __name__ == "__main__":
    unittest.main()
