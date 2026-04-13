from rest_framework import serializers

from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    visit_datetime = serializers.ReadOnlyField()
    days_since_visit = serializers.ReadOnlyField()
    days_until_follow_up = serializers.ReadOnlyField()
    symptom_improvement = serializers.ReadOnlyField()
    prescribed_medicine_names = serializers.ReadOnlyField(
        source="get_prescribed_medicine_names"
    )
    examination_names = serializers.ReadOnlyField(source="get_examination_names")
    out_of_pocket_cost = serializers.ReadOnlyField(
        source="calculate_out_of_pocket_cost"
    )
    is_follow_up_due = serializers.ReadOnlyField()

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "user",
            "visit_date",
            "visit_time",
            "hospital",
            "department",
            "doctor",
            "diagnosis",
            "chief_complaint",
            "present_illness",
            "treatment",
            "medical_orders",
            "follow_up_date",
            "status",
            "urgency",
            "total_cost",
            "insurance_coverage",
            "out_of_pocket_cost",
            "satisfaction_score",
            "notes",
            "attachments",
            "created_at",
            "updated_at",
            "visit_datetime",
            "days_since_visit",
            "days_until_follow_up",
            "symptom_improvement",
            "is_follow_up_due",
            "prescribed_medicine_names",
            "examination_names",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_visit_date(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("就诊日期不能是未来日期")
        return value

    def validate_follow_up_date(self, value):
        visit_date = self.initial_data.get("visit_date")
        if value and visit_date and value <= visit_date:
            raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        return value

    def validate(self, attrs):
        follow_up_date = attrs.get("follow_up_date")
        visit_date = attrs.get("visit_date")
        if follow_up_date and visit_date and follow_up_date <= visit_date:
            raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        symptom_score = attrs.get("symptom_improvement")
        if symptom_score is not None and not (1 <= symptom_score <= 10):
            raise serializers.ValidationError("症状评分必须在1-10之间")
        satisfaction = attrs.get("satisfaction_score")
        if satisfaction is not None and not (1 <= satisfaction <= 5):
            raise serializers.ValidationError("满意度评分必须在1-5之间")
        total_cost = attrs.get("total_cost")
        if total_cost is not None and total_cost < 0:
            raise serializers.ValidationError("总费用不能为负数")
        insurance = attrs.get("insurance_coverage")
        if insurance is not None and insurance < 0:
            raise serializers.ValidationError("医保报销金额不能为负数")
        out_of_pocket = attrs.get("out_of_pocket_cost")
        if out_of_pocket is not None and out_of_pocket < 0:
            raise serializers.ValidationError("自费金额不能为负数")
        return attrs


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            "visit_date",
            "visit_time",
            "hospital",
            "department",
            "doctor",
            "diagnosis",
            "chief_complaint",
            "present_illness",
            "treatment",
            "medical_orders",
            "follow_up_date",
            "status",
            "urgency",
            "total_cost",
            "insurance_coverage",
            "satisfaction_score",
            "notes",
            "attachments",
            "visit_type",
        ]

    def validate_visit_date(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("就诊日期不能是未来日期")
        return value

    def validate(self, attrs):
        follow_up_date = attrs.get("follow_up_date")
        visit_date = attrs.get("visit_date")
        if follow_up_date and visit_date and follow_up_date <= visit_date:
            raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        return attrs


class MedicalRecordListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor", read_only=True)
    treatment_plan = serializers.CharField(source="treatment", read_only=True)
    urgency_level = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "visit_date",
            "hospital",
            "department",
            "doctor_name",
            "diagnosis",
            "chief_complaint",
            "treatment_plan",
            "status",
            "urgency_level",
            "total_cost",
            "attachments",
        ]

    def get_urgency_level(self, obj):
        urgency_map = {
            "routine": "low",
            "urgent": "medium",
            "emergency": "high",
            "critical": "critical",
        }
        return urgency_map.get(obj.urgency, obj.urgency)


class MedicalRecordSummarySerializer(serializers.ModelSerializer):
    """
    病历摘要序列化器
    """

    visit_summary = serializers.ReadOnlyField(source="get_visit_summary")

    class Meta:
        model = MedicalRecord
        fields = ["id", "visit_summary"]


class MedicalRecordStatisticsSerializer(serializers.Serializer):
    """
    病历统计序列化器
    """

    total_visits = serializers.IntegerField()
    recent_visits = serializers.IntegerField()
    hospitals = serializers.ListField(child=serializers.DictField())
    departments = serializers.ListField(child=serializers.DictField())
    visit_types = serializers.ListField(child=serializers.DictField())
    monthly_visits = serializers.ListField(child=serializers.DictField())
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=2)
    follow_up_due = serializers.IntegerField()
