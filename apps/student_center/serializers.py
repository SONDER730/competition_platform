# apps/student_center/serializers.py

from rest_framework import serializers
from .models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('name', 'school', 'major', 'grade', 'gender', 'phone', 'email', 'student_id')
        extra_kwargs = {
            'name': {'required': True},  # 可以为空，用户后续填写
            'school': {'required': True},
            'major': {'required': True},
            'grade': {'required': True},
            'gender': {'required': True},
            'phone': {'required': True},
            'email': {'required': True},
            'student_id': {'required': False},
        }
