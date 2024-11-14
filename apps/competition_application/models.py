# apps/competition_application/models.py
from apps.competitions.models import Competition
from apps.student_center.models import StudentProfile
from apps.teacher_center.models import TeacherProfile
from django.db import models

class CompetitionApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', '申报中'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已撤销'),
    ]
    PROCESS_STATUS_CHOICES = [
        ('ongoing', '进行中'),
        ('ended', '已结束')
    ]

    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='competition_applications'
    )
    competition = models.ForeignKey(
        Competition, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    teacher = models.ForeignKey(
        TeacherProfile, 
        on_delete=models.CASCADE, 
        related_name='applications',
        to_field='teacher_id'  # 使用 teacher_id 作为关联字段
    )
    application_status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    contact_info = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    submission_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # 文件字段
    photo = models.FileField(
        upload_to='competition_files/',
        null=True,
        blank=True
    )
    summary = models.FileField(
        upload_to='competition_files/',
        null=True,
        blank=True
    )
    certificate = models.FileField(
        upload_to='competition_files/',
        null=True,
        blank=True
    )
    process_status = models.CharField(
        max_length=20,
        choices=PROCESS_STATUS_CHOICES,
        default='ongoing',
        verbose_name='流程状态'
    )

    def get_file_path(self, file_type):
        if file_type == 'photo':
            return self.photo.path if self.photo else None
        elif file_type == 'summary':
            return self.summary.path if self.summary else None
        elif file_type == 'certificate':
            return self.certificate.path if self.certificate else None
        return None

    def __str__(self):
        return f'{self.student.name} - {self.competition.name} - {self.application_status}'

    class Meta:
        ordering = ['-submission_time']
        verbose_name = '竞赛申请'
        verbose_name_plural = '竞赛申请'

    @property
    def teacher_id(self):
        """
        获取教师工号
        """
        return self.teacher.teacher_id if self.teacher else None

class CompetitionReimbursement(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]


    application = models.OneToOneField(
        CompetitionApplication,
        on_delete=models.CASCADE,
        related_name='reimbursement'
    )
    registration_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='报名费'
    )
    transportation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='交通费'
    )
    accommodation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='住宿费'
    )
    other_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='其他费用'
    )
    other_fee_description = models.TextField(
        blank=True,
        verbose_name='其他费用说明'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='总金额'
    )
    bank_name = models.CharField(
        max_length=100,
        verbose_name='开户银行'
    )
    bank_account = models.CharField(
        max_length=50,
        verbose_name='银行账号'
    )
    account_name = models.CharField(
        max_length=50,
        verbose_name='开户人姓名'
    )
    invoice = models.FileField(
        upload_to='reimbursement_files/',
        verbose_name='发票/票据'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    submit_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, verbose_name='审批意见')

    def __str__(self):
        return f"{self.application.student.name} - {self.total_amount}"

    class Meta:
        ordering = ['-submit_time']
        verbose_name = '竞赛报销'
        verbose_name_plural = '竞赛报销'