from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


class YoutubeUploaderService:
    def __init__(self):
        self.youtube_service = None
        self.video_upload_request = None

    def authenticate(self, credentials_file_path: str):
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
        credentials = flow.run_console()
        self.youtube_service = build("youtube", "v3", credentials=credentials)

    def upload_video(self, video_title: str, video_file_path: str) -> str:
        body = {
            "snippet": {"title": video_title},
            "status": {"privacyStatus": "unlisted"},
        }
        self.video_upload_request = self.youtube_service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_file_path, chunksize=-1, resumable=True),
        )
        response = self.video_upload_request.next_chunk()
        return response[1]["id"]

    def add_video_to_playlist(self, playlist_id: str, video_id: str):
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            },
        }
        self.youtube_service.playlistItems().insert(part="snippet", body=body).execute()
