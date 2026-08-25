import json
import tempfile
import unittest
from pathlib import Path

from tools.ai_workbook.validate_music_prompt_registry import validate


class MusicPromptRegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = Path("workbook/music_prompt_registry/experiments.jsonl")

    def test_canonical_registry_is_valid(self):
        self.assertEqual(validate(self.registry), [])

    def test_duplicate_id_is_rejected(self):
        row = json.loads(self.registry.read_text(encoding="utf-8").splitlines()[1])
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
            handle.write(json.dumps(row) + "\n" + json.dumps(row) + "\n")
            path = Path(handle.name)
        try:
            self.assertTrue(any("duplicate experiment_id" in error for error in validate(path)))
        finally:
            path.unlink()

    def test_release_requires_provider_download(self):
        row = json.loads(self.registry.read_text(encoding="utf-8").splitlines()[1])
        row.update(
            stage="selected_release",
            generated_at="2026-08-25T21:30:00+08:00",
            provider_song_id="song-1",
        )
        row["audio_asset"] = {"method": "screen_recording", "path": "x.mp3", "sha256": "abc"}
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
            handle.write(json.dumps(row) + "\n")
            path = Path(handle.name)
        try:
            self.assertTrue(any("provider_download" in error for error in validate(path)))
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
