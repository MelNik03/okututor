from django.db import models
from django.conf import settings

class Course(models.Model):
    # Выбор для дней недели
    DAYS_CHOICES = (
        ('weekdays', 'Будни'),
        ('weekends', 'Выходные'),
        ('specific', 'Конкретные дни'),
    )
    
    # Выбор для размера группы
    GROUP_SIZE_CHOICES = (
        ('individual', 'Лично с учеником'),
        ('group', 'Групповое занятие'),
    )
    
    # Выбор для места проведения
    LOCATION_TYPE_CHOICES = (
        ('offline', 'Offline'),
        ('online', 'Online'),
    )

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Преподаватель")
    title = models.CharField(max_length=255, verbose_name="Название курса")
    days = models.CharField(max_length=10, choices=DAYS_CHOICES, verbose_name="Дни недели")
    specific_days = models.CharField(max_length=255, blank=True, null=True, verbose_name="Конкретные дни (если выбрано)")
    group_size = models.CharField(max_length=10, choices=GROUP_SIZE_CHOICES, verbose_name="Размер группы")
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES, verbose_name="Место проведения")
    description = models.TextField(verbose_name="Описание")
    experience = models.PositiveIntegerField(verbose_name="Стаж работы (лет)")  # В годах
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за час (KGS)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"