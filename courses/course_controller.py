from okututor_backend.firebase_config import db, firestore_module
from typing import Dict, List, Optional
import re

# Простая реализация filter_bad_words (можно заменить на более сложную логику)
def filter_bad_words(text: str) -> str:
    bad_words = ['badword1', 'badword2']  # Замени на свой список нежелательных слов
    for word in bad_words:
        text = re.sub(r'\b' + word + r'\b', '***', text, flags=re.IGNORECASE)
    return text

class CourseController:
    # Определяем возможные значения для полей
    DAYS_CHOICES = {
        'weekdays': 'Будни',
        'weekends': 'Выходные',
        'specific': 'Конкретные дни'
    }
    
    GROUP_SIZE_CHOICES = {
        'individual': 'Лично с учеником',
        'group': 'Групповое занятие'
    }
    
    LOCATION_TYPE_CHOICES = {
        'offline': 'Offline',
        'online': 'Online'
    }

    def create_course(self, user_id: str, title: str, description: str, days: str, specific_days: Optional[str], 
                     group_size: str, location_type: str, experience: int, price_per_hour: float) -> Dict[str, str]:
        try:
            # Валидация входных данных
            if days not in self.DAYS_CHOICES:
                return {"error": f"Invalid days value. Must be one of {list(self.DAYS_CHOICES.keys())}"}
            if group_size not in self.GROUP_SIZE_CHOICES:
                return {"error": f"Invalid group_size value. Must be one of {list(self.GROUP_SIZE_CHOICES.keys())}"}
            if location_type not in self.LOCATION_TYPE_CHOICES:
                return {"error": f"Invalid location_type value. Must be one of {list(self.LOCATION_TYPE_CHOICES.keys())}"}
            if experience < 0:
                return {"error": "Experience must be a non-negative integer"}
            if price_per_hour < 0:
                return {"error": "Price per hour must be a non-negative number"}

            # Формируем данные курса
            course_data = {
                "teacher_id": user_id,
                "title": title,
                "description": description,
                "days": days,
                "specific_days": specific_days if days == "specific" else None,
                "group_size": group_size,
                "location_type": location_type,
                "experience": experience,
                "price_per_hour": float(price_per_hour),
                "created_at": firestore_module.SERVER_TIMESTAMP
            }
            
            # Сохраняем курс в Firestore
            course_ref = db.collection("courses").document()
            course_ref.set(course_data)
            return {"course_id": course_ref.id, "message": "Course created successfully"}
        except Exception as e:
            return {"error": str(e)}

    def update_course(self, course_id: str, user_id: str, update_data: Dict) -> Dict[str, str]:
        try:
            # Проверяем, существует ли курс
            course_ref = db.collection("courses").document(course_id)
            course_doc = course_ref.get()
            if not course_doc.exists:
                return {"error": "Course not found"}

            # Проверяем, является ли пользователь создателем курса
            course_data = course_doc.to_dict()
            if course_data["teacher_id"] != user_id:
                return {"error": "You are not authorized to edit this course"}

            # Разрешённые поля для обновления
            allowed_fields = {
                "title", "description", "days", "specific_days", 
                "group_size", "location_type", "experience", "price_per_hour"
            }
            update_dict = {key: update_data.get(key) for key in allowed_fields if key in update_data}

            # Валидация обновляемых полей
            if "days" in update_dict and update_dict["days"] not in self.DAYS_CHOICES:
                return {"error": f"Invalid days value. Must be one of {list(self.DAYS_CHOICES.keys())}"}
            if "group_size" in update_dict and update_dict["group_size"] not in self.GROUP_SIZE_CHOICES:
                return {"error": f"Invalid group_size value. Must be one of {list(self.GROUP_SIZE_CHOICES.keys())}"}
            if "location_type" in update_dict and update_dict["location_type"] not in self.LOCATION_TYPE_CHOICES:
                return {"error": f"Invalid location_type value. Must be one of {list(self.LOCATION_TYPE_CHOICES.keys())}"}
            if "experience" in update_dict and update_dict["experience"] < 0:
                return {"error": "Experience must be a non-negative integer"}
            if "price_per_hour" in update_dict and update_dict["price_per_hour"] < 0:
                return {"error": "Price per hour must be a non-negative number"}

            # Если обновляется days, обрабатываем specific_days
            if "days" in update_dict:
                if update_dict["days"] != "specific":
                    update_dict["specific_days"] = None
                elif "specific_days" not in update_dict:
                    update_dict["specific_days"] = None

            # Приводим price_per_hour к float, если он обновляется
            if "price_per_hour" in update_dict:
                update_dict["price_per_hour"] = float(update_dict["price_per_hour"])

            if not update_dict:
                return {"error": "No valid fields to update"}

            # Обновляем курс
            course_ref.update(update_dict)
            return {"message": "Course updated successfully"}
        except Exception as e:
            return {"error": str(e)}

    def get_courses_by_teacher(self, teacher_id: str) -> List[Dict]:
        try:
            # Получаем курсы преподавателя
            courses_ref = db.collection("courses").where("teacher_id", "==", teacher_id).stream()
            courses = [{"id": course.id, **course.to_dict()} for course in courses_ref]
            
            # Для каждого курса вычисляем среднюю оценку
            for course in courses:
                course["average_rating"] = self._get_average_rating(course["id"])
            
            return courses
        except Exception as e:
            return [{"error": str(e)}]

    def delete_course(self, course_id: str) -> Dict[str, str]:
        try:
            # Удаляем курс
            db.collection("courses").document(course_id).delete()
            # Удаляем связанные отзывы (подколлекцию reviews)
            reviews_ref = db.collection("courses").document(course_id).collection("reviews")
            for review in reviews_ref.stream():
                reviews_ref.document(review.id).delete()
            return {"message": "Course deleted successfully"}
        except Exception as e:
            return {"error": str(e)}

    def create_review(self, course_id: str, student_id: str, rating: int, comment: str) -> Dict[str, str]:
        try:
            # Проверяем, существует ли курс
            course_ref = db.collection("courses").document(course_id)
            if not course_ref.get().exists:
                return {"error": "Course not found"}

            # Проверяем, оставлял ли студент уже отзыв на этот курс
            existing_review = db.collection("courses").document(course_id).collection("reviews")\
                .where("student_id", "==", student_id).limit(1).stream()
            if next(existing_review, None):
                return {"error": "Student has already reviewed this course"}

            # Валидация рейтинга
            if not (1 <= rating <= 5):
                return {"error": "Rating must be between 1 and 5"}

            # Фильтруем комментарий
            filtered_comment = filter_bad_words(comment)

            # Формируем данные отзыва
            review_data = {
                "course_id": course_id,
                "student_id": student_id,
                "rating": rating,
                "comment": filtered_comment,
                "created_at": firestore_module.SERVER_TIMESTAMP
            }

            # Сохраняем отзыв в подколлекции reviews курса
            review_ref = db.collection("courses").document(course_id).collection("reviews").document()
            review_ref.set(review_data)
            return {"review_id": review_ref.id, "message": "Review created successfully"}
        except Exception as e:
            return {"error": str(e)}

    def get_reviews(self, course_id: str) -> List[Dict]:
        try:
            # Проверяем, существует ли курс
            if not db.collection("courses").document(course_id).get().exists:
                return [{"error": "Course not found"}]

            # Получаем отзывы
            reviews_ref = db.collection("courses").document(course_id).collection("reviews").stream()
            reviews = [{"id": review.id, **review.to_dict()} for review in reviews_ref]
            return reviews
        except Exception as e:
            return [{"error": str(e)}]

    def delete_review(self, course_id: str, review_id: str, student_id: str) -> Dict[str, str]:
        try:
            # Проверяем, существует ли курс
            course_ref = db.collection("courses").document(course_id)
            if not course_ref.get().exists:
                return {"error": "Course not found"}

            # Проверяем, существует ли отзыв
            review_ref = db.collection("courses").document(course_id).collection("reviews").document(review_id)
            review_doc = review_ref.get()
            if not review_doc.exists:
                return {"error": "Review not found"}

            # Проверяем, является ли студент автором отзыва
            review_data = review_doc.to_dict()
            if review_data["student_id"] != student_id:
                return {"error": "You are not authorized to delete this review"}

            # Удаляем отзыв
            review_ref.delete()
            return {"message": "Review deleted successfully"}
        except Exception as e:
            return {"error": str(e)}

    def _get_average_rating(self, course_id: str) -> Optional[float]:
        """
        Вычисляет среднюю оценку курса на основе отзывов.
        Возвращает None, если отзывов нет.
        """
        try:
            reviews_ref = db.collection("courses").document(course_id).collection("reviews").stream()
            ratings = [review.to_dict().get("rating") for review in reviews_ref]
            if ratings:
                return round(sum(ratings) / len(ratings), 1)
            return None
        except Exception as e:
            return None