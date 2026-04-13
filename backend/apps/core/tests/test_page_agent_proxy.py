from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class _MockResponse:
    def __init__(
        self, status_code: int, json_data=None, raises_json: bool = False, text: str = ""
    ):
        self.status_code = status_code
        self._json_data = json_data
        self._raises_json = raises_json
        self.text = text

    def json(self):
        if self._raises_json:
            raise ValueError("invalid json")
        return self._json_data


class PageAgentProxyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="page-agent-user", password="pass12345"
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="secret-key",
        BAICHUAN_M3_MODEL="proxy-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=5,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=256,
    )
    def test_page_agent_proxy_forwards_plain_chat_payload(self):
        from apps.core import views

        captured = {}

        def _mock_post(*args, **kwargs):
            captured["url"] = args[0]
            captured["headers"] = kwargs.get("headers", {})
            captured["json"] = kwargs.get("json", {})
            return _MockResponse(
                200,
                {
                    "id": "chatcmpl-test",
                    "choices": [{"message": {"content": "页面摘要"}}],
                },
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/page-agent/chat/completions/",
                {
                    "messages": [{"role": "user", "content": "总结当前页面"}],
                    "temperature": 0.2,
                    "max_tokens": 999,
                },
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(captured["url"], "http://llm.test/v1/chat/completions")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer secret-key")
        self.assertEqual(captured["json"]["model"], "proxy-model")
        self.assertEqual(captured["json"]["messages"][0]["content"], "总结当前页面")
        self.assertEqual(captured["json"]["max_tokens"], 256)
        self.assertEqual(resp.json()["choices"][0]["message"]["content"], "页面摘要")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="secret-key",
        BAICHUAN_M3_MODEL="proxy-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=5,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=256,
    )
    def test_page_agent_proxy_retries_without_v1_when_primary_returns_unexpected_shape(self):
        from apps.core import views

        captured_urls = []

        def _mock_post(*args, **kwargs):
            captured_urls.append(args[0])
            if args[0].endswith("/v1/chat/completions"):
                return _MockResponse(
                    200,
                    {"error": {"message": "Unexpected endpoint or method"}},
                    text='{"error":{"message":"Unexpected endpoint or method"}}',
                )
            return _MockResponse(
                200,
                {
                    "id": "chatcmpl-test-fallback",
                    "choices": [{"message": {"content": "fallback ok"}}],
                },
            )

        orig = views.requests.post
        views.requests.post = _mock_post
        try:
            resp = self.client.post(
                "/api/ai/page-agent/chat/completions/",
                {
                    "messages": [{"role": "user", "content": "总结当前页面"}],
                    "temperature": 0.2,
                    "max_tokens": 999,
                },
                format="json",
            )
        finally:
            views.requests.post = orig

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            captured_urls,
            [
                "http://llm.test/v1/chat/completions",
                "http://llm.test/chat/completions",
            ],
        )
        self.assertEqual(resp.json()["choices"][0]["message"]["content"], "fallback ok")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_API_KEY="secret-key",
        BAICHUAN_M3_MODEL="proxy-model",
        BAICHUAN_M3_TIMEOUT_SECONDS=5,
        BAICHUAN_M3_MAX_OUTPUT_TOKENS=256,
    )
    def test_page_agent_proxy_falls_back_to_json_mode_for_tools(self):
        from apps.core import views

        captured = {}

        def _mock_completion(**kwargs):
            captured.update(kwargs)
            return '{"text":"已完成页面分析","success":true}'

        orig = views._openai_chat_completion
        views._openai_chat_completion = _mock_completion
        try:
            resp = self.client.post(
                "/api/ai/page-agent/chat/completions/",
                {
                    "messages": [
                        {"role": "system", "content": "你是页面助手。"},
                        {"role": "user", "content": "总结当前页面"},
                    ],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "AgentOutput",
                                "description": "输出页面助手动作",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "success": {"type": "boolean"},
                                    },
                                    "required": ["text", "success"],
                                },
                            },
                        }
                    ],
                    "tool_choice": {
                        "type": "function",
                        "function": {"name": "AgentOutput"},
                    },
                    "temperature": 0.2,
                    "max_tokens": 128,
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = orig

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(captured["base_url"], "http://llm.test")
        self.assertEqual(captured["model"], "proxy-model")
        self.assertEqual(captured["max_tokens"], 128)
        self.assertEqual(captured["messages"][0]["role"], "system")
        self.assertIn("你是页面助手。", captured["messages"][0]["content"])
        self.assertEqual(len([m for m in captured["messages"] if m["role"] == "system"]), 1)
        self.assertEqual(captured["messages"][1]["content"], "总结当前页面")
        body = resp.json()
        tool_call = body["choices"][0]["message"]["tool_calls"][0]
        self.assertEqual(tool_call["function"]["name"], "AgentOutput")
        self.assertEqual(
            tool_call["function"]["arguments"],
            '{"text": "已完成页面分析", "success": true}',
        )
        self.assertEqual(body["choices"][0]["finish_reason"], "tool_calls")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_MODEL="proxy-model",
    )
    def test_page_agent_proxy_returns_502_when_fallback_output_is_not_json(self):
        from apps.core import views

        orig = views._openai_chat_completion
        views._openai_chat_completion = lambda **kwargs: "not-json"
        try:
            resp = self.client.post(
                "/api/ai/page-agent/chat/completions/",
                {
                    "messages": [{"role": "user", "content": "总结当前页面"}],
                    "tools": [{"type": "function", "function": {"name": "AgentOutput"}}],
                    "tool_choice": {
                        "type": "function",
                        "function": {"name": "AgentOutput"},
                    },
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = orig

        self.assertEqual(resp.status_code, 502)
        self.assertIn("JSON", resp.json()["error"]["message"])

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_MODEL="proxy-model",
    )
    def test_page_agent_proxy_returns_502_when_fallback_upstream_rejects_payload(self):
        from apps.core import views

        orig = views._openai_chat_completion
        views._openai_chat_completion = lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("llm_http_error:400:bad request")
        )
        try:
            resp = self.client.post(
                "/api/ai/page-agent/chat/completions/",
                {
                    "messages": [{"role": "user", "content": "总结当前页面"}],
                    "tools": [{"type": "function", "function": {"name": "AgentOutput"}}],
                    "tool_choice": {
                        "type": "function",
                        "function": {"name": "AgentOutput"},
                    },
                },
                format="json",
            )
        finally:
            views._openai_chat_completion = orig

        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.json()["error"]["type"], "upstream_error")

    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://llm.test",
        BAICHUAN_M3_MODEL="proxy-model",
    )
    def test_page_agent_proxy_rejects_invalid_messages(self):
        resp = self.client.post(
            "/api/ai/page-agent/chat/completions/",
            {"messages": "invalid"},
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("messages", resp.json()["error"]["message"])
