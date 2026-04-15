from django.utils import timezone
from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    """
    用药提醒序列化器
    """

    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_image = serializers.CharField(source="medicine.image", read_only=True)
    response_rate = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Reminder
        fields = [
            "id",
            "user",
            "medicine",
            "medicine_name",
            "medicine_image",
            "reminder_time",
            "frequency",
            "dosage",
            "dosage_unit",
            "is_active",
            "title",
            "message",
            "notification_types",
            "advance_minutes",
            "repeat_interval",
            "max_repeats",
            "start_date",
            "end_date",
            "weekdays",
            "meal_timing",
            "special_instructions",
            "last_reminded_at",
            "reminder_count",
            "response_count",
            "response_rate",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "last_reminded_at",
            "reminder_count",
            "response_count",
            "created_at",
            "updated_at",
        ]

    def validate_medicine(self, value):
        """
        验证药品是否属于当前用户
        """
        user = self.context["request"].user
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
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")

        frequency = attrs.get("frequency")
        weekdays = attrs.get("weekdays", [])

        if frequency == "custom" and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")

        return attrs

    def create(self, validated_data):
        """
        创建提醒时自动设置用户
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReminderCreateSerializer(serializers.ModelSerializer):
    """
    创建提醒的序列化器
    """

    class Meta:
        model = Reminder
        fields = [
            "medicine",
            "reminder_time",
            "frequency",
            "dosage",
            "dosage_unit",
            "is_active",
            "title",
            "message",
            "notification_types",
            "advance_minutes",
            "repeat_interval",
            "max_repeats",
            "start_date",
            "end_date",
            "weekdays",
            "meal_timing",
            "special_instructions",
        ]

    def validate_medicine(self, value):
        """
        验证药品是否属于当前用户
        """
        user = self.context["request"].user
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
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")

        frequency = attrs.get("frequency")
        weekdays = attrs.get("weekdays", [])

        if frequency == "custom" and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")

        return attrs

    def create(self, validated_data):
        """
        创建提醒时自动设置用户
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReminderUpdateSerializer(serializers.ModelSerializer):
    """
    更新提醒的序列化器
    """

    class Meta:
        model = Reminder
        fields = [
            "reminder_time",
            "frequency",
            "dosage",
            "dosage_unit",
            "is_active",
            "title",
            "message",
            "notification_types",
            "advance_minutes",
            "repeat_interval",
            "max_repeats",
            "start_date",
            "end_date",
            "weekdays",
            "meal_timing",
            "special_instructions",
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
        start_date = attrs.get("start_date", self.instance.start_date)
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")

        frequency = attrs.get("frequency", self.instance.frequency)
        weekdays = attrs.get("weekdays", self.instance.weekdays)

        if frequency == "custom" and not weekdays:
            raise serializers.ValidationError("自定义频率时必须设置星期")

        return attrs


class ReminderConfirmSerializer(serializers.Serializer):
    """
    提醒确认动作序列化器
    """

    ACTION_CHOICES = [
        ("taken", "已服药"),
        ("missed", "漏服"),
        ("delayed", "延迟服药"),
        ("partial", "部分服用"),
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True)
    taken_at = serializers.DateTimeField(required=False)
    delay_minutes = serializers.IntegerField(required=False, min_value=1, max_value=1440)
    quantity_taken = serializers.IntegerField(required=False, min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_taken_at(self, value):
        """
        验证实际服药时间不能晚于当前时间
        """
        if value > timezone.now():
            raise serializers.ValidationError("实际服药时间不能是未来时间")
        return value

    def validate(self, attrs):
        """
        根据动作类型校验附加参数
        """
        action = attrs.get("action")
        delay_minutes = attrs.get("delay_minutes")
        quantity_taken = attrs.get("quantity_taken")
        reminder = self.context.get("reminder")

        if action == "delayed" and not delay_minutes:
            raise serializers.ValidationError({"delay_minutes": "延迟服药必须提供延迟分钟数"})

        if action == "partial":
            if not quantity_taken:
                raise serializers.ValidationError({"quantity_taken": "部分服用必须提供实际服药数量"})
            if reminder and quantity_taken >= reminder.dosage:
                raise serializers.ValidationError(
                    {"quantity_taken": "部分服用数量必须小于提醒剂量，完整服用请使用 taken"}
                )

        if action == "missed":
            if quantity_taken is not None:
                raise serializers.ValidationError({"quantity_taken": "漏服动作不应传入服药数量"})
            if delay_minutes is not None:
                raise serializers.ValidationError({"delay_minutes": "漏服动作不应传入延迟时间"})

        if action == "taken":
            if delay_minutes is not None:
                raise serializers.ValidationError({"delay_minutes": "已服药动作不应传入延迟时间"})

        return attrs


class ReminderListSerializer(serializers.ModelSerializer):
    """
    提醒列表序列化器
    """

    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "reminder_time",
            "frequency",
            "dosage",
            "dosage_unit",
            "is_active",
            "title",
            "meal_timing",
            "start_date",
            "end_date",
            "special_instructions",
            "reminder_count",
            "response_count",
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
