from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medicines.models import Medicine
from apps.records.models import MedicationRecord
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
class MedicationRecordAdherenceApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="adherence_user",
            password="pass123",
            email="adherence@example.com",
            phone="13800000031",
        )
        self.client.force_authenticate(user=self.user)

        self.medicine = Medicine.objects.create(
            user=self.user,
            name="氯沙坦",
            quantity=100,
        )
        self.other_medicine = Medicine.objects.create(
            user=self.user,
            name="阿托伐他汀",
            quantity=100,
        )
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            title="早晨服药",
            reminder_time=time(8, 0),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
        )
        self.other_reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.other_medicine,
            title="睡前服药",
            reminder_time=time(21, 0),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
        )

        today = timezone.now()
        self._create_record(days_ago=1, status="taken", quantity=1)
        self._create_record(days_ago=2, status="delayed", quantity=1, delay_minutes=20)
        self._create_record(days_ago=3, status="missed", quantity=0)
        self._create_record(days_ago=4, status="partial", quantity=1)
        self._create_record(days_ago=20, status="taken", quantity=1)

        MedicationRecord.objects.create(
            user=self.user,
            medicine=self.medicine,
            taken_at=today - timedelta(days=2),
            quantity_taken=1,
            administration_method="oral",
            status="taken",
            source="manual",
        )

        self._create_history(days_ago=1, response_type="taken")
        self._create_history(days_ago=2, response_type="delayed")
        self._create_history(days_ago=3, response_type="no_response")
        self._create_history(days_ago=4, response_type="skipped")
        self._create_history(days_ago=5, response_type="no_response")

        self._create_other_medicine_record(days_ago=1, status="taken", quantity=1)

    def _create_record(self, days_ago, status, quantity, delay_minutes=None):
        scheduled_time = timezone.now() - timedelta(days=days_ago)
        taken_at = scheduled_time
        if status == "delayed" and delay_minutes:
            taken_at = scheduled_time + timedelta(minutes=delay_minutes)

        return MedicationRecord.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder=self.reminder,
            taken_at=taken_at,
            scheduled_time=scheduled_time,
            quantity_taken=quantity,
            administration_method="oral",
            status=status,
            delay_minutes=delay_minutes,
            source="reminder",
        )

    def _create_other_medicine_record(self, days_ago, status, quantity):
        scheduled_time = timezone.now() - timedelta(days=days_ago)
        return MedicationRecord.objects.create(
            user=self.user,
            medicine=self.other_medicine,
            reminder=self.other_reminder,
            taken_at=scheduled_time,
            scheduled_time=scheduled_time,
            quantity_taken=quantity,
            administration_method="oral",
            status=status,
            source="reminder",
        )

    def _create_history(self, days_ago, response_type):
        scheduled_time = timezone.now() - timedelta(days=days_ago)
        responded_at = None
        if response_type != "no_response":
            responded_at = scheduled_time + timedelta(minutes=5)

        ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            sent_at=scheduled_time,
            scheduled_time=scheduled_time,
            reminder_type="scheduled",
            title="服药提醒",
            message="请按时服药",
            notification_methods=["push"],
            status="sent",
            response_type=response_type,
            responded_at=responded_at,
        )

    def test_adherence_endpoint_returns_multi_period_summary_and_trend(self):
        response = self.client.get("/api/records/medication-records/adherence/?days=7")

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]

        self.assertEqual(data["summary_7d"]["total_records"], 5)
        self.assertEqual(data["summary_7d"]["taken_count"], 2)
        self.assertEqual(data["summary_7d"]["missed_count"], 1)
        self.assertEqual(data["summary_7d"]["delayed_count"], 1)
        self.assertEqual(data["summary_7d"]["partial_count"], 1)
        self.assertEqual(data["summary_7d"]["completed_count"], 4)
        self.assertEqual(data["summary_7d"]["adherence_rate"], 80.0)
        self.assertEqual(data["summary_7d"]["on_time_rate"], 40.0)
        self.assertEqual(data["summary_7d"]["avg_delay_minutes"], 20.0)
        self.assertEqual(data["summary_7d"]["risk_level"], "medium")
        self.assertIn("存在漏服", data["summary_7d"]["risk_flags"])

        self.assertEqual(data["summary_30d"]["total_records"], 6)
        self.assertEqual(data["summary_30d"]["response_summary"]["scheduled_count"], 5)
        self.assertEqual(data["summary_30d"]["response_summary"]["responded_count"], 3)
        self.assertEqual(data["summary_30d"]["response_summary"]
                         ["unresponded_count"], 2)
        self.assertEqual(data["summary_30d"]["response_summary"]["response_rate"], 60.0)

        self.assertEqual(len(data["trend"]), 7)
        recent_day = next(item for item in data["trend"] if item["taken"] == 2)
        self.assertEqual(recent_day["adherence_rate"], 100.0)
        self.assertEqual(recent_day["on_time_rate"], 100.0)

    def test_adherence_endpoint_supports_medicine_filter(self):
        response = self.client.get(
            f"/api/records/medication-records/adherence/?days=7&medicine_id={self.other_medicine.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["current_period"]["total_records"], 1)
        self.assertEqual(data["current_period"]["taken_count"], 1)
        self.assertEqual(data["current_period"]["missed_count"], 0)

    def test_adherence_endpoint_rejects_invalid_date(self):
        response = self.client.get(
            "/api/records/medication-records/adherence/?start_date=2026-99-99&end_date=2026-04-13"
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
