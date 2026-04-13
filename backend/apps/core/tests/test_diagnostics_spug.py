from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class DiagnosticsSpugTest(TestCase):
    @override_settings(
        SPUG_PUSH_ENABLED=True,
        SPUG_TEMPLATE_ID="tmpl123",
        SPUG_PUSH_URL="http://spug.test",
        SPUG_PUSH_TOKEN="",
        SPUG_PUSH_TIMEOUT_SECONDS=2,
    )
    def test_diagnostics_spug_details_present(self):
        client = APIClient()
        resp = client.get("/api/diagnostics/")
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
        client = APIClient()
        resp = client.get("/api/diagnostics/")
        self.assertEqual(resp.status_code, 206)
        data = resp.json().get("data")
        problems = data.get("problems", [])
        self.assertIn("SPUG_PUSH_ENABLED 已开启但缺少 SPUG_TEMPLATE_ID", problems)
