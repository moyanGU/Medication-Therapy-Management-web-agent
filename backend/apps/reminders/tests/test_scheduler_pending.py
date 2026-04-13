from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.medicines.models import Medicine
from apps.reminders.history_models import ReminderHistory
from apps.reminders.models import Reminder
from apps.reminders.scheduler import ReminderScheduler


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class SchedulerPendingTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="pass123",
            email="t@example.com",
            phone="13800000000",
        )
        self.medicine = Medicine.objects.create(user=self.user, name="维生素C")
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime("23:59", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["sms"],  # 使用短信以避免推送依赖
        )

    def test_scheduler_sends_pending_history(self):
        # 创建一个5秒前的待发送历史
        h = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title="补发提醒",
            message="请按时服药",
            notification_methods=["sms"],
            scheduled_time=timezone.now() - timezone.timedelta(seconds=5),
            reminder_type="repeat",
            status="pending",
        )

        scheduler = ReminderScheduler()
        sent = scheduler.check_and_send_reminders()

        h.refresh_from_db()
        self.assertEqual(h.status, "sent")
        self.assertIsNotNone(h.sent_at)
        self.assertGreaterEqual(sent, 1)
