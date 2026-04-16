from rest_framework import serializers

from .models import MTMAssessment, MTMFollowUp, MTMInterview, MTMPlan, MTMServiceCase


def _has_meaningful_content(value):
    """
    递归判断字段中是否包含可视为已填写的有效内容
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_has_meaningful_content(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_meaningful_content(item) for item in value)
    return bool(value)


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


class MTMInterviewFormSerializer(serializers.Serializer):
    """
    问诊表单读取序列化器
    """

    id = serializers.IntegerField(read_only=True)
    basic_info_snapshot = serializers.JSONField()
    medication_history = serializers.JSONField()
    allergy_history = serializers.JSONField()
    lifestyle_info = serializers.JSONField()
    economic_context = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    health_expectations = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    completed_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MTMInterviewDraftSerializer(serializers.Serializer):
    """
    问诊草稿保存序列化器
    """

    basic_info_snapshot = serializers.JSONField(required=False)
    medication_history = serializers.JSONField(required=False)
    allergy_history = serializers.JSONField(required=False)
    lifestyle_info = serializers.JSONField(required=False)
    economic_context = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    health_expectations = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def validate_basic_info_snapshot(self, value):
        """
        约束基础信息必须是对象结构
        """
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("基础信息必须是对象格式")
        return value

    def validate_medication_history(self, value):
        """
        约束用药史必须是列表结构
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("用药史必须是列表格式")
        return value

    def validate_allergy_history(self, value):
        """
        约束过敏史必须是列表结构
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("过敏史必须是列表格式")
        return value

    def validate_lifestyle_info(self, value):
        """
        约束生活方式信息必须是对象结构
        """
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("生活方式信息必须是对象格式")
        return value

    def validate_economic_context(self, value):
        """
        清洗经济背景字段中的首尾空白
        """
        if value is None:
            return value
        return value.strip()

    def validate_health_expectations(self, value):
        """
        清洗健康期望字段中的首尾空白
        """
        if value is None:
            return value
        return value.strip()

    def validate_notes(self, value):
        """
        清洗备注字段中的首尾空白
        """
        if value is None:
            return value
        return value.strip()


class MTMInterviewCompleteSerializer(MTMInterviewDraftSerializer):
    """
    问诊完成提交序列化器
    """

    def validate(self, attrs):
        """
        校验问诊完成所需的最小关键字段
        """
        attrs = super().validate(attrs)
        basic_info = attrs.get("basic_info_snapshot") or {}
        medication_history = attrs.get("medication_history") or []
        health_expectations = attrs.get("health_expectations") or ""
        notes = attrs.get("notes") or ""

        if not _has_meaningful_content(basic_info):
            raise serializers.ValidationError(
                {"basic_info_snapshot": ["请至少补充一项基础信息后再完成问诊。"]}
            )

        if not _has_meaningful_content(medication_history):
            raise serializers.ValidationError(
                {"medication_history": ["请至少补充一项当前或既往用药信息后再完成问诊。"]}
            )

        if not health_expectations.strip() and not notes.strip():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "请至少填写本次健康期望或补充说明中的一项后再完成问诊。"
                    ]
                }
            )

        return attrs


class MTMAssessmentFormSerializer(serializers.Serializer):
    """
    评估表单读取序列化器
    """

    id = serializers.IntegerField(read_only=True)
    appropriateness_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    effectiveness_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    safety_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    adherence_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    economic_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    problem_list = serializers.JSONField(required=False)
    summary = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    risk_level = serializers.ChoiceField(
        choices=MTMAssessment.RISK_LEVEL_CHOICES, required=False
    )
    completed_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MTMAssessmentDraftSerializer(serializers.Serializer):
    """
    评估草稿保存序列化器
    """

    appropriateness_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    effectiveness_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    safety_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    adherence_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    economic_score = serializers.IntegerField(
        allow_null=True, required=False, min_value=0, max_value=100
    )
    problem_list = serializers.JSONField(required=False)
    summary = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    risk_level = serializers.ChoiceField(
        choices=MTMAssessment.RISK_LEVEL_CHOICES, required=False
    )

    def validate_problem_list(self, value):
        """
        约束问题清单必须是列表结构
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("问题清单必须是列表格式")
        return value

    def validate_summary(self, value):
        """
        清洗评估总结中的首尾空白
        """
        if value is None:
            return value
        return value.strip()


class MTMAssessmentCompleteSerializer(MTMAssessmentDraftSerializer):
    """
    评估完成提交序列化器
    """

    def validate(self, attrs):
        """
        校验评估完成所需的最小关键字段
        """
        attrs = super().validate(attrs)
        scores = [
            attrs.get("appropriateness_score"),
            attrs.get("effectiveness_score"),
            attrs.get("safety_score"),
            attrs.get("adherence_score"),
            attrs.get("economic_score"),
        ]
        problem_list = attrs.get("problem_list") or []
        summary = attrs.get("summary") or ""
        risk_level = attrs.get("risk_level")

        if not any(score is not None for score in scores):
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "请至少补充一项评估评分后再完成评估。"
                    ]
                }
            )

        if not risk_level:
            raise serializers.ValidationError(
                {"risk_level": ["请选择综合风险等级后再完成评估。"]}
            )

        if not _has_meaningful_content(problem_list) and not summary.strip():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "请至少填写一项问题清单或评估总结后再完成评估。"
                    ]
                }
            )

        return attrs


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
