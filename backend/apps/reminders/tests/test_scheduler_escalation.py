from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.medicines.models import Medicine
from apps.reminders.models import Reminder
from apps.reminders.history_models import ReminderHistory
from apps.reminders.scheduler import ReminderScheduler


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class SchedulerEscalationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='esc_user',
            password='pass123',
            email='esc@example.com',
            phone='13800000003',
        )

        self.medicine = Medicine.objects.create(user=self.user, name='维生素B')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title='升级通道测试',
            message='若推送失败则升级到短信',
            reminder_time=timezone.now().time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
        )

    def test_pending_push_failure_escalates_to_sms(self):
        h = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='用药提醒',
            message='推送失败升级',
            notification_methods=['push'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=1),
            status='pending',
        )

        scheduler = ReminderScheduler()
        sent = scheduler.check_and_send_reminders()

        h.refresh_from_db()
        self.assertEqual(h.status, 'failed')
        # 由于 push 在测试环境不可用，应该创建新的待发送历史（sms）
        pending_all = ReminderHistory.objects.filter(
            user=self.user, reminder=self.reminder, status='pending'
        )
        count_sms = sum(1 for x in pending_all if (x.notification_methods or []) and 'sms' in x.notification_methods)
        self.assertEqual(count_sms, 1)
