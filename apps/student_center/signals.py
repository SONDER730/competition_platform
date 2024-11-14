# apps/student_center/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        StudentProfile.objects.create(
            user=instance,
            name=instance.username,  # 使用 username 代替 name
            school=instance.school if hasattr(instance, 'school') else '',
            major=instance.major if hasattr(instance, 'major') else '',
            grade=instance.grade if hasattr(instance, 'grade') else '',
            gender=instance.gender if hasattr(instance, 'gender') else 'male',
            phone=instance.phone if hasattr(instance, 'phone') else '',
            email=instance.email if hasattr(instance, 'email') else 'example@example.com',  # 映射 email
            student_id=instance.student_id if hasattr(instance, 'student_id') else '000000',  # 映射 student_id
        )

@receiver(post_save, sender=CustomUser)
def save_student_profile(sender, instance, **kwargs):
    if instance.role == 'student':
        try:
            instance.student_profile.save()
        except StudentProfile.DoesNotExist:
            StudentProfile.objects.create(
                user=instance,
                name=instance.username,
                school=instance.school if hasattr(instance, 'school') else '',
                major=instance.major if hasattr(instance, 'major') else '',
                grade=instance.grade if hasattr(instance, 'grade') else '',
                gender=instance.gender if hasattr(instance, 'gender') else 'male',
                phone=instance.phone if hasattr(instance, 'phone') else '',
                email=instance.email if hasattr(instance, 'email') else 'example@example.com',
                student_id=instance.student_id if hasattr(instance, 'student_id') else '000000',
            )
