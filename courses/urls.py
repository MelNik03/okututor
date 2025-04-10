from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_courses, name='get_courses'),
    path('create/', views.create_course, name='create_course'),
    path('reviews/create/', views.create_review, name='create_review'),
]