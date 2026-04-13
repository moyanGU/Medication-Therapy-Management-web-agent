import django_filters
from django.db import models
from django.utils import timezone

from .models import MedicalRecord


class MedicalRecordFilter(django_filters.FilterSet):
    """
    病历记录过滤器
    """

    # 日期范围过滤
    visit_date_from = django_filters.DateFilter(
        field_name="visit_date", lookup_expr="gte", label="就诊开始日期"
    )
    visit_date_to = django_filters.DateFilter(
        field_name="visit_date", lookup_expr="lte", label="就诊结束日期"
    )

    # 医院搜索（模糊匹配）
    hospital = django_filters.CharFilter(
        field_name="hospital", lookup_expr="icontains", label="医院名称"
    )

    # 科室搜索（模糊匹配）
    department = django_filters.CharFilter(
        field_name="department", lookup_expr="icontains", label="科室"
    )

    # 医生搜索（模糊匹配）
    doctor = django_filters.CharFilter(
        field_name="doctor", lookup_expr="icontains", label="医生姓名"
    )

    # 诊断搜索（模糊匹配）
    diagnosis = django_filters.CharFilter(
        field_name="diagnosis", lookup_expr="icontains", label="诊断结果"
    )

    # 主诉搜索（模糊匹配）
    chief_complaint = django_filters.CharFilter(
        field_name="chief_complaint", lookup_expr="icontains", label="主诉"
    )

    # 就诊类型过滤
    visit_type = django_filters.ChoiceFilter(
        choices=MedicalRecord.VISIT_TYPE_CHOICES, label="就诊类型"
    )

    # 就医状态过滤
    status = django_filters.ChoiceFilter(
        choices=MedicalRecord.STATUS_CHOICES, label="就医状态"
    )

    # 紧急程度过滤
    urgency = django_filters.ChoiceFilter(
        choices=MedicalRecord.URGENCY_CHOICES, label="紧急程度"
    )

    # 费用范围过滤
    total_cost_min = django_filters.NumberFilter(
        field_name="total_cost", lookup_expr="gte", label="最低费用"
    )
    total_cost_max = django_filters.NumberFilter(
        field_name="total_cost", lookup_expr="lte", label="最高费用"
    )

    # 满意度评分过滤
    satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", label="满意度评分"
    )
    satisfaction_score_min = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="gte", label="最低满意度评分"
    )

    # 复诊相关过滤
    has_follow_up = django_filters.BooleanFilter(
        field_name="follow_up_date", lookup_expr="isnull", exclude=True, label="有复诊安排"
    )

    follow_up_due = django_filters.BooleanFilter(
        method="filter_follow_up_due", label="复诊到期"
    )

    # 最近就诊过滤
    recent_days = django_filters.NumberFilter(
        method="filter_recent_days", label="最近天数内就诊"
    )

    # 关键词搜索（在多个字段中搜索）
    search = django_filters.CharFilter(method="filter_search", label="关键词搜索")

    # 按年份过滤
    visit_year = django_filters.NumberFilter(
        field_name="visit_date__year", label="就诊年份"
    )

    # 按月份过滤
    visit_month = django_filters.NumberFilter(
        field_name="visit_date__month", label="就诊月份"
    )

    # 诊断代码过滤
    diagnosis_code = django_filters.CharFilter(
        field_name="diagnosis_code", lookup_expr="icontains", label="诊断代码"
    )

    # 医生职称过滤
    doctor_title = django_filters.CharFilter(
        field_name="doctor_title", lookup_expr="icontains", label="医生职称"
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "visit_date_from",
            "visit_date_to",
            "hospital",
            "department",
            "doctor",
            "diagnosis",
            "chief_complaint",
            "visit_type",
            "status",
            "urgency",
            "total_cost_min",
            "total_cost_max",
            "satisfaction_score",
            "satisfaction_score_min",
            "has_follow_up",
            "follow_up_due",
            "recent_days",
            "search",
            "visit_year",
            "visit_month",
            "diagnosis_code",
            "doctor_title",
        ]

    def filter_follow_up_due(self, queryset, name, value):
        """
        过滤复诊到期的记录
        """
        if value:
            today = timezone.now().date()
            return queryset.filter(
                follow_up_date__isnull=False, follow_up_date__lte=today
            )
        return queryset

    def filter_recent_days(self, queryset, name, value):
        """
        过滤最近指定天数内的就诊记录
        """
        if value:
            cutoff_date = timezone.now().date() - timezone.timedelta(days=value)
            return queryset.filter(visit_date__gte=cutoff_date)
        return queryset

    def filter_search(self, queryset, name, value):
        """
        在多个字段中进行关键词搜索
        """
        if value:
            return queryset.filter(
                models.Q(hospital__icontains=value)
                | models.Q(department__icontains=value)
                | models.Q(doctor__icontains=value)
                | models.Q(diagnosis__icontains=value)
                | models.Q(chief_complaint__icontains=value)
                | models.Q(present_illness__icontains=value)
                | models.Q(treatment__icontains=value)
                | models.Q(medical_orders__icontains=value)
                | models.Q(notes__icontains=value)
            )
        return queryset


class MedicalRecordStatisticsFilter(django_filters.FilterSet):
    """
    病历统计过滤器
    """

    # 统计时间范围
    date_from = django_filters.DateFilter(
        field_name="visit_date", lookup_expr="gte", label="统计开始日期"
    )
    date_to = django_filters.DateFilter(
        field_name="visit_date", lookup_expr="lte", label="统计结束日期"
    )

    # 按医院统计
    hospital = django_filters.CharFilter(
        field_name="hospital", lookup_expr="icontains", label="医院名称"
    )

    # 按科室统计
    department = django_filters.CharFilter(
        field_name="department", lookup_expr="icontains", label="科室"
    )

    # 按就诊类型统计
    visit_type = django_filters.ChoiceFilter(
        choices=MedicalRecord.VISIT_TYPE_CHOICES, label="就诊类型"
    )

    class Meta:
        model = MedicalRecord
        fields = ["date_from", "date_to", "hospital", "department", "visit_type"]
