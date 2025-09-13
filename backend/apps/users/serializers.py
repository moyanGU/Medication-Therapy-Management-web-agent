from rest_framework import serializers
from .models import User

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