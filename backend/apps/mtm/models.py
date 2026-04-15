import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.users.models import User


class MTMServiceCase(models.Model):
    """
    MTM 服务单主实体
    """

    ALLOWED_STATUS_TRANSITIONS = {
        "pending": {"interviewing"},
        "interviewing": {"assessing"},
        "assessing": {"intervening"},
        "intervening": {"following_up", "completed"},
        "following_up": {"completed"},
        "completed": set(),
    }

    STATUS_CHOICES = [
        ("pending", "待开始"),
        ("interviewing", "问诊中"),
        ("assessing", "评估中"),
        ("intervening", "干预中"),
        ("following_up", "随访中"),
        ("completed", "已完成"),
    ]

    TRIGGER_SOURCE_CHOICES = [
        ("manual", "手动发起"),
        ("self_requested", "用户主动申请"),
        ("adherence_alert", "依从性预警"),
        ("followup_due", "复诊到期"),
        ("polypharmacy", "多重用药"),
        ("referral", "转介"),
    ]

    case_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name="服务编号",
        help_text="MTM 服务业务编号",
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mtm_service_cases",
        verbose_name="患者",
        help_text="服务对应的患者用户",
    )
    assigned_pharmacist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_mtm_service_cases",
        blank=True,
        null=True,
        verbose_name="主责药师",
        help_text="当前负责该 MTM 服务的药师用户",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="服务状态",
        help_text="MTM 服务当前所处的流程状态",
    )
    trigger_source = models.CharField(
        max_length=20,
        choices=TRIGGER_SOURCE_CHOICES,
        default="manual",
        verbose_name="触发来源",
        help_text="MTM 服务的触发来源",
    )
    service_goal = models.TextField(
        blank=True,
        null=True,
        verbose_name="服务目标",
        help_text="本次 MTM 服务的主要目标",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="备注",
        help_text="服务单层面的补充说明",
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="启动时间",
        help_text="服务单正式建立或开始处理的时间",
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="完成时间",
        help_text="服务单完成的时间",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "mtm_service_cases"
        verbose_name = "MTM服务单"
        verbose_name_plural = "MTM服务单"
        indexes = [
            models.Index(fields=["case_number"], name="idx_mtm_case_number"),
            models.Index(fields=["patient"], name="idx_mtm_case_patient"),
            models.Index(fields=["assigned_pharmacist"], name="idx_mtm_case_pharm"),
            models.Index(fields=["status"], name="idx_mtm_case_status"),
            models.Index(fields=["trigger_source"], name="idx_mtm_case_trigger"),
            models.Index(fields=["created_at"], name="idx_mtm_case_created"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.case_number} - {self.patient.username}"

    def save(self, *args, **kwargs):
        """
        保存服务单时补齐业务编号
        """
        if not self.case_number:
            self.case_number = self.generate_case_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_case_number():
        """
        生成可读的服务业务编号
        """
        date_prefix = timezone.now().strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:8].upper()
        return f"MTM-{date_prefix}-{unique_suffix}"

    def can_transition_to(self, target_status):
        """
        判断当前服务单是否允许流转到目标状态
        """
        return target_status in self.ALLOWED_STATUS_TRANSITIONS.get(self.status, set())

    def transition_to(self, target_status, note=None):
        """
        执行最小状态流转，并在完成时自动补齐完成时间
        """
        if target_status == self.status:
            raise ValidationError("服务单已经处于目标状态")

        if not self.can_transition_to(target_status):
            raise ValidationError(
                f"当前状态 {self.status} 不允许流转到 {target_status}"
            )

        previous_status = self.status
        self.status = target_status

        if target_status == "completed":
            self.completed_at = timezone.now()

        if note:
            transition_note = (
                f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"状态流转 {previous_status} -> {target_status}: {note.strip()}"
            )
            self.notes = "\n".join(
                [item for item in [self.notes, transition_note] if item]
            )

        self.save(update_fields=["status", "completed_at", "notes", "updated_at"])


class MTMInterview(models.Model):
    """
    MTM 问诊信息
    """

    service_case = models.OneToOneField(
        MTMServiceCase,
        on_delete=models.CASCADE,
        related_name="interview",
        verbose_name="服务单",
        help_text="对应的 MTM 服务单",
    )
    basic_info_snapshot = models.JSONField(
        default=dict,
        verbose_name="基本信息快照",
        help_text="患者当前基础资料快照",
    )
    medication_history = models.JSONField(
        default=list,
        verbose_name="用药史",
        help_text="结构化的既往与当前用药信息",
    )
    allergy_history = models.JSONField(
        default=list,
        verbose_name="过敏史",
        help_text="结构化过敏史记录",
    )
    lifestyle_info = models.JSONField(
        default=dict,
        verbose_name="生活方式",
        help_text="饮食、运动、睡眠等生活方式信息",
    )
    economic_context = models.TextField(
        blank=True,
        null=True,
        verbose_name="经济情况",
        help_text="支付能力、取药便利性等补充信息",
    )
    health_expectations = models.TextField(
        blank=True,
        null=True,
        verbose_name="健康期望",
        help_text="患者对本次服务的目标和期望",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="备注",
        help_text="问诊补充记录",
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="完成时间",
        help_text="问诊完成时间",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "mtm_interviews"
        verbose_name = "MTM问诊"
        verbose_name_plural = "MTM问诊"

    def __str__(self):
        return f"{self.service_case.case_number} - 问诊"


class MTMAssessment(models.Model):
    """
    MTM 五维评估结果
    """

    RISK_LEVEL_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
    ]

    service_case = models.OneToOneField(
        MTMServiceCase,
        on_delete=models.CASCADE,
        related_name="assessment",
        verbose_name="服务单",
        help_text="对应的 MTM 服务单",
    )
    appropriateness_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="适宜性评分",
        help_text="药物选择适宜性评分",
    )
    effectiveness_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="有效性评分",
        help_text="治疗有效性评分",
    )
    safety_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="安全性评分",
        help_text="安全风险评分",
    )
    adherence_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="依从性评分",
        help_text="依从性评分",
    )
    economic_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="经济性评分",
        help_text="经济负担评分",
    )
    problem_list = models.JSONField(
        default=list,
        verbose_name="问题清单",
        help_text="结构化药物治疗问题列表",
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="评估总结",
        help_text="本次评估的总结说明",
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="medium",
        verbose_name="风险等级",
        help_text="评估综合风险等级",
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="完成时间",
        help_text="评估完成时间",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "mtm_assessments"
        verbose_name = "MTM评估"
        verbose_name_plural = "MTM评估"
        indexes = [
            models.Index(fields=["risk_level"], name="idx_mtm_assess_risk"),
            models.Index(fields=["completed_at"], name="idx_mtm_assess_done"),
        ]

    def __str__(self):
        return f"{self.service_case.case_number} - 评估"


class MTMPlan(models.Model):
    """
    MTM 干预计划
    """

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
        ("urgent", "紧急"),
    ]

    PATIENT_CONFIRMATION_CHOICES = [
        ("pending", "待确认"),
        ("confirmed", "已确认"),
        ("declined", "已拒绝"),
    ]

    service_case = models.OneToOneField(
        MTMServiceCase,
        on_delete=models.CASCADE,
        related_name="plan",
        verbose_name="服务单",
        help_text="对应的 MTM 服务单",
    )
    interventions = models.JSONField(
        default=list,
        verbose_name="干预措施",
        help_text="结构化干预措施列表",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="优先级",
        help_text="当前计划整体优先级",
    )
    patient_confirmation_status = models.CharField(
        max_length=20,
        choices=PATIENT_CONFIRMATION_CHOICES,
        default="pending",
        verbose_name="患者确认状态",
        help_text="患者对干预计划的确认状态",
    )
    patient_confirmation_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="患者确认说明",
        help_text="患者确认或拒绝时的补充说明",
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="确认时间",
        help_text="患者确认时间",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "mtm_plans"
        verbose_name = "MTM干预计划"
        verbose_name_plural = "MTM干预计划"
        indexes = [
            models.Index(fields=["priority"], name="idx_mtm_plan_priority"),
            models.Index(
                fields=["patient_confirmation_status"],
                name="idx_mtm_plan_confirm",
            ),
        ]

    def __str__(self):
        return f"{self.service_case.case_number} - 干预计划"


class MTMFollowUp(models.Model):
    """
    MTM 随访记录
    """

    FOLLOW_UP_METHOD_CHOICES = [
        ("phone", "电话"),
        ("in_person", "面谈"),
        ("video", "视频"),
        ("wechat", "微信"),
        ("other", "其他"),
    ]

    EXECUTION_STATUS_CHOICES = [
        ("pending", "待执行"),
        ("completed", "已完成"),
        ("missed", "未完成"),
        ("cancelled", "已取消"),
    ]

    RISK_CHANGE_CHOICES = [
        ("improved", "改善"),
        ("stable", "稳定"),
        ("worsened", "恶化"),
        ("unknown", "未知"),
    ]

    service_case = models.ForeignKey(
        MTMServiceCase,
        on_delete=models.CASCADE,
        related_name="follow_ups",
        verbose_name="服务单",
        help_text="对应的 MTM 服务单",
    )
    follow_up_time = models.DateTimeField(
        verbose_name="随访时间",
        help_text="本次随访计划或实际发生时间",
    )
    follow_up_method = models.CharField(
        max_length=20,
        choices=FOLLOW_UP_METHOD_CHOICES,
        default="phone",
        verbose_name="随访方式",
        help_text="本次随访使用的方式",
    )
    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS_CHOICES,
        default="pending",
        verbose_name="执行情况",
        help_text="本次随访执行结果",
    )
    risk_change = models.CharField(
        max_length=20,
        choices=RISK_CHANGE_CHOICES,
        default="unknown",
        verbose_name="风险变化",
        help_text="本次随访后风险变化情况",
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="随访总结",
        help_text="本次随访的主要结论",
    )
    next_follow_up_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="下次随访时间",
        help_text="建议的下一次随访时间",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "mtm_follow_ups"
        verbose_name = "MTM随访"
        verbose_name_plural = "MTM随访"
        indexes = [
            models.Index(fields=["service_case"], name="idx_mtm_follow_case"),
            models.Index(fields=["follow_up_time"], name="idx_mtm_follow_time"),
            models.Index(fields=["execution_status"], name="idx_mtm_follow_exec"),
        ]
        ordering = ["-follow_up_time", "-created_at"]

    def __str__(self):
        return f"{self.service_case.case_number} - 随访"
