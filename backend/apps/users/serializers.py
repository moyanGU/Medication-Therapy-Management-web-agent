from rest_framework import serializers
from .models import User
from .models import PushSubscription

class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    - 输出字段使用 snake_case，前端在 store 中做 camelCase 映射
    - 更新时仅允许部分资料字段可写
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email', 'avatar', 'birth_date', 'gender',
            'emergency_contact', 'emergency_phone', 'is_admin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_admin', 'created_at', 'updated_at', 'username', 'phone']

    def validate_gender(self, value):
        if value and value not in ['male', 'female', 'other']:
            raise serializers.ValidationError('性别必须是 male/female/other 之一')
        return value


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """
    Push 订阅序列化器
    - 验证 keys 中包含 p256dh 与 auth
    - 读取/写入 UA、时区、应用标识
    """
    class Meta:
        model = PushSubscription
        fields = [
            'id', 'endpoint', 'keys', 'expiration_time', 'user_agent', 'time_zone', 'app',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']

    def validate_keys(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('keys 必须为对象')
        if 'p256dh' not in value or 'auth' not in value:
            raise serializers.ValidationError('keys 必须包含 p256dh 与 auth 字段')
        return value