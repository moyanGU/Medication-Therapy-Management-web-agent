"""核心应用首页聚合视图"""

import logging
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.records.adherence import build_dashboard_adherence_summary

from .utils import error_response, success_response

logger = logging.getLogger("mtm_helper")


def _build_dashboard_adherence_summary(request):
    return build_dashboard_adherence_summary(
        user=request.user,
        today=timezone.now().date(),
    )


def _build_dashboard_today_tasks(reminders, processed_records, today):
    processed_by_reminder = {}
    for record in processed_records:
        if record.reminder_id and record.reminder_id not in processed_by_reminder:
            processed_by_reminder[record.reminder_id] = record

    items = []
    completed = 0
    for reminder in reminders:
        record = processed_by_reminder.get(reminder.id)
        is_completed = record is not None
        if is_completed:
            completed += 1

        items.append(
            {
                "reminder_id": reminder.id,
                "medicine_id": reminder.medicine_id,
                "medicine_name": reminder.medicine.name,
                "title": reminder.title or f"{reminder.medicine.name} 用药提醒",
                "reminder_time": reminder.reminder_time.strftime("%H:%M"),
                "dosage": reminder.dosage,
                "dosage_unit": reminder.dosage_unit,
                "meal_timing": reminder.meal_timing,
                "is_completed": is_completed,
                "record_status": record.status if record else None,
                "scheduled_date": today.isoformat(),
            }
        )

    return {
        "date": today.isoformat(),
        "total": len(items),
        "completed": completed,
        "pending": max(len(items) - completed, 0),
        "items": items,
    }


def _build_dashboard_risk_alerts(
    low_stock_items, expiring_soon_items, followup_due_items, adherence_summary
):
    alerts = []

    if low_stock_items:
        alerts.append(
            {
                "type": "low_stock",
                "level": "medium",
                "title": "库存偏低",
                "count": len(low_stock_items),
                "message": f"有 {len(low_stock_items)} 种药品库存偏低，建议尽快补充",
            }
        )

    if expiring_soon_items:
        alerts.append(
            {
                "type": "expiring_soon",
                "level": "medium",
                "title": "药品临期",
                "count": len(expiring_soon_items),
                "message": f"有 {len(expiring_soon_items)} 种药品将在 30 天内到期",
            }
        )

    if followup_due_items:
        alerts.append(
            {
                "type": "followup_due",
                "level": "high",
                "title": "复诊到期",
                "count": len(followup_due_items),
                "message": f"有 {len(followup_due_items)} 条复诊已到期，建议尽快安排就诊",
            }
        )

    summary_7d = adherence_summary["summary_7d"]
    if summary_7d["total_records"] > 0 and summary_7d["risk_level"] in ["medium", "high"]:
        alerts.append(
            {
                "type": "adherence_risk",
                "level": summary_7d["risk_level"],
                "title": "依从性风险",
                "count": summary_7d["missed_count"] + summary_7d["delayed_count"],
                "message": "近 7 天存在漏服或延迟情况，建议及时关注用药执行",
            }
        )

    return alerts


def _serialize_dashboard_medicine_item(medicine):
    return {
        "id": medicine.id,
        "name": medicine.name,
        "quantity": medicine.quantity,
        "expiry_date": medicine.expiry_date.isoformat() if medicine.expiry_date else None,
        "days_until_expiry": medicine.days_until_expiry,
        "is_low_stock": medicine.is_low_stock,
    }


def _serialize_dashboard_followup_item(record):
    return {
        "id": record.id,
        "hospital": record.hospital,
        "department": record.department,
        "doctor": record.doctor,
        "visit_date": record.visit_date.isoformat(),
        "follow_up_date": record.follow_up_date.isoformat() if record.follow_up_date else None,
        "days_until_follow_up": record.days_until_follow_up,
        "is_follow_up_due": record.is_follow_up_due(),
    }


def _build_dashboard_mtm_hint(
    total_medicines, adherence_summary, followup_due_count, risk_alerts
):
    reasons = []
    summary_7d = adherence_summary["summary_7d"]

    if total_medicines >= 5:
        reasons.append("当前管理药品较多，建议做一次专业梳理")
    if summary_7d["total_records"] > 0 and summary_7d["adherence_rate"] < 70:
        reasons.append("近 7 天依从性偏低，建议获取专业用药指导")
    if followup_due_count > 0:
        reasons.append("存在到期复诊，建议同步梳理当前用药与复诊安排")
    if len(risk_alerts) >= 2:
        reasons.append("当前存在多项风险提醒，建议进入专业服务进一步评估")

    recommended = len(reasons) > 0
    return {
        "recommended": recommended,
        "reason_count": len(reasons),
        "reasons": reasons,
        "message": (
            "建议进入专业用药指导，帮助你更系统地梳理当前用药情况"
            if recommended
            else "当前日常管理整体稳定，如需更深入评估也可进入专业用药指导"
        ),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    from apps.medical_records.models import MedicalRecord
    from apps.medicines.models import Medicine
    from apps.records.models import MedicationRecord
    from apps.reminders.models import Reminder

    try:
        today = timezone.localtime().date()
        next_seven_days = today + timedelta(days=7)
        next_thirty_days = today + timedelta(days=30)

        logger.info(
            "首页聚合摘要请求，user=%s, date=%s",
            request.user.username,
            today.isoformat(),
        )

        reminders_queryset = (
            Reminder.objects.filter(
                user=request.user,
                is_active=True,
                start_date__lte=today,
            )
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            .select_related("medicine")
        )
        today_reminders = [item for item in reminders_queryset if item.should_remind_today()]
        today_records = list(
            MedicationRecord.objects.filter(
                user=request.user,
                scheduled_time__date=today,
            )
            .filter(Q(source="reminder") | Q(reminder__isnull=False))
            .select_related("medicine", "reminder")
            .order_by("-updated_at")
        )

        medicines_queryset = Medicine.objects.filter(user=request.user)
        low_stock_items = list(
            medicines_queryset.filter(quantity__lte=5).order_by("quantity", "name")[:5]
        )
        expiring_soon_items = list(
            medicines_queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=next_thirty_days,
            )
            .order_by("expiry_date", "name")[:5]
        )

        medical_records_queryset = MedicalRecord.objects.filter(user=request.user)
        followup_due_qs = medical_records_queryset.filter(
            follow_up_date__isnull=False,
            follow_up_date__lte=today,
            status="completed",
        ).order_by("follow_up_date", "-visit_date")
        upcoming_followup_qs = medical_records_queryset.filter(
            follow_up_date__isnull=False,
            follow_up_date__gt=today,
            follow_up_date__lte=next_seven_days,
            status="completed",
        ).order_by("follow_up_date", "-visit_date")
        followup_due_items = list(followup_due_qs[:5])
        upcoming_followup_items = list(upcoming_followup_qs[:5])
        next_followup = (
            medical_records_queryset.filter(
                follow_up_date__isnull=False,
                follow_up_date__gte=today,
                status="completed",
            )
            .order_by("follow_up_date", "-visit_date")
            .first()
        )

        adherence_summary = _build_dashboard_adherence_summary(request)
        risk_alerts = _build_dashboard_risk_alerts(
            low_stock_items=low_stock_items,
            expiring_soon_items=expiring_soon_items,
            followup_due_items=followup_due_items,
            adherence_summary=adherence_summary,
        )

        data = {
            "today_tasks": _build_dashboard_today_tasks(
                reminders=today_reminders,
                processed_records=today_records,
                today=today,
            ),
            "risk_alerts": risk_alerts,
            "medication_summary": {
                "total_medicines": medicines_queryset.count(),
                "active_reminders": reminders_queryset.count(),
                "low_stock_count": medicines_queryset.filter(quantity__lte=5).count(),
                "expiring_soon_count": medicines_queryset.filter(
                    expiry_date__isnull=False,
                    expiry_date__gte=today,
                    expiry_date__lte=next_thirty_days,
                ).count(),
                "low_stock_items": [_serialize_dashboard_medicine_item(item) for item in low_stock_items],
                "expiring_soon_items": [
                    _serialize_dashboard_medicine_item(item) for item in expiring_soon_items
                ],
            },
            "followup_summary": {
                "due_count": followup_due_qs.count(),
                "upcoming_count": upcoming_followup_qs.count(),
                "next_followup": _serialize_dashboard_followup_item(next_followup) if next_followup else None,
                "due_items": [_serialize_dashboard_followup_item(item) for item in followup_due_items],
                "upcoming_items": [
                    _serialize_dashboard_followup_item(item) for item in upcoming_followup_items
                ],
            },
            "adherence_summary": adherence_summary,
            "mtm_entry_hint": _build_dashboard_mtm_hint(
                total_medicines=medicines_queryset.count(),
                adherence_summary=adherence_summary,
                followup_due_count=followup_due_qs.count(),
                risk_alerts=risk_alerts,
            ),
        }

        return success_response(data, "获取首页聚合摘要成功")
    except Exception as exc:
        logger.error(f"获取首页聚合摘要失败: {exc}")
        return error_response("获取首页聚合摘要失败", "DASHBOARD_SUMMARY_ERROR", 500)

