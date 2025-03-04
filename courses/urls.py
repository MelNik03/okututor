from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet
from .teachers.views import TeacherListView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
]
