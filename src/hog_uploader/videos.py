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

    @property
    def date_string(self) -> str:
        return self.date.isoformat()


def load_videos(path: str) -> list[Path]:
    p = Path(path)
    return [file for file in p.iterdir() if file.suffix == ".mkv"]


def get_days(videos: list[Path]) -> list[Day]:
    days: dict[str, list[Path]] = defaultdict(list)

    for video in videos:
        video_creation_timestamp = video.stat().st_mtime
        video_creation_datetime = datetime.fromtimestamp(video_creation_timestamp)
        day = video_creation_datetime.date()

        if video_creation_datetime.hour < 12:
            day -= timedelta(days=1)

        days[day].append(video)

    return [Day(day, videos) for day, videos in days.items()]


def concatenate_videos(
    days: list[Day], archive_directory: Path, output_directory: Path
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    for day in days:
        videoclips = [VideoFileClip(video) for video in day.videos]
        final = concatenate_videoclips(videoclips)
        final.write_videofile(output_directory / f"{day.date_string}.mkv", threads=12)

        for video in day.videos:
            move_file(video, archive_directory / day.date_string)


def move_file(file_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.move(file_path, destination)


def main():
    path = "/home/hi/hog-uploader/input"
    videos = load_videos(path)
    days = get_days(videos)

    archive_path = Path("archive")
    output_path = Path("output")

    concatenate_videos(days, archive_path, output_path)


if __name__ == "__main__":
    main()
    # test = load_videos_2("input")
    # # print(test)

    # for file in test:
    #     print(isinstance(file, Path))
    #     # print(file.name)
    #     # print(file.absolute)
    #     # print(datetime.fromtimestamp(file.stat().st_mtime))
    #     print(type((datetime.fromtimestamp(file.stat().st_mtime)).date()))

    #     # print(file.resolve())

    # # test = map(lambda x: VideoClip(x.resolve()), test)
    # # for x in list(test):
    # #     print(x._path)
