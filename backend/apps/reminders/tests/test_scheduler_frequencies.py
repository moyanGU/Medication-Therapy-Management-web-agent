from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.medicines.models import Medicine
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
class SchedulerFrequenciesTest(TestCase):
    def setUp(self):
        """
        初始化测试数据，包括用户、药品和基础配置
        """
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="pass123",
            email="t@example.com",
            phone="13800000001",
        )
        self.medicine = Medicine.objects.create(user=self.user, name="维生素D")

    def test_daily_reminder_sends_on_time(self):
        """
        测试每日提醒在时间命中时会被调度发送
        """
        now_local = timezone.localtime()
        r = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=now_local.time(),
            start_date=now_local.date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["sms"],
        )

        scheduler = ReminderScheduler()
        sent = scheduler.check_and_send_reminders()

        r.refresh_from_db()
        self.assertGreaterEqual(sent, 1)
        self.assertEqual(r.reminder_count, 1)
        self.assertIsNotNone(r.last_reminded_at)

    def test_weekly_reminder_respects_frequency(self):
        """
        测试每周提醒仅在满足 7 天周期时发送
        """
        today = timezone.localtime().date()
        start_aligned = today - timezone.timedelta(days=7)  # 满足 7 天周期
        start_not_aligned = today - timezone.timedelta(days=6)  # 不满足 7 天周期

        # 命中提醒
        r_hit = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.localtime().time(),
            start_date=start_aligned,
            frequency="weekly",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["sms"],
        )

        # 未命中提醒
        r_miss = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.localtime().time(),
            start_date=start_not_aligned,
            frequency="weekly",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["sms"],
        )

        scheduler = ReminderScheduler()
        sent = scheduler.check_and_send_reminders()

        r_hit.refresh_from_db()
        r_miss.refresh_from_db()
        self.assertGreaterEqual(sent, 1)
        self.assertEqual(r_hit.reminder_count, 1)
        self.assertEqual(r_miss.reminder_count, 0)

    def test_temporary_time_adjustment_triggers_send(self):
        """
        测试临时调整提醒时间后，调度器会按更新后的时间发送
        """
        now_local = timezone.localtime()
        future_time = (now_local + timezone.timedelta(minutes=10)).time()

        r = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=future_time,  # 初始不命中当前时间
            start_date=now_local.date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["sms"],
        )

        scheduler = ReminderScheduler()
        sent_before = scheduler.check_and_send_reminders()
        self.assertEqual(sent_before, 0)

        # 临时调整到当前时间
        r.reminder_time = now_local.time()
        r.save(update_fields=["reminder_time"])

        sent_after = scheduler.check_and_send_reminders()
        r.refresh_from_db()
        self.assertGreaterEqual(sent_after, 1)
        self.assertEqual(r.reminder_count, 1)
        self.assertIsNotNone(r.last_reminded_at)
