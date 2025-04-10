from okututor_backend.firebase_config import db, firestore_module
from typing import Dict, List, Optional

class CourseController:
    def create_course(self, user_id: str, title: str, description: str, schedule: List[str], group_size: int) -> Dict[str, str]:
        try:
            course_data = {
                "teacher_id": user_id,
                "title": title,
                "description": description,
                "schedule": schedule,
                "group_size": group_size,
                "created_at": firestore_module.SERVER_TIMESTAMP  # Используем firestore_module
            }
            course_ref = db.collection("courses").document()
            course_ref.set(course_data)
            return {"course_id": course_ref.id, "message": "Course created successfully"}
        except Exception as e:
            return {"error": str(e)}

    def get_courses_by_teacher(self, teacher_id: str) -> List[Dict]:
        try:
            courses_ref = db.collection("courses").where("teacher_id", "==", teacher_id).stream()
            courses = [{"id": course.id, **course.to_dict()} for course in courses_ref]
            return courses
        except Exception as e:
            return [{"error": str(e)}]

    def delete_course(self, course_id: str) -> Dict[str, str]:
        try:
            db.collection("courses").document(course_id).delete()
            return {"message": "Course deleted successfully"}
        except Exception as e:
            return {"error": str(e)}