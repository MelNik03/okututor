import logging
from okututor_backend.firebase_config import db, firestore_module
from typing import Dict, Optional
from firebase_admin import auth, firestore

class UserController:
    def register_user(self, email: str, password: str, repeat_password: str, full_name: str, user_id: str) -> Dict[str, str]:
        try:
            # Проверяем совпадение паролей
            if password != repeat_password:
                return {"error": "Passwords do not match"}

            # Проверяем, существует ли пользователь в Firestore (на случай, если клиентская регистрация прошла, но данные не сохранены)
            user_ref = db.collection("users").document(user_id)
            if user_ref.get().exists:
                return {"error": "User already exists in database"}

            # Сохраняем данные пользователя в Firestore
            user_data = {
                "email": email,
                "full_name": full_name,
                "role": "student",
                "created_at": firestore_module.SERVER_TIMESTAMP,
                "phone": None,
                "location": None,
                "bio": None,
                "avatar": None,
                "whatsapp": None,
                "instagram": None,
                "telegram": None
            }
            user_ref.set(user_data)
            return {"user_id": user_id, "message": "User registered successfully"}
        except Exception as e:
            return {"error": str(e)}

    # user_controller.py
    def google_login(self, id_token: str) -> Dict[str, str]:
        try:
            logging.debug(f"Verifying ID token: {id_token[:50]}...")
            # Проверяем Google ID Token
            decoded_token = auth.verify_id_token(id_token)
            logging.debug(f"Decoded token: {decoded_token}")
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            full_name = decoded_token.get('name', '')

            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()

            if not user_doc.exists:
                logging.info(f"User {uid} not found in Firestore, creating new user")
                user_data = {
                    "email": email,
                    "full_name": full_name,
                    "role": "student",
                    "created_at": firestore_module.SERVER_TIMESTAMP,
                    "phone": None,
                    "location": None,
                    "bio": None,
                    "avatar": None,
                    "whatsapp": None,
                    "instagram": None,
                    "telegram": None
                }
                user_ref.set(user_data)
                logging.info(f"User {uid} created in Firestore with email: {email}")
            else:
                logging.info(f"User {uid} already exists in Firestore with email: {email}")

            return {"user_id": uid, "message": "Google login successful"}
        except auth.InvalidIdTokenError as e:
            logging.error(f"Invalid ID token error: {str(e)}")
            # Декодируем payload токена для отладки
            try:
                import base64
                import json
                payload = id_token.split('.')[1]
                decoded_payload = json.loads(base64.urlsafe_b64decode(payload + '==' * (4 - len(payload) % 4)).decode('utf-8'))
                logging.error(f"Token payload: {decoded_payload}")
            except Exception as decode_error:
                logging.error(f"Failed to decode token payload: {str(decode_error)}")
            return {"error": f"Invalid Google ID token: {str(e)}"}
        except Exception as e:
            logging.error(f"Unexpected error during Google login: {str(e)}")
            return {"error": str(e)}

    def google_login(self, id_token: str) -> Dict[str, str]:
        try:
            # Проверяем Google ID Token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            full_name = decoded_token.get('name', '')

            # Проверяем, существует ли пользователь в Firestore
            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()

            if not user_doc.exists:
                # Если пользователь не существует, создаём его
                user_data = {
                    "email": email,
                    "full_name": full_name,
                    "role": "student",
                    "created_at": firestore_module.SERVER_TIMESTAMP,
                    "phone": None,
                    "location": None,
                    "bio": None,
                    "avatar": None,
                    "whatsapp": None,
                    "instagram": None,
                    "telegram": None
                }
                user_ref.set(user_data)

            return {"user_id": uid, "message": "Google login successful"}
        except auth.InvalidIdTokenError:
            return {"error": "Invalid Google ID token"}
        except Exception as e:
            return {"error": str(e)}

    def update_user_profile(self, user_id: str, profile_data: Dict) -> Dict[str, str]:
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            if not user_doc.exists:
                return {"error": "User not found"}

            allowed_fields = {"phone", "location", "bio", "avatar", "whatsapp", "instagram", "telegram"}
            update_data = {key: profile_data.get(key) for key in allowed_fields if key in profile_data}

            if not update_data:
                return {"error": "No valid fields to update"}

            user_ref.update(update_data)
            return {"message": "Profile updated successfully"}
        except Exception as e:
            return {"error": str(e)}

    def login_user(self, email: str, password: str) -> Dict[str, Optional[str]]:
        try:
            from firebase_admin import auth
            user = auth.get_user_by_email(email)
            return {"user_id": user.uid, "message": "User found, proceed with client-side login"}
        except auth.UserNotFoundError:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}

    def get_user(self, user_id: str) -> Dict[str, Optional[Dict]]:
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}