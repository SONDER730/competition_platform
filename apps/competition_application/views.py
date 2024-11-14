from rest_framework import viewsets, permissions, status, serializers, generics # 添加 serializers
from .models import CompetitionApplication, CompetitionReimbursement
from .serializers import CompetitionApplicationSerializer, CompetitionApplicationCreateSerializer,ReimbursementSerializer
from .permissions import IsOwnerOrTeacherAssigned
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from apps.student_center.models import StudentProfile
from utils.pdf_generator import CompetitionProcessPDF
from rest_framework.decorators import action
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import status
import logging
import os
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class CompetitionApplicationViewSet(viewsets.ModelViewSet):
    """
    提供学生的竞赛申请列表和创建、删除功能
    教师可以查看和审核分配给自己的申请
    """
    queryset = CompetitionApplication.objects.all()
    serializer_class = CompetitionApplicationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrTeacherAssigned]

    def get_serializer_class(self):
        if self.action in ['create']:
            return CompetitionApplicationCreateSerializer
        return CompetitionApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        logger.info(f"Getting queryset for user: {user}")

        if hasattr(user, 'teacher_profile'):
            # 教师只能看到分配给自己的申请
            queryset = CompetitionApplication.objects.filter(
                teacher__teacher_id=user.teacher_id
            ).select_related('student', 'competition', 'teacher')
            logger.info(f"Teacher queryset count: {queryset.count()}")
            return queryset

        if hasattr(user, 'student_profile'):
            # 学生只能看到自己的申请
            queryset = CompetitionApplication.objects.filter(
                student=user.student_profile
            ).select_related('competition', 'teacher')
            logger.info(f"Student queryset count: {queryset.count()}")
            return queryset

        return CompetitionApplication.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        try:
            student_profile = StudentProfile.objects.get(user=user)
            serializer.save(student=student_profile)
        except StudentProfile.DoesNotExist:
            raise serializers.ValidationError({"detail": "未找到学生信息。"})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审批通过竞赛申请
        """
        logger.info(f"Processing approval for application {pk}")
        try:
            application = self.get_object()

            # 检查申请状态
            if application.application_status != 'pending':
                return Response(
                    {'detail': '只能审批处于申报中的申请'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 更新状态
            application.application_status = 'approved'
            application.save()
            logger.info(f"Application {pk} approved successfully")

            return Response({
                'detail': '申请已通过',
                'data': self.get_serializer(application).data
            })

        except Exception as e:
            logger.error(f"Error in approve action: {str(e)}", exc_info=True)
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        拒绝竞赛申请
        """
        application = self.get_object()
        if application.application_status != 'pending':
            return Response(
                {'detail': '只能审核申报中的申请。'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 确认是否为指导教师
        if not hasattr(request.user, 'teacher_profile') or application.teacher.teacher_id != request.user.teacher_id:
            return Response(
                {'detail': '只有指导教师可以审批此申请。'},
                status=status.HTTP_403_FORBIDDEN
            )

        application.application_status = 'rejected'
        application.save()

        return Response({
            'status': 'rejected',
            'detail': '申请已被拒绝'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        撤销竞赛申请
        """
        try:
            application = self.get_object()

            # 确认是否为申请学生
            if not hasattr(request.user, 'student_profile') or application.student.user != request.user:
                return Response(
                    {"detail": "只有申请人可以撤销申请"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if application.application_status != 'pending':
                return Response(
                    {"detail": "只能撤销申报中的申请"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            application.application_status = 'cancelled'
            application.save()

            return Response({
                "detail": "申请已成功撤销",
                "status": "cancelled"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=True, methods=['post'])
    def upload_files(self, request, pk=None):
        application = self.get_object()
        if request.FILES.get('photo'):
            application.photo = request.FILES['photo']
        if request.FILES.get('summary'):
            application.summary = request.FILES['summary']
        if request.FILES.get('certificate'):
            application.certificate = request.FILES['certificate']
        application.save()
        return Response({'detail': '文件上传成功'})

    @action(detail=True, methods=['post'])
    def reimbursement(self, request, pk=None):
        """提交报销申请"""
        try:
            application = self.get_object()

            # 检查是否已经存在报销申请
            if hasattr(application, 'reimbursement'):
                return Response(
                    {'detail': '该申请已存在报销记录'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 准备报销数据
            reimbursement_data = {
                'application': application,
                'registration_fee': request.data.get('registration_fee', 0),
                'transportation_fee': request.data.get('transportation_fee', 0),
                'accommodation_fee': request.data.get('accommodation_fee', 0),
                'other_fee': request.data.get('other_fee', 0),
                'other_fee_description': request.data.get('other_fee_description', ''),
                'bank_name': request.data.get('bank_name'),
                'bank_account': request.data.get('bank_account'),
                'account_name': request.data.get('account_name'),
            }

            # 计算总金额
            reimbursement_data['total_amount'] = (
                    float(reimbursement_data['registration_fee']) +
                    float(reimbursement_data['transportation_fee']) +
                    float(reimbursement_data['accommodation_fee']) +
                    float(reimbursement_data['other_fee'])
            )

            # 创建报销记录
            reimbursement = CompetitionReimbursement.objects.create(**reimbursement_data)

            # 处理发票文件
            if 'invoice' in request.FILES:
                invoice_file = request.FILES['invoice']

                # 构建保存路径
                reimbursement_dir = os.path.join(
                    settings.MEDIA_ROOT,
                    'reimbursement_files',
                    f'application_{application.id}'
                )
                os.makedirs(reimbursement_dir, exist_ok=True)

                # 构建文件名
                file_extension = os.path.splitext(invoice_file.name)[1]
                invoice_path = os.path.join(
                    reimbursement_dir,
                    f'invoice_{reimbursement.id}{file_extension}'
                )

                # 保存文件
                with open(invoice_path, 'wb+') as destination:
                    for chunk in invoice_file.chunks():
                        destination.write(chunk)

                # 更新数据库中的文件路径
                relative_path = os.path.relpath(invoice_path, settings.MEDIA_ROOT)
                reimbursement.invoice = relative_path
                reimbursement.save()

            return Response({
                'detail': '报销申请提交成功',
                'id': reimbursement.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'detail': f'报销申请提交失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reimbursement_review(self, request, pk=None):
        """审核报销申请"""
        try:
            application = self.get_object()
            reimbursement = application.reimbursement

            if not reimbursement:
                return Response(
                    {'detail': '未找到报销申请'},
                    status=status.HTTP_404_NOT_FOUND
                )

            status_input = request.data.get('status')
            comment = request.data.get('comment', '')

            if status_input not in ['approved', 'rejected']:
                return Response(
                    {'detail': '无效的审核状态'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            reimbursement.status = status_input
            reimbursement.comment = comment
            reimbursement.save()

            serializer = self.get_serializer(application)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='download_reimbursement_file')
    def download_reimbursement_file(self, request, pk=None):
        """下载报销相关文件"""
        try:
            application = self.get_object()

            if not hasattr(application, 'reimbursement'):
                return Response(
                    {'detail': '未找到报销申请'},
                    status=status.HTTP_404_NOT_FOUND
                )

            reimbursement = application.reimbursement
            file_path = os.path.join(settings.MEDIA_ROOT, str(reimbursement.invoice))

            if not os.path.exists(file_path):
                return Response(
                    {'detail': '文件不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                # 打开并读取文件
                with open(file_path, 'rb') as f:
                    # 获取文件名
                    file_name = os.path.basename(file_path)
                    # 创建响应
                    response = FileResponse(f)
                    response['Content-Type'] = 'application/pdf'  # 设置正确的 content type
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    return response

            except IOError:
                return Response(
                    {'detail': '文件读取失败'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'detail': f'文件下载失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def finish_process(self, request, pk=None):
        """结束流程"""
        try:
            application = self.get_object()

            # 检查是否可以结束流程
            if not hasattr(application, 'reimbursement'):
                return Response(
                    {'detail': '没有相关的报销申请'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if application.reimbursement.status != 'approved':
                return Response(
                    {'detail': '只有报销通过的申请才能结束流程'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if application.process_status == 'ended':
                return Response(
                    {'detail': '流程已经结束'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 更新流程状态
            application.process_status = 'ended'
            application.save()

            # 返回更新后的数据
            serializer = self.get_serializer(application)
            return Response({
                'detail': '流程已成功结束',
                'data': serializer.data
            })

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """生成流程PDF"""
        try:
            # 获取申请对象
            application = self.get_object()

            # 检查流程状态
            if application.process_status != 'ended':
                return Response(
                    {'detail': '只有已结束的流程才能生成PDF'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # 设置PDF文件路径
                pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_files')
                os.makedirs(pdf_dir, exist_ok=True)
                pdf_filename = f'competition_process_{pk}.pdf'
                pdf_path = os.path.join(pdf_dir, pdf_filename)

                # 如果PDF已经存在且创建时间在24小时内，直接返回
                if os.path.exists(pdf_path):
                    file_age = time.time() - os.path.getmtime(pdf_path)
                    if file_age < 86400:  # 24小时 = 86400秒
                        return FileResponse(
                            open(pdf_path, 'rb'),
                            content_type='application/pdf',
                            filename=pdf_filename
                        )

                # 生成PDF
                pdf_generator = CompetitionProcessPDF(application)
                pdf_content = pdf_generator.generate()

                if not pdf_content:
                    return Response(
                        {'detail': 'PDF生成失败：内容为空'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # 保存PDF文件
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)

                # 创建响应
                response = FileResponse(
                    open(pdf_path, 'rb'),
                    content_type='application/pdf',
                    filename=pdf_filename
                )

                # 添加响应头
                response['Cache-Control'] = 'no-cache'
                response['X-Content-Type-Options'] = 'nosniff'

                return response

            except Exception as e:
                logger.error(f"PDF生成错误: {str(e)}", exc_info=True)
                return Response(
                    {'detail': f'PDF生成失败: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"获取申请信息失败: {str(e)}", exc_info=True)
            return Response(
                {'detail': f'获取申请信息失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_object(self):
        """重写获取对象方法，添加错误日志"""
        try:
            obj = super().get_object()
            return obj
        except Exception as e:
            logger.error(f"获取申请对象失败: {str(e)}")
            raise

class UploadFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # 获取申请记录
            application = CompetitionApplication.objects.get(
                id=pk,
                student__user=request.user,
                application_status='approved'
            )

            # 创建文件目录
            competition_dir = os.path.join(
                settings.COMPETITION_FILES_DIR,
                f'application_{application.id}'
            )
            os.makedirs(competition_dir, exist_ok=True)

            uploaded_files = []

            # 处理照片
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                photo_path = os.path.join(competition_dir, f'photo_{application.id}.jpg')
                with open(photo_path, 'wb+') as f:
                    for chunk in photo.chunks():
                        f.write(chunk)
                application.photo = f'competition_files/application_{application.id}/photo_{application.id}.jpg'
                uploaded_files.append('照片')

            # 处理总结
            if 'summary' in request.FILES:
                summary = request.FILES['summary']
                summary_path = os.path.join(competition_dir, f'summary_{application.id}.pdf')
                with open(summary_path, 'wb+') as f:
                    for chunk in summary.chunks():
                        f.write(chunk)
                application.summary = f'competition_files/application_{application.id}/summary_{application.id}.pdf'
                uploaded_files.append('总结')

            # 处理证书
            if 'certificate' in request.FILES:
                cert = request.FILES['certificate']
                cert_path = os.path.join(competition_dir, f'certificate_{application.id}.pdf')
                with open(cert_path, 'wb+') as f:
                    for chunk in cert.chunks():
                        f.write(chunk)
                application.certificate = f'competition_files/application_{application.id}/certificate_{application.id}.pdf'
                uploaded_files.append('证书')

            # 保存文件路径到数据库
            application.save()

            return Response({
                'detail': f'成功上传: {", ".join(uploaded_files)}',
                'files': uploaded_files
            })

        except CompetitionApplication.DoesNotExist:
            return Response(
                {'detail': '未找到申请或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f'文件上传错误: {str(e)}')
            return Response(
                {'detail': f'上传失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, file_type):
        try:
            # 获取申请记录
            application = CompetitionApplication.objects.get(
                id=pk,
                teacher__user=request.user  # 确保是指导教师
            )

            # 确定文件路径
            file_path = None
            content_type = None

            # 根据文件类型获取相应路径
            if file_type == 'photo':
                file_path = os.path.join(settings.MEDIA_ROOT, application.photo.name)
                content_type = 'image/jpeg'
            elif file_type == 'summary':
                file_path = os.path.join(settings.MEDIA_ROOT, application.summary.name)
                content_type = 'application/pdf'
            elif file_type == 'certificate':
                file_path = os.path.join(settings.MEDIA_ROOT, application.certificate.name)
                content_type = 'application/pdf'
            else:
                return Response(
                    {'detail': '无效的文件类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not file_path or not os.path.exists(file_path):
                return Response(
                    {'detail': '文件不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

            response = FileResponse(open(file_path, 'rb'))
            response['Content-Type'] = content_type
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response

        except CompetitionApplication.DoesNotExist:
            return Response(
                {'detail': '未找到申请或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f'文件下载错误: {str(e)}')
            return Response(
                {'detail': f'下载失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )