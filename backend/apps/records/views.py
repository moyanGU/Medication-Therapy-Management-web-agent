import json
from datetime import datetime, timedelta

from django.db.models import Avg, Count, F, Q
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.response import APIResponse

from .adherence import (
    build_adherence_summary,
    build_adherence_trend,
    build_response_summary,
    build_risk_level,
    get_adherence_records_queryset,
    get_reminder_history_queryset,
)
from .filters import MedicationRecordFilter
from .models import MedicationRecord
from .serializers import (
    MedicationRecordCreateSerializer,
    MedicationRecordListSerializer,
    MedicationRecordSerializer,
    MedicationRecordStatsSerializer,
)


class MedicationRecordViewSet(viewsets.ModelViewSet):
    """
    用药记录视图集
    提供用药记录的CRUD操作、统计分析和导出功能
    """

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = MedicationRecordFilter
    search_fields = ["medicine__name", "notes", "side_effects"]
    ordering_fields = ["taken_at", "created_at", "adherence_score"]
    ordering = ["-taken_at"]

    def get_queryset(self):
        """
        获取当前用户的用药记录
        """
        return MedicationRecord.objects.filter(user=self.request.user).select_related(
            "medicine", "user", "reminder"
        )

    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == "create":
            return MedicationRecordCreateSerializer
        elif self.action == "list":
            return MedicationRecordListSerializer
        return MedicationRecordSerializer

    def perform_create(self, serializer):
        """
        创建用药记录时自动设置用户
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        创建用药记录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 使用详细序列化器返回完整数据
        response_serializer = MedicationRecordSerializer(serializer.instance)

        return APIResponse.success(
            data=response_serializer.data,
            message="用药记录创建成功",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        获取用药记录统计信息
        """
        # 获取查询参数
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        medicine_id = request.query_params.get("medicine_id")

        # 构建查询条件
        queryset = self.get_queryset()

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                queryset = queryset.filter(taken_at__date__gte=start_date)
            except ValueError:
                return Response(
                    {"error": "开始日期格式错误，请使用YYYY-MM-DD格式"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(taken_at__date__lte=end_date)
            except ValueError:
                return Response(
                    {"error": "结束日期格式错误，请使用YYYY-MM-DD格式"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if medicine_id:
            queryset = queryset.filter(medicine_id=medicine_id)

        # 计算统计数据
        total_records = queryset.count()

        if total_records == 0:
            stats_data = {
                "total_records": 0,
                "taken_count": 0,
                "missed_count": 0,
                "delayed_count": 0,
                "adherence_rate": 0.0,
                "avg_effectiveness": 0.0,
                "most_used_medicine": "",
                "daily_average": 0.0,
            }
        else:
            # 按状态统计
            status_stats = queryset.values("status").annotate(count=Count("id"))
            status_dict = {item["status"]: item["count"] for item in status_stats}

            taken_count = status_dict.get("taken", 0)
            missed_count = status_dict.get("missed", 0)
            delayed_count = status_dict.get("delayed", 0)

            # 计算依从性
            adherence_rate = (
                (taken_count / total_records) * 100 if total_records > 0 else 0
            )

            # 计算平均效果评分
            avg_effectiveness = (
                queryset.filter(effectiveness_score__isnull=False).aggregate(
                    avg=Avg("effectiveness_score")
                )["avg"]
                or 0
            )

            # 最常用药品
            most_used = (
                queryset.values("medicine__name")
                .annotate(count=Count("id"))
                .order_by("-count")
                .first()
            )
            most_used_medicine = most_used["medicine__name"] if most_used else ""

            # 计算日均用药次数
            if start_date and end_date:
                days = (end_date - start_date).days + 1
                daily_average = total_records / days if days > 0 else 0
            else:
                # 默认计算最近30天
                thirty_days_ago = timezone.now().date() - timedelta(days=30)
                recent_records = queryset.filter(
                    taken_at__date__gte=thirty_days_ago
                ).count()
                daily_average = recent_records / 30

            stats_data = {
                "total_records": total_records,
                "taken_count": taken_count,
                "missed_count": missed_count,
                "delayed_count": delayed_count,
                "adherence_rate": round(adherence_rate, 2),
                "avg_effectiveness": round(avg_effectiveness, 2),
                "most_used_medicine": most_used_medicine,
                "daily_average": round(daily_average, 2),
            }

        serializer = MedicationRecordStatsSerializer(stats_data)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def adherence(self, request):
        """
        获取提醒闭环依从性聚合数据
        """
        try:
            period = self._parse_adherence_period(request)
            medicine_id = request.query_params.get("medicine_id")

            logger_message = (
                "获取依从性聚合数据，user=%s，start_date=%s，end_date=%s，days=%s，medicine_id=%s"
            )
            print(
                logger_message
                % (
                    request.user.username,
                    period["start_date"],
                    period["end_date"],
                    period["days"],
                    medicine_id,
                )
            )

            current_records = self._get_adherence_records_queryset(
                start_date=period["start_date"],
                end_date=period["end_date"],
                medicine_id=medicine_id,
            )
            current_history = self._get_reminder_history_queryset(
                start_date=period["start_date"],
                end_date=period["end_date"],
                medicine_id=medicine_id,
            )

            summary_7d_start = timezone.now().date() - timedelta(days=6)
            summary_30d_start = timezone.now().date() - timedelta(days=29)

            data = {
                "period": {
                    "start_date": period["start_date"].isoformat(),
                    "end_date": period["end_date"].isoformat(),
                    "days": period["days"],
                    "medicine_id": int(medicine_id) if medicine_id else None,
                },
                "summary_7d": self._build_adherence_summary(
                    self._get_adherence_records_queryset(
                        start_date=summary_7d_start,
                        end_date=timezone.now().date(),
                        medicine_id=medicine_id,
                    ),
                    self._get_reminder_history_queryset(
                        start_date=summary_7d_start,
                        end_date=timezone.now().date(),
                        medicine_id=medicine_id,
                    ),
                ),
                "summary_30d": self._build_adherence_summary(
                    self._get_adherence_records_queryset(
                        start_date=summary_30d_start,
                        end_date=timezone.now().date(),
                        medicine_id=medicine_id,
                    ),
                    self._get_reminder_history_queryset(
                        start_date=summary_30d_start,
                        end_date=timezone.now().date(),
                        medicine_id=medicine_id,
                    ),
                ),
                "current_period": self._build_adherence_summary(
                    current_records,
                    current_history,
                ),
                "trend": self._build_adherence_trend(
                    current_records,
                    period["start_date"],
                    period["end_date"],
                ),
            }

            return APIResponse.success(data=data, message="获取依从性聚合数据成功")
        except ValueError as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return APIResponse.server_error(message=f"获取依从性聚合数据失败: {exc}")

    @action(detail=False, methods=["get"])
    def categories(self, request):
        """
        分类数据占位接口（与前端期望的分类筛选结构对齐）
        注意：MedicationRecord 模型不包含医院/科室/医生/诊断等字段，此处返回空列表结构，避免 404 并保持接口契约一致。
        """
        data = {
            "hospitals": [],
            "departments": [],
            "doctors": [],
            "diagnoses": [],
            "visit_types": [],
            "urgency_levels": [],
        }
        return Response({"success": True, "data": data})

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """
        获取用药趋势数据
        """
        # 获取最近30天的数据
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        queryset = self.get_queryset().filter(taken_at__date__gte=thirty_days_ago)

        # 按日期分组统计
        daily_stats = {}
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            daily_stats[date.strftime("%Y-%m-%d")] = {
                "date": date.strftime("%Y-%m-%d"),
                "total": 0,
                "taken": 0,
                "missed": 0,
                "delayed": 0,
            }

        # 填充实际数据
        records = queryset.values("taken_at__date", "status").annotate(
            count=Count("id")
        )
        for record in records:
            date_str = record["taken_at__date"].strftime("%Y-%m-%d")
            if date_str in daily_stats:
                daily_stats[date_str]["total"] += record["count"]
                daily_stats[date_str][record["status"]] += record["count"]

        # 转换为列表格式
        trend_data = list(daily_stats.values())

        return Response({"success": True, "data": trend_data})

    @action(detail=False, methods=["get"], url_path="today-medicine-types")
    def today_medicine_types(self, request):
        """
        今日用药种类统计（按去重后的medicine_id计数）
        可选查询参数：
        - date: YYYY-MM-DD，不传则默认今天
        返回：{ success: true, data: { date: 'YYYY-MM-DD', count: number } }
        """
        # 解析日期参数
        date_str = request.query_params.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"success": False, "error": "日期格式错误，请使用YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            target_date = timezone.now().date()

        queryset = self.get_queryset().filter(taken_at__date=target_date)
        # 统计去重后的药品种类数
        medicine_ids = list(queryset.values_list("medicine_id", flat=True).distinct())
        count = len(medicine_ids)

        return Response(
            {
                "success": True,
                "data": {"date": target_date.strftime("%Y-%m-%d"), "count": count},
            }
        )

    @action(detail=False, methods=["get"])
    def export(self, request):
        """
        导出用药记录数据
        """
        # 获取查询参数
        format_type = request.query_params.get("format", "json")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # 构建查询条件
        queryset = self.get_queryset()

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                queryset = queryset.filter(taken_at__date__gte=start_date)
            except ValueError:
                return Response(
                    {"error": "开始日期格式错误"}, status=status.HTTP_400_BAD_REQUEST
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(taken_at__date__lte=end_date)
            except ValueError:
                return Response(
                    {"error": "结束日期格式错误"}, status=status.HTTP_400_BAD_REQUEST
                )

        # 序列化数据
        serializer = MedicationRecordSerializer(queryset, many=True)

        if format_type == "json":
            # JSON格式导出
            response = HttpResponse(
                json.dumps(serializer.data, ensure_ascii=False, indent=2),
                content_type="application/json; charset=utf-8",
            )
            response[
                "Content-Disposition"
            ] = 'attachment; filename="medication_records.json"'
            return response

        return Response({"error": "不支持的导出格式"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """
        获取最近的用药记录
        """
        limit = int(request.query_params.get("limit", 10))
        queryset = self.get_queryset()[:limit]
        serializer = MedicationRecordListSerializer(queryset, many=True)

        return Response({"success": True, "data": serializer.data})

    def _parse_adherence_period(self, request):
        """
        解析依从性统计区间
        """
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        days = int(request.query_params.get("days", 30))

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError("开始日期格式错误，请使用YYYY-MM-DD格式") from exc
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError("结束日期格式错误，请使用YYYY-MM-DD格式") from exc

        if start_date and not end_date:
            end_date = timezone.now().date()
        if end_date and not start_date:
            start_date = end_date - timedelta(days=max(days - 1, 0))

        if not start_date and not end_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=max(days - 1, 0))

        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期")

        actual_days = (end_date - start_date).days + 1
        return {
            "start_date": start_date,
            "end_date": end_date,
            "days": actual_days,
        }

    def _get_adherence_records_queryset(self, start_date, end_date, medicine_id=None):
        """
        获取提醒闭环来源的正式用药记录
        """
        return get_adherence_records_queryset(
            user=self.request.user,
            start_date=start_date,
            end_date=end_date,
            medicine_id=medicine_id,
        )

    def _get_reminder_history_queryset(self, start_date, end_date, medicine_id=None):
        """
        获取提醒历史，用于补充响应摘要
        """
        return get_reminder_history_queryset(
            user=self.request.user,
            start_date=start_date,
            end_date=end_date,
            medicine_id=medicine_id,
        )

    def _build_adherence_summary(self, queryset, history_queryset):
        """
        构造依从性摘要
        """
        return build_adherence_summary(queryset, history_queryset)

    def _build_response_summary(self, history_queryset):
        """
        构造提醒响应补充摘要
        """
        return build_response_summary(history_queryset)

    def _build_risk_level(
        self, adherence_rate, missed_count, delayed_count, partial_count, response_rate
    ):
        """
        根据依从性和响应情况输出风险等级
        """
        return build_risk_level(
            adherence_rate=adherence_rate,
            missed_count=missed_count,
            delayed_count=delayed_count,
            partial_count=partial_count,
            response_rate=response_rate,
        )

    def _build_adherence_trend(self, queryset, start_date, end_date):
        """
        构造依从性按日趋势
        """
        return build_adherence_trend(queryset, start_date, end_date)
