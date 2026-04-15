from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.mtm.models import (
    MTMAssessment,
    MTMFollowUp,
    MTMInterview,
    MTMPlan,
    MTMServiceCase,
)


class MTMServiceCaseApiTest(TestCase):
    def setUp(self):
        """
        初始化 MTM 服务接口测试数据
        """
        self.client = APIClient()
        user_model = get_user_model()
        self.patient = user_model.objects.create_user(
            username="mtm_api_patient",
            password="pass123",
            email="mtm_api_patient@example.com",
            phone="13800000111",
        )
        self.other_user = user_model.objects.create_user(
            username="mtm_api_other",
            password="pass123",
            email="mtm_api_other@example.com",
            phone="13800000112",
        )
        self.pharmacist = user_model.objects.create_user(
            username="mtm_api_pharmacist",
            password="pass123",
            email="mtm_api_pharmacist@example.com",
            phone="13800000113",
        )
        self.client.force_authenticate(user=self.patient)

    def test_create_service_case_uses_current_user_as_patient(self):
        """
        验证服务单创建时自动使用当前登录用户作为患者
        """
        response = self.client.post(
            "/api/mtm/service-cases/",
            {
                "trigger_source": "self_requested",
                "service_goal": "需要专业评估当前联合用药",
                "notes": "最近新增两种药物",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        data = response.json()["data"]
        self.assertEqual(data["patient"]["id"], self.patient.id)
        self.assertEqual(data["status"], "pending")
        self.assertEqual(MTMServiceCase.objects.count(), 1)

    def test_list_only_returns_cases_current_user_participates_in(self):
        """
        验证列表接口只返回当前用户参与的服务单
        """
        own_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="我的服务单",
        )
        MTMServiceCase.objects.create(
            patient=self.other_user,
            service_goal="别人的服务单",
        )

        response = self.client.get("/api/mtm/service-cases/")

        self.assertEqual(response.status_code, 200)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], own_case.id)

    def test_detail_returns_related_summary_blocks(self):
        """
        验证详情接口会返回最小关联摘要
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="following_up",
            service_goal="复盘近期低依从性问题",
        )
        MTMInterview.objects.create(
            service_case=service_case,
            basic_info_snapshot={"age": 72},
            medication_history=[{"name": "缬沙坦"}],
        )
        MTMAssessment.objects.create(
            service_case=service_case,
            adherence_score=52,
            risk_level="high",
        )
        MTMPlan.objects.create(
            service_case=service_case,
            interventions=[{"type": "education", "title": "补充服药教育"}],
        )
        MTMFollowUp.objects.create(
            service_case=service_case,
            follow_up_time=timezone.now(),
            execution_status="pending",
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/")

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIsNotNone(data["interview"])
        self.assertIsNotNone(data["assessment"])
        self.assertIsNotNone(data["plan"])
        self.assertEqual(len(data["follow_ups"]), 1)

    def test_transition_updates_status_with_valid_next_step(self):
        """
        验证合法状态流转可以成功执行
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
        )

        response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/transition/",
            {"target_status": "interviewing", "notes": "开始第一轮问诊"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        service_case.refresh_from_db()
        self.assertEqual(service_case.status, "interviewing")
        self.assertIn("开始第一轮问诊", service_case.notes)

    def test_transition_rejects_invalid_jump(self):
        """
        验证非法状态跳转会被拦截
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
        )

        response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/transition/",
            {"target_status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_non_participant_cannot_access_case_detail(self):
        """
        验证非参与者无法查看他人的服务单详情
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.other_user,
            assigned_pharmacist=self.pharmacist,
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/")

        self.assertEqual(response.status_code, 404)
