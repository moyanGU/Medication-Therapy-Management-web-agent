from django.contrib import admin

from .models import MTMAssessment, MTMFollowUp, MTMInterview, MTMPlan, MTMServiceCase


class MTMFollowUpInline(admin.TabularInline):
    """
    在服务单后台页内快速查看和维护随访记录
    """

    model = MTMFollowUp
    extra = 0
    fields = (
        "follow_up_time",
        "follow_up_method",
        "execution_status",
        "risk_change",
        "next_follow_up_time",
    )
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(MTMServiceCase)
class MTMServiceCaseAdmin(admin.ModelAdmin):
    """
    MTM 服务单后台管理
    """

    list_display = (
        "id",
        "case_number",
        "patient",
        "assigned_pharmacist",
        "status",
        "trigger_source",
        "started_at",
        "completed_at",
        "created_at",
    )
    list_filter = ("status", "trigger_source", "created_at", "started_at")
    search_fields = (
        "case_number",
        "patient__username",
        "patient__phone",
        "assigned_pharmacist__username",
    )
    readonly_fields = ("case_number", "created_at", "updated_at")
    autocomplete_fields = ("patient", "assigned_pharmacist")
    inlines = (MTMFollowUpInline,)


@admin.register(MTMInterview)
class MTMInterviewAdmin(admin.ModelAdmin):
    """
    MTM 问诊后台管理
    """

    list_display = ("id", "service_case", "completed_at", "created_at", "updated_at")
    search_fields = ("service_case__case_number", "service_case__patient__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("service_case",)


@admin.register(MTMAssessment)
class MTMAssessmentAdmin(admin.ModelAdmin):
    """
    MTM 评估后台管理
    """

    list_display = (
        "id",
        "service_case",
        "risk_level",
        "appropriateness_score",
        "effectiveness_score",
        "safety_score",
        "adherence_score",
        "economic_score",
        "completed_at",
    )
    list_filter = ("risk_level", "completed_at")
    search_fields = ("service_case__case_number", "service_case__patient__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("service_case",)


@admin.register(MTMPlan)
class MTMPlanAdmin(admin.ModelAdmin):
    """
    MTM 干预计划后台管理
    """

    list_display = (
        "id",
        "service_case",
        "priority",
        "patient_confirmation_status",
        "confirmed_at",
        "created_at",
    )
    list_filter = ("priority", "patient_confirmation_status", "confirmed_at")
    search_fields = ("service_case__case_number", "service_case__patient__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("service_case",)


@admin.register(MTMFollowUp)
class MTMFollowUpAdmin(admin.ModelAdmin):
    """
    MTM 随访后台管理
    """

    list_display = (
        "id",
        "service_case",
        "follow_up_time",
        "follow_up_method",
        "execution_status",
        "risk_change",
        "next_follow_up_time",
        "created_at",
    )
    list_filter = ("follow_up_method", "execution_status", "risk_change")
    search_fields = ("service_case__case_number", "service_case__patient__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("service_case",)
