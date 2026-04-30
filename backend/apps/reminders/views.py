import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsOwnerOrReadOnly
from apps.records.models import MedicationRecord

from .filters import ReminderFilter
from .models import Reminder
from .notifications import notification_service
from .serializers import (
    ReminderConfirmSerializer,
    ReminderCreateSerializer,
    ReminderListSerializer,
    ReminderSerializer,
    ReminderUpdateSerializer,
)

logger = logging.getLogger(__name__)

REMINDER_HISTORY_RESPONSE_MAP = {
    "taken": "taken",
    "missed": "skipped",
    "delayed": "delayed",
    "partial": "taken",
}


def build_reminder_confirm_payload(reminder, validated_data):
    """
    构造后续记录落库可复用的标准载荷
    """
    action = validated_data["action"]
    scheduled_time = timezone.make_aware(
        datetime.combine(timezone.localdate(), reminder.reminder_time)
    )
    taken_at = validated_data.get("taken_at")
    delay_minutes = validated_data.get("delay_minutes")

    if action == "delayed" and delay_minutes and not taken_at:
        taken_at = scheduled_time + timedelta(minutes=delay_minutes)

    if action == "taken" and not taken_at:
        taken_at = timezone.now()

    quantity_taken = validated_data.get("quantity_taken")
    if quantity_taken is None:
        if action == "partial":
            quantity_taken = max(1, reminder.dosage - 1)
        elif action == "missed":
            quantity_taken = 0
        else:
            quantity_taken = reminder.dosage

    return {
        "reminder_id": reminder.id,
        "medicine_id": reminder.medicine_id,
        "action": action,
        "record_status": action,
        "scheduled_time": scheduled_time.isoformat(),
        "taken_at": taken_at.isoformat() if taken_at else None,
        "delay_minutes": delay_minutes,
        "quantity_taken": quantity_taken,
        "notes": validated_data.get("notes", ""),
        "source": "reminder",
        "administration_method": "oral",
    }


def sync_medication_record_from_payload(reminder, record_payload):
    """
    将提醒确认结果同步到正式用药记录
    """
    scheduled_time = datetime.fromisoformat(record_payload["scheduled_time"])
    taken_at = (
        datetime.fromisoformat(record_payload["taken_at"])
        if record_payload.get("taken_at")
        else scheduled_time
    )

    record_defaults = {
        "medicine": reminder.medicine,
        "taken_at": taken_at,
        "quantity_taken": record_payload["quantity_taken"],
        "administration_method": record_payload["administration_method"],
        "status": record_payload["record_status"],
        "notes": record_payload.get("notes", ""),
        "delay_minutes": record_payload.get("delay_minutes"),
        "source": record_payload["source"],
    }

    record, created = MedicationRecord.objects.update_or_create(
        user=reminder.user,
        reminder=reminder,
        scheduled_time=scheduled_time,
        defaults=record_defaults,
    )
    return record, created


class ReminderViewSet(viewsets.ModelViewSet):
    """
    提醒视图集
    提供提醒的CRUD操作和相关功能
    """

    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReminderFilter
    search_fields = ["title", "message", "medicine__name"]
    ordering_fields = ["reminder_time", "created_at", "updated_at"]
    ordering = ["reminder_time"]

    def get_queryset(self):
        """
        获取当前用户的提醒
        """
        return (
            Reminder.objects.filter(user=self.request.user)
            .select_related("medicine", "user")
            .order_by("reminder_time")
        )

    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == "create":
            return ReminderCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ReminderUpdateSerializer
        elif self.action == "confirm":
            return ReminderConfirmSerializer
        elif self.action == "list":
            return ReminderListSerializer
        return ReminderSerializer

    def create(self, request, *args, **kwargs):
        """
        创建新的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 创建提醒，数据: {request.data}")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            reminder = serializer.save()

            # 返回完整的提醒信息
            response_serializer = ReminderSerializer(reminder)

            logger.info(f"提醒创建成功，ID: {reminder.id}")
            return Response(
                {
                    "success": True,
                    "message": "提醒创建成功",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"创建提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"创建提醒失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        """
        获取提醒列表
        """
        try:
            logger.info(f"用户 {request.user.username} 获取提醒列表")

            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                # 分页响应统一使用分页器封装，results 为纯数组
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"success": True, "message": "获取提醒列表成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取提醒列表失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取提醒列表失败: {str(e)}", "data": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """
        获取单个提醒详情
        """
        try:
            reminder = self.get_object()
            logger.info(f"用户 {request.user.username} 获取提醒详情，ID: {reminder.id}")

            serializer = self.get_serializer(reminder)
            return Response(
                {"success": True, "message": "获取提醒详情成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取提醒详情失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取提醒详情失败: {str(e)}", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        """
        更新提醒
        """
        try:
            reminder = self.get_object()
            logger.info(
                f"用户 {request.user.username} 更新提醒，ID: {reminder.id}，数据: {request.data}"
            )

            serializer = self.get_serializer(
                reminder, data=request.data, partial=kwargs.get("partial", False)
            )
            serializer.is_valid(raise_exception=True)
            reminder = serializer.save()

            # 返回完整的提醒信息
            response_serializer = ReminderSerializer(reminder)

            logger.info(f"提醒更新成功，ID: {reminder.id}")
            return Response(
                {"success": True, "message": "提醒更新成功", "data": response_serializer.data}
            )

        except Exception as e:
            logger.error(f"更新提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"更新提醒失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        """
        删除提醒
        """
        try:
            reminder = self.get_object()
            reminder_id = reminder.id
            logger.info(f"用户 {request.user.username} 删除提醒，ID: {reminder_id}")

            reminder.delete()

            logger.info(f"提醒删除成功，ID: {reminder_id}")
            return Response(
                {"success": True, "message": "提醒删除成功", "data": None},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"删除提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"删除提醒失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def today(self, request):
        """
        获取今天的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取今天的提醒")

            today = timezone.now().date()
            reminders = (
                self.get_queryset()
                .filter(is_active=True, start_date__lte=today)
                .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            )

            # 过滤出今天应该提醒的
            today_reminders = [r for r in reminders if r.should_remind_today()]

            serializer = ReminderListSerializer(today_reminders, many=True)

            return Response(
                {"success": True, "message": "获取今天的提醒成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取今天的提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取今天的提醒失败: {str(e)}", "data": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """
        获取即将到来的提醒（未来7天）
        """
        try:
            logger.info(f"用户 {request.user.username} 获取即将到来的提醒")

            today = timezone.now().date()
            next_week = today + timedelta(days=7)

            reminders = (
                self.get_queryset()
                .filter(is_active=True, start_date__lte=next_week)
                .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            )

            serializer = ReminderListSerializer(reminders, many=True)

            return Response(
                {"success": True, "message": "获取即将到来的提醒成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取即将到来的提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取即将到来的提醒失败: {str(e)}", "data": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        获取活跃的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取活跃的提醒")

            reminders = self.get_queryset().filter(is_active=True)
            serializer = ReminderListSerializer(reminders, many=True)

            return Response(
                {"success": True, "message": "获取活跃的提醒成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取活跃的提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取活跃的提醒失败: {str(e)}", "data": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        获取已过期的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取已过期的提醒")

            reminders = self.get_queryset()
            expired_reminders = [r for r in reminders if r.is_expired]

            serializer = ReminderListSerializer(expired_reminders, many=True)

            return Response(
                {"success": True, "message": "获取已过期的提醒成功", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"获取已过期的提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取已过期的提醒失败: {str(e)}", "data": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _ics_weekday(self, d: int) -> str:
        return {
            1: "MO",
            2: "TU",
            3: "WE",
            4: "TH",
            5: "FR",
            6: "SA",
            7: "SU",
        }.get(d, "MO")

    def _build_ics_rrule_parts(self, reminder):
        parts: list[str] = []
        if reminder.frequency == "daily":
            parts = ["FREQ=DAILY", "INTERVAL=1"]
        elif reminder.frequency == "every_other_day":
            parts = ["FREQ=DAILY", "INTERVAL=2"]
        elif reminder.frequency == "weekly":
            parts = ["FREQ=WEEKLY", "INTERVAL=1"]
        elif reminder.frequency == "custom" and reminder.weekdays:
            byday = ",".join(self._ics_weekday(d) for d in reminder.weekdays)
            parts = ["FREQ=WEEKLY", f"BYDAY={byday}"]
        elif reminder.frequency in [
            "twice_daily",
            "three_times_daily",
            "four_times_daily",
        ]:
            parts = ["FREQ=DAILY", "INTERVAL=1"]

        if reminder.end_date and parts:
            parts.append(f"UNTIL={reminder.end_date.strftime('%Y%m%d')}")
        return parts

    def _build_ics_event_lines(self, reminder, tzid: str, now):
        title = reminder.title or f"用药提醒 - {reminder.medicine.name}"
        description = (
            reminder.message
            or f"请按计划服用 {reminder.medicine.name}，剂量：{reminder.dosage}{reminder.dosage_unit}"
        )

        start_date = reminder.start_date or now.date()
        dtstart = timezone.make_aware(
            timezone.datetime.combine(start_date, reminder.reminder_time)
        )

        dtstart_str = dtstart.strftime("%Y%m%dT%H%M%S")
        dtstamp_str = now.strftime("%Y%m%dT%H%M%S")

        lines = [
            "BEGIN:VEVENT",
            f"UID:mtm-helper-reminder-{reminder.id}@mtm-helper.com",
            f"DTSTAMP;TZID={tzid}:{dtstamp_str}",
            f"DTSTART;TZID={tzid}:{dtstart_str}",
            f"SUMMARY:{title}",
            f"DESCRIPTION:{description}",
        ]

        rrule_parts = self._build_ics_rrule_parts(reminder)
        if rrule_parts:
            lines.append("RRULE:" + ";".join(rrule_parts))

        lines.append("END:VEVENT")
        return lines

    def _build_ics_calendar_content(self, reminders, tzid: str, now):
        lines: list[str] = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//MTM Helper//EN",
            "CALSCALE:GREGORIAN",
        ]
        for reminder in reminders:
            lines.extend(self._build_ics_event_lines(reminder, tzid, now))
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    @action(detail=False, methods=["get"])
    def calendar_ics(self, request):
        try:
            logger.info(f"用户 {request.user.username} 获取 ICS 日历订阅")

            tzid = getattr(settings, "TIME_ZONE", "UTC")
            now = timezone.localtime()

            reminders = self.get_queryset().filter(is_active=True)
            content = self._build_ics_calendar_content(reminders, tzid, now)
            resp = HttpResponse(content, content_type="text/calendar; charset=utf-8")
            resp["Content-Disposition"] = 'attachment; filename="mtm-reminders.ics"'
            return resp
        except Exception as e:
            logger.error(f"生成 ICS 失败: {str(e)}")
            return Response(
                {"success": False, "message": f"生成 ICS 失败: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        获取提醒统计信息
        """
        try:
            logger.info(f"用户 {request.user.username} 获取提醒统计信息")

            queryset = self.get_queryset()

            stats = {
                "total_reminders": queryset.count(),
                "active_reminders": queryset.filter(is_active=True).count(),
                "inactive_reminders": queryset.filter(is_active=False).count(),
                "expired_reminders": len([r for r in queryset if r.is_expired]),
                "today_reminders": len(
                    [r for r in queryset if r.should_remind_today()]
                ),
                "response_rate": 0,  # 需要从历史记录计算
                "total_responses": 0,  # 需要从历史记录计算
            }

            # 计算响应率（如果有历史记录）
            total_reminders = (
                queryset.aggregate(total_count=models.Sum("reminder_count"))[
                    "total_count"
                ]
                or 0
            )

            total_responses = (
                queryset.aggregate(total_responses=models.Sum("response_count"))[
                    "total_responses"
                ]
                or 0
            )

            if total_reminders > 0:
                stats["response_rate"] = round(
                    (total_responses / total_reminders) * 100, 2
                )

            stats["total_responses"] = total_responses

            return Response({"success": True, "message": "获取提醒统计信息成功", "data": stats})

        except Exception as e:
            logger.error(f"获取提醒统计信息失败: {str(e)}")
            return Response(
                {"success": False, "message": f"获取提醒统计信息失败: {str(e)}", "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        切换提醒的激活状态
        """
        try:
            reminder = self.get_object()
            reminder.is_active = not reminder.is_active
            reminder.save()

            logger.info(
                f"用户 {request.user.username} 切换提醒状态，ID: {reminder.id}，新状态: {reminder.is_active}"
            )

            serializer = ReminderSerializer(reminder)

            return Response(
                {
                    "success": True,
                    "message": f'提醒已{"激活" if reminder.is_active else "停用"}',
                    "data": serializer.data,
                }
            )

        except Exception as e:
            logger.error(f"切换提醒状态失败: {str(e)}")
            return Response(
                {"success": False, "message": f"切换提醒状态失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def mark_responded(self, request, pk=None):
        """
        标记提醒已响应
        """
        try:
            reminder = self.get_object()
            reminder.increment_response_count()

            logger.info(f"用户 {request.user.username} 标记提醒已响应，ID: {reminder.id}")

            serializer = ReminderSerializer(reminder)

            return Response(
                {"success": True, "message": "提醒已标记为已响应", "data": serializer.data}
            )

        except Exception as e:
            logger.error(f"标记提醒响应失败: {str(e)}")
            return Response(
                {"success": False, "message": f"标记提醒响应失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """
        记录提醒确认动作，并返回后续记录落库所需载荷
        """
        try:
            reminder = self.get_object()
            serializer = self.get_serializer(
                data=request.data,
                context={"request": request, "reminder": reminder},
            )
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            action_type = validated_data["action"]

            logger.info(
                "用户 %s 提交提醒确认动作，reminder_id=%s，action=%s，payload=%s",
                request.user.username,
                reminder.id,
                action_type,
                validated_data,
            )

            history_recorded = False
            record_created = False
            record = None
            record_payload = build_reminder_confirm_payload(reminder, validated_data)
            with transaction.atomic():
                reminder.increment_response_count()
                history_recorded = self._record_confirm_action_history(
                    reminder=reminder,
                    action_type=action_type,
                    notes=validated_data.get("notes", ""),
                    delay_minutes=validated_data.get("delay_minutes"),
                )
                record, record_created = sync_medication_record_from_payload(
                    reminder=reminder,
                    record_payload=record_payload,
                )

            reminder.refresh_from_db()

            return Response(
                {
                    "success": True,
                    "message": "提醒确认成功",
                    "data": {
                        "reminder_id": reminder.id,
                        "action": action_type,
                        "response_recorded": True,
                        "response_count": reminder.response_count,
                        "history_recorded": history_recorded,
                        "record_id": record.id if record else None,
                        "record_created": record_created,
                        "record_payload": record_payload,
                    },
                }
            )
        except Http404:
            logger.warning(
                "提醒确认失败：用户 %s 无权访问提醒 %s",
                request.user.username,
                pk,
            )
            return Response(
                {"success": False, "message": "提醒不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"提醒确认失败: {str(e)}")
            return Response(
                {"success": False, "message": f"提醒确认失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def batch_toggle(self, request):
        """
        批量切换提醒状态
        """
        try:
            reminder_ids = request.data.get("reminder_ids", [])
            is_active = request.data.get("is_active", True)

            if not reminder_ids:
                return Response(
                    {"success": False, "message": "请提供提醒ID列表", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reminders = self.get_queryset().filter(id__in=reminder_ids)
            updated_count = reminders.update(is_active=is_active)

            logger.info(f"用户 {request.user.username} 批量切换提醒状态，更新了 {updated_count} 个提醒")

            return Response(
                {
                    "success": True,
                    "message": f"成功更新 {updated_count} 个提醒的状态",
                    "data": {"updated_count": updated_count},
                }
            )

        except Exception as e:
            logger.error(f"批量切换提醒状态失败: {str(e)}")
            return Response(
                {"success": False, "message": f"批量切换提醒状态失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["delete"])
    def batch_delete(self, request):
        """
        批量删除提醒
        """
        try:
            reminder_ids = request.data.get("reminder_ids", [])

            if not reminder_ids:
                return Response(
                    {"success": False, "message": "请提供提醒ID列表", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reminders = self.get_queryset().filter(id__in=reminder_ids)
            deleted_count, _ = reminders.delete()

            logger.info(f"用户 {request.user.username} 批量删除提醒，删除了 {deleted_count} 个提醒")

            return Response(
                {
                    "success": True,
                    "message": f"成功删除 {deleted_count} 个提醒",
                    "data": {"deleted_count": deleted_count},
                }
            )

        except Exception as e:
            logger.error(f"批量删除提醒失败: {str(e)}")
            return Response(
                {"success": False, "message": f"批量删除提醒失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def test_notification(self, request, pk=None):
        """
        测试提醒通知
        """
        try:
            reminder = self.get_object()

            # 发送测试通知
            success = notification_service.send_notification(
                user=request.user,
                title=f"测试提醒: {reminder.title}",
                message=f"这是一条测试通知。药品: {reminder.medicine.name}，剂量: {reminder.dosage}{reminder.get_dosage_unit_display()}",
                reminder=reminder,
            )

            if success:
                logger.info(f"用户 {request.user.username} 测试提醒通知成功，ID: {reminder.id}")
                return Response(
                    {"success": True, "message": "测试通知发送成功", "data": {"delivered": True}}
                )

            logger.warning(
                f"用户 {request.user.username} 测试提醒通知未送达（可能未配置可用通道），ID: {reminder.id}"
            )
            return Response(
                {
                    "success": True,
                    "message": "测试通知已触发，当前环境未检测到可用通知通道",
                    "data": {"delivered": False},
                }
            )

        except Exception as e:
            logger.error(f"测试提醒通知失败: {str(e)}")
            return Response(
                {"success": False, "message": f"测试提醒通知失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def respond_by_subscription(self, request):
        try:
            parsed, error = self._parse_subscription_response_payload(request)
            if error is not None:
                return error

            endpoint = parsed["endpoint"]
            response_type = parsed["response_type"]
            history_id = parsed["history_id"]
            reminder_id = parsed["reminder_id"]
            delay_minutes = parsed["delay_minutes"]

            user, error = self._get_subscription_user(endpoint)
            if error is not None:
                return error

            if history_id:
                return self._respond_history_by_subscription(
                    user, history_id, response_type, delay_minutes
                )

            if not reminder_id:
                return Response(
                    {"success": False, "message": "缺少提醒ID", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reminder = Reminder.objects.filter(id=reminder_id, user=user).first()
            if not reminder:
                return Response(
                    {"success": False, "message": "提醒不存在", "data": None},
                    status=status.HTTP_404_NOT_FOUND,
                )

            self._apply_subscription_response(reminder, response_type, delay_minutes)
            return Response(
                {
                    "success": True,
                    "message": "响应已记录",
                    "data": {"reminder_id": reminder.id},
                }
            )
        except Exception as e:
            logger.error(f"订阅响应处理失败: {str(e)}")
            return Response(
                {"success": False, "message": f"订阅响应处理失败: {str(e)}", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _parse_subscription_response_payload(self, request):
        endpoint = (request.data or {}).get("endpoint")
        response_type = (request.data or {}).get("response_type")
        history_id = (request.data or {}).get("history_id")
        reminder_id = (request.data or {}).get("reminder_id")
        delay_minutes = int((request.data or {}).get("delay_minutes", 5))

        if not endpoint or not response_type:
            return None, Response(
                {"success": False, "message": "缺少必需参数", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return (
            {
                "endpoint": endpoint,
                "response_type": response_type,
                "history_id": history_id,
                "reminder_id": reminder_id,
                "delay_minutes": delay_minutes,
            },
            None,
        )

    def _get_subscription_user(self, endpoint):
        from apps.users.models import PushSubscription

        sub = (
            PushSubscription.objects.filter(endpoint=endpoint, is_active=True)
            .select_related("user")
            .first()
        )
        if not sub:
            return None, Response(
                {"success": False, "message": "订阅不存在或已失效", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return sub.user, None

    def _respond_history_by_subscription(
        self, user, history_id, response_type, delay_minutes: int
    ):
        from .history_models import ReminderHistory

        history = (
            ReminderHistory.objects.filter(id=history_id, user=user)
            .select_related("reminder")
            .first()
        )
        if not history:
            return Response(
                {"success": False, "message": "历史记录不存在", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        history.mark_responded(response_type)
        reminder = history.reminder
        self._apply_subscription_response(
            reminder, response_type, delay_minutes, history=history
        )
        return Response(
            {
                "success": True,
                "message": "响应已记录",
                "data": {"history_id": history.id},
            }
        )

    def _create_delayed_pending_history(self, user, reminder, title, message, delay_minutes: int):
        try:
            from django.utils import timezone as dj_tz

            from .history_models import ReminderHistory

            ReminderHistory.objects.create(
                user=user,
                reminder=reminder,
                title=title,
                message=message,
                notification_methods=["push"],
                scheduled_time=dj_tz.now() + dj_tz.timedelta(minutes=delay_minutes),
                reminder_type="repeat",
                status="pending",
            )
        except Exception as e:
            logger.error(f"创建延迟补发历史失败: {e}")

    def _apply_subscription_response(self, reminder, response_type, delay_minutes: int, history=None):
        if response_type == "taken":
            reminder.increment_response_count()
            return
        if response_type != "delayed":
            return
        user = getattr(reminder, "user", None)
        if history is not None:
            title = history.title
            message = history.message
        else:
            title = reminder.title or f"用药提醒 - {reminder.medicine.name}"
            message = reminder.get_default_message()
        self._create_delayed_pending_history(user, reminder, title, message, delay_minutes)

    def _record_confirm_action_history(
        self, reminder, action_type, notes="", delay_minutes=None
    ):
        """
        尽量将确认动作同步到最近一条未响应历史；若没有可匹配历史则最小化创建一条手动历史。
        """
        from .history_models import ReminderHistory

        mapped_response_type = REMINDER_HISTORY_RESPONSE_MAP[action_type]
        history = (
            ReminderHistory.objects.filter(
                reminder=reminder,
                user=reminder.user,
                response_type="no_response",
            )
            .order_by("-scheduled_time", "-created_at")
            .first()
        )

        if history:
            history.mark_responded(mapped_response_type, notes=notes)
            logger.info(
                "提醒确认动作已写回现有历史，reminder_id=%s，history_id=%s，action=%s",
                reminder.id,
                history.id,
                action_type,
            )
        else:
            scheduled_time = timezone.make_aware(
                datetime.combine(timezone.localdate(), reminder.reminder_time)
            )
            history = ReminderHistory.objects.create(
                user=reminder.user,
                reminder=reminder,
                title=reminder.title or f"用药提醒 - {reminder.medicine.name}",
                message=reminder.get_default_message(),
                notification_methods=["manual_confirm"],
                scheduled_time=scheduled_time,
                reminder_type="manual",
                status="sent",
                response_type=mapped_response_type,
                responded_at=timezone.now(),
                notes=notes or "由提醒确认动作接口生成",
            )
            if history.sent_at:
                response_delay = history.responded_at - history.sent_at
                history.response_delay_minutes = int(response_delay.total_seconds() / 60)
                history.save(update_fields=["response_delay_minutes"])
            logger.info(
                "提醒确认动作已补建手动历史，reminder_id=%s，history_id=%s，action=%s",
                reminder.id,
                history.id,
                action_type,
            )

        if action_type == "delayed" and delay_minutes:
            ReminderHistory.objects.create(
                user=reminder.user,
                reminder=reminder,
                title=history.title,
                message=history.message,
                notification_methods=["push"],
                scheduled_time=timezone.now() + timedelta(minutes=delay_minutes),
                reminder_type="repeat",
                status="pending",
            )
            logger.info(
                "提醒确认动作已创建延迟补发历史，reminder_id=%s，delay_minutes=%s",
                reminder.id,
                delay_minutes,
            )

        return True
