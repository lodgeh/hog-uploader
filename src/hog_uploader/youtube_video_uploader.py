from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
PLAYLIST_ID = "PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH"


def create_youtube_service(credentials_file_path: Path) -> Resource:
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file=str(credentials_file_path), scopes=SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)


class YoutubeVideoUploader:
    def __init__(self, service: Resource):
        self.youtube = service

    def upload_video(self, video_title: str, video_file_path: Path) -> str:
        body = {
            "snippet": {"title": video_title},
            "status": {"privacyStatus": "unlisted"},
        }
        video_upload_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(
                str(video_file_path), chunksize=-1, resumable=True
            ),
        )
        response = None
        while response is None:
            _, response = video_upload_request.next_chunk()
        return response[1]["id"]

    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> None:
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            },
        }
        self.youtube.playlistItems().insert(part="snippet", body=body).execute()

    def upload_video_and_add_to_playlist(
        self, video_title: str, video_file_path: Path, playlist_id: str
    ):
        video_id = self.upload_video(
            video_title=video_title, video_file_path=video_file_path
        )
        self.add_video_to_playlist(playlist_id=playlist_id, video_id=video_id)
