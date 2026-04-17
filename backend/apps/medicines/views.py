from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.response import APIResponse

from .models import Medicine
from .serializers import (
    MedicineCreateSerializer,
    MedicineListSerializer,
    MedicineSerializer,
    MedicineUpdateSerializer,
)


from django.db.models import Sum


class MedicineViewSet(viewsets.ModelViewSet):
    """
    药品管理视图集
    提供药品的CRUD操作
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # 搜索字段
    search_fields = ["name", "manufacturer", "specification", "description"]

    # 过滤字段
    filterset_fields = {
        "medicine_type": ["exact"],
        "is_prescription": ["exact"],
        "expiry_date": ["gte", "lte"],
        "quantity": ["gte", "lte"],
        "created_at": ["gte", "lte"],
    }

    # 排序字段
    ordering_fields = [
        "name",
        "expiry_date",
        "quantity",
        "created_at",
        "purchase_price",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        获取当前用户的药品列表
        """
        return Medicine.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        根据操作类型选择序列化器
        """
        if self.action == "create":
            return MedicineCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return MedicineUpdateSerializer
        elif self.action == "list":
            return MedicineListSerializer
        return MedicineSerializer

    def perform_create(self, serializer):
        """
        创建药品时自动关联当前用户
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        创建药品
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.info(
            f"🔵 [Medicine View] create 开始执行 - 用户: {request.user.id if request.user.is_authenticated else 'Anonymous'}"
        )
        logger.info(f"🔵 [Medicine View] 原始请求字段: {list(request.data.keys())}")

        try:
            # 预处理请求数据，移除空的image_url字段
            cleaned_data = dict(request.data)

            # 如果image_url为空字符串或None，则删除该字段
            if "image_url" in cleaned_data:
                image_url_value = cleaned_data["image_url"]
                if (
                    image_url_value == ""
                    or image_url_value is None
                    or image_url_value == "undefined"
                ):
                    del cleaned_data["image_url"]
                    logger.info(
                        f"🔵 [Medicine View] 删除空的image_url字段: '{image_url_value}'"
                    )

            logger.info(f"🔵 [Medicine View] 清理后的字段: {list(cleaned_data.keys())}")

            serializer = self.get_serializer(data=cleaned_data)
            logger.info(f"🔵 [Medicine View] 序列化器创建完成: {type(serializer).__name__}")

            if serializer.is_valid():
                logger.info("🔵 [Medicine View] 数据验证通过")
                logger.info(
                    f"🔵 [Medicine View] 验证后的字段: {list(serializer.validated_data.keys())}"
                )

                self.perform_create(serializer)
                logger.info(f"🟢 [Medicine View] 药品创建成功 - ID: {serializer.instance.id}")

                response_data = MedicineSerializer(serializer.instance).data
                logger.info(f"🟢 [Medicine View] 返回字段: {list(response_data.keys())}")

                return APIResponse.success(data=response_data, message="药品创建成功")
            else:
                logger.error(f"🔴 [Medicine View] 数据验证失败: {serializer.errors}")
                return APIResponse.error(message="数据验证失败", errors=serializer.errors)
        except Exception as e:
            logger.error(f"🔴 [Medicine View] 创建药品异常: {str(e)}")
            logger.error(f"🔴 [Medicine View] 异常详情: {e.__class__.__name__}: {e}")
            import traceback

            logger.error(f"🔴 [Medicine View] 异常堆栈: {traceback.format_exc()}")
            raise

    def list(self, request, *args, **kwargs):
        """
        获取药品列表
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取药品列表成功")

    def retrieve(self, request, *args, **kwargs):
        """
        获取药品详情
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data, message="获取药品详情成功")

    def update(self, request, *args, **kwargs):
        """
        更新药品信息
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return APIResponse.success(
                data=MedicineSerializer(serializer.instance).data, message="药品更新成功"
            )
        return APIResponse.error(message="数据验证失败", errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """
        删除药品
        """
        instance = self.get_object()
        medicine_name = instance.name
        self.perform_destroy(instance)
        return APIResponse.success(message=f"药品 '{medicine_name}' 删除成功")

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        获取已过期的药品列表
        """
        today = timezone.now().date()
        queryset = (
            self.get_queryset()
            .filter(expiry_date__lt=today)
            .exclude(expiry_date__isnull=True)
        )

        serializer = MedicineListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取过期药品列表成功")

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """
        获取即将过期的药品列表（30天内）
        """
        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)

        queryset = self.get_queryset().filter(
            expiry_date__gte=today, expiry_date__lte=thirty_days_later
        )

        serializer = MedicineListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取即将过期药品列表成功")

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """
        获取库存不足的药品列表
        """
        threshold = int(request.query_params.get("threshold", 5))
        queryset = self.get_queryset().filter(quantity__lte=threshold)

        serializer = MedicineListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取库存不足药品列表成功")

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        获取药品统计信息
        """
        queryset = self.get_queryset()
        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)

        total_quantity_agg = queryset.aggregate(total=Sum('quantity'))

        stats = {
            "total_medicines": queryset.count(),
            "expired_count": queryset.filter(expiry_date__lt=today)
            .exclude(expiry_date__isnull=True)
            .count(),
            "expiring_soon_count": queryset.filter(
                expiry_date__gte=today, expiry_date__lte=thirty_days_later
            ).count(),
            "low_stock_count": queryset.filter(quantity__lte=5).count(),
            "prescription_count": queryset.filter(is_prescription=True).count(),
            "total_quantity": total_quantity_agg.get('total') or 0,
        }

        return APIResponse.success(data=stats, message="获取药品统计信息成功")

    @action(detail=False, methods=["get"])
    def types(self, request):
        """
        获取药品类型列表
        """
        types = [
            {"value": choice[0], "label": choice[1]}
            for choice in Medicine.MEDICINE_TYPE_CHOICES
        ]
        return APIResponse.success(data=types, message="获取药品类型列表成功")

    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        """
        更新药品数量
        """
        instance = self.get_object()
        quantity = request.data.get("quantity")

        if quantity is None:
            return APIResponse.error(message="请提供数量参数")

        try:
            quantity = int(quantity)
            if quantity < 0:
                return APIResponse.error(message="数量不能为负数")

            instance.quantity = quantity
            instance.save()

            serializer = MedicineSerializer(instance)
            return APIResponse.success(data=serializer.data, message="药品数量更新成功")
        except ValueError:
            return APIResponse.error(message="数量必须是有效的整数")
