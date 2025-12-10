from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.users.models import PushSubscription
from apps.medicines.models import Medicine
from apps.reminders.models import Reminder
from apps.reminders.history_models import ReminderHistory

@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class RespondBySubscriptionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tester',
            password='pass123',
            email='t@example.com',
            phone='13800000000'
        )
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(user=self.user, name='阿莫西林')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title='每日服药',
            message='早上服用',
            reminder_time=timezone.datetime.strptime('08:00', '%H:%M').time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
        )

        self.sub = PushSubscription.objects.create(
            user=self.user,
            endpoint='https://push.example/123',
            keys={'p256dh': 'x', 'auth': 'y'},
            user_agent='UA',
            time_zone='Asia/Shanghai'
        )

    def test_respond_by_subscription_reminder(self):
        resp = self.client.post('/api/reminders/respond_by_subscription/', {
            'endpoint': self.sub.endpoint,
            'response_type': 'taken',
            'reminder_id': self.reminder.id,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.response_count, 1)

    def test_respond_by_subscription_history(self):
        history = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='提醒',
            message='服用药品',
            notification_methods=['push'],
            scheduled_time=timezone.now(),
            status='sent',
        )
        resp = self.client.post('/api/reminders/respond_by_subscription/', {
            'endpoint': self.sub.endpoint,
            'response_type': 'skipped',
            'history_id': history.id,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        history.refresh_from_db()
        self.assertIsNotNone(history.responded_at)
        self.assertEqual(history.response_type, 'skipped')

    def test_respond_by_subscription_delayed_creates_pending(self):
        history = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title='提醒',
            message='服用药品',
            notification_methods=['push'],
            scheduled_time=timezone.now(),
            status='sent',
        )
        resp = self.client.post('/api/reminders/respond_by_subscription/', {
            'endpoint': self.sub.endpoint,
            'response_type': 'delayed',
            'history_id': history.id,
            'delay_minutes': 1,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        # 检查是否创建了 pending 历史
        pending_count = ReminderHistory.objects.filter(user=self.user, reminder=self.reminder, status='pending').count()
        self.assertEqual(pending_count, 1)
