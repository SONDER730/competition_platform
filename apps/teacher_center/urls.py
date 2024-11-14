# apps/teacher_center/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherProfileView, ApproveCompetitionApplicationView, search_teachers,TeacherAssignedApplicationsView

router = DefaultRouter()
# 注册 TeacherProfileViewSet，如果有多个视图，推荐使用 ViewSet
# 由于 TeacherProfileView 是 RetrieveUpdateAPIView，单独添加路径
# 这里保持原有路径

urlpatterns = [
    path('updateProfile/', TeacherProfileView.as_view(), name='teacher-update-profile'),
    path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('approve-competition-application/<int:pk>/', ApproveCompetitionApplicationView.as_view(), name='approve-competition-application'),
    path('', include(router.urls)),  # 如果有其他视图，可以继续注册
    path('search/', search_teachers, name='teacher-search'),
    path('applications/', TeacherAssignedApplicationsView.as_view(), name='teacher-applications'),
]
