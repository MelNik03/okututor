from django.db import models
from django.conf import settings
from .utils import filter_bad_words

class Course(models.Model):
    DAYS_CHOICES = (
        ('weekdays', 'Будни'),
        ('weekends', 'Выходные'),
        ('specific', 'Конкретные дни'),
    )
    
    GROUP_SIZE_CHOICES = (
        ('individual', 'Лично с учеником'),
        ('group', 'Групповое занятие'),
    )
    
    LOCATION_TYPE_CHOICES = (
        ('offline', 'Offline'),
        ('online', 'Online'),
    )

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Преподаватель")
    title = models.CharField(max_length=255, verbose_name="Название курса")
    days = models.CharField(max_length=10, choices=DAYS_CHOICES, default='weekdays', verbose_name="Дни недели")
    specific_days = models.CharField(max_length=255, blank=True, null=True, verbose_name="Конкретные дни (если выбрано)")
    group_size = models.CharField(max_length=10, choices=GROUP_SIZE_CHOICES, default='individual', verbose_name="Размер группы")
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES, default='online', verbose_name="Место проведения")
    description = models.TextField(verbose_name="Описание")
    experience = models.PositiveIntegerField(default=0, verbose_name="Стаж работы (лет)")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена за час (KGS)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def get_average_rating(self):
        """
        Вычисляет среднюю оценку курса на основе отзывов.
        Возвращает None, если отзывов нет.
        """
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)  # Округляем до 1 знака после запятой
        return None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

class Review(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='reviews', verbose_name="Курс")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Ученик")
    rating = models.PositiveIntegerField(verbose_name="Оценка (1-5)", choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        # Фильтруем комментарий перед сохранением
        self.comment = filter_bad_words(self.comment)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отзыв от {self.student.fullname} на {self.course.title}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('course', 'student')