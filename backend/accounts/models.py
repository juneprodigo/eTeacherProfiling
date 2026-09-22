"""
accounts/models.py — Custom User Model with Role-Based Access
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        HR = 'hr', 'HR Officer'
        TEACHER = 'teacher', 'Teacher'

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TEACHER)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'

    def get_full_name(self):
        return f'{self.last_name}, {self.first_name}'.strip()

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hr(self):
        return self.role == self.Role.HR

    @property
    def is_teacher_role(self):
        return self.role == self.Role.TEACHER
