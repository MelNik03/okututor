import requests
import base64
from django.conf import settings

class ZoomService:
    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.redirect_uri = settings.ZOOM_REDIRECT_URI
        self.base_url = "https://api.zoom.us/v2"

    def get_authorization_url(self):
        return (
            "https://zoom.us/oauth/authorize?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
        )

    def get_access_token(self, code):
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        response = requests.post(
            "https://zoom.us/oauth/token",
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            },
        )
        return response.json()

    def create_meeting(self, access_token, user_id, topic, start_time, duration):
        response = requests.post(
            f"{self.base_url}/users/{user_id}/meetings",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "topic": topic,
                "type": 2,  # Запланированная встреча
                "start_time": start_time,  # Формат: "2025-05-10T10:00:00Z"
                "duration": duration,  # В минутах
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "join_before_host": False,
                },
            },
        )
        return response.json()