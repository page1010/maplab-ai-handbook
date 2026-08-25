import unittest

from tools.ai_workbook.a8_lyrics_engine import analyze_rhyme, review_lyrics


class A8LyricsEngineTest(unittest.TestCase):
    def test_numbered_verse_and_vocal_cues_are_supported(self) -> None:
        lyrics = """[Chorus][Female Vocal]\n今天神氣\n全都歡喜\n[Verse 1][Male Rap]\n站得好乖\n笑開懷\n"""
        review = review_lyrics(lyrics)
        self.assertTrue(review["ok"])
        self.assertEqual(review["rhyme"]["total_lines"], 4)
        self.assertNotIn("[Female Vocal]", str(review["rhyme"]))
        self.assertNotIn("[Male Rap]", str(review["rhyme"]))

    def test_analyze_rhyme_ignores_standalone_cue(self) -> None:
        result = analyze_rhyme("[Verse 2][Female Vocal]\n一起走向未來\n笑容盛開\n")
        self.assertEqual(result["total_lines"], 2)
        self.assertEqual(result["rhymed_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
