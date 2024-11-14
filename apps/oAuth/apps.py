# apps/oAuth/apps.py

from django.apps import AppConfig

class OauthConfig(AppConfig):
    name = 'apps.oAuth'
    label = 'oAuth'  # 确保这个标签在整个项目中是唯一的