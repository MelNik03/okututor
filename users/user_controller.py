from okututor_backend.firebase_config import db, auth_client, firestore_module
from firebase_admin import auth
from typing import Dict, Optional

class UserController:
    def register_user(self, email: str, password: str, full_name: str) -> Dict[str, str]:
        try:
            user = auth_client.create_user(
                email=email,
                password=password,
                display_name=full_name
            )
            user_data = {
                "email": email,
                "full_name": full_name,
                "role": "student",
                "created_at": firestore_module.SERVER_TIMESTAMP  # Используем firestore_module
            }
            db.collection("users").document(user.uid).set(user_data)
            return {"user_id": user.uid, "message": "User registered successfully"}
        except auth.EmailAlreadyExistsError:
            return {"error": "Email already exists"}
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