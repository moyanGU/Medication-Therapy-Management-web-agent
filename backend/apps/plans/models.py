from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.medicines.models import Medicine
from apps.users.models import User


class MedicationPlan(models.Model):
    """
    用药计划模型，管理用户的用药方案
    """

    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medication_plans",
        verbose_name="用户",
        help_text="计划所属用户",
    )

    # 计划名称
    name = models.CharField(max_length=100, verbose_name="计划名称", help_text="用药计划的名称")

    # 计划类型
    PLAN_TYPE_CHOICES = [
        ("long_term", "长期用药"),
        ("short_term", "短期用药"),
        ("acute", "急性治疗"),
        ("chronic", "慢性管理"),
        ("preventive", "预防用药"),
        ("rehabilitation", "康复治疗"),
    ]
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        default="short_term",
        verbose_name="计划类型",
        help_text="用药计划的类型",
    )

    # 开始日期
    start_date = models.DateField(verbose_name="开始日期", help_text="计划开始执行的日期")

    # 结束日期
    end_date = models.DateField(
        blank=True, null=True, verbose_name="结束日期", help_text="计划结束日期，为空表示长期计划"
    )

    # 计划描述
    description = models.TextField(
        blank=True, null=True, verbose_name="计划描述", help_text="用药计划的详细描述"
    )

    # 治疗目标
    treatment_goal = models.TextField(
        blank=True, null=True, verbose_name="治疗目标", help_text="此用药计划要达到的治疗目标"
    )

    # 是否激活
    is_active = models.BooleanField(
        default=True, verbose_name="是否激活", help_text="计划是否处于激活状态"
    )

    # 优先级
    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
        ("urgent", "紧急"),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="优先级",
        help_text="计划的优先级",
    )

    # 创建来源
    SOURCE_CHOICES = [
        ("doctor", "医生开具"),
        ("self", "自行制定"),
        ("pharmacist", "药师建议"),
        ("import", "导入"),
        ("template", "模板创建"),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="self",
        verbose_name="创建来源",
        help_text="计划的创建来源",
    )

    # 医生信息
    doctor_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="医生姓名",
        help_text="开具此计划的医生姓名",
    )

    # 医院信息
    hospital_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="医院名称",
        help_text="开具此计划的医院名称",
    )

    # 科室信息
    department = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="科室", help_text="开具此计划的科室"
    )

    # 诊断信息
    diagnosis = models.TextField(
        blank=True, null=True, verbose_name="诊断信息", help_text="相关的诊断信息"
    )

    # 注意事项
    precautions = models.TextField(
        blank=True, null=True, verbose_name="注意事项", help_text="用药过程中的注意事项"
    )

    # 副作用监控
    side_effects_monitoring = models.TextField(
        blank=True, null=True, verbose_name="副作用监控", help_text="需要监控的副作用"
    )

    # 复查时间
    review_date = models.DateField(
        blank=True, null=True, verbose_name="复查时间", help_text="建议的复查时间"
    )

    # 计划状态
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("active", "执行中"),
        ("paused", "暂停"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="计划状态",
        help_text="当前计划的状态",
    )

    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="计划创建时间"
    )

    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="更新时间", help_text="计划最后更新时间"
    )

    class Meta:
        db_table = "medication_plans"
        verbose_name = "用药计划"
        verbose_name_plural = "用药计划"
        indexes = [
            models.Index(fields=["user"], name="idx_med_plan_user"),
            models.Index(fields=["start_date"], name="idx_med_plan_start"),
            models.Index(fields=["end_date"], name="idx_med_plan_end"),
            models.Index(fields=["status"], name="idx_med_plan_status"),
            models.Index(fields=["created_at"], name="idx_med_plan_created"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def duration_days(self):
        """
        计算计划持续天数
        """
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None

    @property
    def is_expired(self):
        """
        检查计划是否已过期
        """
        if self.end_date:
            return self.end_date < timezone.now().date()
        return False

    @property
    def progress_percentage(self):
        """
        计算计划进度百分比
        """
        if not self.end_date:
            return None

        today = timezone.now().date()
        if today < self.start_date:
            return 0
        if today > self.end_date:
            return 100

        total_days = (self.end_date - self.start_date).days
        elapsed_days = (today - self.start_date).days

        if total_days == 0:
            return 100

        return min(100, (elapsed_days / total_days) * 100)

    def get_medicines_count(self):
        """
        获取计划中的药品数量
        """
        return self.plan_medicines.count()

    def check_drug_interactions(self):
        """
        检查药物相互作用（简化版本）
        """
        medicines = [pm.medicine for pm in self.plan_medicines.all()]
        interactions = []

        # 这里可以实现更复杂的药物相互作用检查逻辑
        # 目前只是一个示例框架
        for i, med1 in enumerate(medicines):
            for med2 in medicines[i + 1:]:
                # 简单的名称匹配检查（实际应该使用药物数据库）
                if self._check_interaction(med1.name, med2.name):
                    interactions.append(
                        {
                            "medicine1": med1.name,
                            "medicine2": med2.name,
                            "severity": "medium",
                            "description": f"{med1.name} 与 {med2.name} 可能存在相互作用",
                        }
                    )

        return interactions

    def _check_interaction(self, med1_name, med2_name):
        """
        简化的药物相互作用检查
        """
        # 这里应该连接到药物相互作用数据库
        # 目前只是示例逻辑
        common_interactions = [
            ("阿司匹林", "华法林"),
            ("地高辛", "胺碘酮"),
            ("辛伐他汀", "红霉素"),
        ]

        for interaction in common_interactions:
            if (med1_name in interaction[0] and med2_name in interaction[1]) or (
                med1_name in interaction[1] and med2_name in interaction[0]
            ):
                return True

        return False


class PlanMedicine(models.Model):
    """
    计划药品关联模型，定义计划中每个药品的具体用法
    """

    # 关联计划
    plan = models.ForeignKey(
        MedicationPlan,
        on_delete=models.CASCADE,
        related_name="plan_medicines",
        verbose_name="用药计划",
        help_text="所属的用药计划",
    )

    # 关联药品
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="plan_medicines",
        verbose_name="药品",
        help_text="计划中的药品",
    )

    # 每日剂量
    daily_dosage = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="每日剂量", help_text="每日总剂量"
    )

    # 服用频率
    FREQUENCY_CHOICES = [
        ("once_daily", "每日一次"),
        ("twice_daily", "每日两次"),
        ("three_times_daily", "每日三次"),
        ("four_times_daily", "每日四次"),
        ("every_other_day", "隔日一次"),
        ("weekly", "每周一次"),
        ("as_needed", "按需服用"),
        ("custom", "自定义"),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="once_daily",
        verbose_name="服用频率",
        help_text="药品的服用频率",
    )

    # 单次剂量
    single_dose = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="单次剂量", help_text="每次服用的剂量"
    )

    # 用药说明
    instructions = models.TextField(
        blank=True, null=True, verbose_name="用药说明", help_text="具体的用药指导说明"
    )

    # 服用时间
    administration_times = models.JSONField(
        default=list, verbose_name="服用时间", help_text="每日具体的服用时间列表"
    )

    # 餐前餐后
    MEAL_TIMING_CHOICES = [
        ("before_meal", "餐前"),
        ("after_meal", "餐后"),
        ("with_meal", "餐中"),
        ("empty_stomach", "空腹"),
        ("anytime", "任意时间"),
    ]
    meal_timing = models.CharField(
        max_length=20,
        choices=MEAL_TIMING_CHOICES,
        default="anytime",
        verbose_name="餐前餐后",
        help_text="相对于用餐时间的服药时机",
    )

    # 特殊要求
    special_requirements = models.TextField(
        blank=True, null=True, verbose_name="特殊要求", help_text="特殊的服药要求或注意事项"
    )

    # 是否必需
    is_required = models.BooleanField(
        default=True, verbose_name="是否必需", help_text="是否为必需药品"
    )

    # 替代药品
    alternative_medicine = models.ForeignKey(
        Medicine,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="alternative_for",
        verbose_name="替代药品",
        help_text="可替代的药品",
    )

    # 开始日期（相对于计划）
    start_day = models.PositiveIntegerField(
        default=1, verbose_name="开始天数", help_text="相对于计划开始的第几天开始服用"
    )

    # 持续天数
    duration_days = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="持续天数", help_text="此药品的服用天数，为空表示跟随计划"
    )

    # 剂量调整记录
    dosage_adjustments = models.JSONField(
        default=list, verbose_name="剂量调整记录", help_text="剂量调整的历史记录"
    )

    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="记录创建时间"
    )

    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="更新时间", help_text="记录最后更新时间"
    )

    class Meta:
        db_table = "plan_medicines"
        verbose_name = "计划药品"
        verbose_name_plural = "计划药品"
        indexes = [
            models.Index(fields=["plan_id"], name="idx_plan_medicines_plan_id"),
            models.Index(fields=["medicine_id"], name="idx_plan_medicines_medicine_id"),
            models.Index(fields=["frequency"], name="idx_plan_medicines_frequency"),
            models.Index(fields=["is_required"], name="idx_plan_medicines_required"),
        ]
        unique_together = ["plan", "medicine"]
        ordering = ["start_day", "created_at"]

    def __str__(self):
        return f"{self.plan.name} - {self.medicine.name}"

    @property
    def total_daily_amount(self):
        """
        计算每日总用量
        """
        frequency_multiplier = {
            "once_daily": 1,
            "twice_daily": 2,
            "three_times_daily": 3,
            "four_times_daily": 4,
            "every_other_day": 0.5,
            "weekly": 1 / 7,
        }

        multiplier = frequency_multiplier.get(self.frequency, 1)
        return self.single_dose * multiplier

    def get_administration_schedule(self):
        """
        获取给药时间表
        """
        if self.administration_times:
            return self.administration_times

        # 根据频率生成默认时间表
        default_schedules = {
            "once_daily": ["08:00"],
            "twice_daily": ["08:00", "20:00"],
            "three_times_daily": ["08:00", "14:00", "20:00"],
            "four_times_daily": ["08:00", "12:00", "16:00", "20:00"],
        }

        return default_schedules.get(self.frequency, ["08:00"])

    def calculate_required_quantity(self, days=None):
        """
        计算所需药品数量
        """
        if days is None:
            days = self.duration_days or self.plan.duration_days or 30

        daily_amount = self.total_daily_amount
        return int(daily_amount * days)

    def check_stock_sufficiency(self):
        """
        检查库存是否充足
        """
        required_quantity = self.calculate_required_quantity()
        return self.medicine.quantity >= required_quantity
