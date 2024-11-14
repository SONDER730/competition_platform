# competition_application/serializers.py
from rest_framework import serializers
from .models import CompetitionApplication
from apps.competitions.models import Competition
from apps.competition_application.models import CompetitionReimbursement
from apps.competitions.serializers import CompetitionSerializer
from apps.teacher_center.models import TeacherProfile
from apps.teacher_center.serializers import TeacherProfileSerializer
import logging

logger = logging.getLogger(__name__)


class CompetitionApplicationSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    teacher_id = serializers.CharField(source='teacher.teacher_id', read_only=True)
    reimbursement = serializers.SerializerMethodField()

    class Meta:
        model = CompetitionApplication
        fields = [
            'id',
            'student',
            'competition',
            'teacher',
            'teacher_id',
            'application_status',
            'contact_info',
            'description',
            'submission_time',
            'update_time',
            'photo',
            'summary',
            'certificate',
            'reimbursement',
            'process_status'
        ]
        read_only_fields = [
            'submission_time',
            'update_time',
            'photo',
            'summary',
            'certificate',
            'application_status',
        ]

    def get_student(self, obj):
        if obj.student:
            return {
                'name': obj.student.name,
                'student_id': obj.student.student_id
            }
        return None

    def get_competition(self, obj):
        if obj.competition:
            return {
                'name': obj.competition.name,
                'type': obj.competition.type
            }
        return None

    def get_teacher(self, obj):
        if obj.teacher:
            return {
                'name': obj.teacher.name,
                'teacher_id': obj.teacher.teacher_id,
                'department': obj.teacher.department
            }
        return None
    def get_reimbursement(self, obj):
        """获取报销信息"""
        try:
            if hasattr(obj, 'reimbursement'):
                return {
                    'id': obj.reimbursement.id,
                    'status': obj.reimbursement.status,
                    'registration_fee': float(obj.reimbursement.registration_fee),
                    'transportation_fee': float(obj.reimbursement.transportation_fee),
                    'accommodation_fee': float(obj.reimbursement.accommodation_fee),
                    'other_fee': float(obj.reimbursement.other_fee),
                    'other_fee_description': obj.reimbursement.other_fee_description,
                    'total_amount': float(obj.reimbursement.total_amount),
                    'bank_name': obj.reimbursement.bank_name,
                    'bank_account': obj.reimbursement.bank_account,
                    'account_name': obj.reimbursement.account_name,
                    'submit_time': obj.reimbursement.submit_time,
                    'comment': obj.reimbursement.comment,
                    'invoice': obj.reimbursement.invoice.url if obj.reimbursement.invoice else None
                }
        except Exception as e:
            print(f"Error getting reimbursement info: {str(e)}")
            return None

class CompetitionApplicationCreateSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(
        queryset=TeacherProfile.objects.all(),
        slug_field='teacher_id'  # 使用 teacher_id 字段进行关联
    )

    class Meta:
        model = CompetitionApplication
        fields = [
            'competition',
            'teacher',
            'contact_info',
            'description',
            'application_status',
            'submission_time',
            'update_time',
        ]
        read_only_fields = [
            'application_status',
            'submission_time',
            'update_time',
        ]

    def validate(self, attrs):
        if not attrs.get('competition'):
            raise serializers.ValidationError({"competition": "竞赛不能为空"})
        if not attrs.get('teacher'):
            raise serializers.ValidationError({"teacher": "指导教师不能为空"})
        if not attrs.get('contact_info'):
            raise serializers.ValidationError({"contact_info": "联系方式不能为空"})
        return attrs

class ReimbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionReimbursement
        fields = [
            'id', 'registration_fee', 'transportation_fee',
            'accommodation_fee', 'other_fee', 'other_fee_description',
            'total_amount', 'bank_name', 'bank_account', 'account_name',
            'invoice', 'status', 'submit_time', 'update_time', 'comment'
        ]
        read_only_fields = ['id', 'total_amount', 'status', 'submit_time',
                           'update_time', 'comment']