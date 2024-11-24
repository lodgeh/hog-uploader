import os

from hog_uploader.video import VideoManager
from hog_uploader.youtube_uploader_service import YoutubeUploaderService


class HogUploader:
    def __init__(
        self,
        youtube_service: YoutubeUploaderService,
        video_manager: VideoManager,
        video_directory_path: str,
        credentials_file_path: str,
        playlist_id: str,
    ):
        self.youtube_service = youtube_service
        self.video_manager = video_manager
        self.video_directory_path = video_directory_path
        self.playlist_id = playlist_id

        self.youtube_service.authenticate(credentials_file_path)

    def get_videos(self):
        self.video_manager.get_video_list(self.video_directory_path)
        self.video_manager.group_videos_for_concatenation()
        self.video_manager.concatenate_videos()
        self.video_manager.move_raw_videos_to_archive()

    def upload_videos_and_add_to_playlist(self):
        concatenated_video_archive_path = os.path.join("archive", "concatenated")
        video_list = self.video_manager.get_video_list("output/")
        for video in video_list:
            video_id = self.youtube_service.upload_video(
                video.creation_date_string, video.file_path
            )
            self.youtube_service.add_video_to_playlist(self.playlist_id, video_id)
            self.video_manager.move_video(
                video.file_path, concatenated_video_archive_path
            )
