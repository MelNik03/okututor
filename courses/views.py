from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Course
from .serializers import CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    # Добавим поиск и фильтрацию
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "teacher__username"]
    ordering_fields = ["price", "title"]
