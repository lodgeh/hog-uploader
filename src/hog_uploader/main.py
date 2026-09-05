import argparse
from pathlib import Path

from hog_uploader.videos import concatenate_videos, get_days, load_videos, move_file
from hog_uploader.youtube_video_uploader import (
    PLAYLIST_ID,
    YoutubeVideoUploader,
    create_youtube_service,
)


def hog_uploader():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action=argparse.BooleanOptionalAction)
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--oauth-client-secrets-file", type=Path)
    parser.add_argument("--youtube-playlist-id", type=str, default=PLAYLIST_ID)
    args = parser.parse_args()

    input_dir = args.input_dir
    raw_dir = args.output_dir / "raw"
    concatenated_dir = args.output_dir / "concatenated"
    uploaded_dir = args.output_dir / "uploaded"

    if args.upload:
        youtube = create_youtube_service(args.oauth_client_secrets_file)
        youtube_uploader = YoutubeVideoUploader(youtube)

    videos = load_videos(input_dir)
    days = get_days(videos)

    for day in days:
        day.concatenated_video = concatenate_videos(day, concatenated_dir)

        for video in day.videos:
            move_file(video, raw_dir)

    if args.upload:
        for day in days:
            youtube_uploader.upload_video_and_add_to_playlist(
                day.date_string, day.concatenated_video, args.youtube_playlist_id
            )
            move_file(day.concatenated_video, uploaded_dir)


if __name__ == "__main__":
    hog_uploader()
