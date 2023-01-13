from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def get_authenticated_service(secret_file_path: str):
    flow = InstalledAppFlow.from_client_secrets_file(secret_file_path, SCOPES)
    credentials = flow.run_console()
    return build("youtube", "v3", credentials=credentials)


def create_video_upload_request(youtube: build, title: str, file_path: str):
    body = dict(snippet=dict(title=title), status=dict(privacyStatus="unlisted"))
    return youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True),
    )


def start_video_upload(video_upload_request: build):
    response = video_upload_request.next_chunk()
    return response[1]["id"]


def add_video_to_playlist(youtube: build, playlist_id: str, video_id: str):
    body = dict(
        snippet=dict(
            playlistId=playlist_id,
            resourceId=dict(kind="youtube#video", videoId=video_id),
        )
    )

    youtube.playlistItems().insert(part="snippet", body=body).execute()
