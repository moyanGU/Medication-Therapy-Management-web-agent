from rest_framework import serializers
from django.utils import timezone
from .models import Reminder
from apps.medicines.models import Medicine


class ReminderSerializer(serializers.ModelSerializer):
    """
    用药提醒序列化器
    """
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_image = serializers.CharField(source='medicine.image', read_only=True)
    response_rate = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'user', 'medicine', 'medicine_name', 'medicine_image',
            'reminder_time', 'frequency', 'dosage', 'dosage_unit',
            'is_active', 'title', 'message', 'notification_types',
            'advance_minutes', 'repeat_interval', 'max_repeats',
            'start_date', 'end_date', 'weekdays', 'meal_timing',
            'special_instructions', 'last_reminded_at', 'reminder_count',
            'response_count', 'response_rate', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'last_reminded_at', 'reminder_count',
            'response_count', 'created_at', 'updated_at'
        ]
    
    def validate_medicine(self, value):
        """
        验证药品是否属于当前用户
        """
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("只能为自己的药品设置提醒")
        return value
    
    def validate_end_date(self, value):
        """
        验证结束日期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("结束日期不能早于今天")
        return value
    
    def validate(self, attrs):
        """
        整体验证
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")
        
        frequency = attrs.get('frequency')
        weekdays = attrs.get('weekdays', [])
        
        if frequency == 'custom' and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")
        
        return attrs
    
    def create(self, validated_data):
        """
        创建提醒时自动设置用户
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReminderCreateSerializer(serializers.ModelSerializer):
    """
    创建提醒的序列化器
    """
    class Meta:
        model = Reminder
        fields = [
            'medicine', 'reminder_time', 'frequency', 'dosage', 'dosage_unit',
            'is_active', 'title', 'message', 'notification_types',
            'advance_minutes', 'repeat_interval', 'max_repeats',
            'start_date', 'end_date', 'weekdays', 'meal_timing',
            'special_instructions'
        ]
    
    def validate_medicine(self, value):
        """
        验证药品是否属于当前用户
        """
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("只能为自己的药品设置提醒")
        return value
    
    def validate_end_date(self, value):
        """
        验证结束日期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("结束日期不能早于今天")
        return value
    
    def validate(self, attrs):
        """
        整体验证
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")
        
        frequency = attrs.get('frequency')
        weekdays = attrs.get('weekdays', [])
        
        if frequency == 'custom' and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")
        
        return attrs
    
    def create(self, validated_data):
        """
        创建提醒时自动设置用户
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReminderUpdateSerializer(serializers.ModelSerializer):
    """
    更新提醒的序列化器
    """
    class Meta:
        model = Reminder
        fields = [
            'reminder_time', 'frequency', 'dosage', 'dosage_unit',
            'is_active', 'title', 'message', 'notification_types',
            'advance_minutes', 'repeat_interval', 'max_repeats',
            'start_date', 'end_date', 'weekdays', 'meal_timing',
            'special_instructions'
        ]
    
    def validate_end_date(self, value):
        """
        验证结束日期
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("结束日期不能早于今天")
        return value
    
    def validate(self, attrs):
        """
        整体验证
        """
        start_date = attrs.get('start_date', self.instance.start_date)
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")
        
        frequency = attrs.get('frequency', self.instance.frequency)
        weekdays = attrs.get('weekdays', self.instance.weekdays)
        
        if frequency == 'custom' and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")
        
        return attrs


class ReminderListSerializer(serializers.ModelSerializer):
    """
    提醒列表序列化器
    """
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_image = serializers.CharField(source='medicine.image', read_only=True)
    response_rate = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    meal_timing_display = serializers.CharField(source='get_meal_timing_display', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_image',
            'reminder_time', 'frequency', 'frequency_display',
            'dosage', 'dosage_unit', 'is_active', 'title',
            'meal_timing', 'meal_timing_display', 'start_date', 'end_date',
            'reminder_count', 'response_count', 'response_rate',
            'is_expired', 'last_reminded_at', 'created_at'
        ]


class ReminderStatsSerializer(serializers.Serializer):
    """
    提醒统计序列化器
    """
    total_reminders = serializers.IntegerField()
    active_reminders = serializers.IntegerField()
    inactive_reminders = serializers.IntegerField()
    expired_reminders = serializers.IntegerField()
    total_reminder_count = serializers.IntegerField()
    total_response_count = serializers.IntegerField()
    average_response_rate = serializers.FloatField()
    today_reminders = serializers.IntegerField()
    upcoming_reminders = serializers.IntegerField()