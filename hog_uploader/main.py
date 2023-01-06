import os

from file_utils import (concatenate_videos_and_save_to_output,
                        get_file_metadata, get_unique_dates,
                        groups_files_into_days)

def concatenate_video_clips():
    directory = os.listdir("../input")
    file_dict = get_file_metadata(directory)
    unique_dates = get_unique_dates(file_dict)
    groups = groups_files_into_days(file_dict, unique_dates)
    concatenate_videos_and_save_to_output(groups)


if __name__ == "__main__":
    concatenate_video_clips()
    