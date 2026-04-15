import logging

from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.response import error_response, success_response

from .models import MTMServiceCase
from .serializers import (
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
