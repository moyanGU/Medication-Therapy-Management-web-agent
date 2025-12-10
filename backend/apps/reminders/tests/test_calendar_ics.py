from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from apps.reminders.models import Reminder
from apps.medicines.models import Medicine


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class CalendarICSTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass123', email='t@example.com')
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(name='阿莫西林', user=self.user)

        Reminder.objects.create(
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

    def test_calendar_ics_endpoint(self):
        resp = self.client.get('/api/calendar/ics/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/calendar', resp.headers.get('Content-Type', ''))
        content = resp.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('BEGIN:VEVENT', content)
        self.assertIn('SUMMARY:每日服药', content)
        self.assertIn('RRULE:FREQ=DAILY', content)
