import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

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

# Инициализация контроллеров
user_controller = UserController()
course_controller = CourseController()

# Эндпоинты для пользователей
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    if not email or not password or not full_name:
        return jsonify({"error": "Missing required fields"}), 400
    result = user_controller.register_user(email, password, full_name)
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    result = user_controller.login_user(email, password)
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/user/<user_id>", methods=["GET"])
def get_user(user_id):
    result = user_controller.get_user(user_id)
    return jsonify(result), 200 if "error" not in result else 404

# Эндпоинты для курсов
@app.route("/api/courses", methods=["POST"])
def create_course():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    schedule = data.get("schedule")
    group_size = data.get("group_size")
    if not all([user_id, title, description, schedule, group_size]):
        return jsonify({"error": "Missing required fields"}), 400
    result = course_controller.create_course(user_id, title, description, schedule, group_size)
    return jsonify(result), 200 if "error" not in result else 400

@app.route("/api/courses/<teacher_id>", methods=["GET"])
def get_courses(teacher_id):
    result = course_controller.get_courses_by_teacher(teacher_id)
    return jsonify(result), 200

@app.route("/api/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    result = course_controller.delete_course(course_id)
    return jsonify(result), 200 if "error" not in result else 400

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)