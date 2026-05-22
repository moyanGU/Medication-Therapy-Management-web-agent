from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.mtm.models import MTMServiceCase


class MTMSoapApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.patient = user_model.objects.create_user(
            username="mtm_soap_patient",
            password="pass123",
            email="mtm_soap_patient@example.com",
            phone="13800000131",
        )
        self.pharmacist = user_model.objects.create_user(
            username="mtm_soap_pharmacist",
            password="pass123",
            email="mtm_soap_pharmacist@example.com",
            phone="13800000132",
        )
        self.client.force_authenticate(user=self.patient)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="secret",
        BAICHUAN_M3_MODEL="soap-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=7,
    )
    def test_generate_soap_returns_unified_ai_failure_when_agent_fails(self):
        service_case = MTMServiceCase.objects.create(
            patient=self.patient,
            assigned_pharmacist=self.pharmacist,
            service_goal="generate soap",
        )

        from apps.core.agents import soap_agent

        original_generate = soap_agent.SoapAgent.generate

        def _raise_failure(self, patient_data):
            raise RuntimeError("llm_request_exception:ConnectionError:connection refused")

        soap_agent.SoapAgent.generate = _raise_failure
        try:
            response = self.client.post(
                f"/api/mtm/service-cases/{service_case.id}/soap/generate/",
                {},
                format="json",
            )
        finally:
            soap_agent.SoapAgent.generate = original_generate

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error_code"], "AI_UPSTREAM_UNAVAILABLE")
