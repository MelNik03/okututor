from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)  # Например, "10 недель"
    level = models.CharField(max_length=50, choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
