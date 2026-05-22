from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class DiagnosticsSpugTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.normal_user = self.user_model.objects.create_user(
            username="diagnostics-user",
            password="pass12345",
            email="diagnostics-user@example.com",
            phone="13800000991",
        )
        self.ops_user = self.user_model.objects.create_user(
            username="diagnostics-ops",
            password="pass12345",
            email="diagnostics-ops@example.com",
            phone="13800000992",
            is_staff=True,
        )

    def test_diagnostics_requires_authenticated_ops_user(self):
        anonymous = self.client.get("/api/diagnostics/")
        self.assertEqual(anonymous.status_code, 401)

        self.client.force_authenticate(user=self.normal_user)
        forbidden = self.client.get("/api/diagnostics/")
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(forbidden.json()["error_code"], "PERMISSION_DENIED")

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID="tmpl123",
        SPUG_PUSH_URL="http://spug.test",
        SPUG_PUSH_TOKEN="",
        SPUG_PUSH_TIMEOUT_SECONDS=2,
    )
    def test_diagnostics_spug_details_present(self):
        self.client.force_authenticate(user=self.ops_user)
        resp = self.client.get("/api/diagnostics/")
        self.assertIn(resp.status_code, (200, 206))
        data = resp.json().get("data")
        self.assertIn("diagnostics", data)
        sms = data["diagnostics"]["notifications"]["sms_spug"]
        self.assertTrue(sms["enabled"])
        self.assertTrue(sms["template_configured"])
        self.assertEqual(sms["url"], "http://spug.test")
        self.assertFalse(sms["token_configured"])
        self.assertEqual(sms["timeout_seconds"], 2)

    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID="",
    )
    def test_diagnostics_spug_missing_template_warn(self):
        self.client.force_authenticate(user=self.ops_user)
        resp = self.client.get("/api/diagnostics/")
        self.assertEqual(resp.status_code, 206)
        data = resp.json().get("data")
        problems = data.get("problems", [])
        self.assertIn("SPUG_PUSH_ENABLED 已开启但缺少 SPUG_TEMPLATE_ID", problems)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://127.0.0.1:1234",
        BAICHUAN_M3_MODEL="test-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=9,
    )
    def test_diagnostics_include_ai_runtime_status(self):
        self.client.force_authenticate(user=self.ops_user)
        resp = self.client.get("/api/diagnostics/")

        self.assertIn(resp.status_code, (200, 206))
        ai = resp.json()["data"]["diagnostics"]["ai"]
        self.assertTrue(ai["enabled"])
        self.assertTrue(ai["configured"])
        self.assertEqual(ai["model"], "test-model")
        self.assertEqual(ai["timeout_seconds"], 9.0)
        self.assertEqual(ai["upstream_url_mode"], "http://127.0.0.1:1234")

    def test_system_info_requires_authenticated_ops_user(self):
        anonymous = self.client.get("/api/system-info/")
        self.assertEqual(anonymous.status_code, 401)

        self.client.force_authenticate(user=self.normal_user)
        forbidden = self.client.get("/api/system-info/")
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(forbidden.json()["error_code"], "PERMISSION_DENIED")
