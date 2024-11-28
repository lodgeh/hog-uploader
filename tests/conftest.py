from datetime import datetime
from unittest.mock import MagicMock

import pytest

from hog_uploader.video_manager import Video, VideoManager


@pytest.fixture(scope="class")
def video_loader_mock() -> MagicMock:
    video_loader_mock = MagicMock()
    video_loader_mock.load_videos.return_value = [
        Video(
            "test_file_4.MP4",
            "test_path/test_file_4.MP4",
            datetime(2024, 5, 25, 23, 0, 0),
            "2024-05-25",
        ),
        Video(
            "test_file_3.MP4",
            "test_path/test_file_3.MP4",
            datetime(2024, 5, 26, 3, 0, 0),
            "2024-05-26",
        ),
        Video(
            "test_file_1.MP4",
            "test_path/test_file_1.MP4",
            datetime(2024, 5, 26, 12, 0, 0),
            "2024-05-26",
        ),
        Video(
            "test_file_2.MP4",
            "test_path/test_file_2.MP4",
            datetime(2024, 5, 26, 17, 30, 0),
            "2024-05-26",
        ),
    ]
    return video_loader_mock


@pytest.fixture(scope="function")
def video_manager_mock(video_loader_mock: MagicMock) -> VideoManager:
    video_manager = VideoManager(video_loader_mock)
    video_manager.day_grouped_videos = {
        "2024-05-26": [
            Video(
                "test_file_1.MP4",
                "test_path/test_file_1.MP4",
                datetime(2024, 5, 26, 12, 0, 0),
                "2024-05-26",
            ),
            Video(
                "test_file_2.MP4",
                "test_path/test_file_2.MP4",
                datetime(2024, 5, 26, 17, 30, 0),
                "2024-05-26",
            ),
        ],
        "2024-05-25": [
            Video(
                "test_file_3.MP4",
                "test_path/test_file_3.MP4",
                datetime(2024, 5, 26, 3, 0, 0),
                "2024-05-26",
            ),
            Video(
                "test_file_4.MP4",
                "test_path/test_file_4.MP4",
                datetime(2024, 5, 25, 23, 0, 0),
                "2024-05-25",
            ),
        ],
    }
    return video_manager
