import argparse
from collections.abc import Sequence
from pathlib import Path

from hog_uploader.videos import concatenate_videos, get_days, load_videos, move_file
from hog_uploader.youtube_video_uploader import (
    YoutubeVideoUploader,
    create_youtube_service,
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir", type=Path, help="Directory containing input video files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for raw, concatenated and uploaded videos",
    )
    parser.add_argument(
        "--upload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Upload concatenated videos to YouTube; defaults to --upload",
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

    if args.upload and (
        args.oauth_client_secrets_file is None or args.youtube_playlist_id is None
    ):
        parser.error(
            "--oauth-client-secrets-file and --youtube-playlist-id are required with --upload"
        )

    hog_uploader(
        input_directory=args.input_dir,
        output_directory=args.output_dir,
        upload=args.upload,
        oauth_client_secrets_file=args.oauth_client_secrets_file,
        youtube_playlist_id=args.youtube_playlist_id,
    )


def hog_uploader(
    input_directory: Path,
    output_directory: Path,
    upload: bool,
    oauth_client_secrets_file: Path,
    youtube_playlist_id: str,
) -> None:
    raw_directory = output_directory / "raw"
    concatenated_directory = output_directory / "concatenated"
    uploaded_directory = output_directory / "uploaded"

    if upload:
        youtube = create_youtube_service(oauth_client_secrets_file)
        youtube_uploader = YoutubeVideoUploader(youtube)

    videos = load_videos(input_directory)
    days = get_days(videos)

    for day in days:
        day.concatenated_video = concatenate_videos(day, concatenated_directory)

        for video in day.videos:
            move_file(video, raw_directory)

    if upload:
        for day in days:
            youtube_uploader.upload_video_and_add_to_playlist(
                day.date_string, day.concatenated_video, youtube_playlist_id
            )
            move_file(day.concatenated_video, uploaded_directory)


if __name__ == "__main__":
    main()
