from rest_framework import serializers

from .models import MTMAssessment, MTMFollowUp, MTMInterview, MTMPlan, MTMServiceCase


class MTMUserSummarySerializer(serializers.Serializer):
    """
    服务单参与者的最小用户摘要
    """

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)


class MTMInterviewSummarySerializer(serializers.ModelSerializer):
    """
    问诊摘要序列化器
    """

    class Meta:
        model = MTMInterview
        fields = [
            "id",
            "basic_info_snapshot",
            "medication_history",
            "allergy_history",
            "lifestyle_info",
            "economic_context",
            "health_expectations",
            "notes",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class MTMAssessmentSummarySerializer(serializers.ModelSerializer):
    """
    评估摘要序列化器
    """

    class Meta:
        model = MTMAssessment
        fields = [
            "id",
            "appropriateness_score",
            "effectiveness_score",
            "safety_score",
            "adherence_score",
            "economic_score",
            "problem_list",
            "summary",
            "risk_level",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class MTMPlanSummarySerializer(serializers.ModelSerializer):
    """
    干预计划摘要序列化器
    """

    class Meta:
        model = MTMPlan
        fields = [
            "id",
            "interventions",
            "priority",
            "patient_confirmation_status",
            "patient_confirmation_notes",
            "confirmed_at",
            "created_at",
            "updated_at",
        ]


class MTMFollowUpSummarySerializer(serializers.ModelSerializer):
    """
    随访摘要序列化器
    """

    class Meta:
        model = MTMFollowUp
        fields = [
            "id",
            "follow_up_time",
            "follow_up_method",
            "execution_status",
            "risk_change",
            "summary",
            "next_follow_up_time",
            "created_at",
            "updated_at",
        ]


class MTMServiceCaseCreateSerializer(serializers.ModelSerializer):
    """
    服务单创建序列化器
    """

    class Meta:
        model = MTMServiceCase
        fields = ["trigger_source", "service_goal", "notes"]

    def validate_service_goal(self, value):
        """
        清洗服务目标中的首尾空白
        """
        if value is None:
            return value
        return value.strip()

    def validate_notes(self, value):
        """
        清洗备注中的首尾空白
        """
        if value is None:
            return value
        return value.strip()

    def create(self, validated_data):
        """
        以当前登录用户作为患者创建首条服务单
        """
        request = self.context["request"]
        return MTMServiceCase.objects.create(patient=request.user, **validated_data)


class MTMServiceCaseListSerializer(serializers.ModelSerializer):
    """
    服务单列表序列化器
    """

    patient = MTMUserSummarySerializer(read_only=True)
    assigned_pharmacist = MTMUserSummarySerializer(read_only=True, allow_null=True)

    class Meta:
        model = MTMServiceCase
        fields = [
            "id",
            "case_number",
            "patient",
            "assigned_pharmacist",
            "status",
            "trigger_source",
            "service_goal",
            "started_at",
            "completed_at",
            "created_at",
        ]


class MTMServiceCaseDetailSerializer(MTMServiceCaseListSerializer):
    """
    服务单详情序列化器
    """

    interview = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    follow_ups = MTMFollowUpSummarySerializer(many=True, read_only=True)

    class Meta(MTMServiceCaseListSerializer.Meta):
        fields = MTMServiceCaseListSerializer.Meta.fields + [
            "notes",
            "updated_at",
            "interview",
            "assessment",
            "plan",
            "follow_ups",
        ]

    def get_interview(self, obj):
        """
        安全返回问诊摘要，没有时返回空值
        """
        interview = getattr(obj, "interview", None)
        if not interview:
            return None
        return MTMInterviewSummarySerializer(interview).data

    def get_assessment(self, obj):
        """
        安全返回评估摘要，没有时返回空值
        """
        assessment = getattr(obj, "assessment", None)
        if not assessment:
            return None
        return MTMAssessmentSummarySerializer(assessment).data

    def get_plan(self, obj):
        """
        安全返回干预计划摘要，没有时返回空值
        """
        plan = getattr(obj, "plan", None)
        if not plan:
            return None
        return MTMPlanSummarySerializer(plan).data


class MTMServiceCaseTransitionSerializer(serializers.Serializer):
    """
    服务单状态流转请求序列化器
    """

    target_status = serializers.ChoiceField(choices=MTMServiceCase.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        """
        校验状态流转是否合法
        """
        service_case = self.context["service_case"]
        target_status = attrs["target_status"]

        if target_status == service_case.status:
            raise serializers.ValidationError("服务单已经处于目标状态")

        if not service_case.can_transition_to(target_status):
            raise serializers.ValidationError(
                f"当前状态 {service_case.status} 不允许流转到 {target_status}"
            )

        return attrs
