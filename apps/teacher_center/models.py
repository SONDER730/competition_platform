from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    name = models.CharField(max_length=100, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    teacher_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(max_length=254)

    class Meta:
        ordering = ['teacher_id']

    def __str__(self):
        return f"{self.teacher_id} - {self.name or '未设置姓名'}"

    def save(self, *args, **kwargs):
        # 只在创建新记录时同步工号
        if not self.pk and not self.teacher_id and self.user:
            self.teacher_id = self.user.teacher_id
        super().save(*args, **kwargs)