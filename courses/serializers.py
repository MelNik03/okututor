from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Course
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
