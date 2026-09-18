import argparse
from collections.abc import Sequence
from pathlib import Path

from hog_uploader.enums import VideoExtension
from hog_uploader.videos import (
    concatenate_videos,
    get_days,
    get_days_from_concatenated,
    load_videos,
    move_file,
)
from hog_uploader.youtube_video_uploader import (
    YoutubeVideoUploader,
    create_youtube_service,
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    upload_group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--input-dir", type=Path, help="Directory containing input video files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for raw, concatenated and uploaded videos",
    )
    parser.add_argument(
        "--video-extension",
        type=str,
        default=VideoExtension.MP4,
        choices=[extension for extension in VideoExtension],
        help="Extension of input and ouput video; defaults to .mp4",
    )
    upload_group.add_argument(
        "--upload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Upload concatenated videos to YouTube; defaults to --upload",
    )
    upload_group.add_argument(
        "--upload-only",
        action="store_true",
        help="Only upload videos that have been concatenated",
    )
    parser.add_argument(
        "--oauth-client-secrets-file",
        type=Path,
        help=(
            "Path of the JSON file that contains the OAuth client secrets; "
            "required with --upload"
        ),
    )
    parser.add_argument(
        "--youtube-playlist-id",
        type=str,
        help=("YouTube playlist ID to add uploaded videos to; required with --upload"),
    )

    args = parser.parse_args(argv)

    if (args.upload or args.upload_only) and (
        args.oauth_client_secrets_file is None or args.youtube_playlist_id is None
    ):
        parser.error(
            "--oauth-client-secrets-file and --youtube-playlist-id are required with --upload and --upload-only"
        )

    hog_uploader(
        input_directory=args.input_dir,
        output_directory=args.output_dir,
        video_extension=args.video_extension,
        upload=args.upload,
        upload_only=args.upload_only,
        oauth_client_secrets_file=args.oauth_client_secrets_file,
        youtube_playlist_id=args.youtube_playlist_id,
    )


def hog_uploader(
    input_directory: Path,
    output_directory: Path,
    video_extension: str,
    upload: bool,
    upload_only: bool,
    oauth_client_secrets_file: Path,
    youtube_playlist_id: str,
) -> None:
    raw_directory = output_directory / "raw"
    concatenated_directory = output_directory / "concatenated"
    uploaded_directory = output_directory / "uploaded"

    if upload or upload_only:
        youtube = create_youtube_service(oauth_client_secrets_file)
        youtube_uploader = YoutubeVideoUploader(youtube)

    if upload_only:
        days = get_days_from_concatenated(concatenated_directory)
    else:
        videos = load_videos(input_directory)
        days = get_days(videos)

        for day in days:
            day.concatenated_video = concatenate_videos(day, concatenated_directory)

            for video in day.source_videos:
                move_file(video, raw_directory / day.date_string)

    if upload or upload_only:
        for day in days:
            youtube_uploader.upload_video_and_add_to_playlist(
                day.date_string, day.concatenated_video, youtube_playlist_id
            )
            move_file(day.concatenated_video, uploaded_directory)


if __name__ == "__main__":
    main()
