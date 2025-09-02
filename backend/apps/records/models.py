from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.medicines.models import Medicine


class MedicationRecord(models.Model):
    """
    用药记录模型，记录用户的用药历史
    """
    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medication_records',
        verbose_name='用户',
        help_text='用药记录所属用户'
    )
    
    # 关联药品
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='medication_records',
        verbose_name='药品',
        help_text='服用的药品'
    )
    
    # 服药时间
    taken_at = models.DateTimeField(
        verbose_name='服药时间',
        help_text='实际服药的时间'
    )
    
    # 服药数量
    quantity_taken = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='服药数量',
        help_text='本次服用的药品数量'
    )
    
    # 服药方式
    ADMINISTRATION_CHOICES = [
        ('oral', '口服'),
        ('injection', '注射'),
        ('topical', '外用'),
        ('inhalation', '吸入'),
        ('sublingual', '舌下含服'),
        ('rectal', '直肠给药'),
        ('other', '其他'),
    ]
    administration_method = models.CharField(
        max_length=20,
        choices=ADMINISTRATION_CHOICES,
        default='oral',
        verbose_name='服药方式',
        help_text='药品的给药方式'
    )
    
    # 服药状态
    STATUS_CHOICES = [
        ('taken', '已服用'),
        ('missed', '漏服'),
        ('delayed', '延迟服用'),
        ('partial', '部分服用'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='taken',
        verbose_name='服药状态',
        help_text='本次服药的状态'
    )
    
    # 服药备注
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='服药备注',
        help_text='服药时的备注信息，如副作用、感受等'
    )
    
    # 症状评分（1-10分）
    symptom_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='症状评分',
        help_text='服药前症状严重程度评分（1-10分）'
    )
    
    # 效果评分（1-10分）
    effectiveness_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='效果评分',
        help_text='服药后效果评分（1-10分）'
    )
    
    # 副作用记录
    side_effects = models.TextField(
        blank=True,
        null=True,
        verbose_name='副作用',
        help_text='服药后出现的副作用描述'
    )
    
    # 是否按时服药
    is_on_time = models.BooleanField(
        default=True,
        verbose_name='是否按时服药',
        help_text='是否按照预定时间服药'
    )
    
    # 延迟时间（分钟）
    delay_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='延迟时间（分钟）',
        help_text='相对于预定时间的延迟分钟数'
    )
    
    # 记录来源
    SOURCE_CHOICES = [
        ('manual', '手动记录'),
        ('reminder', '提醒记录'),
        ('import', '导入记录'),
        ('auto', '自动记录'),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual',
        verbose_name='记录来源',
        help_text='记录的创建来源'
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
        db_table = 'medication_records'
        verbose_name = '用药记录'
        verbose_name_plural = '用药记录'
        indexes = [
            models.Index(fields=['user'], name='idx_med_rec_user'),
            models.Index(fields=['medicine'], name='idx_med_rec_medicine'),
            models.Index(fields=['taken_at'], name='idx_med_rec_taken'),
            models.Index(fields=['user', 'taken_at'], name='idx_med_rec_user_taken'),
            models.Index(fields=['created_at'], name='idx_med_rec_created'),
        ]
        ordering = ['-taken_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.medicine.name} - {self.taken_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def adherence_score(self):
        """
        计算依从性评分
        """
        score = 100
        
        # 根据服药状态扣分
        if self.status == 'missed':
            score = 0
        elif self.status == 'partial':
            score = 50
        elif self.status == 'delayed':
            if self.delay_minutes:
                # 延迟超过30分钟开始扣分
                if self.delay_minutes > 30:
                    score = max(70, 100 - (self.delay_minutes - 30) * 2)
        
        return score
    
    def get_time_difference(self, scheduled_time):
        """
        计算与预定时间的差异
        """
        if scheduled_time:
            delta = self.taken_at - scheduled_time
            return delta.total_seconds() / 60  # 返回分钟数
        return None
    
    @classmethod
    def get_adherence_rate(cls, user, start_date=None, end_date=None):
        """
        计算用户在指定时间段内的依从性率
        """
        queryset = cls.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(taken_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(taken_at__lte=end_date)
        
        total_records = queryset.count()
        if total_records == 0:
            return 0
        
        taken_records = queryset.filter(status='taken').count()
        return (taken_records / total_records) * 100
    
    def save(self, *args, **kwargs):
        """
        保存时的自动处理
        """
        # 如果是延迟服药，自动设置is_on_time为False
        if self.status == 'delayed':
            self.is_on_time = False
        
        super().save(*args, **kwargs)
        
        # 更新药品库存
        if self.status in ['taken', 'partial']:
            self.medicine.quantity = max(0, self.medicine.quantity - self.quantity_taken)
            self.medicine.save(update_fields=['quantity'])