from rest_framework import serializers
from django.utils import timezone
from .models import MedicationRecord
from apps.medicines.models import Medicine
from apps.users.models import User


class MedicationRecordSerializer(serializers.ModelSerializer):
    """
    用药记录序列化器
    """
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_specification = serializers.CharField(source='medicine.specification', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    adherence_score = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicationRecord
        fields = [
            'id', 'user', 'medicine', 'taken_at', 'quantity_taken',
            'administration_method', 'status', 'notes', 'symptom_score',
            'effectiveness_score', 'side_effects', 'is_on_time',
            'delay_minutes', 'source', 'created_at', 'updated_at',
            'medicine_name', 'medicine_specification', 'user_name',
            'adherence_score'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def validate_taken_at(self, value):
        """
        验证服药时间不能是未来时间
        """
        if value > timezone.now():
            raise serializers.ValidationError("服药时间不能是未来时间")
        return value
    
    def validate_quantity_taken(self, value):
        """
        验证服药数量
        """
        if value <= 0:
            raise serializers.ValidationError("服药数量必须大于0")
        return value
    
    def validate_medicine(self, value):
        """
        验证药品是否属于当前用户
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("只能为自己的药品创建用药记录")
        return value
    
    def validate(self, attrs):
        """
        整体数据验证
        """
        # 如果状态是延迟服用，必须提供延迟时间
        if attrs.get('status') == 'delayed' and not attrs.get('delay_minutes'):
            raise serializers.ValidationError({
                'delay_minutes': '延迟服用状态必须提供延迟时间'
            })
        
        # 如果状态是漏服，不应该有服药数量
        if attrs.get('status') == 'missed' and attrs.get('quantity_taken', 0) > 0:
            raise serializers.ValidationError({
                'quantity_taken': '漏服状态下服药数量应为0'
            })
        
        return attrs


class MedicationRecordCreateSerializer(MedicationRecordSerializer):
    """
    用药记录创建序列化器
    """
    def create(self, validated_data):
        """
        创建用药记录
        """
        # 自动设置用户为当前登录用户
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        # 根据延迟时间自动设置是否按时服药
        delay_minutes = validated_data.get('delay_minutes', 0)
        if delay_minutes and delay_minutes > 15:  # 超过15分钟算延迟
            validated_data['is_on_time'] = False
        
        return super().create(validated_data)


class MedicationRecordListSerializer(serializers.ModelSerializer):
    """
    用药记录列表序列化器（简化版）
    """
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_image = serializers.URLField(source='medicine.image_url', read_only=True)
    adherence_score = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicationRecord
        fields = [
            'id', 'medicine_name', 'medicine_image', 'taken_at',
            'quantity_taken', 'status', 'adherence_score', 'created_at'
        ]


class MedicationRecordStatsSerializer(serializers.Serializer):
    """
    用药记录统计序列化器
    """
    total_records = serializers.IntegerField()
    taken_count = serializers.IntegerField()
    missed_count = serializers.IntegerField()
    delayed_count = serializers.IntegerField()
    adherence_rate = serializers.FloatField()
    avg_effectiveness = serializers.FloatField()
    most_used_medicine = serializers.CharField()
    daily_average = serializers.FloatField()