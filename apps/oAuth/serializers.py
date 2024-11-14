# apps/oAuth/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

CustomUser = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True
    )
    student_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    teacher_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password',
            'password_confirmation',
            'role',
            'student_id',
            'teacher_id'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})

        role = attrs.get('role')
        if role == 'student':
            if not attrs.get('student_id'):
                raise serializers.ValidationError({"student_id": "学生必须填写学号"})
        elif role == 'teacher':
            if not attrs.get('teacher_id'):
                raise serializers.ValidationError({"teacher_id": "教师必须填写工号"})
        else:
            raise serializers.ValidationError({"role": "无效的身份选择"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        base_username = validated_data.pop('username')

        # 生成唯一的 username
        username = base_username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        try:
            # 仅包含角色对应的 ID
            if validated_data['role'] == 'student':
                validated_data.pop('teacher_id', None)
            elif validated_data['role'] == 'teacher':
                validated_data.pop('student_id', None)

            user = CustomUser(username=username, **validated_data)
            user.set_password(password)
            user.save()
        except IntegrityError:
            raise serializers.ValidationError({"detail": "用户名、邮箱或学号/工号已存在。"})

        return user


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[('student', '学生'), ('teacher', '教师')],
        required=True
    )
    student_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    teacher_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate(self, attrs):
        role = attrs.get('role')
        if role == 'student':
            if not attrs.get('student_id'):
                raise serializers.ValidationError({"student_id": "学生登录需要提供学号"})
        elif role == 'teacher':
            if not attrs.get('teacher_id'):
                raise serializers.ValidationError({"teacher_id": "教师登录需要提供工号"})
        else:
            raise serializers.ValidationError({"role": "无效的身份选择"})
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'role', 'student_id', 'teacher_id', 'student_profile')