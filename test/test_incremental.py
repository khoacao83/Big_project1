import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

from etl.extract.incremental import find_new_video_ids


class IncrementalTests(unittest.TestCase):
    def test_existing_videos_are_not_fetched_again(self):
        self.assertEqual(find_new_video_ids(["a", "b"], {"a", "b"}), [])

    def test_only_unique_new_videos_are_returned_in_playlist_order(self):
        self.assertEqual(
            find_new_video_ids(["b", "a", "c", "b", None, ""], {"a"}),
            ["b", "c"],
        )

    def test_empty_bigquery_allows_initial_load(self):
        self.assertEqual(find_new_video_ids(["a", "b"], set()), ["a", "b"])


class ChannelConfigurationTests(unittest.TestCase):
    def load_settings(self, environment):
        path = Path(__file__).resolve().parents[1] / "config" / "setting.py"
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test", **environment}, clear=True):
            with patch("dotenv.load_dotenv"):
                return runpy.run_path(str(path))

    def test_playlist_environment_does_not_override_channel(self):
        settings = self.load_settings({"TEST_UPLOADS_PLAYLIST_ID": "UU_playlist"})
        self.assertEqual(settings["CHANNEL_ID"], "UC_x5XG1OV2P6uZZ5FSM9Ttw")
        self.assertEqual(settings["UPLOADS_PLAYLIST_ID"], "UU_playlist")

    def test_legacy_channel_environment(self):
        settings = self.load_settings({"TEST_CHANNEL_ID": "UC_legacy"})
        self.assertEqual(settings["CHANNEL_ID"], "UC_legacy")

    def test_explicit_settings_take_precedence_and_trim_whitespace(self):
        settings = self.load_settings({
            "CHANNEL_ID": " UC_channel ",
            "TEST_CHANNEL_ID": "UC_legacy",
            "UPLOADS_PLAYLIST_ID": " UU_playlist ",
            "TEST_UPLOADS_PLAYLIST_ID": "UU_legacy",
        })
        self.assertEqual(settings["CHANNEL_ID"], "UC_channel")
        self.assertEqual(settings["UPLOADS_PLAYLIST_ID"], "UU_playlist")


if __name__ == "__main__":
    unittest.main()
