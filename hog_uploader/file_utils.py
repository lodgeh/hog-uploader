import os
import shutil
import sys
from datetime import datetime, timedelta

import pandas as pd
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pandas import DatetimeIndex, Timestamp


def check_if_any_files(folder: str) -> None:
    files = os.listdir(folder)
    if not files:
        sys.exit(f"There are no video files in the {folder} folder!")


def get_file_metadata(files: list) -> dict[str, datetime]:
    file_dict = {}
    for file in files:
        file_creation_unix_time: float = os.path.getmtime(f"input/{file}")
        file_creation_datetime: datetime = datetime.fromtimestamp(
            file_creation_unix_time
        )
        file_dict[file] = file_creation_datetime
    return file_dict


def get_unique_dates(file_dict: dict) -> DatetimeIndex:
    dates: list = [file_dict[file].date() for file in file_dict]
    min_date = min(dates)
    max_date = max(dates)
    return pd.date_range(start=min_date, end=max_date)


def groups_files_into_days(
    file_dict: dict, unique_dates: list
) -> list[dict[Timestamp, list[str]]]:
    daily_file_groupings_list: list = []
    for date in unique_dates:
        start_datetime: datetime = date + timedelta(hours=12)
        end_datetime: datetime = date + timedelta(hours=36)

        file_list: list = []
        for file in file_dict:
            file_date: datetime = file_dict[file]
            if start_datetime <= file_date < end_datetime:
                file_list.append(file)

        sorted_file_list = sorted(file_list)
        daily_file_group: dict = {}
        daily_file_group[date] = sorted_file_list
        daily_file_groupings_list.append(daily_file_group)
    return daily_file_groupings_list


def concatenate_videos_and_save_to_output(
    groups: list[dict[Timestamp, list[str]]]
) -> None:
    for group in groups:
        ((date, files),) = group.items()
        if not files:
            continue
        clips: list = [VideoFileClip(f"input/{file}") for file in files]
        final_clip = concatenate_videoclips(clips)
        os.makedirs(os.path.dirname("output/"), exist_ok=True)
        final_clip.write_videofile(f"output/{date.date()}.mp4")


def move_file(current_path: str, new_path: str) -> None:
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.move(current_path, new_path)


def move_raw_videoclips_to_archive(groups: list) -> None:
    for group in groups:
        ((date, files),) = group.items()
        if not files:
            continue
        for file in files:
            file_path = os.path.join("input", file)
            move_file(file_path, os.path.join(f"archive/raw/{date.date()}/"))
