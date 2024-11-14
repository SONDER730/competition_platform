# apps/student_center/models.py

from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100, blank=True, null=True)  # 可为空，等待用户填写
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254,null=True)  # 始终在注册时自动填入
    student_id = models.CharField(max_length=20, unique=True,null=True)  # 始终在注册时自动填入

    def __str__(self):
        return f"{self.student_id}'s profile"