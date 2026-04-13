from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditLog(models.Model):
    """
    审计日志模型
    记录用户的敏感操作和数据变更
    """

    ACTION_CHOICES = [
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
        ('ACCESS', '访问'),  # 用于敏感数据查看
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
        ('EXPORT', '导出'),
        ('OTHER', '其他'),
    ]

    # 操作人 (如果为 None 可能是系统自动操作或未登录)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作用户',
        related_name='audit_logs'
    )

    # 操作类型
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='操作类型'
    )

    # 资源类型 (例如: MedicalRecord, Medicine)
    resource_type = models.CharField(
        max_length=100,
        verbose_name='资源类型',
        help_text='被操作对象的模型名称'
    )

    # 资源ID
    resource_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='资源ID'
    )

    # 变更详情 (JSON格式存储前后变化，或者简述)
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='操作详情'
    )

    # IP地址
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP地址'
    )

    # 用户代理
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='用户代理'
    )

    # 操作时间
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='操作时间'
    )

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at}] {self.user} - {self.action} {self.resource_type}"
