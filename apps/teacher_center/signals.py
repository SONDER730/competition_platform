# apps/teacher_center/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import TeacherProfile

CustomUser = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_or_update_teacher_profile(sender, instance, created, **kwargs):
    """
    当创建新用户时，如果是教师角色则自动创建对应的教师资料
    """
    if instance.role == 'teacher':
        if created:
            TeacherProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'name': instance.username,
                    'department': '',
                    'teacher_id': instance.teacher_id,
                    'phone': '',
                    'email': instance.email,
                }
            )
        else:
            try:
                profile = TeacherProfile.objects.get(user=instance)
                profile.email = instance.email
                profile.teacher_id = instance.teacher_id
                profile.save()
            except TeacherProfile.DoesNotExist:
                pass