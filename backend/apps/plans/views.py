import logging

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.response import APIResponse

from .models import MedicationPlan
from .serializers import MedicationPlanListSerializer, MedicationPlanSerializer

logger = logging.getLogger(__name__)


class MedicationPlanViewSet(viewsets.ModelViewSet):
    """
    用药计划 视图集
    - 列表、详情、创建、更新、删除
    - 仅当前登录用户数据
    - 与现有统一响应和分页结构保持一致
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # 搜索字段：名称、描述、诊断、目标
    search_fields = ["name", "description", "diagnosis", "treatment_goal"]

    # 过滤字段：类型、状态、日期范围、是否激活、优先级
    filterset_fields = {
        "plan_type": ["exact"],
        "status": ["exact", "in"],
        "is_active": ["exact"],
        "priority": ["exact", "in"],
        "start_date": ["gte", "lte"],
        "end_date": ["gte", "lte", "isnull"],
        "created_at": ["gte", "lte"],
    }

    # 排序字段
    ordering_fields = ["created_at", "start_date", "end_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        仅返回当前用户的计划
        """
        queryset = MedicationPlan.objects.filter(user=self.request.user).annotate(
            medicines_count=Count("plan_medicines")
        )
        if self.action == "list":
            return queryset
        return queryset.prefetch_related("plan_medicines__medicine")

    def get_serializer_class(self):
        if self.action == "list":
            return MedicationPlanListSerializer
        return MedicationPlanSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"🔵 [Plans] create - user={request.user.id}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"🟢 [Plans] created id={serializer.instance.id}")
            return APIResponse.success(
                data=MedicationPlanSerializer(serializer.instance).data,
                message="创建用药计划成功",
            )
        logger.error(f"🔴 [Plans] create invalid: {serializer.errors}")
        return APIResponse.error(message="数据验证失败", errors=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取用药计划列表成功")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data, message="获取用药计划详情成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=MedicationPlanSerializer(serializer.instance).data,
                message="更新用药计划成功",
            )
        return APIResponse.error(message="数据验证失败", errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除用药计划成功", data=None)
