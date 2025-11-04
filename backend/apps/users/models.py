from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    自定义用户模型
    继承Django内置的AbstractUser，添加额外字段
    """
    # 在交互式 createsuperuser 时强制要求填写邮箱和手机号
    REQUIRED_FIELDS = ['email', 'phone']

    phone = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='手机号',
        help_text='用户手机号码'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='邮箱',
        help_text='用户邮箱地址'
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name='管理员',
        help_text='是否为管理员用户'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    avatar = models.URLField(
        blank=True,
        null=True,
        verbose_name='头像',
        help_text='用户头像URL'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='出生日期'
    )
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', '男'),
            ('female', '女'),
            ('other', '其他')
        ],
        blank=True,
        null=True,
        verbose_name='性别'
    )
    emergency_contact = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='紧急联系人',
        help_text='紧急联系人姓名'
    )
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='紧急联系电话',
        help_text='紧急联系人电话'
    )
    
    # 解决与Django内置User模型的冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['phone'], name='idx_users_phone'),
            models.Index(fields=['username'], name='idx_users_username'),
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['created_at'], name='idx_users_created_at'),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.phone})"
    
    def get_full_name(self):
        """
        获取用户全名
        """
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """
        获取用户简称
        """
        return self.first_name or self.username
    
    @property
    def age(self):
        """
        计算用户年龄
        """
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None