from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medicines.models import Medicine
from apps.reminders.history_models import ReminderHistory
from apps.reminders.models import Reminder


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class MetricsWarningsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="warn_user",
            password="pass123",
            email="t@example.com",
            phone="13800000004",
        )
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(user=self.user, name="阿司匹林")
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime("08:00", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
        )

        # 构造低响应率与高失败率场景
        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title="提醒1",
            message="push 发送",
            notification_methods=["push"],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=10),
            sent_at=timezone.now(),
            status="sent",
            response_type="no_response",
        )
        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title="提醒2",
            message="失败",
            notification_methods=["sms"],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=5),
            sent_at=timezone.now(),
            status="failed",
        )

    def test_metrics_warnings_present(self):
        resp = self.client.get("/api/reminders/reminder-history/metrics/?days=30")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        data = payload["data"]
        self.assertIn("warnings", data)
        self.assertTrue(
            any("响应率" in w or "失败率" in w or "失败记录" in w for w in data["warnings"])
        )
