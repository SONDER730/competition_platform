# apps/oAuth/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
    )
    email = models.EmailField(unique=True)  # 设置 email 为唯一
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    teacher_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username
