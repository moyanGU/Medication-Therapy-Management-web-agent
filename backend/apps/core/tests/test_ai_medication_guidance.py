from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class _MockResponse:
    def __init__(self, status_code: int, json_data: dict, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data


class MedicationGuidanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="u1", password="pass12345"
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=64,
        BAICHUAN_M3_CLASSIFIER_MAX_TOKENS=64,
    )
    def test_medication_guidance_allowed(self):
        from apps.core import views

        calls = {"n": 0}

        def _mock_post(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                return _MockResponse(
                    200,
                    {
                        "choices": [
                            {"message": {"content": '{"allowed": true, "reason": ""}'}}
                        ]
                    },
                )
            return _MockResponse(
                200,
                {"choices": [{"message": {"content": "用药建议内容"}}]},
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/medication-guidance/",
                {"question": "布洛芬怎么吃？"},
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get("success"))
        self.assertFalse(body.get("data", {}).get("blocked"))
        self.assertEqual(body.get("data", {}).get("answer"), "用药建议内容")
        self.assertEqual(calls["n"], 2)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=64,
        BAICHUAN_M3_CLASSIFIER_MAX_TOKENS=64,
    )
    def test_medication_guidance_reasoning_content_fallback(self):
        from apps.core import views

        calls = {"n": 0}

        def _mock_post(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                return _MockResponse(
                    200,
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": "",
                                    "reasoning_content": '{"allowed": true, "reason": ""}',
                                }
                            }
                        ]
                    },
                )
            return _MockResponse(
                200,
                {
                    "choices": [
                        {
                            "message": {
                                "content": " ",
                                "reasoning_content": "用药建议内容",
                            }
                        }
                    ]
                },
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/medication-guidance/",
                {"question": "布洛芬怎么吃？"},
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get("success"))
        self.assertFalse(body.get("data", {}).get("blocked"))
        self.assertEqual(body.get("data", {}).get("answer"), "用药建议内容")
        self.assertEqual(calls["n"], 2)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=64,
        BAICHUAN_M3_CLASSIFIER_MAX_TOKENS=64,
    )
    def test_medication_guidance_blocked(self):
        from apps.core import views

        def _mock_post(*args, **kwargs):
            return _MockResponse(
                200,
                {
                    "choices": [
                        {"message": {"content": '{"allowed": false, "reason": "需要诊断"}'}}
                    ]
                },
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/medication-guidance/",
                {"question": "我头痛是什么病？"},
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get("success"))
        self.assertTrue(body.get("data", {}).get("blocked"))

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=64,
        BAICHUAN_M3_CLASSIFIER_MAX_TOKENS=64,
    )
    def test_medication_guidance_classifier_failure_heuristic_allow(self):
        from apps.core import views

        calls = {"n": 0}

        def _mock_post(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                return _MockResponse(200, {"choices": [{"message": {"content": "not-json"}}]})
            return _MockResponse(
                200,
                {"choices": [{"message": {"content": "阿司匹林通常建议餐后服用。"}}]},
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/medication-guidance/",
                {"question": "阿司匹林的用药方法"},
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get("success"))
        self.assertFalse(body.get("data", {}).get("blocked"))
        self.assertIn("阿司匹林", body.get("data", {}).get("answer", ""))

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
    )
    def test_medication_guidance_missing_config(self):
        resp = self.client.post(
            "/api/ai/medication-guidance/",
            {"question": "布洛芬怎么吃？"},
            format="json",
        )
        self.assertEqual(resp.status_code, 503)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="m",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=64,
        BAICHUAN_M3_CLASSIFIER_MAX_TOKENS=64,
    )
    def test_medication_guidance_generation_failure_returns_fallback_success(self):
        from apps.core import views
        import requests

        calls = {"n": 0}

        def _mock_post(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                return _MockResponse(
                    200,
                    {
                        "choices": [
                            {"message": {"content": '{"allowed": true, "reason": ""}'}}
                        ]
                    },
                )
            raise requests.RequestException("upstream down")

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/medication-guidance/",
                {"question": "阿司匹林怎么吃？"},
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get("success"))
        self.assertFalse(body.get("data", {}).get("blocked"))
        self.assertTrue(body.get("data", {}).get("fallback_used"))
        self.assertTrue(body.get("data", {}).get("answer"))
