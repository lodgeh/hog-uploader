import os

from file_utils import (
    concatenate_videos_and_save_to_output,
    get_file_metadata,
    get_unique_dates,
    groups_files_into_days,
    move_file,
)

from yt_upload_utils import (
    get_authenticated_service,
    create_video_upload_request,
    start_video_upload,
    add_video_to_playlist,
)

INPUT_DIRECTORY = os.listdir("../input")
OUTPUT_DIRECTORY = os.listdir("../output")

PLAYLIST_ID = "PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH"


def main():
    youtube = get_authenticated_service()
    concatenate_video_clips(INPUT_DIRECTORY)

    for file in OUTPUT_DIRECTORY:
        file_name = file.split(".mp4")[0]
        file_path = f"../output/{file}"
        video_id = upload_youtube_video(youtube, file_name, file_path)
        add_video_to_playlist(youtube, video_id, PLAYLIST_ID)
        move_file(file)


def concatenate_video_clips(input_directory):
    file_dict = get_file_metadata(input_directory)
    unique_dates = get_unique_dates(file_dict)
    groups = groups_files_into_days(file_dict, unique_dates)
    concatenate_videos_and_save_to_output(groups)


def upload_youtube_video(youtube, video_title, file_path):
    video_upload_request = create_video_upload_request(youtube, video_title, file_path)
    video_id = start_video_upload(video_upload_request)
    return video_id


if __name__ == "__main__":
    main()
