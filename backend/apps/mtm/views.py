import logging

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.response import error_response, success_response

from .models import MTMAssessment, MTMInterview, MTMServiceCase, MTMPlan
from .serializers import (
    MTMAssessmentCompleteSerializer,
    MTMAssessmentDraftSerializer,
    MTMAssessmentFormSerializer,
    MTMInterviewCompleteSerializer,
    MTMInterviewDraftSerializer,
    MTMInterviewFormSerializer,
    MTMPlanCompleteSerializer,
    MTMPlanDraftSerializer,
    MTMPlanFormSerializer,
    MTMServiceCaseCreateSerializer,
    MTMServiceCaseDetailSerializer,
    MTMServiceCaseListSerializer,
    MTMServiceCaseTransitionSerializer,
)

logger = logging.getLogger(__name__)


class MTMServiceCaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    MTM 服务单最小视图集
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "status": ["exact", "in"],
        "trigger_source": ["exact", "in"],
        "created_at": ["gte", "lte"],
    }
    search_fields = ["case_number", "service_goal", "notes", "patient__username"]
    ordering_fields = ["created_at", "started_at", "completed_at"]
    ordering = ["-created_at"]

    def _build_initial_interview_payload(self, service_case):
        """
        为首次进入问诊页的服务单生成最小草稿内容
        """
        patient = service_case.patient
        return {
            "service_case": service_case,
            "basic_info_snapshot": {
                "patient_name": patient.get_full_name() or patient.username,
                "age": patient.age,
                "gender": patient.get_gender_display() if patient.gender else "",
                "contact_phone": patient.phone,
                "main_diagnosis": service_case.service_goal,
            },
            "medication_history": [],
            "allergy_history": [],
            "lifestyle_info": {
                "smoking": "",
                "drinking": "",
                "exercise": "",
                "sleep": "",
            },
            "economic_context": "",
            "health_expectations": service_case.service_goal or "",
            "notes": "",
        }

    def _get_or_create_interview(self, service_case):
        """
        获取当前服务单问诊记录；若不存在则生成最小草稿
        """
        interview, created = MTMInterview.objects.get_or_create(
            service_case=service_case,
            defaults=self._build_initial_interview_payload(service_case),
        )
        if created:
            logger.info(
                "🟢 [MTM] interview draft initialized - case=%s interview=%s",
                service_case.id,
                interview.id,
            )
        return interview

    def _build_initial_assessment_payload(self, service_case):
        """
        为首次进入评估页的服务单生成最小草稿内容
        """
        return {
            "service_case": service_case,
            "appropriateness_score": None,
            "effectiveness_score": None,
            "safety_score": None,
            "adherence_score": None,
            "economic_score": None,
            "problem_list": [],
            "summary": "",
            "risk_level": "medium",
        }

    def _build_initial_plan_payload(self, service_case):
        """
        为首次进入干预计划页的服务单生成最小草稿内容
        """
        return {
            "service_case": service_case,
            "interventions": [],
            "priority": "medium",
        }

    def _get_or_create_assessment(self, service_case):
        """
        获取当前服务单评估记录；若不存在则生成最小草稿
        """
        assessment, created = MTMAssessment.objects.get_or_create(
            service_case=service_case,
            defaults=self._build_initial_assessment_payload(service_case),
        )
        if created:
            logger.info(
                "🟢 [MTM] assessment draft initialized - case=%s assessment=%s",
                service_case.id,
                assessment.id,
            )
        return assessment

    def _get_or_create_plan(self, service_case):
        """
        获取当前服务单干预计划记录；若不存在则生成最小草稿
        """
        plan, created = MTMPlan.objects.get_or_create(
            service_case=service_case,
            defaults=self._build_initial_plan_payload(service_case),
        )
        if created:
            logger.info(
                "🟢 [MTM] plan draft initialized - case=%s plan=%s",
                service_case.id,
                plan.id,
            )
        return plan

    def _save_interview_payload(self, interview, validated_data, *, mark_completed=False):
        """
        将校验后的问诊数据写入模型，并根据需要标记完成时间
        """
        fields_to_update = []
        for field in [
            "basic_info_snapshot",
            "medication_history",
            "allergy_history",
            "lifestyle_info",
            "economic_context",
            "health_expectations",
            "notes",
        ]:
            if field in validated_data:
                setattr(interview, field, validated_data[field])
                fields_to_update.append(field)

        if mark_completed:
            interview.completed_at = timezone.now()
            fields_to_update.append("completed_at")

        if not fields_to_update:
            interview.save(update_fields=["updated_at"])
        else:
            fields_to_update.append("updated_at")
            interview.save(update_fields=fields_to_update)

        return interview

    def _save_assessment_payload(self, assessment, validated_data, *, mark_completed=False):
        """
        将校验后的评估数据写入模型，并根据需要标记完成时间
        """
        fields_to_update = []
        for field in [
            "appropriateness_score",
            "effectiveness_score",
            "safety_score",
            "adherence_score",
            "economic_score",
            "problem_list",
            "summary",
            "risk_level",
        ]:
            if field in validated_data:
                setattr(assessment, field, validated_data[field])
                fields_to_update.append(field)

        if mark_completed:
            assessment.completed_at = timezone.now()
            fields_to_update.append("completed_at")

        if not fields_to_update:
            assessment.save(update_fields=["updated_at"])
        else:
            fields_to_update.append("updated_at")
            assessment.save(update_fields=fields_to_update)

        return assessment

    def _save_plan_payload(self, plan, validated_data, *, mark_completed=False):
        """
        将校验后的干预计划数据写入模型，并根据需要标记完成时间
        """
        fields_to_update = []
        for field in [
            "interventions",
            "priority",
        ]:
            if field in validated_data:
                setattr(plan, field, validated_data[field])
                fields_to_update.append(field)

        if mark_completed:
            plan.completed_at = timezone.now()
            fields_to_update.append("completed_at")

        if fields_to_update:
            fields_to_update.append("updated_at")
            plan.save(update_fields=fields_to_update)

        return plan

    def get_queryset(self):
        """
        仅返回当前用户参与的服务单
        """
        user = self.request.user
        queryset = (
            MTMServiceCase.objects.filter(
                Q(patient=user) | Q(assigned_pharmacist=user)
            )
            .select_related("patient", "assigned_pharmacist", "interview", "assessment", "plan")
            .prefetch_related("follow_ups")
            .distinct()
        )
        return queryset

    def get_serializer_class(self):
        """
        根据动作选择最小序列化器
        """
        if self.action == "create":
            return MTMServiceCaseCreateSerializer
        if self.action == "list":
            return MTMServiceCaseListSerializer
        if self.action == "transition":
            return MTMServiceCaseTransitionSerializer
        if self.action == "interview":
            if self.request.method == "PUT":
                return MTMInterviewDraftSerializer
            return MTMInterviewFormSerializer
        if self.action == "complete_interview":
            return MTMInterviewCompleteSerializer
        if self.action == "assessment":
            if self.request.method == "PUT":
                return MTMAssessmentDraftSerializer
            return MTMAssessmentFormSerializer
        if self.action == "complete_assessment":
            return MTMAssessmentCompleteSerializer
        if self.action == "plan":
            if self.request.method == "PUT":
                return MTMPlanDraftSerializer
            return MTMPlanFormSerializer
        if self.action == "complete_plan":
            return MTMPlanCompleteSerializer
        return MTMServiceCaseDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        创建 MTM 服务单
        """
        logger.info("🔵 [MTM] create service case - user=%s", request.user.id)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("🟡 [MTM] create invalid - errors=%s", serializer.errors)
            return error_response(message="数据验证失败", errors=serializer.errors)

        service_case = serializer.save()
        logger.info(
            "🟢 [MTM] service case created - id=%s case_number=%s",
            service_case.id,
            service_case.case_number,
        )
        return success_response(
            data=MTMServiceCaseDetailSerializer(service_case).data,
            message="创建MTM服务单成功",
            status_code=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        """
        获取当前用户参与的 MTM 服务单列表
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="获取MTM服务单列表成功")

    def retrieve(self, request, *args, **kwargs):
        """
        获取 MTM 服务单详情
        """
        service_case = self.get_object()
        serializer = self.get_serializer(service_case)
        return success_response(data=serializer.data, message="获取MTM服务单详情成功")

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        """
        驱动服务单进入下一个合法状态
        """
        service_case = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={"service_case": service_case}
        )

        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] transition invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="数据验证失败", errors=serializer.errors)

        validated_data = serializer.validated_data
        target_status = validated_data["target_status"]
        notes = validated_data.get("notes")

        try:
            logger.info(
                "🔵 [MTM] transition start - case=%s from=%s to=%s",
                service_case.id,
                service_case.status,
                target_status,
            )
            service_case.transition_to(target_status=target_status, note=notes)
            logger.info(
                "🟢 [MTM] transition success - case=%s current=%s",
                service_case.id,
                service_case.status,
            )
            return success_response(
                data=MTMServiceCaseDetailSerializer(service_case).data,
                message="MTM服务单状态更新成功",
            )
        except ValidationError as exc:
            logger.warning(
                "🟡 [MTM] transition rejected - case=%s error=%s",
                service_case.id,
                exc,
            )
            return error_response(message="状态流转校验失败", errors=exc.messages)

    @action(detail=True, methods=["get", "put"])
    def interview(self, request, pk=None):
        """
        读取或保存当前服务单的问诊草稿
        """
        service_case = self.get_object()
        interview = self._get_or_create_interview(service_case)

        if request.method == "GET":
            logger.info(
                "🔵 [MTM] interview fetch - case=%s interview=%s",
                service_case.id,
                interview.id,
            )
            return success_response(
                data=MTMInterviewFormSerializer(interview).data,
                message="获取问诊表单成功",
            )

        logger.info(
            "🔵 [MTM] interview draft save start - case=%s interview=%s",
            service_case.id,
            interview.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] interview draft invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="问诊草稿校验失败", errors=serializer.errors)

        interview = self._save_interview_payload(interview, serializer.validated_data)
        logger.info(
            "🟢 [MTM] interview draft saved - case=%s interview=%s",
            service_case.id,
            interview.id,
        )
        return success_response(
            data=MTMInterviewFormSerializer(interview).data,
            message="问诊草稿保存成功",
        )

    @action(detail=True, methods=["post"], url_path="interview/complete")
    def complete_interview(self, request, pk=None):
        """
        完成当前服务单的问诊填写
        """
        service_case = self.get_object()
        interview = self._get_or_create_interview(service_case)
        logger.info(
            "🔵 [MTM] interview complete start - case=%s interview=%s",
            service_case.id,
            interview.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] interview complete invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="问诊完成校验失败", errors=serializer.errors)

        interview = self._save_interview_payload(
            interview, serializer.validated_data, mark_completed=True
        )
        logger.info(
            "🟢 [MTM] interview completed - case=%s interview=%s completed_at=%s",
            service_case.id,
            interview.id,
            interview.completed_at,
        )
        return success_response(
            data=MTMInterviewFormSerializer(interview).data,
            message="问诊已完成",
        )

    @action(detail=True, methods=["get", "put"])
    def assessment(self, request, pk=None):
        """
        读取或保存当前服务单的评估草稿
        """
        service_case = self.get_object()
        assessment = self._get_or_create_assessment(service_case)

        if request.method == "GET":
            logger.info(
                "🔵 [MTM] assessment fetch - case=%s assessment=%s",
                service_case.id,
                assessment.id,
            )
            return success_response(
                data=MTMAssessmentFormSerializer(assessment).data,
                message="获取评估表单成功",
            )

        logger.info(
            "🔵 [MTM] assessment draft save start - case=%s assessment=%s",
            service_case.id,
            assessment.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] assessment draft invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="评估草稿校验失败", errors=serializer.errors)

        assessment = self._save_assessment_payload(assessment, serializer.validated_data)
        logger.info(
            "🟢 [MTM] assessment draft saved - case=%s assessment=%s",
            service_case.id,
            assessment.id,
        )
        return success_response(
            data=MTMAssessmentFormSerializer(assessment).data,
            message="评估草稿保存成功",
        )

    @action(detail=True, methods=["post"], url_path="assessment/complete")
    def complete_assessment(self, request, pk=None):
        """
        完成当前服务单的评估填写
        """
        service_case = self.get_object()
        assessment = self._get_or_create_assessment(service_case)
        logger.info(
            "🔵 [MTM] assessment complete start - case=%s assessment=%s",
            service_case.id,
            assessment.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] assessment complete invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="评估完成校验失败", errors=serializer.errors)

        assessment = self._save_assessment_payload(
            assessment, serializer.validated_data, mark_completed=True
        )
        logger.info(
            "🟢 [MTM] assessment completed - case=%s assessment=%s completed_at=%s",
            service_case.id,
            assessment.id,
            assessment.completed_at,
        )
        return success_response(
            data=MTMAssessmentFormSerializer(assessment).data,
            message="评估已完成",
        )

    @action(detail=True, methods=["get", "put"])
    def plan(self, request, pk=None):
        """
        读取或保存当前服务单的干预计划草稿
        """
        service_case = self.get_object()
        plan_obj = self._get_or_create_plan(service_case)

        if request.method == "GET":
            logger.info(
                "🔵 [MTM] plan fetch - case=%s plan=%s",
                service_case.id,
                plan_obj.id,
            )
            return success_response(
                data=MTMPlanFormSerializer(plan_obj).data,
                message="获取干预计划表单成功",
            )

        logger.info(
            "🔵 [MTM] plan draft save start - case=%s plan=%s",
            service_case.id,
            plan_obj.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] plan draft invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="草稿数据验证失败", errors=serializer.errors)

        plan_obj = self._save_plan_payload(
            plan_obj, serializer.validated_data, mark_completed=False
        )
        logger.info(
            "🟢 [MTM] plan draft saved - case=%s plan=%s",
            service_case.id,
            plan_obj.id,
        )
        return success_response(
            data=MTMPlanFormSerializer(plan_obj).data,
            message="草稿保存成功",
        )

    @action(detail=True, methods=["post"], url_path="plan/complete")
    def complete_plan(self, request, pk=None):
        """
        完成当前服务单的干预计划填写
        """
        service_case = self.get_object()
        plan_obj = self._get_or_create_plan(service_case)
        logger.info(
            "🔵 [MTM] plan complete start - case=%s plan=%s",
            service_case.id,
            plan_obj.id,
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "🟡 [MTM] plan complete invalid - case=%s errors=%s",
                service_case.id,
                serializer.errors,
            )
            return error_response(message="计划完成校验失败", errors=serializer.errors)

        plan_obj = self._save_plan_payload(
            plan_obj, serializer.validated_data, mark_completed=True
        )
        logger.info(
            "🟢 [MTM] plan completed - case=%s plan=%s completed_at=%s",
            service_case.id,
            plan_obj.id,
            plan_obj.completed_at,
        )
        return success_response(
            data=MTMPlanFormSerializer(plan_obj).data,
            message="干预计划已完成",
        )
