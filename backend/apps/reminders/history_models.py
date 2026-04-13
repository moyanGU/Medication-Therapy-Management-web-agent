from django.db import models
from django.utils import timezone

from apps.users.models import User

from .models import Reminder


class ReminderHistory(models.Model):
    """
    提醒历史记录模型
    记录每次提醒的发送和响应情况
    """

    # 关联提醒
    reminder = models.ForeignKey(
        Reminder,
        on_delete=models.CASCADE,
        related_name="history_records",
        verbose_name="提醒",
        help_text="关联的提醒设置",
    )

    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reminder_history",
        verbose_name="用户",
        help_text="提醒的用户",
    )

    # 提醒发送时间
    sent_at = models.DateTimeField(
        default=timezone.now, verbose_name="发送时间", help_text="提醒发送的时间"
    )

    # 计划提醒时间
    scheduled_time = models.DateTimeField(verbose_name="计划时间", help_text="原计划的提醒时间")

    # 提醒类型
    REMINDER_TYPE_CHOICES = [
        ("scheduled", "定时提醒"),
        ("repeat", "重复提醒"),
        ("manual", "手动提醒"),
        ("makeup", "补服提醒"),
    ]
    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default="scheduled",
        verbose_name="提醒类型",
        help_text="提醒的类型",
    )

    # 提醒标题
    title = models.CharField(max_length=200, verbose_name="提醒标题", help_text="发送的提醒标题")

    # 提醒内容
    message = models.TextField(verbose_name="提醒内容", help_text="发送的提醒内容")

    # 通知方式
    notification_methods = models.JSONField(
        default=list, verbose_name="通知方式", help_text="使用的通知方式列表"
    )

    # 发送状态
    STATUS_CHOICES = [
        ("sent", "已发送"),
        ("failed", "发送失败"),
        ("pending", "待发送"),
        ("cancelled", "已取消"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="sent",
        verbose_name="发送状态",
        help_text="提醒的发送状态",
    )

    # 用户响应时间
    responded_at = models.DateTimeField(
        blank=True, null=True, verbose_name="响应时间", help_text="用户响应提醒的时间"
    )

    # 响应类型
    RESPONSE_TYPE_CHOICES = [
        ("taken", "已服用"),
        ("skipped", "跳过"),
        ("delayed", "延迟"),
        ("ignored", "忽略"),
        ("no_response", "无响应"),
    ]
    response_type = models.CharField(
        max_length=20,
        choices=RESPONSE_TYPE_CHOICES,
        default="no_response",
        verbose_name="响应类型",
        help_text="用户的响应类型",
    )

    # 响应延迟时间（分钟）
    response_delay_minutes = models.IntegerField(
        blank=True, null=True, verbose_name="响应延迟（分钟）", help_text="从发送到响应的延迟时间"
    )

    # 备注
    notes = models.TextField(
        blank=True, null=True, verbose_name="备注", help_text="额外的备注信息"
    )

    # 设备信息
    device_info = models.JSONField(
        default=dict, blank=True, verbose_name="设备信息", help_text="发送通知时的设备信息"
    )

    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="记录创建时间"
    )

    class Meta:
        db_table = "reminder_history"
        verbose_name = "提醒历史记录"
        verbose_name_plural = "提醒历史记录"
        indexes = [
            models.Index(fields=["user_id"], name="idx_reminder_history_user"),
            models.Index(fields=["reminder_id"], name="idx_reminder_history_reminder"),
            models.Index(fields=["sent_at"], name="idx_reminder_history_sent_at"),
            models.Index(fields=["status"], name="idx_reminder_history_status"),
            models.Index(
                fields=["response_type"], name="idx_reminder_history_response"
            ),
            models.Index(
                fields=["user_id", "sent_at"], name="idx_reminder_history_user_sent"
            ),
        ]
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.user.username} - {self.reminder.medicine.name} - {self.sent_at}"

    @property
    def is_responded(self):
        """
        是否已响应
        """
        return self.response_type != "no_response"

    @property
    def is_successful(self):
        """
        是否成功（已发送且已响应）
        """
        return self.status == "sent" and self.is_responded

    def mark_responded(self, response_type, notes=None):
        """
        标记用户已响应
        """
        self.responded_at = timezone.now()
        self.response_type = response_type

        # 计算响应延迟
        if self.sent_at:
            delay = self.responded_at - self.sent_at
            self.response_delay_minutes = int(delay.total_seconds() / 60)

        if notes:
            self.notes = notes

        self.save(
            update_fields=[
                "responded_at",
                "response_type",
                "response_delay_minutes",
                "notes",
            ]
        )

    def get_response_delay_display(self):
        """
        获取响应延迟的显示文本
        """
        if not self.response_delay_minutes:
            return "无延迟"

        if self.response_delay_minutes < 60:
            return f"{self.response_delay_minutes}分钟"
        else:
            hours = self.response_delay_minutes // 60
            minutes = self.response_delay_minutes % 60
            if minutes > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{hours}小时"


class ReminderStats(models.Model):
    """
    提醒统计模型
    按日期汇总提醒统计数据
    """

    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reminder_stats",
        verbose_name="用户",
        help_text="统计的用户",
    )

    # 统计日期
    date = models.DateField(verbose_name="统计日期", help_text="统计的日期")

    # 计划提醒数
    scheduled_count = models.PositiveIntegerField(
        default=0, verbose_name="计划提醒数", help_text="当日计划的提醒数量"
    )

    # 实际发送数
    sent_count = models.PositiveIntegerField(
        default=0, verbose_name="实际发送数", help_text="当日实际发送的提醒数量"
    )

    # 用户响应数
    responded_count = models.PositiveIntegerField(
        default=0, verbose_name="用户响应数", help_text="当日用户响应的提醒数量"
    )

    # 已服用数
    taken_count = models.PositiveIntegerField(
        default=0, verbose_name="已服用数", help_text="当日标记为已服用的数量"
    )

    # 跳过数
    skipped_count = models.PositiveIntegerField(
        default=0, verbose_name="跳过数", help_text="当日跳过的提醒数量"
    )

    # 延迟数
    delayed_count = models.PositiveIntegerField(
        default=0, verbose_name="延迟数", help_text="当日延迟的提醒数量"
    )

    # 忽略数
    ignored_count = models.PositiveIntegerField(
        default=0, verbose_name="忽略数", help_text="当日忽略的提醒数量"
    )

    # 平均响应时间（分钟）
    avg_response_time = models.FloatField(
        default=0, verbose_name="平均响应时间（分钟）", help_text="当日平均响应时间"
    )

    # 响应率
    response_rate = models.FloatField(
        default=0, verbose_name="响应率（%）", help_text="当日的响应率百分比"
    )

    # 服药率
    adherence_rate = models.FloatField(
        default=0, verbose_name="服药率（%）", help_text="当日的服药率百分比"
    )

    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="统计创建时间"
    )

    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="更新时间", help_text="统计更新时间"
    )

    class Meta:
        db_table = "reminder_stats"
        verbose_name = "提醒统计"
        verbose_name_plural = "提醒统计"
        unique_together = ["user", "date"]
        indexes = [
            models.Index(fields=["user_id"], name="idx_reminder_stats_user"),
            models.Index(fields=["date"], name="idx_reminder_stats_date"),
            models.Index(
                fields=["user_id", "date"], name="idx_reminder_stats_user_date"
            ),
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date} - 响应率{self.response_rate:.1f}%"

    def calculate_rates(self):
        """
        计算响应率和服药率
        """
        if self.sent_count > 0:
            self.response_rate = (self.responded_count / self.sent_count) * 100
            self.adherence_rate = (self.taken_count / self.sent_count) * 100
        else:
            self.response_rate = 0
            self.adherence_rate = 0

    def update_from_history(self):
        """
        从历史记录更新统计数据
        """
        from django.db.models import Avg

        history_records = ReminderHistory.objects.filter(
            user=self.user, sent_at__date=self.date
        )

        self.sent_count = history_records.filter(status="sent").count()
        self.responded_count = history_records.exclude(
            response_type="no_response"
        ).count()
        self.taken_count = history_records.filter(response_type="taken").count()
        self.skipped_count = history_records.filter(response_type="skipped").count()
        self.delayed_count = history_records.filter(response_type="delayed").count()
        self.ignored_count = history_records.filter(response_type="ignored").count()

        # 计算平均响应时间
        avg_time = history_records.filter(
            response_delay_minutes__isnull=False
        ).aggregate(avg=Avg("response_delay_minutes"))["avg"]
        self.avg_response_time = avg_time or 0

        # 计算率
        self.calculate_rates()

        self.save()
