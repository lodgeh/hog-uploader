import os
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from moviepy.editor import VideoFileClip, concatenate_videoclips


@dataclass
class Video:
    file_name: str
    file_path: str
    creation_datetime: datetime
    creation_date_string: str


class VideoLoader:
    def load_videos(self, video_directory_path: str) -> list[Video]:
        raw_video_list = []
        video_files = sorted(os.listdir(video_directory_path))

        for file in video_files:
            if ".MP4" not in file:
                continue

            name = file.split(".MP4")[0]
            path = os.path.join(video_directory_path, file)

            file_creation_unix_time = os.path.getmtime(path)
            file_creation_datetime = datetime.fromtimestamp(file_creation_unix_time)

            raw_video_list.append(
                Video(
                    name,
                    path,
                    file_creation_datetime,
                    str(file_creation_datetime.date()),
                )
            )

        return raw_video_list


class VideoManager:
    def __init__(self, video_loader: VideoLoader):
        self.video_loader: VideoLoader = video_loader
        self.raw_video_list: list[Video] = []
        self.concatenated_video_list: list[Video] = []
        self.day_grouped_videos: defaultdict[str, list[Video]] = defaultdict(list)

    def get_video_list(self, video_directory_path: str):
        self.raw_video_list = self.video_loader.load_videos(video_directory_path)

    def group_videos_for_concatenation(self):
        """
        we want to group videos into 24 hour periods, starting at midday
        on the current date and ending at midday for the next date

        e.g. the date 2024-05-25 would include all videos between
        2024-05-25 12:00:00 and 2024-05-26 11:59:59
        """
        for video in self.raw_video_list:
            period_start = video.creation_datetime.replace(
                hour=12, minute=0, second=0, microsecond=0
            )

            if video.creation_datetime >= period_start:
                group_date = video.creation_datetime.date()
            else:
                group_date = video.creation_datetime.date() - timedelta(days=1)

            self.day_grouped_videos[str(group_date)].append(video)

    def concatenate_videos(self):
        output_path = "output/"
        for day in self.day_grouped_videos:
            clips = [
                VideoFileClip(video.file_path) for video in self.day_grouped_videos[day]
            ]

            day_clip = concatenate_videoclips(clips)
            day_clip_file_name = f"{day}.mp4"
            day_clip_output_path = os.path.join(output_path, day_clip_file_name)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            day_clip.write_videofile(day_clip_output_path)

            self.concatenated_video_list.append(
                Video(
                    day_clip_file_name,
                    day_clip_output_path,
                    datetime.now(),
                    day,
                )
            )

    def move_raw_videos_to_archive(self):
        for day, videos in self.concatenated_video_list.items():
            archive_directory = os.path.join("archive", "raw", day)
            os.makedirs(archive_directory, exist_ok=True)

            for video in videos:
                shutil.move(video.file_path, archive_directory)
