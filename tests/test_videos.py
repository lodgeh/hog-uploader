from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from hog_uploader.videos import (
    Day,
    concatenate_videos,
    get_days,
    get_days_from_concatenated,
    load_videos,
    move_file,
)


def test_Day():
    test_date = datetime(2026, 8, 23, 12).date()
    test_videos = [Path("test.mp4")]

    actual_day = Day(date=test_date, source_videos=test_videos)

    assert isinstance(actual_day.date_string, str)
    assert actual_day.date_string == "2026-08-23"
    assert actual_day.concatenated_video is None


def test_load_videos(tmp_path):
    # given
    test_path = tmp_path / "something"
    test_file_1 = test_path / "video1.mp4"
    test_file_2 = test_path / "video2.MP4"
    test_file_3 = test_path / "notavideo.csv"

    test_path.mkdir()
    test_file_1.touch()
    test_file_2.touch()
    test_file_3.touch()

    # when
    actual = load_videos(test_path)

    # then
    expected = [test_file_1, test_file_2]
    assert actual == expected


@patch.object(
    Path,
    "stat",
    side_effect=[
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 12, 1).timestamp()),
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 12, 5).timestamp()),
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 11, 1).timestamp()),
        SimpleNamespace(st_mtime=datetime(2026, 8, 23, 3, 1).timestamp()),
    ],
)
def test_get_days(mock_stats, tmp_path):
    video_1 = tmp_path / "video1.mp4"
    video_2 = tmp_path / "video2.mp4"
    video_3 = tmp_path / "video3.mp4"
    video_4 = tmp_path / "video4.mp4"

    actual = get_days([video_1, video_2, video_3, video_4])

    expected = [
        Day(date=date(2026, 8, 22), source_videos=[video_1, video_2, video_4]),
        Day(date=date(2026, 8, 21), source_videos=[video_3]),
    ]

    assert actual == expected


def test_get_days_from_concatenated(tmp_path):
    # given
    test_video_1 = tmp_path / "2026-09-09.mp4"
    test_video_2 = tmp_path / "2026-10-10.mp4"

    test_video_1.touch()
    test_video_2.touch()

    # when
    actual = get_days_from_concatenated(tmp_path)

    # then
    expected = [
        Day(date=date(2026, 9, 9), concatenated_video=test_video_1),
        Day(date=date(2026, 10, 10), concatenated_video=test_video_2),
    ]
    assert actual == expected


@patch("hog_uploader.videos.concatenate_videoclips")
@patch("hog_uploader.videos.VideoFileClip")
def test_concatenate_videos(
    mock_video_file_clip, mock_concatenate_videoclips, tmp_path
):
    # given
    video_1 = tmp_path / "video1.mp4"
    video_2 = tmp_path / "video2.mp4"
    video_3 = tmp_path / "video3.mp4"
    test_output_directory = tmp_path / "output"
    test_day = Day(
        date=datetime(2026, 8, 23).date(), source_videos=[video_1, video_2, video_3]
    )

    mock_final_videoclip = MagicMock()
    mock_concatenate_videoclips.return_value = mock_final_videoclip
    mock_final_videoclip.__enter__.return_value = mock_final_videoclip

    mock_videoclip_1 = MagicMock()
    mock_videoclip_2 = MagicMock()
    mock_videoclip_3 = MagicMock()
    mock_video_file_clip.side_effect = [
        mock_videoclip_1,
        mock_videoclip_2,
        mock_videoclip_3,
    ]

    # when
    actual = concatenate_videos(test_day, test_output_directory)

    # then
    expected = tmp_path / "output" / "2026-08-23.mp4"
    assert actual == expected

    mock_video_file_clip.assert_has_calls([call(video_1), call(video_2), call(video_3)])
    mock_videoclip_1.close.assert_called_once()
    mock_videoclip_2.close.assert_called_once()
    mock_videoclip_3.close.assert_called_once()

    mock_final_videoclip.__enter__.assert_called_once()
    mock_final_videoclip.write_videofile.assert_called_once_with(expected)
    mock_final_videoclip.__exit__.assert_called_once()


def test_concatenate_videos_no_source_videos(tmp_path):
    test_date = date(2026, 9, 9)
    test_video = tmp_path / "2026-09-09.mp4"
    test_day = Day(date=test_date, concatenated_video=test_video)

    with pytest.raises(
        ValueError, match="The day 2026-09-09 has no source videos to concatenate"
    ):
        concatenate_videos(day=test_day, concatenated_videos_directory=tmp_path)


@patch("hog_uploader.videos.shutil.move")
def test_move_file(mock_move, tmp_path):
    test_file_path = tmp_path / "some_file.txt"
    test_destination = tmp_path / "some_destination"

    move_file(test_file_path, test_destination)

    mock_move.assert_called_with(test_file_path, test_destination)
