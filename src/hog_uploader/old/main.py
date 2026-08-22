import argparse

from hog_uploader.hog_uploader import HogUploader
from hog_uploader.video_manager import VideoLoader, VideoManager
from hog_uploader.youtube_uploader_service import YoutubeUploaderService

PLAYLIST_ID = "PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upload-only",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    hog_uploader = HogUploader(
        YoutubeUploaderService(),
        VideoManager(VideoLoader()),
        "input/",
        "youtube_secrets.json",
        PLAYLIST_ID,
    )

    if not args.upload_only:
        hog_uploader.get_videos()

    hog_uploader.upload_videos_and_add_to_playlist()


if __name__ == "__main__":
    main()
