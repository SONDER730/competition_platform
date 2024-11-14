# apps/competition_application/permissions.py

from rest_framework import permissions

import logging

logger = logging.getLogger(__name__)


class IsOwnerOrTeacherAssigned(permissions.BasePermission):
    """
    自定义权限：
    - 学生只能访问自己的竞赛申请
    - 教师只能访问分配给自己的竞赛申请
    """

    def has_permission(self, request, view):
        # 基本认证检查
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        logger.info(f"Checking permissions for user {user} on action {view.action}")

        # 教师权限检查
        if hasattr(user, 'teacher_profile'):
            is_assigned_teacher = obj.teacher.teacher_id == user.teacher_id
            logger.info(f"Teacher check - User ID: {user.teacher_id}, Application teacher ID: {obj.teacher.teacher_id}")
            logger.info(f"Is assigned teacher: {is_assigned_teacher}")

            # 教师可以查看和审批分配给自己的申请
            if view.action in ['retrieve', 'approve', 'reject']:
                return is_assigned_teacher
            return True  # 其他操作默认允许

        # 学生权限检查
        if hasattr(user, 'student_profile'):
            is_owner = obj.student == user.student_profile
            logger.info(f"Student check - Is owner: {is_owner}")

            # 撤销操作只允许申请人操作
            if view.action == 'cancel':
                return is_owner

            # 学生只能查看自己的申请
            return is_owner

        logger.warning(f"User has neither teacher nor student profile")
        return False
