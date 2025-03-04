from django.contrib.auth import get_user_model
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from courses.serializers import TeacherSerializer  # Обновленный импорт

User = get_user_model()

class TeacherListView(generics.ListAPIView):
    queryset = User.objects.filter(is_staff=True)  # Фильтруем преподавателей
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    # Фильтрация и поиск
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "first_name"]
