from rest_framework import serializers
from django.utils import timezone
from .models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    """
    药品序列化器
    用于药品数据的序列化和反序列化
    """
    # 只读字段
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    # 用户字段（从请求中获取，不需要在创建时传递）
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    # 使用CharField存储图片文件路径
    image_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'user', 'name', 'specification', 'manufacturer',
            'expiry_date', 'quantity', 'storage_conditions', 'image_path',
            'description', 'medicine_type', 'is_prescription', 'batch_number',
            'purchase_date', 'purchase_price', 'created_at', 'updated_at',
            'is_expired', 'days_until_expiry', 'is_low_stock'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'days_until_expiry', 'is_low_stock']
    
    def validate_name(self, value):
        """
        验证药品名称
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("药品名称至少需要2个字符")
        return value.strip()
    
    def validate_quantity(self, value):
        """
        验证药品数量
        """
        if value < 0:
            raise serializers.ValidationError("药品数量不能为负数")
        return value
    
    def validate_expiry_date(self, value):
        """
        验证有效期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("有效期不能早于今天")
        return value
    
    def validate_purchase_price(self, value):
        """
        验证购买价格
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("购买价格不能为负数")
        return value
    
    def validate_image_path(self, value):
        """
        验证图片路径
        """
        # 如果值为空或None，直接返回None
        if not value or value.strip() == '':
            return None
        return value
    
    def validate(self, attrs):
        """
        整体数据验证
        """
        # 验证购买日期不能晚于有效期
        purchase_date = attrs.get('purchase_date')
        expiry_date = attrs.get('expiry_date')
        
        if purchase_date and expiry_date and purchase_date > expiry_date:
            raise serializers.ValidationError("购买日期不能晚于有效期")
        
        return attrs


class MedicineListSerializer(serializers.ModelSerializer):
    """
    药品列表序列化器
    用于列表展示，包含较少字段以提高性能
    """
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    medicine_type_display = serializers.CharField(source='get_medicine_type_display', read_only=True)
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'name', 'specification', 'manufacturer', 'expiry_date',
            'quantity', 'medicine_type', 'medicine_type_display', 'is_prescription',
            'image_path', 'created_at', 'is_expired', 'days_until_expiry', 'is_low_stock'
        ]


class MedicineCreateSerializer(serializers.ModelSerializer):
    """
    药品创建序列化器
    用于创建新药品时的数据验证
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # 使用CharField存储图片文件路径
    image_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Medicine
        fields = [
            'user', 'name', 'specification', 'manufacturer', 'expiry_date',
            'quantity', 'storage_conditions', 'image_path', 'description',
            'medicine_type', 'is_prescription', 'batch_number', 'purchase_date',
            'purchase_price'
        ]
    
    def validate_name(self, value):
        """
        验证药品名称
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("药品名称至少需要2个字符")
        return value.strip()
    
    def validate_quantity(self, value):
        """
        验证药品数量
        """
        if value < 0:
            raise serializers.ValidationError("药品数量不能为负数")
        return value
    
    def validate_expiry_date(self, value):
        """
        验证有效期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("有效期不能早于今天")
        return value
    
    def validate_image_path(self, value):
        """
        验证图片路径 - 支持可选路径
        """
        # 如果值为空或None，直接返回None
        if not value or value.strip() == '':
            return None
        return value
    
    def create(self, validated_data):
        """
        创建药品实例
        """
        # 如果image_path为None或空字符串，不设置该字段
        if 'image_path' in validated_data and not validated_data['image_path']:
            validated_data['image_path'] = None
            
        return super().create(validated_data)


class MedicineUpdateSerializer(serializers.ModelSerializer):
    """
    药品更新序列化器
    用于更新药品信息
    """
    # 使用CharField存储图片文件路径
    image_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Medicine
        fields = [
            'name', 'specification', 'manufacturer', 'expiry_date',
            'quantity', 'storage_conditions', 'image_path', 'description',
            'medicine_type', 'is_prescription', 'batch_number', 'purchase_date',
            'purchase_price'
        ]
    
    def validate_name(self, value):
        """
        验证药品名称
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("药品名称至少需要2个字符")
        return value.strip()
    
    def validate_quantity(self, value):
        """
        验证药品数量
        """
        if value < 0:
            raise serializers.ValidationError("药品数量不能为负数")
        return value
    
    def validate_expiry_date(self, value):
        """
        验证有效期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("有效期不能早于今天")
        return value
    
    def validate_image_path(self, value):
        """
        验证图片路径
        """
        # 如果值为空或None，直接返回None
        if not value or value.strip() == '':
            return None
        return value