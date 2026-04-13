from rest_framework import serializers

from .history_models import ReminderHistory, ReminderStats


class ReminderHistorySerializer(serializers.ModelSerializer):
    """
    提醒历史记录序列化器
    """

    reminder_title = serializers.CharField(source="reminder.title", read_only=True)
    medicine_name = serializers.CharField(
        source="reminder.medicine.name", read_only=True
    )
    medicine_id = serializers.IntegerField(
        source="reminder.medicine.id", read_only=True
    )
    response_delay_display = serializers.CharField(
        source="get_response_delay_display", read_only=True
    )
    is_responded = serializers.BooleanField(read_only=True)
    is_successful = serializers.BooleanField(read_only=True)

    class Meta:
        model = ReminderHistory
        fields = [
            "id",
            "reminder",
            "reminder_title",
            "medicine_name",
            "medicine_id",
            "sent_at",
            "scheduled_time",
            "reminder_type",
            "title",
            "message",
            "notification_methods",
            "status",
            "responded_at",
            "response_type",
            "response_delay_minutes",
            "response_delay_display",
            "notes",
            "device_info",
            "is_responded",
            "is_successful",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "response_delay_minutes", "created_at"]


class ReminderHistoryCreateSerializer(serializers.ModelSerializer):
    """
    创建提醒历史记录序列化器
    """

    class Meta:
        model = ReminderHistory
        fields = [
            "reminder",
            "scheduled_time",
            "reminder_type",
            "title",
            "message",
            "notification_methods",
            "status",
            "notes",
            "device_info",
        ]

    def validate_reminder(self, value):
        """
        验证提醒是否属于当前用户
        """
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("只能为自己的提醒创建历史记录")
        return value

    def create(self, validated_data):
        """
        创建提醒历史记录
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReminderHistoryResponseSerializer(serializers.Serializer):
    """
    提醒响应序列化器
    """

    response_type = serializers.ChoiceField(
        choices=ReminderHistory.RESPONSE_TYPE_CHOICES, required=True
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_response_type(self, value):
        """
        验证响应类型
        """
        if value == "no_response":
            raise serializers.ValidationError("不能设置为无响应状态")
        return value


class ReminderStatsSerializer(serializers.ModelSerializer):
    """
    提醒统计序列化器
    """

    class Meta:
        model = ReminderStats
        fields = [
            "id",
            "date",
            "scheduled_count",
            "sent_count",
            "responded_count",
            "taken_count",
            "skipped_count",
            "delayed_count",
            "ignored_count",
            "avg_response_time",
            "response_rate",
            "adherence_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReminderStatsDetailSerializer(serializers.Serializer):
    """
    提醒统计详情序列化器
    """

    # 基础统计
    total_reminders = serializers.IntegerField()
    sent_reminders = serializers.IntegerField()
    responded_reminders = serializers.IntegerField()
    taken_reminders = serializers.IntegerField()

    # 率统计
    response_rate = serializers.FloatField()
    adherence_rate = serializers.FloatField()

    # 时间统计
    avg_response_time = serializers.FloatField()

    # 按类型统计
    response_type_stats = serializers.DictField()

    # 按药品统计
    medicine_stats = serializers.ListField()

    # 按时间统计
    time_stats = serializers.ListField()


class ReminderAnalyticsSerializer(serializers.Serializer):
    """
    提醒分析序列化器
    """

    # 时间范围
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    # 分析维度
    group_by = serializers.ChoiceField(
        choices=[
            ("day", "按天"),
            ("week", "按周"),
            ("month", "按月"),
            ("medicine", "按药品"),
            ("frequency", "按频率"),
        ],
        default="day",
    )

    # 药品筛选
    medicine_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def validate(self, data):
        """
        验证时间范围
        """
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("开始日期不能晚于结束日期")

            # 限制查询范围不超过1年
            if (end_date - start_date).days > 365:
                raise serializers.ValidationError("查询范围不能超过1年")

        return data


class ReminderTrendSerializer(serializers.Serializer):
    """
    提醒趋势序列化器
    """

    date = serializers.DateField()
    scheduled_count = serializers.IntegerField()
    sent_count = serializers.IntegerField()
    responded_count = serializers.IntegerField()
    taken_count = serializers.IntegerField()
    response_rate = serializers.FloatField()
    adherence_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()


class MedicineReminderStatsSerializer(serializers.Serializer):
    """
    药品提醒统计序列化器
    """

    medicine_id = serializers.IntegerField()
    medicine_name = serializers.CharField()
    total_reminders = serializers.IntegerField()
    sent_reminders = serializers.IntegerField()
    responded_reminders = serializers.IntegerField()
    taken_reminders = serializers.IntegerField()
    response_rate = serializers.FloatField()
    adherence_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()


class ReminderEffectivenessSerializer(serializers.Serializer):
    """
    提醒效果分析序列化器
    """

    # 总体效果
    overall_stats = ReminderStatsDetailSerializer()

    # 趋势分析
    trend_data = serializers.ListField(child=ReminderTrendSerializer())

    # 药品分析
    medicine_analysis = serializers.ListField(child=MedicineReminderStatsSerializer())

    # 时间分布分析
    time_distribution = serializers.DictField()

    # 响应模式分析
    response_patterns = serializers.DictField()

    # 改进建议
    recommendations = serializers.ListField(child=serializers.CharField())


class ReminderComplianceSerializer(serializers.Serializer):
    """
    服药依从性序列化器
    """

    # 依从性评分（0-100）
    compliance_score = serializers.FloatField()

    # 依从性等级
    compliance_level = serializers.CharField()

    # 连续服药天数
    consecutive_days = serializers.IntegerField()

    # 最长连续天数
    max_consecutive_days = serializers.IntegerField()

    # 本周依从性
    weekly_compliance = serializers.FloatField()

    # 本月依从性
    monthly_compliance = serializers.FloatField()

    # 依从性趋势
    compliance_trend = serializers.CharField()

    # 详细统计
    detailed_stats = ReminderStatsDetailSerializer()
