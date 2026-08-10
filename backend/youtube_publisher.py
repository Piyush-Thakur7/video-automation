import os
import json
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']

class YouTubePublisher:
    def __init__(self, credentials_path: str = "config/client_secrets.json"):
        self.credentials_path = credentials_path
        os.makedirs("config", exist_ok=True)
        self._ensure_config_files()

    def _get_token_path(self, profile_id: str = "quantum_facts") -> str:
        if profile_id == "kids_wonder":
            return "config/youtube_token_kids_wonder.json"
        
        # Primary profile token
        primary_path = "config/youtube_token_quantum_facts.json"
        if os.path.exists(primary_path):
            return primary_path
        return "config/youtube_token.json"

    def _ensure_config_files(self):
        try:
            if not os.path.exists(self.credentials_path):
                raw_secrets = os.environ.get("CLIENT_SECRETS_JSON")
                b64_secrets = os.environ.get("CLIENT_SECRETS_B64")
                if b64_secrets:
                    raw_secrets = base64.b64decode(b64_secrets).decode("utf-8")
                if raw_secrets:
                    secrets_data = json.loads(raw_secrets)
                    with open(self.credentials_path, "w", encoding="utf-8") as f:
                        json.dump(secrets_data, f, indent=2)

            token_path = self._get_token_path("quantum_facts")
            if not os.path.exists(token_path):
                raw_token = os.environ.get("YOUTUBE_TOKEN_JSON")
                b64_token = os.environ.get("YOUTUBE_TOKEN_B64")
                if b64_token:
                    raw_token = base64.b64decode(b64_token).decode("utf-8")
                if raw_token:
                    token_data = json.loads(raw_token)
                    with open(token_path, "w", encoding="utf-8") as f:
                        json.dump(token_data, f, indent=2)
        except Exception as e:
            print(f"[YouTubePublisher Init Error] {e}")

    def _get_credentials(self, profile_id: str = "quantum_facts"):
        self._ensure_config_files()
        token_path = self._get_token_path(profile_id)

        if not os.path.exists(token_path):
            return None

        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w', encoding="utf-8") as f:
                    f.write(creds.to_json())
            return creds
        except Exception as e:
            print(f"[YouTubePublisher] Credential error for profile '{profile_id}': {e}")
            return None

    def is_authenticated(self, profile_id: str = "quantum_facts") -> bool:
        creds = self._get_credentials(profile_id)
        return bool(creds and creds.valid)

    def get_channel_info(self, profile_id: str = "quantum_facts") -> dict:
        creds = self._get_credentials(profile_id)
        if not creds or not creds.valid:
            return {"authenticated": False, "profile_id": profile_id, "channel": None}

        try:
            youtube = build('youtube', 'v3', credentials=creds)
            res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
            if res.get("items"):
                ch = res["items"][0]
                return {
                    "authenticated": True,
                    "profile_id": profile_id,
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
            print(f"[YouTubePublisher] Error fetching channel for '{profile_id}': {e}")

        return {"authenticated": False, "profile_id": profile_id, "channel": None}

    def get_auth_url(self, redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback", profile_id: str = "quantum_facts") -> str:
        if not os.path.exists(self.credentials_path):
            return None
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, 
                SCOPES, 
                redirect_uri=redirect_uri
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true', state=profile_id)
            return auth_url
        except Exception as e:
            print(f"[YouTubePublisher] Error generating auth URL: {e}")
            return None

    def exchange_code(self, code: str, redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback", profile_id: str = "quantum_facts") -> bool:
        if not os.path.exists(self.credentials_path):
            return False
        token_path = self._get_token_path(profile_id)
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, 
                SCOPES, 
                redirect_uri=redirect_uri
            )
            flow.fetch_token(code=code)
            creds = flow.credentials
            with open(token_path, 'w', encoding="utf-8") as f:
                f.write(creds.to_json())
            print(f"[YouTubePublisher] Successfully authenticated profile '{profile_id}' -> saved to {token_path}")
            return True
        except Exception as e:
            print(f"[YouTubePublisher] Error exchanging code for '{profile_id}': {e}")
            return False

    def save_client_secrets(self, secrets_dict: dict) -> bool:
        """Saves Google OAuth2 client_secrets.json to config directory."""
        try:
            with open(self.credentials_path, 'w', encoding="utf-8") as f:
                json.dump(secrets_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"[YouTubePublisher] Error saving client secrets: {e}")
            return False

    def upload_video(self, video_path: str, title: str, description: str, tags: list, category_id: str = "27", privacy_status: str = "private", notify_subscribers: bool = True, profile_id: str = "quantum_facts") -> dict:
        """
        Uploads an MP4 video to YouTube channel using YouTube Data API v3.
        Category 27 = Education, 24 = Entertainment, 28 = Science & Tech.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at {video_path}")

        creds = self._get_credentials(profile_id)
        if not creds or not creds.valid:
            return {
                "success": False,
                "error": f"YouTube Channel for profile '{profile_id}' is not authenticated. Please link YouTube account in Channel Settings.",
                "simulated": True,
                "video_id": "simulated_yt_" + os.path.basename(video_path).rsplit(".", 1)[0]
            }

        try:
            youtube = build('youtube', 'v3', credentials=creds)

            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:20],
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": True if profile_id == "kids_wonder" else False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"[{profile_id} YT Upload] Uploaded {int(status.progress() * 100)}%")

            video_id = response.get("id")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"[{profile_id} YT Upload] Video uploaded successfully! URL: {video_url}")

            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url,
                "privacy_status": privacy_status,
                "profile_id": profile_id,
                "details": response
            }

        except Exception as e:
            print(f"[{profile_id} YT Upload Error] {e}")
            return {
                "success": False,
                "error": str(e),
                "simulated": False
            }

youtube_publisher = YouTubePublisher()
