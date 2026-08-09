import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']

class YouTubePublisher:
    def __init__(self, credentials_path: str = "config/client_secrets.json", token_path: str = "config/youtube_token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        os.makedirs("config", exist_ok=True)

    def is_authenticated(self) -> bool:
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                return creds and creds.valid
            except Exception:
                return False
        return False

    def get_channel_info(self) -> dict:
        if not self.is_authenticated():
            return {"authenticated": False, "channel": None}

        try:
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            youtube = build('youtube', 'v3', credentials=creds)
            res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
            if res.get("items"):
                ch = res["items"][0]
                return {
                    "authenticated": True,
                    "channel": {
                        "id": ch["id"],
                        "title": ch["snippet"]["title"],
                        "customUrl": ch["snippet"].get("customUrl", ""),
                        "thumbnails": ch["snippet"]["thumbnails"],
                        "subscriberCount": ch["statistics"].get("subscriberCount", "0"),
                        "videoCount": ch["statistics"].get("videoCount", "0")
                    }
                }
        except Exception as e:
            print(f"[YouTubePublisher] Error fetching channel: {e}")

        return {"authenticated": False, "channel": None}

    def upload_video(self, video_path: str, title: str, description: str, tags: list, category_id: str = "27", privacy_status: str = "private", notify_subscribers: bool = True) -> dict:
        """
        Uploads an MP4 video to YouTube channel using YouTube Data API v3.
        Category 27 = Education, 24 = Entertainment, 28 = Science & Tech.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at {video_path}")

        if not self.is_authenticated():
            return {
                "success": False,
                "error": "YouTube Channel is not authenticated. Please configure client_secrets.json in settings.",
                "simulated": True,
                "video_id": "simulated_yt_" + os.path.basename(video_path).rsplit(".", 1)[0]
            }

        try:
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            youtube = build('youtube', 'v3', credentials=creds)

            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description[:5000],
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/mp4')

            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"[YouTube] Upload progress: {int(status.progress() * 100)}%")

            video_id = response.get('id')
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtu.be/{video_id}",
                "privacy_status": privacy_status
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

youtube_publisher = YouTubePublisher()
