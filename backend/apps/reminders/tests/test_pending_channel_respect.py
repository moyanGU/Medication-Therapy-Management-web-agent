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
class PendingChannelRespectTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='sms_user',
            password='pass123',
            email='sms@example.com',
            phone='13800000002',
        )

        self.medicine = Medicine.objects.create(user=self.user, name='维生素C')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title='测试短信通道',
            message='请按时服用',
            reminder_time=timezone.now().time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
        )

    def test_pending_history_respects_sms_channel(self):
        h = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='用药提醒',
            message='短信发送优先',
            notification_methods=['sms'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=1),
            status='pending',
        )

        scheduler = ReminderScheduler()
        sent = scheduler.check_and_send_reminders()

        self.assertGreaterEqual(sent, 1)
        h.refresh_from_db()
        self.assertEqual(h.status, 'sent')
        self.assertIn('sms', h.notification_methods)

