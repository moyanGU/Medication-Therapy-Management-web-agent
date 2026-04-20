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

from .models import MTMAssessment, MTMInterview, MTMServiceCase
from .serializers import (
    MTMAssessmentCompleteSerializer,
    MTMAssessmentDraftSerializer,
    MTMAssessmentFormSerializer,
    MTMInterviewCompleteSerializer,
    MTMInterviewDraftSerializer,
    MTMInterviewFormSerializer,
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
        "assigned_pharmacist": ["exact", "isnull"],
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


    def _build_initial_plan_payload(self, service_case):
        return {
            "service_case": service_case,
            "interventions": [],
            "priority": "medium",
            "patient_confirmation_status": "pending",
            "patient_confirmation_notes": "",
        }

    def _get_or_create_plan(self, service_case):
        from .models import MTMPlan
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

    def get_queryset(self):
        """
        仅返回当前用户参与的服务单。
        如果是药师（is_staff=True 或 is_admin=True），除了返回指派给自己的，
        也可以返回没有 assigned_pharmacist 的待认领单（如果业务需要）。
        目前为了数据隔离，默认返回患者为本人，或指派给自己的服务单。
        """
        user = self.request.user
        if getattr(user, "is_staff", False) or getattr(user, "is_admin", False):
            # 药师：能看到指派给自己的，以及还未指派药师的（可以认领）
            queryset = MTMServiceCase.objects.filter(
                Q(assigned_pharmacist=user) | Q(assigned_pharmacist__isnull=True)
            )
        else:
            # 患者：只能看到自己的
            queryset = MTMServiceCase.objects.filter(patient=user)
            
        queryset = (
            queryset.select_related(
                "patient", "assigned_pharmacist", "interview", "assessment", "plan"
            )
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

    @action(detail=True, methods=["post"], url_path="claim")
    def claim(self, request, pk=None):
        """
        药师认领服务单
        """
        service_case = self.get_object()
        
        # 必须是药师
        if not (getattr(request.user, "is_staff", False) or getattr(request.user, "is_admin", False)):
            return error_response(message="只有药师可以认领服务单", status_code=403)
            
        if service_case.assigned_pharmacist is not None:
            if service_case.assigned_pharmacist == request.user:
                return success_response(message="您已经认领了该服务单")
            return error_response(message="该服务单已被其他药师认领", status_code=400)
            
        service_case.assigned_pharmacist = request.user
        service_case.save(update_fields=["assigned_pharmacist", "updated_at"])
        
        logger.info(
            "🟢 [MTM] service case claimed - case=%s pharmacist=%s",
            service_case.id,
            request.user.id,
        )
        return success_response(
            data=MTMServiceCaseDetailSerializer(service_case).data,
            message="认领成功"
        )

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
        service_case = self.get_object()
        plan = self._get_or_create_plan(service_case)
        from .serializers import MTMPlanSummarySerializer

        if request.method == "GET":
            logger.info("🔵 [MTM] plan fetch - case=%s plan=%s", service_case.id, plan.id)
            serializer = MTMPlanSummarySerializer(plan)
            return success_response(data=serializer.data)

        if request.method == "PUT":
            from .serializers import MTMPlanDraftSerializer
            serializer = MTMPlanDraftSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message="保存草稿失败", errors=serializer.errors)

            for field, value in serializer.validated_data.items():
                setattr(plan, field, value)
            plan.save()
            logger.info("🟢 [MTM] plan draft saved - case=%s", service_case.id)
            return success_response(data=MTMPlanSummarySerializer(plan).data)

    @action(detail=True, methods=["post"], url_path="plan/complete")
    def complete_plan(self, request, pk=None):
        service_case = self.get_object()
        plan = self._get_or_create_plan(service_case)

        from .serializers import MTMPlanCompleteSerializer, MTMPlanSummarySerializer
        serializer = MTMPlanCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="完成计划失败，数据不完整", errors=serializer.errors)

        with transaction.atomic():
            for field, value in serializer.validated_data.items():
                setattr(plan, field, value)
            plan.save()

            if service_case.status in ["assessing", "interviewing", "pending"]:
                service_case.transition_to("intervening", note="干预计划已制定，自动进入干预阶段")
            
        logger.info("🟢 [MTM] plan completed - case=%s", service_case.id)
        return success_response(data=MTMPlanSummarySerializer(plan).data)

    @action(detail=True, methods=["get", "post"], url_path="follow-ups")
    def follow_ups(self, request, pk=None):
        service_case = self.get_object()
        from .serializers import MTMFollowUpSummarySerializer

        if request.method == "GET":
            follow_ups = service_case.follow_ups.all().order_by("-follow_up_time")
            return success_response(data=MTMFollowUpSummarySerializer(follow_ups, many=True).data)

        if request.method == "POST":
            from .serializers import MTMFollowUpFormSerializer
            serializer = MTMFollowUpFormSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message="保存随访记录失败", errors=serializer.errors)

            with transaction.atomic():
                follow_up = serializer.save(service_case=service_case)
                logger.info("🟢 [MTM] follow-up created - case=%s id=%s", service_case.id, follow_up.id)
                
                if service_case.status == "intervening":
                    service_case.transition_to("follow_up", note="随访记录已创建，自动进入随访阶段")

            return success_response(data=MTMFollowUpSummarySerializer(follow_up).data)


    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, pk=None):
        """
        获取服务单完整的 PMR (个人用药记录) & MAP (药物行动计划) 聚合数据
        用于在前端渲染医疗级文档和导出 PDF
        """
        service_case = self.get_object()
        
        # 依赖已有关系和序列化器，拼接完整的报告对象
        from .serializers import (
            MTMServiceCaseDetailSerializer,
        )
        from apps.medical_records.models import MedicalRecord
        from apps.medical_records.serializers import MedicalRecordListSerializer
        
        # 1. 基础服务单详情 (含问诊、评估、计划、随访的最新快照)
        case_data = MTMServiceCaseDetailSerializer(service_case).data
        
        # 2. PMR: 患者当前的用药记录 (聚合其在系统中维护的 MedicalRecord / Medicines)
        # 获取患者当前所有有效的处方和用药记录
        patient = service_case.patient
        active_records = MedicalRecord.objects.filter(patient=patient).prefetch_related("medicines").order_by("-visit_date")
        
        pmr_data = []
        for record in active_records:
            pmr_data.append({
                "record_id": record.id,
                "visit_date": record.visit_date,
                "hospital": record.hospital,
                "department": record.department,
                "diagnosis": record.diagnosis,
                "medicines": [
                    {
                        "name": m.medicine_name,
                        "dosage": m.dosage,
                        "frequency": m.frequency,
                        "instructions": m.instructions
                    } for m in record.medicines.all()
                ]
            })
            
        # 组装完整的 Report 结构
        report_data = {
            "case_info": {
                "case_number": case_data.get("case_number"),
                "status": case_data.get("status"),
                "service_goal": case_data.get("service_goal"),
                "created_at": case_data.get("created_at"),
                "completed_at": case_data.get("completed_at"),
            },
            "patient_info": case_data.get("patient"),
            "pharmacist_info": case_data.get("assigned_pharmacist"),
            "pmr": {
                "medical_records": pmr_data,
                "allergies": case_data.get("interview", {}).get("allergy_history", []),
                "medication_history": case_data.get("interview", {}).get("medication_history", []),
                "lifestyle": case_data.get("interview", {}).get("lifestyle_info", {}),
            },
            "assessment": case_data.get("assessment", {}),
            "map": case_data.get("plan", {}),
            "follow_ups": case_data.get("follow_ups", [])
        }

        logger.info("🔵 [MTM] report generated - case=%s", service_case.id)
        return success_response(data=report_data)


    @action(detail=True, methods=["get", "put"], url_path="soap")
    def soap_notes(self, request, pk=None):
        """
        获取或保存 SOAP 药历记录
        """
        service_case = self.get_object()
        
        if request.method == "GET":
            return success_response(data=service_case.soap_notes)
            
        if request.method == "PUT":
            soap_data = request.data
            service_case.soap_notes = soap_data
            service_case.save(update_fields=["soap_notes", "updated_at"])
            logger.info("🟢 [MTM] SOAP notes updated - case=%s", service_case.id)
            return success_response(data=service_case.soap_notes)

    @action(detail=True, methods=["post"], url_path="soap/generate")
    def generate_soap(self, request, pk=None):
        """
        调用 AI 辅助一键生成 SOAP 草稿
        """
        service_case = self.get_object()
        
        from django.conf import settings
        if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
            return error_response("AI 服务未启用", status_code=503)
            
        # 收集上下文信息 (问诊记录、评估记录)
        patient_data = {
            "case_number": service_case.case_number,
            "service_goal": service_case.service_goal,
            "patient_age": service_case.patient.age,
            "patient_gender": service_case.patient.get_gender_display() if service_case.patient.gender else "未知",
        }
        
        interview = getattr(service_case, "interview", None)
        if interview:
            patient_data["medication_history"] = interview.medication_history
            patient_data["allergy_history"] = interview.allergy_history
            patient_data["lifestyle_info"] = interview.lifestyle_info
            patient_data["health_expectations"] = interview.health_expectations
            
        assessment = getattr(service_case, "assessment", None)
        if assessment:
            patient_data["problem_list"] = assessment.problem_list
            patient_data["assessment_summary"] = assessment.summary
            patient_data["risk_level"] = assessment.risk_level
            
        # 准备调用大模型子代理
        from apps.core.agents.soap_agent import SoapAgent
        
        try:
            logger.info("🔵 [MTM] SOAP AI Generation start - case=%s", service_case.id)
            agent = SoapAgent(user_id=request.user.id, session_id=f"mtm_soap_{service_case.id}")
            soap_json = agent.generate(patient_data)
            return success_response(data=soap_json)
        except Exception as e:
            logger.error("🔴 [MTM] SOAP Generation Failed: %s", str(e))
            return error_response(f"AI 生成失败: {str(e)}", status_code=500)
