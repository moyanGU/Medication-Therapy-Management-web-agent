from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from apps.reminders.history_models import ReminderHistory

from .models import MedicationRecord


def get_adherence_records_queryset(user, start_date, end_date, medicine_id=None):
    """
    获取提醒闭环来源的正式用药记录查询集。
    """
    queryset = (
        MedicationRecord.objects.filter(user=user)
        .select_related("medicine", "user", "reminder")
        .filter(Q(source="reminder") | Q(reminder__isnull=False))
        .annotate(event_date=TruncDate(Coalesce("scheduled_time", "taken_at")))
        .filter(event_date__gte=start_date, event_date__lte=end_date)
    )
    if medicine_id:
        queryset = queryset.filter(medicine_id=medicine_id)
    return queryset


def get_reminder_history_queryset(user, start_date, end_date, medicine_id=None):
    """
    获取提醒历史查询集，用于补充响应摘要。
    """
    queryset = ReminderHistory.objects.filter(
        user=user,
        scheduled_time__date__gte=start_date,
        scheduled_time__date__lte=end_date,
    )
    if medicine_id:
        queryset = queryset.filter(reminder__medicine_id=medicine_id)
    return queryset


def build_response_summary(history_queryset):
    """
    构造提醒响应补充摘要。
    """
    history_queryset = history_queryset.exclude(status="pending")
    scheduled_count = history_queryset.count()
    responded_count = history_queryset.exclude(response_type="no_response").count()
    unresponded_count = max(scheduled_count - responded_count, 0)
    response_rate = round((responded_count / scheduled_count) * 100, 2) if scheduled_count else 0.0

    return {
        "scheduled_count": scheduled_count,
        "responded_count": responded_count,
        "unresponded_count": unresponded_count,
        "response_rate": response_rate,
    }


def build_risk_level(
    adherence_rate, missed_count, delayed_count, partial_count, response_rate
):
    """
    根据依从性和响应情况输出风险等级。
    """
    risk_flags = []

    if missed_count > 0:
        risk_flags.append("存在漏服")
    if delayed_count >= 2:
        risk_flags.append("延迟服药较多")
    if partial_count > 0:
        risk_flags.append("存在部分服用")
    if response_rate < 60:
        risk_flags.append("提醒响应率偏低")

    if adherence_rate >= 90 and missed_count == 0:
        return "low", risk_flags
    if adherence_rate < 70 or missed_count >= 2:
        return "high", risk_flags
    return "medium", risk_flags


def build_adherence_summary(queryset, history_queryset):
    """
    构造依从性摘要。
    """
    aggregated = queryset.aggregate(
        total_records=Count("id"),
        taken_count=Count("id", filter=Q(status="taken")),
        missed_count=Count("id", filter=Q(status="missed")),
        delayed_count=Count("id", filter=Q(status="delayed")),
        partial_count=Count("id", filter=Q(status="partial")),
        avg_delay_minutes=Avg("delay_minutes", filter=Q(delay_minutes__isnull=False)),
    )

    total_records = aggregated["total_records"] or 0
    taken_count = aggregated["taken_count"] or 0
    missed_count = aggregated["missed_count"] or 0
    delayed_count = aggregated["delayed_count"] or 0
    partial_count = aggregated["partial_count"] or 0
    completed_count = taken_count + delayed_count + partial_count
    adherence_rate = round((completed_count / total_records) * 100, 2) if total_records else 0.0
    on_time_rate = round((taken_count / total_records) * 100, 2) if total_records else 0.0
    avg_delay_minutes = round(aggregated["avg_delay_minutes"] or 0, 2)

    response_summary = build_response_summary(history_queryset)
    risk_level, risk_flags = build_risk_level(
        adherence_rate=adherence_rate,
        missed_count=missed_count,
        delayed_count=delayed_count,
        partial_count=partial_count,
        response_rate=response_summary["response_rate"],
    )

    return {
        "total_records": total_records,
        "taken_count": taken_count,
        "missed_count": missed_count,
        "delayed_count": delayed_count,
        "partial_count": partial_count,
        "completed_count": completed_count,
        "adherence_rate": adherence_rate,
        "on_time_rate": on_time_rate,
        "avg_delay_minutes": avg_delay_minutes,
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "response_summary": response_summary,
    }


def build_adherence_trend(queryset, start_date, end_date):
    """
    构造依从性按日趋势。
    """
    trend_map = {}
    days = (end_date - start_date).days + 1
    for index in range(days):
        current_date = start_date + timedelta(days=index)
        key = current_date.isoformat()
        trend_map[key] = {
            "date": key,
            "total": 0,
            "taken": 0,
            "missed": 0,
            "delayed": 0,
            "partial": 0,
            "completed": 0,
            "adherence_rate": 0.0,
            "on_time_rate": 0.0,
        }

    aggregated = (
        queryset.values("event_date", "status")
        .annotate(count=Count("id"))
        .order_by("event_date")
    )

    for item in aggregated:
        if not item["event_date"]:
            continue
        date_key = item["event_date"].isoformat()
        if date_key not in trend_map:
            continue
        trend_map[date_key]["total"] += item["count"]
        trend_map[date_key][item["status"]] += item["count"]

    for data in trend_map.values():
        data["completed"] = data["taken"] + data["delayed"] + data["partial"]
        if data["total"]:
            data["adherence_rate"] = round((data["completed"] / data["total"]) * 100, 2)
            data["on_time_rate"] = round((data["taken"] / data["total"]) * 100, 2)

    return list(trend_map.values())


def build_dashboard_adherence_summary(user, today=None, medicine_id=None):
    """
    为首页聚合摘要构造 7 天与 30 天依从性摘要。
    """
    today = today or timezone.now().date()
    summary_7d_start = today - timedelta(days=6)
    summary_30d_start = today - timedelta(days=29)

    summary_7d = build_adherence_summary(
        get_adherence_records_queryset(
            user=user,
            start_date=summary_7d_start,
            end_date=today,
            medicine_id=medicine_id,
        ),
        get_reminder_history_queryset(
            user=user,
            start_date=summary_7d_start,
            end_date=today,
            medicine_id=medicine_id,
        ),
    )
    summary_30d = build_adherence_summary(
        get_adherence_records_queryset(
            user=user,
            start_date=summary_30d_start,
            end_date=today,
            medicine_id=medicine_id,
        ),
        get_reminder_history_queryset(
            user=user,
            start_date=summary_30d_start,
            end_date=today,
            medicine_id=medicine_id,
        ),
    )

    return {
        "summary_7d": summary_7d,
        "summary_30d": summary_30d,
        "current_period": summary_7d,
    }
