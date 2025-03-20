from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from .forms import CourseForm, ReviewForm

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def course_list(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'courses/course_list.html', {'courses': courses})

def all_courses(request):
    courses = Course.objects.all()
    return render(request, 'courses/all_courses.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    reviews = course.reviews.all()
    user_review = reviews.filter(student=request.user).first()  # Проверяем, оставил ли пользователь отзыв

    # Проверяем, является ли пользователь владельцем курса
    if course.teacher == request.user:
        messages.error(request, "Вы не можете оставить отзыв на свой собственный курс.")
        form = None
    else:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=user_review)  # Если отзыв есть, редактируем его
            if form.is_valid():
                review = form.save(commit=False)
                if not user_review:  # Если это новый отзыв
                    review.course = course
                    review.student = request.user
                review.save()
                messages.success(request, "Отзыв успешно сохранён!")
                return redirect('course_detail', course_id=course.id)
        else:
            form = ReviewForm(instance=user_review)  # Заполняем форму текущими данными отзыва, если он есть

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    })