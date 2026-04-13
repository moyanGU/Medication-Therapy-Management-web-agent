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
class NotificationFallbackTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="nf_user", password="pass123", email="", phone="13800000001"
        )
        self.medicine = Medicine.objects.create(user=self.user, name="维生素D")
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime("07:30", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["push"],
        )

    def test_escalate_to_sms_when_push_unavailable(self):
        scheduler = ReminderScheduler()
        ok = scheduler._send_reminder(self.reminder)
        self.assertFalse(ok)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.reminder_count, 0)
        self.assertFalse(
            ReminderHistory.objects.filter(
                user=self.user, reminder=self.reminder, status="sent"
            ).exists()
        )
        qs = ReminderHistory.objects.filter(
            user=self.user,
            reminder=self.reminder,
            status="pending",
            reminder_type="repeat",
        )
        self.assertEqual(qs.count(), 1)
        h = qs.first()
        self.assertIn("sms", h.notification_methods)
