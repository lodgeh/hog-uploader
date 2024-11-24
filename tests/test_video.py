from datetime import datetime
from unittest.mock import MagicMock, call

from pytest import MonkeyPatch

from hog_uploader.video import Video, VideoLoader, VideoManager


class TestVideoLoader:
    def test_load_videos(self, monkeypatch: MonkeyPatch):
        # given
        test_video_loader = VideoLoader()
        video_directory_path = "test_path"

        monkeypatch.setattr(
            "os.listdir",
            lambda video_files: [
                "DSCF0418.MP4",
                "DSCF0419.MP4",
                "DSCF0420.MP4",
                "DSCF0421.MP4",
                "some_random_file.text",
            ],
        )

        def mocked_getmtime(file_path: str) -> str:
            video_file_dict = {
                f"{video_directory_path}/DSCF0418.MP4": 1716761032,
                f"{video_directory_path}/DSCF0419.MP4": 1716761912,
                f"{video_directory_path}/DSCF0420.MP4": 1716767472,
                f"{video_directory_path}/DSCF0421.MP4": 1716767494,
            }
            return video_file_dict[file_path]

        monkeypatch.setattr("os.path.getmtime", mocked_getmtime)

        # when
        actual = test_video_loader.load_videos(video_directory_path)

        # then
        expected = [
            Video(
                "DSCF0418",
                f"{video_directory_path}/DSCF0418.MP4",
                datetime(2024, 5, 26, 23, 3, 52),
                "2024-05-26",
            ),
            Video(
                "DSCF0419",
                f"{video_directory_path}/DSCF0419.MP4",
                datetime(2024, 5, 26, 23, 18, 32),
                "2024-05-26",
            ),
            Video(
                "DSCF0420",
                f"{video_directory_path}/DSCF0420.MP4",
                datetime(2024, 5, 27, 0, 51, 12),
                "2024-05-27",
            ),
            Video(
                "DSCF0421",
                f"{video_directory_path}/DSCF0421.MP4",
                datetime(2024, 5, 27, 0, 51, 34),
                "2024-05-27",
            ),
        ]
        assert expected == actual


class TestVideoManager:
    def test_get_video_list(self):
        # given
        video_loader_mock = MagicMock()
        video_loader_mock.load_videos.return_value = [
            Video(
                "test_file_1.MP4",
                "test_path/test_file_1.MP4",
                datetime(2024, 11, 22, 0, 0, 0),
                "2024-11-22",
            ),
            Video(
                "test_file_2.MP4",
                "test_path/test_file_2.MP4",
                datetime(2024, 11, 22, 0, 0, 0),
                "2024-11-22",
            ),
        ]

        test_video_mananager = VideoManager(video_loader_mock)

        # when
        test_video_mananager.get_video_list("test_path")

        # then
        expected = [
            Video(
                "test_file_1.MP4",
                "test_path/test_file_1.MP4",
                datetime(2024, 11, 22, 0, 0, 0),
                "2024-11-22",
            ),
            Video(
                "test_file_2.MP4",
                "test_path/test_file_2.MP4",
                datetime(2024, 11, 22, 0, 0, 0),
                "2024-11-22",
            ),
        ]

        assert expected == test_video_mananager.raw_video_list

    def test_group_videos_for_concatination(self):
        # given
        test_video_manager = VideoManager(VideoLoader())
        test_video_manager.raw_video_list = [
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

        # when
        test_video_manager.group_videos_for_concatenation()

        # then
        # video's should be in ascending order within each day
        expected = {
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
            ],
        }
        assert expected == test_video_manager.day_grouped_videos

    def test_concatenate_videos(self, monkeypatch: MonkeyPatch):
        # given
        test_video_manager = VideoManager(VideoLoader())
        test_video_manager.day_grouped_videos = {
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

        mock_videoclip = MagicMock()
        monkeypatch.setattr(
            "hog_uploader.video.VideoFileClip",
            lambda path: mock_videoclip,
        )

        mock_concatenated_videoclip = MagicMock()
        monkeypatch.setattr(
            "hog_uploader.video.concatenate_videoclips",
            lambda clips: mock_concatenated_videoclip,
        )

        fixed_datetime = datetime(2024, 12, 23, 12, 0, 0, 0)
        mock_datetime = MagicMock()
        mock_datetime.now.return_value = fixed_datetime

        monkeypatch.setattr(
            "hog_uploader.video.datetime",
            mock_datetime,
        )

        # when
        test_video_manager.concatenate_videos()

        # then
        expected = [
            Video(
                "2024-05-26.mp4",
                "output/2024-05-26.mp4",
                fixed_datetime,
                "2024-05-26",
            ),
            Video(
                "2024-05-25.mp4",
                "output/2024-05-25.mp4",
                fixed_datetime,
                "2024-05-25",
            ),
        ]

        mock_concatenated_videoclip.assert_has_calls(
            [
                call.write_videofile("output/2024-05-26.mp4"),
                call.write_videofile("output/2024-05-25.mp4"),
            ]
        )
        assert expected == test_video_manager.concatenated_video_list

    def test_move_video(self, monkeypatch: MonkeyPatch):
        # given
        test_video_manager = VideoManager(VideoLoader())
        file_path = "test/file.mp4"
        output_directory_path = "test/output/"

        mock_makedirs = MagicMock()
        monkeypatch.setattr("os.makedirs", mock_makedirs)

        mock_move = MagicMock()
        monkeypatch.setattr("shutil.move", mock_move)

        # when
        test_video_manager.move_video(file_path, output_directory_path)

        # then
        mock_makedirs.assert_has_calls([call(output_directory_path, exist_ok=True)])
        assert mock_makedirs.call_count == 1

        mock_move.assert_has_calls([call(file_path, output_directory_path)])
        assert mock_move.call_count == 1

    def test_move_raw_videos_to_archive(self, monkeypatch: MonkeyPatch):
        # given
        test_video_mananger = VideoManager(VideoLoader())
        test_video_mananger.day_grouped_videos = {
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

        mock_makedirs = MagicMock()
        monkeypatch.setattr("os.makedirs", mock_makedirs)

        mock_move = MagicMock()
        monkeypatch.setattr("shutil.move", mock_move)

        # when
        test_video_mananger.move_raw_videos_to_archive()

        # then
        mock_makedirs.assert_has_calls(
            [
                call("archive/raw/2024-05-26", exist_ok=True),
                call("archive/raw/2024-05-25", exist_ok=True),
            ]
        )
        assert mock_makedirs.call_count == 4

        mock_move.assert_has_calls(
            [
                call("test_path/test_file_1.MP4", "archive/raw/2024-05-26"),
                call("test_path/test_file_2.MP4", "archive/raw/2024-05-26"),
                call("test_path/test_file_3.MP4", "archive/raw/2024-05-25"),
                call("test_path/test_file_4.MP4", "archive/raw/2024-05-25"),
            ]
        )
        assert mock_move.call_count == 4
