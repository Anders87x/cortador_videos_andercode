import unittest

from utils.video_helpers import build_segments, time_for_filename


class VideoHelpersTest(unittest.TestCase):
    def test_build_segments_respects_intro_and_last_partial_clip(self):
        segments = build_segments(66.0, 5, 30)

        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0]["start"], 5.0)
        self.assertEqual(segments[0]["end"], 35.0)
        self.assertEqual(segments[-1]["start"], 65.0)
        self.assertEqual(segments[-1]["end"], 66.0)
        self.assertEqual(segments[-1]["duration"], 1.0)

    def test_time_for_filename(self):
        self.assertEqual(time_for_filename(65), "01-05")
        self.assertEqual(time_for_filename(3661), "01-01-01")


if __name__ == "__main__":
    unittest.main()
