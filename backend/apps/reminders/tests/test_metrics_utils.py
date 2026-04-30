from datetime import datetime, timezone as dt_timezone, timedelta
from types import SimpleNamespace
from unittest import TestCase

from apps.reminders.metrics_utils import build_history_metrics, parse_days


class MetricsUtilsTest(TestCase):
    def test_parse_days(self):
        self.assertEqual(parse_days("7"), 7)
        self.assertEqual(parse_days("0", default=7), 7)
        self.assertEqual(parse_days("-1", default=7), 7)
        self.assertEqual(parse_days("9999"), 365)
        self.assertEqual(parse_days("abc", default=7), 7)

    def test_build_history_metrics_basic(self):
        t0 = datetime(2026, 1, 1, 8, 0, tzinfo=dt_timezone.utc)
        t1 = t0 + timedelta(minutes=10)
        t2 = t0 + timedelta(minutes=20)

        items = [
            SimpleNamespace(
                status="sent",
                notification_methods=["sms"],
                sent_at=t1,
                scheduled_time=t0,
                response_type="taken",
                title="用药提醒",
            ),
            SimpleNamespace(
                status="sent",
                notification_methods=["push"],
                sent_at=t2,
                scheduled_time=t0,
                response_type="no_response",
                title="用药提醒",
            ),
            SimpleNamespace(
                status="failed",
                notification_methods=["push"],
                sent_at=None,
                scheduled_time=t0,
                response_type=None,
                title="补发提醒",
            ),
            SimpleNamespace(
                status="pending",
                notification_methods=["email"],
                sent_at=None,
                scheduled_time=t0,
                response_type=None,
                title="补发提醒",
            ),
        ]

        m = build_history_metrics(items, days=7)
        self.assertEqual(m.total, 4)
        self.assertEqual(m.sent, 2)
        self.assertEqual(m.failed, 1)
        self.assertEqual(m.pending, 1)
        self.assertEqual(m.sms_sent, 1)
        self.assertEqual(m.push_sent, 1)
        self.assertEqual(m.email_sent, 0)
        self.assertEqual(m.push_failed, 1)
        self.assertEqual(m.sms_failed, 0)
        self.assertEqual(m.response_rate, 50.0)
        self.assertEqual(m.escalated_total, 2)
        self.assertEqual(m.escalated_sent, 0)
        self.assertEqual(m.escalation_success_rate, 0.0)
        self.assertEqual(m.avg_response_delay_minutes, 15.0)

