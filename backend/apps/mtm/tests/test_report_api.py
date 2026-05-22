from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.medical_records.models import MedicalRecord
from apps.mtm.models import MTMAssessment, MTMInterview, MTMPlan, MTMServiceCase


class MTMReportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.patient = user_model.objects.create_user(
            username="mtm_report_patient",
            password="pass123",
            email="mtm_report_patient@example.com",
            phone="13800000121",
        )
        self.pharmacist = user_model.objects.create_user(
            username="mtm_report_pharmacist",
            password="pass123",
            email="mtm_report_pharmacist@example.com",
            phone="13800000122",
        )
        self.client.force_authenticate(user=self.patient)

    def test_report_returns_pmr_and_map_blocks(self):
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="梳理双源用药记录",
        )
        MTMInterview.objects.create(
            service_case=service_case,
            medication_history=[{"name": "缬沙坦", "dosage": "5mg"}],
            allergy_history=[{"item": "青霉素"}],
            lifestyle_info={"exercise": "每周三次"},
        )
        MTMAssessment.objects.create(
            service_case=service_case,
            summary="存在潜在相互作用风险",
            risk_level="medium",
        )
        MTMPlan.objects.create(
            service_case=service_case,
            interventions=[{"title": "核对用药时间"}],
        )
        MedicalRecord.objects.create(
            user=self.patient,
            visit_date=timezone.localdate(),
            hospital="协和医院",
            department="心内科",
            doctor="张医生",
            diagnosis="高血压",
            prescribed_medicines=[
                {
                    "name": "缬沙坦",
                    "dosage": "5mg",
                    "frequency": "qd",
                    "instructions": "早餐后服用",
                }
            ],
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/report/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        data = response.json()["data"]
        self.assertEqual(data["case_info"]["case_number"], service_case.case_number)
        self.assertEqual(len(data["pmr"]["medical_records"]), 1)
        self.assertEqual(
            data["pmr"]["medical_records"][0]["medicines"][0]["name"],
            "缬沙坦",
        )
        self.assertEqual(data["assessment"]["risk_level"], "medium")
        self.assertEqual(data["map"]["interventions"][0]["title"], "核对用药时间")

    def test_report_handles_missing_related_blocks(self):
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="仅创建服务单后直接预览报告",
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/report/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        data = response.json()["data"]
        self.assertEqual(data["pmr"]["medical_records"], [])
        self.assertEqual(data["pmr"]["allergies"], [])
        self.assertEqual(data["pmr"]["medication_history"], [])
        self.assertEqual(data["pmr"]["lifestyle"], {})
        self.assertEqual(data["assessment"], {})
        self.assertEqual(data["map"], {})
