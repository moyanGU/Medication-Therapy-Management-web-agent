from rest_framework import serializers

from .models import MedicationPlan, PlanMedicine


class PlanMedicineSerializer(serializers.ModelSerializer):
    """
    计划-药品 序列化器（只读用于嵌套展示）
    """

    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_specification = serializers.CharField(
        source="medicine.specification", read_only=True
    )

    class Meta:
        model = PlanMedicine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_specification",
            "daily_dosage",
            "frequency",
            "single_dose",
            "instructions",
            "administration_times",
            "meal_timing",
            "is_required",
            "start_day",
            "duration_days",
            "special_requirements",
            "dosage_adjustments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicationPlanListSerializer(serializers.ModelSerializer):
    """
    用药计划 列表序列化器（轻量字段以提升列表性能）
    """

    duration_days = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    medicines_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MedicationPlan
        fields = [
            "id",
            "name",
            "plan_type",
            "start_date",
            "end_date",
            "status",
            "priority",
            "is_active",
            "duration_days",
            "is_expired",
            "progress_percentage",
            "medicines_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicationPlanSerializer(serializers.ModelSerializer):
    """
    用药计划 详情序列化器（包含更多字段与嵌套药品）
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    duration_days = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    medicines = PlanMedicineSerializer(
        source="plan_medicines", many=True, read_only=True
    )

    class Meta:
        model = MedicationPlan
        fields = [
            "id",
            "user",
            "name",
            "plan_type",
            "start_date",
            "end_date",
            "description",
            "treatment_goal",
            "is_active",
            "priority",
            "source",
            "doctor_name",
            "hospital_name",
            "department",
            "diagnosis",
            "precautions",
            "side_effects_monitoring",
            "review_date",
            "status",
            "duration_days",
            "is_expired",
            "progress_percentage",
            "created_at",
            "updated_at",
            "medicines",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "duration_days",
            "is_expired",
            "progress_percentage",
        ]

    def validate_name(self, value):
        """
        校验计划名称
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("计划名称至少需要2个字符")
        return value.strip()

    def validate(self, attrs):
        """
        跨字段校验
        - start_date 必须存在
        - end_date 若存在不得早于 start_date
        """
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if not start_date:
            raise serializers.ValidationError("开始日期是必填项")
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("结束日期不能早于开始日期")
        return attrs
