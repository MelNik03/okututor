from django.http import JsonResponse
from okututor_backend.firebase_config import db, auth_client
import json

def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            username = data.get("username")

            if not email or not password or not username:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Создаём пользователя в Firebase Authentication
            user = auth_client.create_user(
                email=email,
                password=password,
                display_name=username
            )

            # Сохраняем данные пользователя в Firestore
            user_data = {
                "email": email,
                "username": username,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            db.collection("users").document(user.uid).set(user_data)

            return JsonResponse({"message": "User registered successfully", "uid": user.uid}, status=201)
        except auth_client.EmailAlreadyExistsError:
            return JsonResponse({"error": "Email already exists"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id_token = data.get("id_token")  # Токен, полученный от фронтенда после входа

            # Проверяем токен
            decoded_token = auth_client.verify_id_token(id_token)
            uid = decoded_token["uid"]
            user = auth_client.get_user(uid)
            return JsonResponse({"message": "User logged in", "uid": uid, "email": user.email}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)
    return JsonResponse({"error": "Invalid request method"}, status=405)