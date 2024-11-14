# competition_application/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionApplicationViewSet, UploadFilesView, DownloadFileView

router = DefaultRouter()
router.register('', CompetitionApplicationViewSet, basename='competition-application')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/upload_files/', UploadFilesView.as_view(), name='upload-files'),
    path('<int:pk>/download/<str:file_type>/', DownloadFileView.as_view(), name='download-file'),
]