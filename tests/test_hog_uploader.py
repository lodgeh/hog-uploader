from datetime import datetime
from unittest.mock import MagicMock, call

from pytest import MonkeyPatch

from hog_uploader.hog_uploader import HogUploader
from hog_uploader.video import Video


class TestHogUploader:
    def test_get_videos(self):
        # given
        mock_youtube_service = MagicMock()
        mock_video_manager = MagicMock()
        input_video_path = "some_input/"
        credentials_file_path = "some_credentials.json"
        playlist_id = "some_playlist_id"

        test_hog_uploader = HogUploader(
            mock_youtube_service,
            mock_video_manager,
            input_video_path,
            credentials_file_path,
            playlist_id,
        )

        # when
        test_hog_uploader.get_videos()

        # then
        mock_video_manager.get_video_list.assert_called_once_with(input_video_path)
        mock_video_manager.group_videos_for_concatenation.assert_called_once()
        mock_video_manager.concatenate_videos.assert_called_once()
        mock_video_manager.move_raw_videos_to_archive.assert_called_once()

    def test_upload_videos_and_add_to_playlist(self, monkeypatch: MonkeyPatch):
        # given
        mock_youtube_service = MagicMock()
        mock_video_manager = MagicMock()
        input_video_path = "some_input/"
        credentials_file_path = "some_credentials.json"
        playlist_id = "some_playlist_id"

        fixed_datetime = datetime(2024, 12, 23, 12, 0, 0, 0)
        mock_datetime = MagicMock()
        mock_datetime.now.return_value = fixed_datetime

        monkeypatch.setattr(
            "hog_uploader.video.datetime",
            mock_datetime,
        )

        mock_video_manager.get_video_list.return_value = [
            Video(
                "output/video_1.mp4",
                fixed_datetime,
                "2024-05-26",
            ),
            Video(
                "output/video_2.mp4",
                fixed_datetime,
                "2024-05-25",
            ),
        ]

        mock_youtube_service.upload_video.side_effect = ["video_id_1", "video_id_2"]

        test_hog_uploader = HogUploader(
            mock_youtube_service,
            mock_video_manager,
            input_video_path,
            credentials_file_path,
            playlist_id,
        )

        # when
        test_hog_uploader.upload_videos_and_add_to_playlist()

        # then
        mock_youtube_service.upload_video.assert_has_calls(
            [
                call("2024-05-26", "output/video_1.mp4"),
                call("2024-05-25", "output/video_2.mp4"),
            ]
        )

        mock_youtube_service.add_video_to_playlist.assert_has_calls(
            [
                call(playlist_id, "video_id_1"),
                call(playlist_id, "video_id_2"),
            ]
        )

        mock_video_manager.move_video.assert_has_calls(
            [
                call("output/video_1.mp4", "archive/concatenated"),
                call("output/video_2.mp4", "archive/concatenated"),
            ]
        )
