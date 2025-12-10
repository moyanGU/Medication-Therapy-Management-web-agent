from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from unittest.mock import patch

from apps.medicines.models import Medicine
from apps.reminders.models import Reminder
from apps.reminders.notifications import NotificationService
from apps.reminders.history_models import ReminderHistory


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class FailureFallbackPendingTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='ffp_user', password='pass123', email='ffp@example.com', phone='13800000003'
        )
        self.medicine = Medicine.objects.create(user=self.user, name='维生素K')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime('09:00', '%H:%M').time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
            notification_types=['push', 'sms', 'email'],
        )

    def test_pending_history_created_when_all_methods_fail(self):
        svc = NotificationService()
        with patch.object(NotificationService, '_send_by_type', return_value=False):
            ok = svc.send_notification(
                user=self.user,
                title='用药提醒',
                message='请按时服用维生素K',
                reminder=self.reminder,
            )
        self.assertFalse(ok)
        qs = ReminderHistory.objects.filter(user=self.user, reminder=self.reminder, status='pending')
        self.assertEqual(qs.count(), 1)
        h = qs.first()
        self.assertIn('sms', h.notification_methods)  # 用户有手机号，默认回退短信
        self.assertGreater(h.scheduled_time, timezone.now())

