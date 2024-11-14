#competitions/views.py

from rest_framework import viewsets, filters
from .models import Competition
from .serializers import CompetitionSerializer
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [AllowAny]  # 确保允许任何人访问
    authentication_classes = []
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

@csrf_exempt
def search_competitions(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)  # 如果没有查询参数，返回空列表
    competitions = Competition.objects.filter(name__icontains=query)  # 按名称搜索
    competition_list = [{"id": comp.id, "name": comp.name} for comp in competitions]
    return JsonResponse(competition_list, safe=False)