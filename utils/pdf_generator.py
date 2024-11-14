#  utils/pdf_generator.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class CompetitionProcessPDF:
    def __init__(self, application):
        self.application = application
        self.buffer = BytesIO()
        self.use_basic_font = True  # 添加这个属性

        try:
            # 注册中文字体
            font_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'noto_sans',
                'NotoSansSC-VariableFont_wght.ttf'
            )
            logger.info(f"字体路径: {font_path}")

            if os.path.exists(font_path):
                logger.info("字体文件存在，尝试注册...")
                pdfmetrics.registerFont(TTFont('NotoSansSC', font_path))
                self.base_font = 'NotoSansSC'
                self.use_basic_font = False  # 如果成功注册字体，设置为False
                logger.info("字体注册成功")
            else:
                logger.warning(f"找不到字体文件: {font_path}")
                self.base_font = 'Helvetica'
                self.use_basic_font = True
        except Exception as e:
            logger.error(f"字体加载失败: {str(e)}")
            self.base_font = 'Helvetica'
            self.use_basic_font = True

        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        self.styles = getSampleStyleSheet()

        # 创建通用样式
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=self.base_font,
            leading=12
        )

        # 创建标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            fontName=self.base_font,
            alignment=1,
            spaceAfter=30
        )

        self.elements = []

    def create_title(self):
        """创建标题"""
        logger.info("创建标题")
        self.elements.append(Paragraph(
            "竞赛申请流程记录",
            self.title_style
        ))
        self.elements.append(Spacer(1, 12))

    def create_basic_info(self):
        """创建基本信息表格"""
        logger.info("创建基本信息")
        data = [
            ['基本信息', '', '', ''],
            ['竞赛名称', str(self.application.competition.name), '申请日期',
             self.application.submission_time.strftime('%Y-%m-%d')],
            ['学生姓名', str(self.application.student.name), '学号', str(self.application.student.student_id)],
            ['指导教师', str(self.application.teacher.name), '工号', str(self.application.teacher.teacher_id)],
            ['竞赛类型', str(self.application.competition.type), '联系方式', str(self.application.contact_info)],
            ['申请描述', str(self.application.description or '无'), '', ''],
        ]

        table = Table(data, colWidths=[100, 150, 100, 150])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (3, 0)),
            ('SPAN', (1, 5), (3, 5)),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 20))

    def create_process_flow(self):
        """创建流程图和时间表"""
        # 流程状态和时间
        status_data = [
            ['流程记录', '', ''],
            ['状态', '时间', '备注'],
            ['申请提交', self.application.submission_time.strftime('%Y-%m-%d'), '已完成'],
            ['申请审核', self._get_approval_date(), self._get_approval_status()],
            ['报销提交', self._get_reimbursement_submit_date(), self._get_reimbursement_status()],
            ['报销审核', self._get_reimbursement_review_date(), self._get_reimbursement_review_status()],
            ['流程结束', self._get_process_end_date(), self._get_process_status()],
        ]

        table = Table(status_data, colWidths=[150, 150, 200])
        base_font = 'NotoSansSC' if not self.use_basic_font else 'Helvetica'
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (2, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 20))

    def create_files_section(self):
        """创建文件资料部分"""
        logger.info("创建文件资料部分")
        files_data = [
            ['文件资料', '', ''],
            ['文件类型', '状态', '上传时间'],
        ]

        # 添加文件信息
        if self.application.photo:
            files_data.append(['参赛照片', '已上传', self._get_file_upload_time(self.application.photo)])
        if self.application.summary:
            files_data.append(['参赛总结', '已上传', self._get_file_upload_time(self.application.summary)])
        if self.application.certificate:
            files_data.append(['获奖证书', '已上传', self._get_file_upload_time(self.application.certificate)])

        table = Table(files_data, colWidths=[200, 150, 150])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (2, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 20))

    def create_reimbursement_info(self):
        """创建报销信息部分"""
        logger.info("创建报销信息")
        if hasattr(self.application, 'reimbursement'):
            reimb = self.application.reimbursement
            reimb_data = [
                ['报销信息', '', '', ''],
                ['报销项目', '金额', '说明', '状态'],
                ['报名费', f'¥{reimb.registration_fee}', '', ''],
                ['交通费', f'¥{reimb.transportation_fee}', '', ''],
                ['住宿费', f'¥{reimb.accommodation_fee}', '', ''],
                ['其他费用', f'¥{reimb.other_fee}', reimb.other_fee_description or '', ''],
                ['合计', f'¥{reimb.total_amount}', '', reimb.status],
                ['开户银行', reimb.bank_name, '账号', reimb.bank_account],
                ['开户人', reimb.account_name, '', ''],
            ]

            table = Table(reimb_data, colWidths=[100, 150, 150, 100])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), self.base_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('SPAN', (0, 0), (3, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]))
            self.elements.append(table)

    def generate(self):
        """生成PDF文件"""
        try:
            logger.info("开始生成PDF...")

            self.create_title()
            self.create_basic_info()
            self.create_files_section()

            if hasattr(self.application, 'reimbursement'):
                self.create_reimbursement_info()

            # 构建PDF
            logger.info("构建PDF...")
            self.doc.build(self.elements)

            # 获取PDF内容
            logger.info("获取PDF内容...")
            pdf_content = self.buffer.getvalue()
            self.buffer.close()

            logger.info("PDF生成完成")
            return pdf_content

        except Exception as e:
            logger.error(f"生成PDF时发生错误: {str(e)}", exc_info=True)
            self.buffer.close()
            raise Exception(f"生成PDF失败: {str(e)}")

    def _get_file_upload_time(self, file_field):
        """获取文件上传时间"""
        try:
            if file_field and hasattr(file_field, 'name'):
                try:
                    file_path = file_field.path
                    if os.path.exists(file_path):
                        timestamp = os.path.getmtime(file_path)
                        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                except Exception as e:
                    logger.error(f"获取文件时间出错: {str(e)}")
            return '未知'
        except Exception as e:
            logger.error(f"处理文件时间时出错: {str(e)}")
            return '未知'

    def _get_approval_date(self):
        """获取审批时间"""
        if self.application.update_time and self.application.application_status in ['approved', 'rejected']:
            return self.application.update_time.strftime('%Y-%m-%d')
        return '未审批'

    def _get_approval_status(self):
        """获取审批状态"""
        status_map = {
            'pending': '待审批',
            'approved': '已通过',
            'rejected': '已拒绝',
            'cancelled': '已撤销'
        }
        return status_map.get(self.application.application_status, '未知状态')

    def _get_reimbursement_submit_date(self):
        """获取报销提交时间"""
        if hasattr(self.application, 'reimbursement'):
            return self.application.reimbursement.submit_time.strftime('%Y-%m-%d')
        return '未提交'

    def _get_reimbursement_status(self):
        """获取报销状态"""
        if not hasattr(self.application, 'reimbursement'):
            return '未提交'

        status_map = {
            'pending': '待审批',
            'approved': '已通过',
            'rejected': '已拒绝'
        }
        return status_map.get(self.application.reimbursement.status, '未知状态')

    def _get_reimbursement_review_date(self):
        """获取报销审核时间"""
        if hasattr(self.application, 'reimbursement'):
            if self.application.reimbursement.status != 'pending':
                return self.application.reimbursement.update_time.strftime('%Y-%m-%d')
        return '未审核'

    def _get_reimbursement_review_status(self):
        """获取报销审核状态"""
        if not hasattr(self.application, 'reimbursement'):
            return '未提交报销'

        status_map = {
            'pending': '审核中',
            'approved': '已通过',
            'rejected': '已拒绝'
        }
        return status_map.get(self.application.reimbursement.status, '未知状态')

    def _get_process_end_date(self):
        """获取流程结束时间"""
        if self.application.process_status == 'ended':
            return self.application.update_time.strftime('%Y-%m-%d')
        return '未结束'

    def _get_process_status(self):
        """获取流程状态"""
        status_map = {
            'ongoing': '进行中',
            'ended': '已结束'
        }
        return status_map.get(self.application.process_status, '未知状态')

