from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, fullname, password=None):
        if not email:
            raise ValueError("Email обязателен")
        if not fullname:
            raise ValueError("Полное имя обязательно")

        user = self.model(email=self.normalize_email(email), fullname=fullname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None):
        user = self.create_user(email, fullname, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    fullname = models.CharField(max_length=255, verbose_name="Полное имя")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Местоположение")
    bio = models.TextField(blank=True, null=True, verbose_name="О себе")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    instagram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram")
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    def __str__(self):
        return self.fullname