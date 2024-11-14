# apps/student_center/apps.py

from django.apps import AppConfig

class StudentCenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.student_center'

    def ready(self):
        import apps.student_center.signals  # 确保导入信号
