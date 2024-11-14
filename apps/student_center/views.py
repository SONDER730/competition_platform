# apps/student_center/views.py

from rest_framework import generics, permissions, status
from .models import StudentProfile
from .serializers import StudentProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.competition_application.serializers import CompetitionApplicationSerializer
class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    获取和更新学生个人资料。
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'name': '',
                'school': '',
                'major': '',
                'grade': '',
                'gender': 'male',
                'phone': '',
                'email': self.request.user.email,  # 映射 email
                'student_id': self.request.user.student_id,
            }
        )
        return profile
