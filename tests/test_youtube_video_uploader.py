from unittest.mock import MagicMock, call

from pytest import MonkeyPatch

from hog_uploader.youtube_video_uploader import (
    SCOPES,
    YoutubeVideoUploader,
    create_youtube_service,
)


def test_create_youtube_service(monkeypatch: MonkeyPatch):
    # given
    some_credential_path = "some_credentials.json"

    mock_install_app_flow = MagicMock()
    mock_credentials = MagicMock()
    mock_install_app_flow.from_client_secrets_file.return_value = mock_install_app_flow
    mock_install_app_flow.run_local_server.return_value = mock_credentials
    monkeypatch.setattr(
        "hog_uploader.youtube_video_uploader.InstalledAppFlow",
        mock_install_app_flow,
    )

    mock_build = MagicMock()
    monkeypatch.setattr("hog_uploader.youtube_video_uploader.build", mock_build)

    # when
    create_youtube_service(some_credential_path)

    # then
    mock_install_app_flow.from_client_secrets_file.assert_called_once_with(
        client_secrets_file=some_credential_path, scopes=SCOPES
    )
    mock_install_app_flow.run_local_server.assert_called_once_with(port=0)

    mock_build.assert_has_calls([call("youtube", "v3", credentials=mock_credentials)])


class TestYoutubeVideoUploader:
    def test_upload_video(self, monkeypatch: MonkeyPatch, tmp_path):
        # given
        test_video_title = "2024-11-23"
        test_video_path = tmp_path / "some_path/some_file.mp4"

        test_service = MagicMock()
        test_service.videos().insert.return_value = test_service
        test_service.next_chunk.return_value = (
            None,
            {"id": "video_id_123"},
        )

        mock_media_file_upload = MagicMock()
        monkeypatch.setattr(
            "hog_uploader.youtube_video_uploader.MediaFileUpload",
            lambda file_path, chunksize, resumable: mock_media_file_upload,
        )

        test_uploader = YoutubeVideoUploader(test_service)

        # when
        video_id = test_uploader.upload_video(test_video_title, test_video_path)

        # then
        test_service.videos().insert.assert_called_once_with(
            part="snippet,status",
            body={
                "snippet": {"title": test_video_title},
                "status": {"privacyStatus": "unlisted"},
            },
            media_body=mock_media_file_upload,
        )

        assert video_id == "video_id_123"

    def test_add_video_to_playlist(self):
        # given
        test_service = MagicMock()
        some_playlist_id = "abc123"
        some_video_id = "video123"

        test_uploader = YoutubeVideoUploader(test_service)

        # when
        test_uploader.add_video_to_playlist(some_playlist_id, some_video_id)

        # then
        test_service.playlistItems().insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": some_playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": some_video_id},
                }
            },
        )
        test_service.playlistItems().insert().execute.assert_called_once()

    def test_upload_video_and_add_to_playlist(self):
        # given
        test_video_title = "some_title_123"
        test_video_file_path = "some_path_123"
        test_playlist_id = "test123"
        test_video_id = "some_video_id"

        test_service = MagicMock()
        test_upload_video = MagicMock()
        test_upload_video.return_value = test_video_id
        test_add_video_to_playlist = MagicMock()

        test_uploader = YoutubeVideoUploader(test_service)
        test_uploader.upload_video = test_upload_video
        test_uploader.add_video_to_playlist = test_add_video_to_playlist

        # when
        test_uploader.upload_video_and_add_to_playlist(
            test_video_title, test_video_file_path, test_playlist_id
        )

        # then
        test_upload_video.assert_called_once_with(
            video_title=test_video_title, video_file_path=test_video_file_path
        )
        test_add_video_to_playlist.assert_called_once_with(
            playlist_id=test_playlist_id, video_id=test_video_id
        )
