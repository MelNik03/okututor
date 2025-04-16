from okututor_backend.firebase_config import db, auth_client, firestore_module
from firebase_admin import auth
from typing import Dict, Optional

class UserController:
    def register_user(self, email: str, password: str, repeat_password: str, full_name: str) -> Dict[str, str]:
        try:
            if password != repeat_password:
                return {"error": "Passwords do not match"}

            user = auth_client.create_user(
                email=email,
                password=password,
                display_name=full_name
            )
            
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
            db.collection("users").document(user.uid).set(user_data)
            return {"user_id": user.uid, "message": "User registered successfully"}
        except auth.EmailAlreadyExistsError:
            return {"error": "Email already exists"}
        except Exception as e:
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
            user = auth_client.get_user_by_email(email)
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