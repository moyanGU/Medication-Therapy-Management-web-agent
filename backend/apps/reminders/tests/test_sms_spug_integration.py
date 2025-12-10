from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock

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
class SmsSpugIntegrationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='spug_user', password='pass123', email='', phone='13800000002'
        )
        self.medicine = Medicine.objects.create(user=self.user, name='维生素B')
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime('08:00', '%H:%M').time(),
            start_date=timezone.now().date(),
            frequency='daily',
            dosage=1,
            dosage_unit='tablet',
            is_active=True,
            notification_types=['sms'],
        )

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID='tmpl123',
        SPUG_PUSH_URL='http://spug.test',
        SPUG_APP_NAME='MTM用药助手',
        SPUG_PUSH_TOKEN='token123',
        SPUG_PUSH_TIMEOUT_SECONDS=2,
    )
    def test_spug_sms_send_success(self):
        svc = NotificationService()
        dummy_resp = Mock()
        dummy_resp.status_code = 200
        dummy_resp.text = 'ok'
        dummy_resp.raise_for_status = Mock()

        with patch('apps.reminders.notifications.requests.post', return_value=dummy_resp) as mpost:
            ok = svc._send_sms_notification(
                user=self.user,
                title='用药提醒',
                message='请按时服用维生素B',
                reminder=self.reminder,
            )

        self.assertTrue(ok)

        self.assertEqual(mpost.call_count, 1)
        called_url = mpost.call_args[0][0]
        called_kwargs = mpost.call_args[1]
        self.assertEqual(called_url, 'http://spug.test/send/tmpl123')
        self.assertIn('data', called_kwargs)
        self.assertIn('headers', called_kwargs)
        self.assertEqual(called_kwargs['headers'].get('Authorization'), 'Bearer token123')
        payload = called_kwargs['data']
        self.assertEqual(payload.get('name'), 'MTM用药助手')
        self.assertEqual(payload.get('title'), '用药提醒')
        self.assertEqual(payload.get('targets'), '13800000002')

        qs = ReminderHistory.objects.filter(user=self.user, reminder=self.reminder, status='sent')
        self.assertEqual(qs.count(), 1)
        self.assertIn('sms', qs.first().notification_methods)

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID='',
        SPUG_PUSH_URL='http://spug.test',
    )
    def test_spug_missing_template_id_returns_false(self):
        svc = NotificationService()
        with patch('apps.reminders.notifications.requests.post') as mpost:
            ok = svc._send_sms_notification(
                user=self.user,
                title='用药提醒',
                message='请按时服用维生素B',
                reminder=self.reminder,
            )
        self.assertFalse(ok)
        self.assertEqual(mpost.call_count, 0)
        self.assertEqual(
            ReminderHistory.objects.filter(user=self.user, reminder=self.reminder).count(),
            0
        )

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID='tmpl123',
        SPUG_PUSH_URL='http://spug.test',
        SPUG_APP_NAME='MTM用药助手',
        SPUG_PUSH_TOKEN='token123',
        SPUG_PUSH_TIMEOUT_SECONDS=2,
    )
    def test_spug_sms_send_failure_returns_false(self):
        svc = NotificationService()
        dummy_resp = Mock()
        dummy_resp.status_code = 500
        dummy_resp.text = 'error'
        def _raise():
            from requests import HTTPError
            raise HTTPError('500 server error')
        dummy_resp.raise_for_status = _raise

        with patch('apps.reminders.notifications.requests.post', return_value=dummy_resp) as mpost:
            ok = svc._send_sms_notification(
                user=self.user,
                title='用药提醒',
                message='请按时服用维生素B',
                reminder=self.reminder,
            )

        self.assertFalse(ok)
        self.assertEqual(mpost.call_count, 1)
        # 失败不应创建 sent 历史
        self.assertEqual(
            ReminderHistory.objects.filter(user=self.user, reminder=self.reminder, status='sent').count(),
            0
        )

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID='tmpl123',
        SPUG_PUSH_URL='http://spug.test',
        SPUG_APP_NAME='MTM用药助手',
        SPUG_PUSH_TOKEN='token123',
        SPUG_PUSH_TIMEOUT_SECONDS=1,
    )
    def test_spug_sms_send_timeout_returns_false(self):
        svc = NotificationService()
        def _raise_timeout(*args, **kwargs):
            from requests import Timeout
            raise Timeout('timeout')
        with patch('apps.reminders.notifications.requests.post', side_effect=_raise_timeout) as mpost:
            ok = svc._send_sms_notification(
                user=self.user,
                title='用药提醒',
                message='请按时服用维生素B',
                reminder=self.reminder,
            )
        self.assertFalse(ok)
        self.assertEqual(mpost.call_count, 1)
        self.assertEqual(
            ReminderHistory.objects.filter(user=self.user, reminder=self.reminder).count(),
            0
        )

