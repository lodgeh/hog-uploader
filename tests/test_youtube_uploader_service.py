from unittest.mock import MagicMock, call

from pytest import MonkeyPatch

from hog_uploader.video import Video
from hog_uploader.youtube_uploader_service import SCOPES, YoutubeUploaderService
from datetime import datetime


class TestYoutubeUploaderService:
    def test_authenticate(self, monkeypatch: MonkeyPatch):
        # given
        test_youtube_service = YoutubeUploaderService()
        some_credential_path = "some_credentials.json"

        mock_install_app_flow = MagicMock()
        mock_credentials = MagicMock()
        mock_install_app_flow.from_client_secrets_file.return_value = (
            mock_install_app_flow
        )
        mock_install_app_flow.run_console.return_value = mock_credentials
        monkeypatch.setattr(
            "hog_uploader.youtube_uploader_service.InstalledAppFlow",
            mock_install_app_flow,
        )

        mock_build = MagicMock()
        monkeypatch.setattr("hog_uploader.youtube_uploader_service.build", mock_build)

        # when
        test_youtube_service.authenticate(some_credential_path)

        # then
        mock_install_app_flow.from_client_secrets_file.assert_called_once_with(
            some_credential_path, SCOPES
        )
        mock_install_app_flow.run_console.assert_called_once()

        mock_build.assert_has_calls(
            [call("youtube", "v3", credentials=mock_credentials)]
        )

    def test_upload_video(self, monkeypatch: MonkeyPatch):
        # given
        test_youtube_service = YoutubeUploaderService()
        test_video = Video(
            "some_file.mp4", "some_path/some_file.mp4", None, "2024-11-23"
        )

        mock_youtube_service = MagicMock()
        mock_youtube_service.videos().insert.return_value = mock_youtube_service
        mock_youtube_service.next_chunk.return_value = [
            "some_other_value",
            {"id": "video_id_123"},
        ]
        test_youtube_service.youtube_service = mock_youtube_service

        mock_media_file_upload = MagicMock()
        monkeypatch.setattr(
            "hog_uploader.youtube_uploader_service.MediaFileUpload",
            lambda file_path, chunksize, resumable: mock_media_file_upload,
        )

        # when
        video_id = test_youtube_service.upload_video(test_video)

        # then
        mock_youtube_service.videos().insert.assert_called_once_with(
            part="snippet,status",
            body={
                "snippet": {"title": test_video.creation_date_string},
                "status": {"privacyStatus": "unlisted"},
            },
            media_body=mock_media_file_upload,
        )

        assert video_id == "video_id_123"

    def test_add_video_to_playlist(self):
        # given
        test_youtube_service = YoutubeUploaderService()
        some_playlist_id = "abc123"
        some_video_id = "video123"

        mock_youtube_service = MagicMock()
        test_youtube_service.youtube_service = mock_youtube_service

        # when
        test_youtube_service.add_video_to_playlist(some_playlist_id, some_video_id)

        # then
        mock_youtube_service.playlistItems().insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": some_playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": some_video_id},
                }
            },
        )
        mock_youtube_service.playlistItems().insert().execute.assert_called_once()
