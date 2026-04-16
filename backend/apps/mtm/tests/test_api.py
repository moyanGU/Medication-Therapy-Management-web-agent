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

    def test_get_interview_initializes_minimum_draft(self):
        """
        验证读取问诊接口时会为当前服务单生成最小草稿
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="梳理当前高血压与糖尿病联合用药",
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/interview/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        data = response.json()["data"]
        self.assertEqual(data["basic_info_snapshot"]["patient_name"], self.patient.username)
        self.assertEqual(data["basic_info_snapshot"]["contact_phone"], self.patient.phone)
        self.assertEqual(data["health_expectations"], service_case.service_goal)
        self.assertTrue(MTMInterview.objects.filter(service_case=service_case).exists())

    def test_put_interview_saves_draft_without_completing(self):
        """
        验证问诊草稿可以保存且不会自动标记完成
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="interviewing",
        )

        response = self.client.put(
            f"/api/mtm/service-cases/{service_case.id}/interview/",
            {
                "basic_info_snapshot": {
                    "age": 71,
                    "gender": "女",
                    "main_diagnosis": "高血压复诊",
                },
                "medication_history": [{"name": "缬沙坦"}],
                "allergy_history": [{"item": "青霉素"}],
                "lifestyle_info": {"exercise": "每周散步三次"},
                "economic_context": "希望控制长期药费",
                "health_expectations": "先把当前药物方案梳理清楚",
                "notes": "最近头晕次数增加",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        interview = MTMInterview.objects.get(service_case=service_case)
        self.assertEqual(interview.basic_info_snapshot["main_diagnosis"], "高血压复诊")
        self.assertIsNone(interview.completed_at)

    def test_complete_interview_requires_key_fields_and_sets_completed_at(self):
        """
        验证完成问诊时会执行最小字段校验，并在通过后写入完成时间
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="interviewing",
        )

        invalid_response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/interview/complete/",
            {
                "basic_info_snapshot": {},
                "medication_history": [],
                "health_expectations": "",
                "notes": "",
            },
            format="json",
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertFalse(invalid_response.json()["success"])

        valid_response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/interview/complete/",
            {
                "basic_info_snapshot": {"age": 71, "main_diagnosis": "高血压"},
                "medication_history": [{"name": "缬沙坦"}],
                "allergy_history": [],
                "lifestyle_info": {"sleep": "一般"},
                "economic_context": "",
                "health_expectations": "希望减少头晕并稳定血压",
                "notes": "",
            },
            format="json",
        )
        self.assertEqual(valid_response.status_code, 200)
        self.assertTrue(valid_response.json()["success"])
        interview = MTMInterview.objects.get(service_case=service_case)
        self.assertIsNotNone(interview.completed_at)

    def test_get_assessment_initializes_minimum_draft(self):
        """
        验证读取评估接口时会为当前服务单生成最小草稿
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="interviewing",
            service_goal="复核当前多重用药的综合风险",
        )

        response = self.client.get(f"/api/mtm/service-cases/{service_case.id}/assessment/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        data = response.json()["data"]
        self.assertEqual(data["risk_level"], "medium")
        self.assertEqual(data["problem_list"], [])
        self.assertTrue(MTMAssessment.objects.filter(service_case=service_case).exists())

    def test_put_assessment_saves_draft_without_completing(self):
        """
        验证评估草稿可以保存且不会自动标记完成
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="assessing",
        )

        response = self.client.put(
            f"/api/mtm/service-cases/{service_case.id}/assessment/",
            {
                "appropriateness_score": 78,
                "effectiveness_score": 72,
                "safety_score": 65,
                "risk_level": "medium",
                "problem_list": [{"item": "存在重复用药风险"}],
                "summary": "当前方案基本可用，但需要继续梳理重复用药问题。",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        assessment = MTMAssessment.objects.get(service_case=service_case)
        self.assertEqual(assessment.appropriateness_score, 78)
        self.assertEqual(assessment.problem_list[0]["item"], "存在重复用药风险")
        self.assertIsNone(assessment.completed_at)

    def test_complete_assessment_requires_key_fields_and_sets_completed_at(self):
        """
        验证完成评估时会执行最小字段校验，并在通过后写入完成时间
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            status="assessing",
        )

        invalid_response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/assessment/complete/",
            {
                "appropriateness_score": None,
                "effectiveness_score": None,
                "safety_score": None,
                "adherence_score": None,
                "economic_score": None,
                "risk_level": "",
                "problem_list": [],
                "summary": "",
            },
            format="json",
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertFalse(invalid_response.json()["success"])

        valid_response = self.client.post(
            f"/api/mtm/service-cases/{service_case.id}/assessment/complete/",
            {
                "appropriateness_score": 82,
                "effectiveness_score": 70,
                "safety_score": 61,
                "adherence_score": 58,
                "economic_score": 76,
                "risk_level": "high",
                "problem_list": [{"item": "当前依从性偏低"}],
                "summary": "需要优先处理依从性和安全性风险。",
            },
            format="json",
        )
        self.assertEqual(valid_response.status_code, 200)
        self.assertTrue(valid_response.json()["success"])
        assessment = MTMAssessment.objects.get(service_case=service_case)
        self.assertIsNotNone(assessment.completed_at)
