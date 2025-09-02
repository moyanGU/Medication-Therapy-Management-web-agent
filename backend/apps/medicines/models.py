from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.users.models import User


class Medicine(models.Model):
    """
    药品模型，存储药品基本信息
    """
    # 关联用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medicines',
        verbose_name='用户',
        help_text='药品所属用户'
    )
    
    # 药品名称
    name = models.CharField(
        max_length=100,
        verbose_name='药品名称',
        help_text='药品的通用名称或商品名称'
    )
    
    # 药品规格
    specification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='药品规格',
        help_text='药品规格，如"100mg*30片"'
    )
    
    # 生产厂家
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='生产厂家',
        help_text='药品生产厂家名称'
    )
    
    # 有效期
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='有效期',
        help_text='药品有效期至日期'
    )
    
    # 药品数量
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='药品数量',
        help_text='当前库存数量'
    )
    
    # 存储条件
    storage_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name='存储条件',
        help_text='药品存储要求，如温度、湿度、光照等条件'
    )
    
    # 药品图片
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='药品图片URL',
        help_text='药品图片的存储URL'
    )
    
    # 药品描述
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='药品描述',
        help_text='药品的详细描述信息'
    )
    
    # 药品类型
    MEDICINE_TYPE_CHOICES = [
        ('tablet', '片剂'),
        ('capsule', '胶囊'),
        ('liquid', '液体'),
        ('injection', '注射剂'),
        ('ointment', '软膏'),
        ('drops', '滴剂'),
        ('other', '其他'),
    ]
    medicine_type = models.CharField(
        max_length=20,
        choices=MEDICINE_TYPE_CHOICES,
        default='tablet',
        verbose_name='药品类型',
        help_text='药品的剂型类型'
    )
    
    # 处方药标识
    is_prescription = models.BooleanField(
        default=False,
        verbose_name='是否为处方药',
        help_text='标识是否为处方药'
    )
    
    # 药品批号
    batch_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='药品批号',
        help_text='药品生产批号'
    )
    
    # 购买日期
    purchase_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='购买日期',
        help_text='药品购买日期'
    )
    
    # 购买价格
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='购买价格',
        help_text='药品购买价格'
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
        db_table = 'medicines'
        verbose_name = '药品'
        verbose_name_plural = '药品'
        indexes = [
            models.Index(fields=['user_id'], name='idx_medicines_user_id'),
            models.Index(fields=['name'], name='idx_medicines_name'),
            models.Index(fields=['expiry_date'], name='idx_medicines_expiry_date'),
            models.Index(fields=['created_at'], name='idx_medicines_created_at'),
            models.Index(fields=['medicine_type'], name='idx_medicines_type'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def is_expired(self):
        """
        检查药品是否已过期
        """
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def days_until_expiry(self):
        """
        计算距离过期还有多少天
        """
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_low_stock(self, threshold=5):
        """
        检查是否库存不足
        """
        return self.quantity <= threshold
    
    def get_storage_requirements(self):
        """
        获取存储要求的结构化信息
        """
        if self.storage_conditions:
            return {
                'conditions': self.storage_conditions,
                'type': self.medicine_type,
                'is_prescription': self.is_prescription
            }
        return None