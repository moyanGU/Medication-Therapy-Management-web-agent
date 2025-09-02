from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class MedicalRecord(models.Model):
    """
    就医记录模型，记录用户的就诊信息
    """
    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name='用户',
        help_text='就医记录所属用户'
    )
    
    # 就诊日期
    visit_date = models.DateField(
        verbose_name='就诊日期',
        help_text='实际就诊的日期'
    )
    
    # 就诊时间
    visit_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='就诊时间',
        help_text='具体的就诊时间'
    )
    
    # 医院名称
    hospital = models.CharField(
        max_length=100,
        verbose_name='医院名称',
        help_text='就诊的医院名称'
    )
    
    # 医院地址
    hospital_address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='医院地址',
        help_text='医院的详细地址'
    )
    
    # 科室
    department = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='科室',
        help_text='就诊的科室'
    )
    
    # 医生姓名
    doctor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='医生姓名',
        help_text='接诊医生的姓名'
    )
    
    # 医生职称
    doctor_title = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='医生职称',
        help_text='医生的职称，如主任医师、副主任医师等'
    )
    
    # 就诊类型
    VISIT_TYPE_CHOICES = [
        ('outpatient', '门诊'),
        ('emergency', '急诊'),
        ('inpatient', '住院'),
        ('follow_up', '复诊'),
        ('consultation', '会诊'),
        ('physical_exam', '体检'),
        ('vaccination', '疫苗接种'),
    ]
    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        default='outpatient',
        verbose_name='就诊类型',
        help_text='就诊的类型'
    )
    
    # 主诉
    chief_complaint = models.TextField(
        blank=True,
        null=True,
        verbose_name='主诉',
        help_text='患者的主要症状和不适'
    )
    
    # 现病史
    present_illness = models.TextField(
        blank=True,
        null=True,
        verbose_name='现病史',
        help_text='当前疾病的发展过程'
    )
    
    # 诊断结果
    diagnosis = models.TextField(
        blank=True,
        null=True,
        verbose_name='诊断结果',
        help_text='医生的诊断结果'
    )
    
    # 诊断代码（ICD-10）
    diagnosis_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='诊断代码',
        help_text='ICD-10诊断代码'
    )
    
    # 治疗方案
    treatment = models.TextField(
        blank=True,
        null=True,
        verbose_name='治疗方案',
        help_text='医生制定的治疗方案'
    )
    
    # 处方药品
    prescribed_medicines = models.JSONField(
        default=list,
        verbose_name='处方药品',
        help_text='医生开具的药品列表'
    )
    
    # 检查项目
    examinations = models.JSONField(
        default=list,
        verbose_name='检查项目',
        help_text='进行的检查项目列表'
    )
    
    # 检查结果
    examination_results = models.TextField(
        blank=True,
        null=True,
        verbose_name='检查结果',
        help_text='各项检查的结果'
    )
    
    # 化验结果
    lab_results = models.JSONField(
        default=dict,
        verbose_name='化验结果',
        help_text='化验检查的具体数值结果'
    )
    
    # 医嘱
    medical_orders = models.TextField(
        blank=True,
        null=True,
        verbose_name='医嘱',
        help_text='医生的医嘱和建议'
    )
    
    # 注意事项
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='注意事项',
        help_text='就医过程中的备注和注意事项'
    )
    
    # 费用信息
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='总费用',
        help_text='本次就医的总费用'
    )
    
    # 医保报销
    insurance_coverage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='医保报销',
        help_text='医保报销的金额'
    )
    
    # 自费金额
    self_pay_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='自费金额',
        help_text='个人自费的金额'
    )
    
    # 复诊时间
    follow_up_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='复诊时间',
        help_text='建议的复诊时间'
    )
    
    # 复诊说明
    follow_up_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='复诊说明',
        help_text='复诊的相关说明'
    )
    
    # 症状评分（就诊前）
    symptom_score_before = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='就诊前症状评分',
        help_text='就诊前症状严重程度评分（1-10分）'
    )
    
    # 症状评分（就诊后）
    symptom_score_after = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='就诊后症状评分',
        help_text='就诊后症状改善程度评分（1-10分）'
    )
    
    # 满意度评分
    satisfaction_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='满意度评分',
        help_text='对本次就医的满意度评分（1-5分）'
    )
    
    # 就医状态
    STATUS_CHOICES = [
        ('scheduled', '已预约'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('no_show', '未到诊'),
        ('rescheduled', '已改期'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name='就医状态',
        help_text='就医记录的状态'
    )
    
    # 紧急程度
    URGENCY_CHOICES = [
        ('routine', '常规'),
        ('urgent', '紧急'),
        ('emergency', '急诊'),
        ('critical', '危重'),
    ]
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='routine',
        verbose_name='紧急程度',
        help_text='就医的紧急程度'
    )
    
    # 相关文件
    attachments = models.JSONField(
        default=list,
        verbose_name='相关文件',
        help_text='相关的医疗文件、报告等'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间',
        help_text='记录创建时间'
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='记录最后更新时间'
    )
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = '就医记录'
        verbose_name_plural = '就医记录'
        indexes = [
            models.Index(fields=['user_id'], name='idx_medical_records_user_id'),
            models.Index(fields=['visit_date'], name='idx_medical_records_visit_date'),
            models.Index(fields=['hospital'], name='idx_medical_records_hospital'),
            models.Index(fields=['department'], name='idx_medical_records_department'),
            models.Index(fields=['doctor'], name='idx_medical_records_doctor'),
            models.Index(fields=['visit_type'], name='idx_medical_records_visit_type'),
            models.Index(fields=['status'], name='idx_medical_records_status'),
            models.Index(fields=['urgency'], name='idx_medical_records_urgency'),
            models.Index(fields=['user_id', 'visit_date'], name='idx_medical_records_user_date'),
        ]
        ordering = ['-visit_date', '-visit_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.hospital} - {self.visit_date}"
    
    @property
    def visit_datetime(self):
        """
        获取完整的就诊时间
        """
        if self.visit_time:
            return timezone.datetime.combine(self.visit_date, self.visit_time)
        return timezone.datetime.combine(self.visit_date, timezone.datetime.min.time())
    
    @property
    def days_since_visit(self):
        """
        计算距离就诊已过去多少天
        """
        today = timezone.now().date()
        return (today - self.visit_date).days
    
    @property
    def days_until_follow_up(self):
        """
        计算距离复诊还有多少天
        """
        if self.follow_up_date:
            today = timezone.now().date()
            return (self.follow_up_date - today).days
        return None
    
    @property
    def symptom_improvement(self):
        """
        计算症状改善程度
        """
        if self.symptom_score_before and self.symptom_score_after:
            return self.symptom_score_before - self.symptom_score_after
        return None
    
    def get_prescribed_medicine_names(self):
        """
        获取处方药品名称列表
        """
        if self.prescribed_medicines:
            return [med.get('name', '') for med in self.prescribed_medicines if med.get('name')]
        return []
    
    def get_examination_names(self):
        """
        获取检查项目名称列表
        """
        if self.examinations:
            return [exam.get('name', '') for exam in self.examinations if exam.get('name')]
        return []
    
    def calculate_out_of_pocket_cost(self):
        """
        计算自付费用
        """
        if self.total_cost and self.insurance_coverage:
            return self.total_cost - self.insurance_coverage
        return self.self_pay_amount or 0
    
    def is_follow_up_due(self):
        """
        检查是否到了复诊时间
        """
        if self.follow_up_date:
            today = timezone.now().date()
            return today >= self.follow_up_date
        return False
    
    def get_visit_summary(self):
        """
        获取就诊摘要
        """
        summary = {
            'date': self.visit_date,
            'hospital': self.hospital,
            'department': self.department,
            'doctor': self.doctor,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'medicines': self.get_prescribed_medicine_names(),
            'examinations': self.get_examination_names(),
            'follow_up': self.follow_up_date,
            'cost': self.total_cost,
        }
        return summary
    
    @classmethod
    def get_recent_visits(cls, user, days=30):
        """
        获取用户最近的就诊记录
        """
        cutoff_date = timezone.now().date() - timezone.timedelta(days=days)
        return cls.objects.filter(
            user=user,
            visit_date__gte=cutoff_date
        ).order_by('-visit_date')
    
    @classmethod
    def get_visits_by_hospital(cls, user, hospital_name):
        """
        获取用户在特定医院的就诊记录
        """
        return cls.objects.filter(
            user=user,
            hospital__icontains=hospital_name
        ).order_by('-visit_date')
    
    @classmethod
    def get_visits_by_department(cls, user, department_name):
        """
        获取用户在特定科室的就诊记录
        """
        return cls.objects.filter(
            user=user,
            department__icontains=department_name
        ).order_by('-visit_date')