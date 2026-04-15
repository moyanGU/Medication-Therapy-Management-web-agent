from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medical_records.models import MedicalRecord
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
class DashboardSummaryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="dashboard_user",
            password="pass123",
            email="dashboard@example.com",
            phone="13800000041",
        )
        self.client.force_authenticate(user=self.user)

    def test_dashboard_summary_returns_aggregated_home_data(self):
        today = timezone.now()

        low_stock_medicine = Medicine.objects.create(
            user=self.user,
            name="阿卡波糖",
            quantity=3,
            expiry_date=timezone.now().date() + timedelta(days=10),
        )
        normal_medicine = Medicine.objects.create(
            user=self.user,
            name="缬沙坦",
            quantity=20,
            expiry_date=timezone.now().date() + timedelta(days=120),
        )

        completed_reminder = Reminder.objects.create(
            user=self.user,
            medicine=low_stock_medicine,
            title="早餐后服药",
            reminder_time=time(8, 0),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
        )
        pending_reminder = Reminder.objects.create(
            user=self.user,
            medicine=normal_medicine,
            title="晚间服药",
            reminder_time=time(20, 0),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
        )

        MedicationRecord.objects.create(
            user=self.user,
            medicine=low_stock_medicine,
            reminder=completed_reminder,
            taken_at=today,
            scheduled_time=today,
            quantity_taken=1,
            administration_method="oral",
            status="taken",
            source="reminder",
        )
        MedicationRecord.objects.create(
            user=self.user,
            medicine=low_stock_medicine,
            reminder=completed_reminder,
            taken_at=today - timedelta(days=1),
            scheduled_time=today - timedelta(days=1),
            quantity_taken=0,
            administration_method="oral",
            status="missed",
            source="reminder",
        )
        MedicationRecord.objects.create(
            user=self.user,
            medicine=normal_medicine,
            reminder=pending_reminder,
            taken_at=today - timedelta(days=2) + timedelta(minutes=15),
            scheduled_time=today - timedelta(days=2),
            quantity_taken=1,
            administration_method="oral",
            status="delayed",
            delay_minutes=15,
            source="reminder",
        )

        ReminderHistory.objects.create(
            user=self.user,
            reminder=completed_reminder,
            sent_at=today - timedelta(days=1),
            scheduled_time=today - timedelta(days=1),
            reminder_type="scheduled",
            title="服药提醒",
            message="请按时服药",
            notification_methods=["push"],
            status="sent",
            response_type="taken",
            responded_at=today - timedelta(days=1) + timedelta(minutes=3),
        )
        ReminderHistory.objects.create(
            user=self.user,
            reminder=pending_reminder,
            sent_at=today - timedelta(days=2),
            scheduled_time=today - timedelta(days=2),
            reminder_type="scheduled",
            title="服药提醒",
            message="请按时服药",
            notification_methods=["push"],
            status="sent",
            response_type="no_response",
        )

        MedicalRecord.objects.create(
            user=self.user,
            visit_date=timezone.now().date() - timedelta(days=7),
            hospital="人民医院",
            department="内科",
            doctor="张医生",
            follow_up_date=timezone.now().date() - timedelta(days=1),
            status="completed",
        )
        MedicalRecord.objects.create(
            user=self.user,
            visit_date=timezone.now().date() - timedelta(days=3),
            hospital="协和医院",
            department="心内科",
            doctor="李医生",
            follow_up_date=timezone.now().date() + timedelta(days=3),
            status="completed",
        )

        response = self.client.get("/api/dashboard/summary/")

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]

        self.assertEqual(
            set(data.keys()),
            {
                "today_tasks",
                "risk_alerts",
                "medication_summary",
                "followup_summary",
                "adherence_summary",
                "mtm_entry_hint",
            },
        )
        self.assertEqual(data["today_tasks"]["total"], 2)
        self.assertEqual(data["today_tasks"]["completed"], 1)
        self.assertEqual(data["today_tasks"]["pending"], 1)

        self.assertEqual(data["medication_summary"]["total_medicines"], 2)
        self.assertEqual(data["medication_summary"]["low_stock_count"], 1)
        self.assertEqual(data["medication_summary"]["expiring_soon_count"], 1)

        risk_types = {item["type"] for item in data["risk_alerts"]}
        self.assertIn("low_stock", risk_types)
        self.assertIn("expiring_soon", risk_types)
        self.assertIn("followup_due", risk_types)
        self.assertIn("adherence_risk", risk_types)

        self.assertEqual(data["followup_summary"]["due_count"], 1)
        self.assertEqual(data["followup_summary"]["upcoming_count"], 1)
        self.assertEqual(data["followup_summary"]["next_followup"]["hospital"], "协和医院")

        self.assertEqual(data["adherence_summary"]["summary_7d"]["total_records"], 3)
        self.assertEqual(data["adherence_summary"]["summary_7d"]["missed_count"], 1)
        self.assertEqual(data["adherence_summary"]["summary_7d"]["delayed_count"], 1)
        self.assertTrue(data["mtm_entry_hint"]["recommended"])
        self.assertGreaterEqual(data["mtm_entry_hint"]["reason_count"], 1)

    def test_dashboard_summary_returns_structured_empty_state(self):
        response = self.client.get("/api/dashboard/summary/")

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]

        self.assertEqual(data["today_tasks"]["total"], 0)
        self.assertEqual(data["today_tasks"]["items"], [])
        self.assertEqual(data["risk_alerts"], [])
        self.assertEqual(data["medication_summary"]["total_medicines"], 0)
        self.assertEqual(data["followup_summary"]["due_count"], 0)
        self.assertEqual(data["followup_summary"]["next_followup"], None)
        self.assertEqual(data["adherence_summary"]["summary_7d"]["total_records"], 0)
        self.assertFalse(data["mtm_entry_hint"]["recommended"])
