from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.core.models import SessionMemory


class SessionMemorySummarizeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="memory-user", password="pass12345"
        )
        self.client.force_authenticate(user=self.user)
        self.session_id = "app:dashboard:page-agent"

    def test_requires_session_id(self):
        response = self.client.post(
            "/api/ai/session-memory/summarize/",
            {"messages": [{"role": "user", "content": "你好"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "VALIDATION_ERROR")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="",
        BAICHUAN_M3_MODEL="memory-model",
    )
    def test_returns_ai_config_missing_when_runtime_not_configured(self):
        response = self.client.post(
            "/api/ai/session-memory/summarize/",
            {
                "session_id": self.session_id,
                "messages": [{"role": "user", "content": "请总结这段对话"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error_code"], "AI_CONFIG_MISSING")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="memory-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
    )
    def test_returns_ai_upstream_unavailable_when_llm_disconnects(self):
        from apps.core import views

        original = views._openai_chat_completion
        views._openai_chat_completion = lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("llm_request_exception:ConnectionError:connection refused")
        )
        try:
            response = self.client.post(
                "/api/ai/session-memory/summarize/",
                {
                    "session_id": self.session_id,
                    "messages": [{"role": "user", "content": "请总结这段对话"}],
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = original

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error_code"], "AI_UPSTREAM_UNAVAILABLE")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="memory-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
    )
    def test_returns_ai_upstream_timeout_when_llm_times_out(self):
        from apps.core import views

        original = views._openai_chat_completion
        views._openai_chat_completion = lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("llm_request_exception:Timeout:request timed out")
        )
        try:
            response = self.client.post(
                "/api/ai/session-memory/summarize/",
                {
                    "session_id": self.session_id,
                    "messages": [{"role": "user", "content": "请总结这段对话"}],
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = original

        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["error_code"], "AI_UPSTREAM_TIMEOUT")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="",
        BAICHUAN_M3_MODEL="memory-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=3,
    )
    def test_summarize_success_updates_summary_and_preserves_messages(self):
        from apps.core import views

        original = views._openai_chat_completion
        views._openai_chat_completion = lambda **kwargs: "总结：用户需要服药提醒"
        try:
            response = self.client.post(
                "/api/ai/session-memory/summarize/",
                {
                    "session_id": self.session_id,
                    "messages": [
                        {"role": "user", "content": "我需要每天提醒吃药"},
                        {"role": "assistant", "content": "好的，我来帮你整理"},
                    ],
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = original

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertEqual(payload["session_id"], self.session_id)
        self.assertEqual(payload["summary"], "总结：用户需要服药提醒")

        memory = SessionMemory.objects.get(user=self.user, session_id=self.session_id)
        self.assertEqual(memory.summary, "总结：用户需要服药提醒")
        self.assertEqual(len(memory.messages), 2)
