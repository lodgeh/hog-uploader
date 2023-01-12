import os
from datetime import datetime, timedelta

from moviepy.editor import VideoFileClip, concatenate_videoclips


def get_file_metadata(directory) -> dict:
    file_dict = {}
    for file in directory:
        file_creation_unix_time: float = os.path.getmtime(f"../input/{file}")
        file_creation_datetime: datetime = datetime.fromtimestamp(
            file_creation_unix_time
        )
        file_dict[file] = file_creation_datetime
    return file_dict


def get_unique_dates(file_dict: dict) -> list:
    dates: list = [file_dict[file].date() for file in file_dict]
    unique_dates: set = set(dates)
    return [datetime(date.year, date.month, date.day, 0, 0) for date in unique_dates]


def groups_files_into_days(file_dict: dict, unique_dates: list) -> list:
    daily_file_groupings_list: list = []
    for date in unique_dates:
        start_datetime: datetime = date + timedelta(hours=12)
        end_datetime: datetime = date + timedelta(hours=36)

        file_list: list = []
        for file in file_dict:
            file_date: datetime = file_dict[file]
            if start_datetime <= file_date < end_datetime:
                file_list.append(file)

        daily_file_group: dict = {}
        daily_file_group[date] = file_list
        daily_file_groupings_list.append(daily_file_group)
    return daily_file_groupings_list


def concatenate_videos_and_save_to_output(groups: list):
    for group in groups:
        for date, files in group.items():
            if not files:
                continue
            clips: list = [VideoFileClip(f"../input/{file}") for file in files]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(f"../output/{date.date()}.mp4")

def move_file(file_name: str):
    output_file_path = f"../output/{file_name}"
    storage_file_path = f"../storage/{file_name}"
    os.rename(output_file_path, storage_file_path)
