# apps/competitions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, search_competitions

router = DefaultRouter()
router.register(r'', CompetitionViewSet, basename='competition')

urlpatterns = [
    path('search/', search_competitions, name='search_competitions'),
    path('', include(router.urls)),
]
