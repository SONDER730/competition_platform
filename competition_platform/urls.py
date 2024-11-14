# competition_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/competitions/', include('apps.competitions.urls')),  # 竞赛相关的 API 路由
    path('api/auth/', include('apps.oAuth.urls')),  # 用户认证相关的 API 路由
    path('api/student/', include('apps.student_center.urls')),  # 学生中心的 API 路由
    path('api/teacher/', include('apps.teacher_center.urls')),
    path('api/competition_applications/', include('apps.competition_application.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # 如果有静态文件和媒体文件的配置，确保正确添加
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
