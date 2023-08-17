import argparse
import os
from typing import Any, Callable

from hog_uploader.file_utils import (
    check_if_any_files,
    concatenate_videos_and_save_to_output,
    get_file_metadata,
    get_unique_dates,
    groups_files_into_days,
    move_file,
    move_raw_videoclips_to_archive,
)
from hog_uploader.yt_upload_utils import (
    add_video_to_playlist,
    create_video_upload_request,
    get_authenticated_service,
    start_video_upload,
)

PLAYLIST_ID = "PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH"


def group_raw_videoclips_into_days() -> list:
    input_path = os.listdir("input")
    file_dict = get_file_metadata(input_path)
    unique_dates = get_unique_dates(file_dict)
    videoclip_groups = groups_files_into_days(file_dict, unique_dates)
    return videoclip_groups


def authenticate_for_youtube() -> Callable[..., object]:
    youtube_secret_path = "youtube_secrets.json"
    return get_authenticated_service(youtube_secret_path)


def upload_youtube_video(
    youtube: Callable[..., object], video_title: str, file_path: str
) -> str:
    video_upload_request = create_video_upload_request(youtube, video_title, file_path)
    return start_video_upload(video_upload_request)


def upload_concatenated_videos_to_youtube(
    authenticated_youtube_service: Callable[..., object],
) -> None:
    output_path = os.listdir("output")
    sorted_output_path = sorted(output_path)
    archive_concatenated_file_path = f"archive/concatenated/"
    for file in sorted_output_path:
        file_name = file.split(".mp4")[0]
        file_path = f"output/{file}"
        video_id = upload_youtube_video(
            authenticated_youtube_service, file_name, file_path
        )
        print(f"{file_name} uploaded!")
        add_video_to_playlist(authenticated_youtube_service, PLAYLIST_ID, video_id)
        move_file(file_path, archive_concatenated_file_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upload-only",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    if args.upload_only:
        check_if_any_files("output")
        youtube = authenticate_for_youtube()
        upload_concatenated_videos_to_youtube(youtube)

    if not args.upload_only:
        check_if_any_files("input")
        youtube = authenticate_for_youtube()
        videoclips_grouped_by_day = group_raw_videoclips_into_days()
        concatenate_videos_and_save_to_output(videoclips_grouped_by_day)
        move_raw_videoclips_to_archive(videoclips_grouped_by_day)
        upload_concatenated_videos_to_youtube(youtube)


if __name__ == "__main__":
    main()
