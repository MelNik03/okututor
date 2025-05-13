import os
import requests

def get_zoom_access_token():
    print("🚀 Получаем Zoom access token...")
    url = "https://zoom.us/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": os.environ.get("ZOOM_ACCOUNT_ID")
    }
    response = requests.post(
        url,
        headers=headers,
        auth=(
            os.environ.get("ZOOM_CLIENT_ID"),
            os.environ.get("ZOOM_CLIENT_SECRET")
        ),
        data=data
    )
    print("📥 Ответ от Zoom (токен):", response.status_code, response.text)
    response.raise_for_status()
    return response.json()["access_token"]

def create_zoom_meeting(topic, start_time, duration=30):
    print("🔧 create_zoom_meeting() вызван")
    token = get_zoom_access_token()
    print("🔑 Токен получен:", token)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
        "duration": duration,
        "timezone": "Asia/Bishkek",
        "settings": {
            "join_before_host": True,
            "approval_type": 0,
            "audio": "both"
        }
    }

    print("📤 Отправляем POST-запрос на создание встречи...")
    response = requests.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=payload)
    print("📥 Ответ от Zoom (создание):", response.status_code, response.text)
    response.raise_for_status()
    return response.json()
