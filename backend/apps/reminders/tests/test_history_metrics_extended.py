from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from apps.medicines.models import Medicine
from apps.reminders.models import Reminder
from apps.reminders.history_models import ReminderHistory


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class ReminderHistoryMetricsExtendedTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='metrics_ext', password='pass123', email='', phone='13800000001'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(user=self.user, name='维生素C')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime('09:00', '%H:%M').time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
            notification_types=['push', 'sms'],
        )

        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='提醒1',
            message='推送已发送',
            notification_methods=['push'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=10),
            sent_at=timezone.now(),
            status='sent',
        )

        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='提醒2',
            message='短信已发送',
            notification_methods=['sms'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=8),
            sent_at=timezone.now(),
            status='sent',
        )

        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='提醒3',
            message='推送失败',
            notification_methods=['push'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=3),
            sent_at=timezone.now(),
            status='failed',
        )

        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='补发提醒',
            message='通道升级短信发送',
            notification_methods=['sms'],
            scheduled_time=timezone.now() - timezone.timedelta(minutes=2),
            sent_at=timezone.now(),
            status='sent',
        )

    def test_metrics_extended_fields(self):
        resp = self.client.get('/api/reminders/reminder-history/metrics/?days=30')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        data = payload['data']

        self.assertIn('escalation', data)
        self.assertEqual(data['escalation']['escalated_total'], 1)
        self.assertEqual(data['escalation']['escalated_sent'], 1)
        self.assertEqual(data['escalation']['escalation_success_rate'], 100.0)

        self.assertIn('channel', data)
        self.assertEqual(data['channel']['push_failed'], 1)
        self.assertEqual(data['channel']['sms_failed'], 0)
        self.assertIn('response_rate', data)
