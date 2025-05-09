import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Импорт контроллеров и конфигурации Firebase
from users.user_controller import UserController
from courses.course_controller import CourseController

# Загружаем переменные окружения из .env (если нужно)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Настраиваем CORS, разрешая запросы с вашего фронтенда
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})

# Инициализация контроллеров
user_controller = UserController()
course_controller = CourseController()

# Эндпоинты для пользователей
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    logging.debug(f"Register request data: {data}")
    email = data.get("email")
    password = data.get("password")
    repeat_password = data.get("repeat_password")
    full_name = data.get("full_name")
user_id = data.get("user_id")  # Добавляем user_id

if not all([email, password, repeat_password, full_name, user_id]):
    logging.error("Missing required fields in register request")
    return jsonify({"error": "Missing required fields"}), 400

result = user_controller.register_user(email, password, repeat_password, full_name, user_id)
logging.debug(f"Register result: {result}")
return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("id_token")
    if not id_token:
        return jsonify({"error": "Missing ID token"}), 400
    result = user_controller.google_login(id_token)
    return jsonify(result), 200 if "error" not in result else 400

# Эндпоинты для авторизации
@app.route("/api/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    logging.debug(f"Google login request data: {data}")

    # Проверяем наличие id_token
    id_token = data.get("id_token")
    if not id_token:
        logging.error("Missing ID token in google-login request")
        return jsonify({"error": "Missing ID token"}), 400

    # Проверяем, что id_token — это строка и выглядит как JWT (содержит точки)
    if not isinstance(id_token, str) or '.' not in id_token:
        logging.error("Invalid ID token format in google-login request")
        return jsonify({"error": "Invalid ID token format"}), 400

    try:
        result = user_controller.google_login(id_token)
        logging.debug(f"Google login result: {result}")
        # Уточняем код ответа в зависимости от типа ошибки
        if "error" in result:
            if "not found" in result["error"].lower():
                return jsonify(result), 404
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Unexpected error in google-login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    logging.debug(f"Login request data: {data}")

    # Проверяем наличие обязательных полей
    email = data.get("email")
    password = data.get("password")
    missing_fields = []
    if not email:
        missing_fields.append("email")
    if not password:
        missing_fields.append("password")
    if missing_fields:
        logging.error(f"Missing required fields in login request: {', '.join(missing_fields)}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Проверяем формат email
    import re
    email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if not email_pattern.match(email):
        logging.error("Invalid email format in login request")
        return jsonify({"error": "Invalid email format"}), 400

    try:
        result = user_controller.login_user(email, password)
        logging.debug(f"Login result: {result}")
        # Уточняем код ответа в зависимости от типа ошибки
        if "error" in result:
            if "not found" in result["error"].lower():
                return jsonify(result), 404
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Unexpected error in login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/user/<user_id>", methods=["GET"])
def get_user(user_id):
    logging.debug(f"Get user request for user_id: {user_id}")
    result = user_controller.get_user(user_id)
    logging.debug(f"Get user result: {result}")
    return jsonify(result), 200 if "error" not in result else 404

@app.route("/api/user/<user_id>/profile", methods=["PUT"])
def update_user_profile(user_id):
    data = request.get_json()
    logging.debug(f"Update user profile request for user_id: {user_id}, data: {data}")
    if not data:
        logging.error("No data provided in update user profile request")
        return jsonify({"error": "No data provided"}), 400
    result = user_controller.update_user_profile(user_id, data)
    logging.debug(f"Update user profile result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

# Эндпоинты для курсов
@app.route("/api/courses", methods=["POST"])
def create_course():
    data = request.get_json()
    logging.debug(f"Create course request data: {data}")
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    days = data.get("days")
    specific_days = data.get("specific_days")
    group_size = data.get("group_size")
    location_type = data.get("location_type")
    experience = data.get("experience")
    price_per_hour = data.get("price_per_hour")

    # Проверяем обязательные поля
    if not all([user_id, title, description, days, group_size, location_type, experience, price_per_hour]):
        logging.error("Missing required fields in create course request")
        return jsonify({"error": "Missing required fields"}), 400

    # Проверяем типы числовых полей
    try:
        experience = int(experience)
        price_per_hour = float(price_per_hour)
    except (ValueError, TypeError):
        logging.error("Invalid type for experience or price_per_hour")
        return jsonify({"error": "Experience must be an integer and price_per_hour must be a number"}), 400

    result = course_controller.create_course(user_id, title, description, days, specific_days, 
                                            group_size, location_type, experience, price_per_hour)
    logging.debug(f"Create course result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/courses/<course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json()
    logging.debug(f"Update course request for course_id: {course_id}, data: {data}")
    user_id = data.get("user_id")
    if not user_id:
        logging.error("Missing user_id in update course request")
        return jsonify({"error": "Missing user_id"}), 400
    if not data:
        logging.error("No data provided in update course request")
        return jsonify({"error": "No data provided"}), 400
    result = course_controller.update_course(course_id, user_id, data)
    logging.debug(f"Update course result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/courses/<teacher_id>", methods=["GET"])
def get_courses(teacher_id):
    logging.debug(f"Get courses request for teacher_id: {teacher_id}")
    result = course_controller.get_courses_by_teacher(teacher_id)
    logging.debug(f"Get courses result: {result}")
    return jsonify(result), 200

@app.route("/api/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    logging.debug(f"Delete course request for course_id: {course_id}")
    result = course_controller.delete_course(course_id)
    logging.debug(f"Delete course result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/courses/<course_id>/reviews", methods=["POST"])
def create_review(course_id):
    data = request.get_json()
    logging.debug(f"Create review request for course_id: {course_id}, data: {data}")
    student_id = data.get("student_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not all([student_id, rating, comment]):
        logging.error("Missing required fields in create review request")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        logging.error("Invalid type for rating in create review request")
        return jsonify({"error": "Rating must be an integer"}), 400

    result = course_controller.create_review(course_id, student_id, rating, comment)
    logging.debug(f"Create review result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/courses/<course_id>/reviews", methods=["GET"])
def get_reviews(course_id):
    logging.debug(f"Get reviews request for course_id: {course_id}")
    result = course_controller.get_reviews(course_id)
    logging.debug(f"Get reviews result: {result}")
    return jsonify(result), 200

@app.route("/api/courses/<course_id>/reviews/<review_id>", methods=["DELETE"])
def delete_review(course_id, review_id):
    data = request.get_json() or {}
    logging.debug(f"Delete review request for course_id: {course_id}, review_id: {review_id}, data: {data}")
    student_id = data.get("student_id")
    if not student_id:
        logging.error("Missing student_id in delete review request")
        return jsonify({"error": "Missing student_id"}), 400
    result = course_controller.delete_review(course_id, review_id, student_id)
    logging.debug(f"Delete review result: {result}")
    return jsonify(result), 200 if "error" not in result else 400

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)