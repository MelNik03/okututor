from django.http import JsonResponse
from okututor_backend.firebase_config import db
import json
from firebase_admin import firestore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .zoom import create_zoom_meeting
from datetime import datetime, timedelta

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_meeting(request):
    topic = request.data.get("topic", "Lesson on Okututor")
    start_time = datetime.utcnow() + timedelta(minutes=5)  # 5 минут от сейчас
    iso_start_time = start_time.isoformat() + "Z"  # ISO 8601 формат
    meeting = create_zoom_meeting(topic, iso_start_time)
    return Response({
        "join_url": meeting["join_url"],
        "start_url": meeting["start_url"],
        "meeting_id": meeting["id"]
    })


def create_course(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description")
            user_id = data.get("user_id")

            if not title or not description or not user_id:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Проверяем, что пользователь существует
            user_ref = db.collection("users").document(user_id).get()
            if not user_ref.exists:
                return JsonResponse({"error": "User not found"}, status=404)

            # Создаём курс
            course_data = {
                "title": title,
                "description": description,
                "user_id": user_id,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            course_ref = db.collection("courses").add(course_data)[1]
            return JsonResponse({"message": "Course created", "course_id": course_ref.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_courses(request):
    if request.method == "GET":
        try:
            courses = db.collection("courses").stream()
            courses_list = [
                {"id": course.id, **course.to_dict()} for course in courses
            ]
            return JsonResponse({"courses": courses_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def create_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_id = data.get("course_id")
            user_id = data.get("user_id")
            rating = data.get("rating")
            comment = data.get("comment")

            if not course_id or not user_id or not rating or not comment:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Проверяем, что курс и пользователь существуют
            course_ref = db.collection("courses").document(course_id).get()
            if not course_ref.exists:
                return JsonResponse({"error": "Course not found"}, status=404)
            user_ref = db.collection("users").document(user_id).get()
            if not user_ref.exists:
                return JsonResponse({"error": "User not found"}, status=404)

            # Создаём отзыв
            review_data = {
                "course_id": course_id,
                "user_id": user_id,
                "rating": rating,
                "comment": comment,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            review_ref = db.collection("reviews").add(review_data)[1]
            return JsonResponse({"message": "Review created", "review_id": review_ref.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)