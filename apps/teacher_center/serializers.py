from rest_framework import serializers
from .models import TeacherProfile

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ('name', 'department', 'teacher_id', 'phone', 'email')
        read_only_fields = ('teacher_id',)  # 只有工号不允许修改
        extra_kwargs = {
            'name': {'required': False},
            'department': {'required': False},
            'phone': {'required': False},
            'email': {'required': False},
        }