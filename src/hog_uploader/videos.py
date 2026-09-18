import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips


@dataclass(kw_only=True)
class Day:
    date: date
    source_videos: list[Path] = field(default_factory=list)
    concatenated_video: Path | None = None

    @property
    def date_string(self) -> str:
        return self.date.isoformat()


def load_videos(path: Path) -> list[Path]:
    return sorted(file for file in path.iterdir() if file.suffix.lower() == ".mp4")


def get_days(videos: list[Path]) -> list[Day]:
    days: dict[date, list[Path]] = defaultdict(list)

    for video in videos:
        video_creation_timestamp = video.stat().st_mtime
        video_creation_datetime = datetime.fromtimestamp(video_creation_timestamp)
        day = video_creation_datetime.date()

        if video_creation_datetime.hour < 12:
            day -= timedelta(days=1)

        days[day].append(video)

    return [Day(date=day, source_videos=sorted(videos)) for day, videos in days.items()]


def get_days_from_concatenated(concatenated_videos_directory: Path) -> list[Day]:
    videos = load_videos(concatenated_videos_directory)
    return [
        Day(date=date.fromisoformat(video.stem), concatenated_video=video)
        for video in videos
    ]


# @time_function
def concatenate_videos(day: Day, concatenated_videos_directory: Path) -> Path:
    if not day.source_videos:
        raise ValueError(
            f"The day {day.date_string} has no source videos to concatenate"
        )

    concatenated_videos_directory.mkdir(parents=True, exist_ok=True)
    output_path = concatenated_videos_directory / f"{day.date_string}.mp4"

    videoclips = [VideoFileClip(video) for video in day.source_videos]

    try:
        with concatenate_videoclips(videoclips) as concatenated:
            concatenated.write_videofile(output_path)
    finally:
        for clip in videoclips:
            clip.close()

    return output_path


def move_file(file_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.move(file_path, destination)
