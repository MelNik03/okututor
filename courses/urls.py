from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_course, name='create_course'),
    path('list/', views.course_list, name='course_list'),
    path('all/', views.all_courses, name='all_courses'),
    path('detail/<int:course_id>/', views.course_detail, name='course_detail'),
]