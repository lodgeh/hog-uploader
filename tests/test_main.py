from pathlib import Path
from unittest.mock import patch

import pytest

from hog_uploader.main import main


@patch("hog_uploader.main.hog_uploader")
def test_main_upload(mock_hog_uploader):
    # given
    test_args = [
        "--input-dir",
        ".",
        "--output-dir",
        ".",
        "--upload",
        "--oauth-client-secrets-file",
        "some-file.json",
        "--youtube-playlist-id",
        "some-id",
    ]

    # when
    main(test_args)

    # then
    mock_hog_uploader.assert_called_once_with(
        input_directory=Path("."),
        output_directory=Path("."),
        upload=True,
        upload_only=False,
        oauth_client_secrets_file=Path("some-file.json"),
        youtube_playlist_id="some-id",
    )


@patch("hog_uploader.main.hog_uploader")
def test_main_no_upload(mock_hog_uploader):
    # given
    test_args = ["--input-dir", ".", "--output-dir", ".", "--no-upload"]

    # when
    main(test_args)

    # then
    mock_hog_uploader.assert_called_once_with(
        input_directory=Path("."),
        output_directory=Path("."),
        upload=False,
        upload_only=False,
        oauth_client_secrets_file=None,
        youtube_playlist_id=None,
    )


def test_main_invalid(capsys):
    # given
    test_args = ["--input-dir", ".", "--output-dir", ".", "--upload"]

    # when
    with pytest.raises(SystemExit):
        main(test_args)

    # then
    assert (
        "--oauth-client-secrets-file and --youtube-playlist-id are required with --upload"
        in capsys.readouterr().err
    )


def test_hog_uploader():
    # i should probably test this...
    pass
