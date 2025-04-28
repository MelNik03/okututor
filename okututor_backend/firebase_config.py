import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Динамически определяем путь к файлу учетных данных
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FIREBASE_CRED_PATH = os.path.join(BASE_DIR, "okututor-f276b-firebase-adminsdk-fbsvc-a53a702b8f.json")

# Проверяем, существует ли файл
if not os.path.exists(FIREBASE_CRED_PATH):
    raise FileNotFoundError(f"Firebase credentials file not found at: {FIREBASE_CRED_PATH}")

# Инициализация Firebase только если приложение ещё не инициализировано
cred = credentials.Certificate(FIREBASE_CRED_PATH)
try:
    firebase_admin.get_app()  # Проверяем, существует ли приложение
except ValueError:
    firebase_admin.initialize_app(cred, {
        'projectId': 'okututor-f276b',  # Явно указываем projectId
    })

# Инициализация Firestore
db = firestore.client()

# Экспортируем firestore для использования в других модулях
firestore_module = firestore

# Инициализация Auth
auth_client = auth