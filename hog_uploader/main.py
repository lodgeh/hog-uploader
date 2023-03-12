import os

from file_utils import (
    concatenate_videos_and_save_to_output,
    get_file_metadata,
    get_unique_dates,
    groups_files_into_days,
    move_file,
    move_raw_videoclips_to_archive,
)

from yt_upload_utils import (
    get_authenticated_service,
    create_video_upload_request,
    start_video_upload,
    add_video_to_playlist,
)


PLAYLIST_ID = "PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH"


def group_raw_videoclips_into_days():
    input_path = os.listdir("../input")
    file_dict = get_file_metadata(input_path)
    unique_dates = get_unique_dates(file_dict)
    videoclip_groups = groups_files_into_days(file_dict, unique_dates)
    return videoclip_groups


def concatenate_videoclips(groups):
    concatenate_videos_and_save_to_output(groups)


def authenticate_for_youtube():
    youtube_secret_path = "../youtube_secrets.json"
    youtube = get_authenticated_service(youtube_secret_path)
    return youtube


def upload_youtube_video(youtube, video_title, file_path):
    video_upload_request = create_video_upload_request(youtube, video_title, file_path)
    video_id = start_video_upload(video_upload_request)
    return video_id


def upload_concatenated_videos_to_youtube():
    output_path = os.listdir("../output")
    archive_concatenated_file_path = f"../archive/concatenated/"
    for file in output_path:
        file_name = file.split(".mp4")[0]
        file_path = f"../output/{file}"
        video_id = upload_youtube_video(youtube, file_name, file_path)
        add_video_to_playlist(youtube, PLAYLIST_ID, video_id)
        move_file(file_path, archive_concatenated_file_path)


def main():
    authenticate_for_youtube()

    videoclips_grouped_by_day = group_raw_videoclips_into_days()
    move_raw_videoclips_to_archive(videoclips_grouped_by_day)
    concatenate_videos_and_save_to_output(videoclips_grouped_by_day)
    move_raw_videoclips_to_archive()
    upload_concatenated_videos_to_youtube()


if __name__ == "__main__":
    main()
