# permissions.py
from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    自定义权限类,确保用户是教师角色
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'