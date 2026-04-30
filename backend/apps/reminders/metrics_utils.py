from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryMetrics:
    period_days: int
    total: int
    sent: int
    failed: int
    pending: int
    avg_response_delay_minutes: float
    push_sent: int
    sms_sent: int
    email_sent: int
    push_failed: int
    sms_failed: int
    email_failed: int
    response_rate: float
    escalated_total: int
    escalated_sent: int
    escalation_success_rate: float
    warnings: list[str]


def parse_days(value, default: int = 7) -> int:
    try:
        days = int(value)
        if days <= 0:
            return default
        return min(days, 365)
    except Exception:
        return default


def _has_method(history, method: str) -> bool:
    methods = getattr(history, "notification_methods", None) or []
    return method in methods


def _compute_avg_delay_minutes(sent_items) -> float:
    delays = []
    for h in sent_items:
        sent_at = getattr(h, "sent_at", None)
        scheduled_time = getattr(h, "scheduled_time", None)
        if sent_at and scheduled_time:
            try:
                delays.append((sent_at - scheduled_time).total_seconds() / 60.0)
            except Exception:
                continue
    return (sum(delays) / len(delays)) if delays else 0.0


def _compute_response_rate(sent_items) -> float:
    responded_count = 0
    for h in sent_items:
        rt = getattr(h, "response_type", None)
        if rt and rt != "no_response":
            responded_count += 1
    return round((responded_count / len(sent_items) * 100.0), 2) if sent_items else 0.0


def _compute_escalation(items) -> tuple[int, int, float]:
    escalated_items = [h for h in items if (getattr(h, "title", "") or "").strip() == "补发提醒"]
    escalated_total = len(escalated_items)
    escalated_sent = sum(1 for h in escalated_items if getattr(h, "status", None) == "sent")
    escalation_success_rate = (
        round((escalated_sent / escalated_total * 100.0), 2) if escalated_total else 0.0
    )
    return escalated_total, escalated_sent, escalation_success_rate


def _compute_warnings(response_rate: float, sent_count: int, failed_count: int) -> list[str]:
    warnings: list[str] = []
    try:
        if response_rate < 60.0:
            warnings.append(f"响应率偏低：{response_rate}%")
        if sent_count > 0:
            fail_rate = round((failed_count / sent_count) * 100.0, 2)
            if fail_rate > 20.0:
                warnings.append(f"失败率偏高：{fail_rate}%")
        else:
            if failed_count > 0:
                warnings.append("存在失败记录且无成功发送")
    except Exception:
        return warnings
    return warnings


def build_history_metrics(items, days: int) -> HistoryMetrics:
    items = list(items or [])
    total = len(items)
    sent_items = [h for h in items if getattr(h, "status", None) == "sent"]
    failed = sum(1 for h in items if getattr(h, "status", None) == "failed")
    pending = sum(1 for h in items if getattr(h, "status", None) == "pending")

    avg_delay = _compute_avg_delay_minutes(sent_items)

    push_sent = sum(1 for h in sent_items if _has_method(h, "push"))
    sms_sent = sum(1 for h in sent_items if _has_method(h, "sms"))
    email_sent = sum(1 for h in sent_items if _has_method(h, "email"))

    push_failed = sum(1 for h in items if getattr(h, "status", None) == "failed" and _has_method(h, "push"))
    sms_failed = sum(1 for h in items if getattr(h, "status", None) == "failed" and _has_method(h, "sms"))
    email_failed = sum(
        1 for h in items if getattr(h, "status", None) == "failed" and _has_method(h, "email")
    )

    response_rate = _compute_response_rate(sent_items)

    escalated_total, escalated_sent, escalation_success_rate = _compute_escalation(items)
    warnings = _compute_warnings(response_rate, len(sent_items), failed)

    return HistoryMetrics(
        period_days=int(days),
        total=total,
        sent=len(sent_items),
        failed=failed,
        pending=pending,
        avg_response_delay_minutes=round(avg_delay or 0.0, 2),
        push_sent=push_sent,
        sms_sent=sms_sent,
        email_sent=email_sent,
        push_failed=push_failed,
        sms_failed=sms_failed,
        email_failed=email_failed,
        response_rate=response_rate,
        escalated_total=escalated_total,
        escalated_sent=escalated_sent,
        escalation_success_rate=escalation_success_rate,
        warnings=warnings,
    )


def history_metrics_to_dict(metrics: HistoryMetrics) -> dict:
    return {
        "period_days": metrics.period_days,
        "total": metrics.total,
        "sent": metrics.sent,
        "failed": metrics.failed,
        "pending": metrics.pending,
        "avg_response_delay_minutes": metrics.avg_response_delay_minutes,
        "channel": {
            "push_sent": metrics.push_sent,
            "sms_sent": metrics.sms_sent,
            "email_sent": metrics.email_sent,
            "push_failed": metrics.push_failed,
            "sms_failed": metrics.sms_failed,
            "email_failed": metrics.email_failed,
        },
        "response_rate": metrics.response_rate,
        "escalation": {
            "escalated_total": metrics.escalated_total,
            "escalated_sent": metrics.escalated_sent,
            "escalation_success_rate": metrics.escalation_success_rate,
        },
        "warnings": metrics.warnings,
    }

