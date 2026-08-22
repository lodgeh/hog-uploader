from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class Day:
    date: date
    videos: list[Path]


def load_videos_2(path: str) -> list[Path]:
    p = Path(path)
    return [file for file in p.iterdir() if file.suffix == ".mkv"]


def get_days(videos: list[Path]) -> list[Day]:
    days: dict[str, list[Path]] = defaultdict(list)

    for video in videos:
        video_creation_datetime = datetime.fromtimestamp(video.stat().st_mtime)
        day = video_creation_datetime.date()

        if video_creation_datetime.hour < 12:
            day -= timedelta(days=1)

        days[day].append(video)

    return [Day(day, videos) for day, videos in days.items()]


def main():
    path = "/home/hi/hog-uploader/input"
    videos = load_videos_2(path)
    get_days(videos)


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
