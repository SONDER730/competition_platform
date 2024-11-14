
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.competition_application.models import CompetitionApplication
from apps.competition_application.serializers import CompetitionApplicationSerializer
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied  # 添加这行导入
from rest_framework.response import Response
from .models import TeacherProfile
from .serializers import TeacherProfileSerializer
from .permissions import IsTeacher
from django.db import models
import logging
logger = logging.getLogger(__name__)

class TeacherProfileView(generics.RetrieveUpdateAPIView):
    """
    获取和更新教师个人资料
    """
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_object(self):
        try:
            profile = TeacherProfile.objects.get(teacher_id=self.request.user.teacher_id)
            return profile
        except TeacherProfile.DoesNotExist:
            logger.info(f"Creating new teacher profile for teacher_id: {self.request.user.teacher_id}")
            # 创建新的教师档案，只填入工号和邮箱
            return TeacherProfile.objects.create(
                user=self.request.user,
                teacher_id=self.request.user.teacher_id,
                email=self.request.user.email,
                name='',           # 留空等待用户填写
                department='',     # 留空等待用户填写
                phone=''          # 留空等待用户填写
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 不允许修改工号
        if 'teacher_id' in request.data:
            return Response(
                {"detail": "工号不允许修改"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "detail": "个人信息更新成功"
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@csrf_exempt
def search_teachers(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)

    # 按名称或部门进行模糊搜索
    teachers = TeacherProfile.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(department__icontains=query)
    )

    # 返回更完整的教师信息
    teacher_list = [
        {
            "id": teacher.id,
            "name": teacher.name,
            "department": teacher.department,
            "teacher_id": teacher.teacher_id
        }
        for teacher in teachers
    ]

    return JsonResponse(teacher_list, safe=False)




class ApproveCompetitionApplicationView(generics.UpdateAPIView):
    queryset = CompetitionApplication.objects.all()
    serializer_class = CompetitionApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        application = self.get_object()  # 获取竞赛申请对象
        user = request.user  # 获取当前登录用户

        # 确保当前用户是该申请的指导教师
        if not hasattr(user, 'teacher_profile') or application.teacher.user != user:
            return Response({'detail': '您无权审核此申请。'}, status=status.HTTP_403_FORBIDDEN)

        # 获取更新的状态
        status_input = request.data.get('status')

        if status_input == 'approved':
            application.application_status = 'approved'  # 设置状态为批准
        elif status_input == 'rejected':
            application.application_status = 'rejected'  # 设置状态为拒绝
        else:
            return Response({'detail': '无效的状态。'}, status=status.HTTP_400_BAD_REQUEST)

        application.save()  # 保存更新后的申请状态
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherAssignedApplicationsView(generics.ListAPIView):
    serializer_class = CompetitionApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        teacher_id = self.request.user.teacher_id
        print(f"查询教师工号: {teacher_id} 的申请")

        # 修改查询条件，确保与数据库字段匹配
        queryset = CompetitionApplication.objects.filter(
            teacher__teacher_id=teacher_id  # 使用双下划线访问关联字段
        ).select_related(
            'student',
            'competition',
            'teacher'
        )
        # 添加调试信息
        print(f"SQL Query: {queryset.query}")
        print(f"找到的申请数量: {queryset.count()}")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)