from datetime import datetime, timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import StandardResultsSetPagination

from .history_filters import ReminderHistoryFilter, ReminderStatsFilter
from .history_models import ReminderHistory, ReminderStats
from .history_serializers import (
    ReminderHistoryCreateSerializer,
    ReminderHistoryResponseSerializer,
    ReminderHistorySerializer,
    ReminderStatsSerializer,
)


class ReminderHistoryViewSet(viewsets.ModelViewSet):
    """
    提醒历史记录视图集
    """

    serializer_class = ReminderHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReminderHistoryFilter
    search_fields = ["title", "message", "reminder__medicine__name"]
    ordering_fields = ["sent_at", "responded_at", "response_delay_minutes"]
    ordering = ["-sent_at"]

    def get_queryset(self):
        """
        获取当前用户的提醒历史记录
        """
        return ReminderHistory.objects.filter(user=self.request.user).select_related(
            "reminder", "reminder__medicine", "user"
        )

    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == "create":
            return ReminderHistoryCreateSerializer
        elif self.action == "respond":
            return ReminderHistoryResponseSerializer
        return ReminderHistorySerializer

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        """
        用户响应提醒
        """
        try:
            history = self.get_object()

            # 检查是否已经响应过
            if history.is_responded:
                return Response(
                    {"error": "该提醒已经响应过了"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # 标记响应
                history.mark_responded(
                    response_type=serializer.validated_data["response_type"],
                    notes=serializer.validated_data.get("notes"),
                )

                # 更新提醒的响应计数
                if history.reminder:
                    history.reminder.increment_response_count()

                return Response(
                    {
                        "success": True,
                        "message": "响应记录成功",
                        "data": ReminderHistorySerializer(history).data,
                    }
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"响应失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def today(self, request):
        """
        获取今天的提醒历史
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(sent_at__date=today)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """
        获取最近的提醒历史（7天内）
        """
        recent_date = timezone.now() - timedelta(days=7)
        queryset = self.get_queryset().filter(sent_at__gte=recent_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        获取提醒历史统计
        """
        try:
            # 获取查询参数
            days = int(request.query_params.get("days", 30))
            start_date = timezone.now() - timedelta(days=days)

            queryset = self.get_queryset().filter(sent_at__gte=start_date)

            # 基础统计
            total_count = queryset.count()
            sent_count = queryset.filter(status="sent").count()
            responded_count = queryset.exclude(response_type="no_response").count()
            taken_count = queryset.filter(response_type="taken").count()

            # 计算率
            response_rate = (
                (responded_count / sent_count * 100) if sent_count > 0 else 0
            )
            adherence_rate = (taken_count / sent_count * 100) if sent_count > 0 else 0

            # 平均响应时间
            avg_response_time = (
                queryset.filter(response_delay_minutes__isnull=False).aggregate(
                    avg=Avg("response_delay_minutes")
                )["avg"]
                or 0
            )

            # 按响应类型统计
            response_type_stats = (
                queryset.values("response_type")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

            # 按药品统计
            medicine_stats = (
                queryset.values("reminder__medicine__id", "reminder__medicine__name")
                .annotate(
                    total_count=Count("id"),
                    taken_count=Count("id", filter=Q(response_type="taken")),
                )
                .order_by("-total_count")[:10]
            )

            return Response(
                {
                    "success": True,
                    "data": {
                        "total_reminders": total_count,
                        "sent_reminders": sent_count,
                        "responded_reminders": responded_count,
                        "taken_reminders": taken_count,
                        "response_rate": round(response_rate, 2),
                        "adherence_rate": round(adherence_rate, 2),
                        "avg_response_time": round(avg_response_time, 2),
                        "response_type_stats": list(response_type_stats),
                        "medicine_stats": list(medicine_stats),
                        "period_days": days,
                    },
                }
            )

        except Exception as e:
            return Response(
                {"error": f"获取统计数据失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def metrics(self, request):
        try:
            days = int(request.query_params.get("days", 7))
            start_dt = timezone.now() - timedelta(days=days)
            qs = list(self.get_queryset().filter(sent_at__gte=start_dt))

            total = len(qs)
            sent_qs = [h for h in qs if h.status == "sent"]
            failed = sum(1 for h in qs if h.status == "failed")
            pending = sum(1 for h in qs if h.status == "pending")

            delays = []
            for h in sent_qs:
                if h.sent_at and h.scheduled_time:
                    delays.append((h.sent_at - h.scheduled_time).total_seconds() / 60.0)
            avg_delay = sum(delays) / len(delays) if delays else 0.0

            push_sent = sum(
                1 for h in sent_qs if "push" in (h.notification_methods or [])
            )
            sms_sent = sum(
                1 for h in sent_qs if "sms" in (h.notification_methods or [])
            )
            email_sent = sum(
                1 for h in sent_qs if "email" in (h.notification_methods or [])
            )

            responded_count = sum(
                1
                for h in sent_qs
                if h.response_type and h.response_type != "no_response"
            )
            response_rate = (
                round((responded_count / len(sent_qs) * 100.0), 2) if sent_qs else 0.0
            )

            channel_failed = {
                "push_failed": sum(
                    1
                    for h in qs
                    if h.status == "failed" and "push" in (h.notification_methods or [])
                ),
                "sms_failed": sum(
                    1
                    for h in qs
                    if h.status == "failed" and "sms" in (h.notification_methods or [])
                ),
                "email_failed": sum(
                    1
                    for h in qs
                    if h.status == "failed"
                    and "email" in (h.notification_methods or [])
                ),
            }

            escalated_items = [h for h in qs if (h.title or "").strip() == "补发提醒"]
            escalated_total = len(escalated_items)
            escalated_sent = sum(1 for h in escalated_items if h.status == "sent")
            escalation_success_rate = (
                round((escalated_sent / escalated_total * 100.0), 2)
                if escalated_total
                else 0.0
            )

            warnings: list[str] = []
            try:
                if response_rate < 60.0:
                    warnings.append(f"响应率偏低：{response_rate}%")
                if sent_qs:
                    fail_rate = round((failed / len(sent_qs)) * 100.0, 2)
                    if fail_rate > 20.0:
                        warnings.append(f"失败率偏高：{fail_rate}%")
                else:
                    if failed > 0:
                        warnings.append("存在失败记录且无成功发送")
            except Exception:
                pass

            data = {
                "period_days": days,
                "total": total,
                "sent": len(sent_qs),
                "failed": failed,
                "pending": pending,
                "avg_response_delay_minutes": round(avg_delay or 0, 2),
                "channel": {
                    "push_sent": push_sent,
                    "sms_sent": sms_sent,
                    "email_sent": email_sent,
                    **channel_failed,
                },
                "response_rate": response_rate,
                "escalation": {
                    "escalated_total": escalated_total,
                    "escalated_sent": escalated_sent,
                    "escalation_success_rate": escalation_success_rate,
                },
                "warnings": warnings,
            }

            return Response({"success": True, "data": data})
        except Exception as e:
            return Response(
                {"success": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReminderStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提醒统计视图集
    """

    serializer_class = ReminderStatsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReminderStatsFilter
    ordering_fields = ["date", "response_rate", "adherence_rate"]
    ordering = ["-date"]

    def get_queryset(self):
        """
        获取当前用户的提醒统计
        """
        return ReminderStats.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def trend(self, request):
        """
        获取趋势数据
        """
        try:
            # 获取查询参数
            days = int(request.query_params.get("days", 30))
            start_date = timezone.now().date() - timedelta(days=days)

            queryset = self.get_queryset().filter(date__gte=start_date)

            # 按日期排序
            trend_data = queryset.order_by("date").values(
                "date",
                "scheduled_count",
                "sent_count",
                "responded_count",
                "taken_count",
                "response_rate",
                "adherence_rate",
                "avg_response_time",
            )

            return Response({"success": True, "data": list(trend_data)})

        except Exception as e:
            return Response(
                {"error": f"获取趋势数据失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        获取统计摘要
        """
        try:
            # 获取查询参数
            days = int(request.query_params.get("days", 30))
            start_date = timezone.now().date() - timedelta(days=days)

            queryset = self.get_queryset().filter(date__gte=start_date)

            # 汇总统计
            summary = queryset.aggregate(
                total_scheduled=Count("scheduled_count"),
                total_sent=Count("sent_count"),
                total_responded=Count("responded_count"),
                total_taken=Count("taken_count"),
                avg_response_rate=Avg("response_rate"),
                avg_adherence_rate=Avg("adherence_rate"),
                avg_response_time=Avg("avg_response_time"),
            )

            # 最近7天的数据
            recent_week = queryset.filter(
                date__gte=timezone.now().date() - timedelta(days=7)
            ).aggregate(
                week_response_rate=Avg("response_rate"),
                week_adherence_rate=Avg("adherence_rate"),
            )

            # 合并数据
            summary.update(recent_week)

            # 计算趋势
            if queryset.count() >= 2:
                latest = queryset.order_by("-date").first()
                previous = queryset.order_by("-date")[1]

                response_trend = latest.response_rate - previous.response_rate
                adherence_trend = latest.adherence_rate - previous.adherence_rate

                summary["response_trend"] = round(response_trend, 2)
                summary["adherence_trend"] = round(adherence_trend, 2)
            else:
                summary["response_trend"] = 0
                summary["adherence_trend"] = 0

            return Response({"success": True, "data": summary})

        except Exception as e:
            return Response(
                {"error": f"获取统计摘要失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def update_stats(self, request):
        """
        更新统计数据
        """
        try:
            # 获取日期参数
            date_str = request.data.get("date")
            if date_str:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                target_date = timezone.now().date()

            # 获取或创建统计记录
            stats, created = ReminderStats.objects.get_or_create(
                user=request.user, date=target_date
            )

            # 从历史记录更新统计
            stats.update_from_history()

            return Response(
                {
                    "success": True,
                    "message": "统计数据更新成功",
                    "data": ReminderStatsSerializer(stats).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"更新统计数据失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
