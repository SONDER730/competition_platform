from django.apps import AppConfig

class TeacherCenterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.teacher_center"

    def ready(self):
        import apps.teacher_center.signals  # 注册信号