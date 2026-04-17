from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medicines.models import Medicine
from apps.records.models import MedicationRecord
from apps.reminders.models import Reminder


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class ReminderConfirmRecordSyncTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="record_sync_user",
            password="pass123",
            email="record-sync@example.com",
            phone="13800000021",
        )
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(
            user=self.user,
            name="二甲双胍",
            quantity=30,
        )
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title="早餐后服药",
            reminder_time=timezone.datetime.strptime("08:00", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=2,
            dosage_unit="tablet",
            is_active=True,
        )

    def test_confirm_taken_creates_record_and_deducts_inventory(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "taken"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        record = MedicationRecord.objects.get(id=payload["record_id"])

        self.assertEqual(record.reminder_id, self.reminder.id)
        self.assertEqual(record.status, "taken")
        self.assertEqual(record.source, "reminder")
        self.assertIsNotNone(record.scheduled_time)
        self.assertEqual(record.quantity_taken, 2)

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 28)

    def test_confirm_missed_creates_record_without_inventory_deduction(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "missed"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        record = MedicationRecord.objects.get(id=payload["record_id"])

        self.assertEqual(record.status, "missed")
        self.assertEqual(record.quantity_taken, 0)

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 30)

    def test_confirm_delayed_creates_record_with_delay_minutes(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "delayed", "delay_minutes": 15},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        record = MedicationRecord.objects.get(id=payload["record_id"])

        self.assertEqual(record.status, "delayed")
        self.assertEqual(record.delay_minutes, 15)
        expected_taken_at = record.scheduled_time + timedelta(minutes=15)
        self.assertEqual(record.taken_at, expected_taken_at)

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 28)

    def test_confirm_partial_creates_record_and_deducts_partial_inventory(self):
        response = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "partial", "quantity_taken": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        record = MedicationRecord.objects.get(id=payload["record_id"])

        self.assertEqual(record.status, "partial")
        self.assertEqual(record.quantity_taken, 1)

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 29)

    def test_repeat_confirm_updates_same_record_and_reconciles_inventory(self):
        first = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "taken"},
            format="json",
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            f"/api/reminders/{self.reminder.id}/confirm/",
            {"action": "partial", "quantity_taken": 1},
            format="json",
        )
        self.assertEqual(second.status_code, 200)

        self.assertEqual(MedicationRecord.objects.count(), 1)
        record = MedicationRecord.objects.first()
        self.assertEqual(record.status, "partial")
        self.assertEqual(record.quantity_taken, 1)

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 29)
