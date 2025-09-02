from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.medicines.models import Medicine


class Reminder(models.Model):
    """
    用药提醒模型，管理用户的用药提醒设置
    """
    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name='用户',
        help_text='提醒所属用户'
    )
    
    # 关联药品
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name='药品',
        help_text='需要提醒的药品'
    )
    
    # 提醒时间
    reminder_time = models.TimeField(
        verbose_name='提醒时间',
        help_text='每日提醒的具体时间'
    )
    
    # 提醒频率
    FREQUENCY_CHOICES = [
        ('daily', '每日'),
        ('twice_daily', '每日两次'),
        ('three_times_daily', '每日三次'),
        ('four_times_daily', '每日四次'),
        ('every_other_day', '隔日'),
        ('weekly', '每周'),
        ('as_needed', '按需'),
        ('custom', '自定义'),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        verbose_name='提醒频率',
        help_text='用药提醒的频率'
    )
    
    # 每次剂量
    dosage = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='每次剂量',
        help_text='每次服用的药品数量'
    )
    
    # 剂量单位
    DOSAGE_UNIT_CHOICES = [
        ('tablet', '片'),
        ('capsule', '粒'),
        ('ml', '毫升'),
        ('mg', '毫克'),
        ('drop', '滴'),
        ('spray', '喷'),
        ('other', '其他'),
    ]
    dosage_unit = models.CharField(
        max_length=20,
        choices=DOSAGE_UNIT_CHOICES,
        default='tablet',
        verbose_name='剂量单位',
        help_text='剂量的计量单位'
    )
    
    # 是否激活
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否激活',
        help_text='提醒是否处于激活状态'
    )
    
    # 提醒标题
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='提醒标题',
        help_text='自定义提醒标题'
    )
    
    # 提醒内容
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name='提醒内容',
        help_text='自定义提醒内容'
    )
    
    # 提醒方式
    NOTIFICATION_TYPE_CHOICES = [
        ('push', '推送通知'),
        ('sms', '短信'),
        ('email', '邮件'),
        ('sound', '声音提醒'),
        ('vibration', '震动'),
    ]
    notification_types = models.JSONField(
        default=list,
        verbose_name='提醒方式',
        help_text='提醒的通知方式列表'
    )
    
    # 提前提醒时间（分钟）
    advance_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1440)],  # 最多提前24小时
        verbose_name='提前提醒时间（分钟）',
        help_text='提前多少分钟进行提醒'
    )
    
    # 重复提醒间隔（分钟）
    repeat_interval = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(60)],  # 最多每小时重复一次
        verbose_name='重复提醒间隔（分钟）',
        help_text='重复提醒的间隔时间，0表示不重复'
    )
    
    # 最大重复次数
    max_repeats = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10)],
        verbose_name='最大重复次数',
        help_text='最多重复提醒的次数'
    )
    
    # 开始日期
    start_date = models.DateField(
        default=timezone.now,
        verbose_name='开始日期',
        help_text='提醒开始的日期'
    )
    
    # 结束日期
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='结束日期',
        help_text='提醒结束的日期，为空表示长期提醒'
    )
    
    # 星期设置（用于自定义频率）
    weekdays = models.JSONField(
        default=list,
        verbose_name='星期设置',
        help_text='自定义频率时的星期设置，1-7表示周一到周日'
    )
    
    # 餐前餐后设置
    MEAL_TIMING_CHOICES = [
        ('before_meal', '餐前'),
        ('after_meal', '餐后'),
        ('with_meal', '餐中'),
        ('empty_stomach', '空腹'),
        ('anytime', '任意时间'),
    ]
    meal_timing = models.CharField(
        max_length=20,
        choices=MEAL_TIMING_CHOICES,
        default='anytime',
        verbose_name='餐前餐后',
        help_text='相对于用餐时间的服药时机'
    )
    
    # 特殊说明
    special_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name='特殊说明',
        help_text='特殊的用药说明或注意事项'
    )
    
    # 最后提醒时间
    last_reminded_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='最后提醒时间',
        help_text='最后一次发送提醒的时间'
    )
    
    # 提醒次数统计
    reminder_count = models.PositiveIntegerField(
        default=0,
        verbose_name='提醒次数',
        help_text='累计提醒次数'
    )
    
    # 响应次数统计
    response_count = models.PositiveIntegerField(
        default=0,
        verbose_name='响应次数',
        help_text='用户响应提醒的次数'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间',
        help_text='提醒创建时间'
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='提醒最后更新时间'
    )
    
    class Meta:
        db_table = 'reminders'
        verbose_name = '用药提醒'
        verbose_name_plural = '用药提醒'
        indexes = [
            models.Index(fields=['user_id'], name='idx_reminders_user_id'),
            models.Index(fields=['medicine_id'], name='idx_reminders_medicine_id'),
            models.Index(fields=['is_active'], name='idx_reminders_is_active'),
            models.Index(fields=['reminder_time'], name='idx_reminders_time'),
            models.Index(fields=['start_date'], name='idx_reminders_start_date'),
            models.Index(fields=['end_date'], name='idx_reminders_end_date'),
            models.Index(fields=['user_id', 'is_active'], name='idx_reminders_user_active'),
        ]
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.medicine.name} - {self.reminder_time}"
    
    @property
    def response_rate(self):
        """
        计算响应率
        """
        if self.reminder_count == 0:
            return 0
        return (self.response_count / self.reminder_count) * 100
    
    @property
    def is_expired(self):
        """
        检查提醒是否已过期
        """
        if self.end_date:
            return self.end_date < timezone.now().date()
        return False
    
    def should_remind_today(self):
        """
        检查今天是否应该提醒
        """
        today = timezone.now().date()
        
        # 检查是否在有效期内
        if today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        
        # 检查是否激活
        if not self.is_active:
            return False
        
        # 根据频率判断
        if self.frequency == 'daily':
            return True
        elif self.frequency == 'every_other_day':
            days_diff = (today - self.start_date).days
            return days_diff % 2 == 0
        elif self.frequency == 'weekly':
            days_diff = (today - self.start_date).days
            return days_diff % 7 == 0
        elif self.frequency == 'custom':
            weekday = today.weekday() + 1  # 转换为1-7
            return weekday in self.weekdays
        
        return True
    
    def get_next_reminder_time(self):
        """
        获取下次提醒时间
        """
        now = timezone.now()
        today = now.date()
        
        # 构建今天的提醒时间
        reminder_datetime = timezone.datetime.combine(today, self.reminder_time)
        reminder_datetime = timezone.make_aware(reminder_datetime)
        
        # 如果今天的提醒时间已过，计算明天或下次的提醒时间
        if reminder_datetime <= now:
            if self.frequency == 'daily':
                reminder_datetime += timezone.timedelta(days=1)
            elif self.frequency == 'every_other_day':
                reminder_datetime += timezone.timedelta(days=2)
            elif self.frequency == 'weekly':
                reminder_datetime += timezone.timedelta(days=7)
        
        return reminder_datetime
    
    def increment_reminder_count(self):
        """
        增加提醒次数
        """
        self.reminder_count += 1
        self.last_reminded_at = timezone.now()
        self.save(update_fields=['reminder_count', 'last_reminded_at'])
    
    def increment_response_count(self):
        """
        增加响应次数
        """
        self.response_count += 1
        self.save(update_fields=['response_count'])
    
    def get_default_message(self):
        """
        获取默认提醒消息
        """
        if self.message:
            return self.message
        
        meal_text = dict(self.MEAL_TIMING_CHOICES).get(self.meal_timing, '')
        return f"该服用 {self.medicine.name} 了！剂量：{self.dosage}{dict(self.DOSAGE_UNIT_CHOICES).get(self.dosage_unit)}，{meal_text}"