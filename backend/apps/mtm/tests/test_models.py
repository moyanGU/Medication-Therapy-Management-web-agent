from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.mtm.models import (
    MTMAssessment,
    MTMFollowUp,
    MTMInterview,
    MTMPlan,
    MTMServiceCase,
)


class MTMModelsTest(TestCase):
    def setUp(self):
        """
        创建 MTM 模型测试所需的最小用户数据
        """
        user_model = get_user_model()
        self.patient = user_model.objects.create_user(
            username="mtm_patient",
            password="pass123",
            email="mtm_patient@example.com",
            phone="13800000101",
        )
        self.pharmacist = user_model.objects.create_user(
            username="mtm_pharmacist",
            password="pass123",
            email="mtm_pharmacist@example.com",
            phone="13800000102",
        )

    def test_service_case_generates_case_number_and_defaults(self):
        """
        验证服务单会自动生成业务编号并带有默认状态
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="提升服药依从性",
        )

        self.assertTrue(service_case.case_number.startswith("MTM-"))
        self.assertEqual(service_case.status, "pending")
        self.assertEqual(service_case.trigger_source, "manual")

    def test_related_models_attach_to_service_case(self):
        """
        验证问诊、评估、计划和随访能按既定关系挂到服务单上
        """
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            trigger_source="adherence_alert",
        )

        interview = MTMInterview.objects.create(
            service_case=service_case,
            basic_info_snapshot={"age": 68},
            medication_history=[{"name": "二甲双胍", "active": True}],
        )
        assessment = MTMAssessment.objects.create(
            service_case=service_case,
            risk_level="high",
            adherence_score=45,
            problem_list=[{"type": "adherence", "severity": "high"}],
        )
        plan = MTMPlan.objects.create(
            service_case=service_case,
            priority="high",
            interventions=[{"type": "education", "title": "建立晨间提醒"}],
        )
        follow_up = MTMFollowUp.objects.create(
            service_case=service_case,
            follow_up_time=service_case.started_at,
            execution_status="pending",
        )

        self.assertEqual(service_case.interview, interview)
        self.assertEqual(service_case.assessment, assessment)
        self.assertEqual(service_case.plan, plan)
        self.assertEqual(service_case.follow_ups.count(), 1)
        self.assertEqual(service_case.follow_ups.first(), follow_up)
