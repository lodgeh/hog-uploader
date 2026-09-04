import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips


@dataclass
class Day:
    date: date
    videos: list[Path]
    concatenated_video: Path | None = None

    @property
    def date_string(self) -> str:
        return self.date.isoformat()


def load_videos(path: Path) -> list[Path]:
    return sorted(file for file in path.iterdir() if file.suffix == ".mkv")


def get_days(videos: list[Path]) -> list[Day]:
    days: dict[date, list[Path]] = defaultdict(list)

    for video in videos:
        video_creation_timestamp = video.stat().st_mtime
        video_creation_datetime = datetime.fromtimestamp(video_creation_timestamp)
        day = video_creation_datetime.date()

        if video_creation_datetime.hour < 12:
            day -= timedelta(days=1)

        days[day].append(video)

    return [Day(day, sorted(videos)) for day, videos in days.items()]


def concatenate_videos(day: Day, concatenated_videos_directory: Path) -> Path:
    output_path = concatenated_videos_directory / f"{day.date_string}.mkv"

    videoclips = [VideoFileClip(video) for video in day.videos]

    try:
        with concatenate_videoclips(videoclips) as final:
            final.write_videofile(output_path, threads=12)
    finally:
        for clip in videoclips:
            clip.close()

    return output_path


def move_file(file_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.move(file_path, destination)
