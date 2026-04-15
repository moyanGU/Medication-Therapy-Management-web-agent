from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medicines.models import Medicine
from apps.reminders.history_models import ReminderHistory
from apps.reminders.models import Reminder


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class ReminderConfirmActionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="confirm_user",
            password="pass123",
            email="confirm@example.com",
            phone="13800000011",
        )
        self.other_user = user_model.objects.create_user(
            username="other_user",
            password="pass123",
            email="other@example.com",
            phone="13800000012",
        )
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(
            user=self.user,
            name="阿司匹林",
            quantity=30,
        )
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title="早餐后服药",
            message="请按时服用",
            reminder_time=timezone.datetime.strptime("08:00", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=2,
            dosage_unit="tablet",
            is_active=True,
        )

    def test_confirm_taken_updates_response_count_and_returns_record_payload(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "taken"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.response_count, 1)

        payload = response.json()["data"]
        self.assertEqual(payload["action"], "taken")
        self.assertEqual(payload["response_count"], 1)
        self.assertEqual(payload["record_payload"]["source"], "reminder")
        self.assertEqual(payload["record_payload"]["quantity_taken"], 2)
        self.assertEqual(payload["record_payload"]["record_status"], "taken")

    def test_confirm_delayed_creates_pending_history(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "delayed", "delay_minutes": 15},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.response_count, 1)

        pending_history = ReminderHistory.objects.filter(
            user=self.user,
            reminder=self.reminder,
            status="pending",
            reminder_type="repeat",
        )
        self.assertEqual(pending_history.count(), 1)
        self.assertEqual(response.json()["data"]["record_payload"]["delay_minutes"], 15)
        self.assertEqual(response.json()["data"]["record_payload"]["record_status"], "delayed")

    def test_confirm_partial_requires_quantity_less_than_dosage(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "partial", "quantity_taken": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.response_count, 0)

    def test_confirm_only_allows_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "taken"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.response_count, 0)
