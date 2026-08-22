from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from hog_uploader.videos import Day, get_days


@patch.object(
    Path,
    "stat",
    side_effect=[
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 12, 1).timestamp()),
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 12, 5).timestamp()),
        SimpleNamespace(st_mtime=datetime(2026, 8, 22, 11, 1).timestamp()),
    ],
)
def test_get_days(mock_stats, tmp_path):
    video_1 = tmp_path / "video1.mp4"
    video_2 = tmp_path / "video2.mp4"
    video_3 = tmp_path / "video3.mp4"

    actual = get_days([video_1, video_2, video_3])

    expected = [
        Day(date=date(2026, 8, 22), videos=[video_1, video_2]),
        Day(date=date(2026, 8, 21), videos=[video_3]),
    ]

    assert actual == expected
