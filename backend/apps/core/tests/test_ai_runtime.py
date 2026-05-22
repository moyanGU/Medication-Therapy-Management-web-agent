from django.test import TestCase, override_settings


class AIRuntimeConfigTest(TestCase):
    @override_settings(
        BAICHUAN_M3_ENABLED=True,
        BAICHUAN_M3_API_BASE_URL="http://127.0.0.1:1234",
        BAICHUAN_M3_API_KEY="primary-key",
        BAICHUAN_M3_MODEL="primary-model",
        AI_FALLBACK_API_BASE_URL="https://api.example.com/v1",
        AI_FALLBACK_API_KEY="fallback-key",
        AI_FALLBACK_MODEL="fallback-model",
        AI_FALLBACK_TIMEOUT_SECONDS=12,
    )
    def test_uses_fallback_when_localhost_upstream_is_unreachable(self):
        from apps.core.ai_runtime import get_ai_runtime_config

        config, error = get_ai_runtime_config()

        self.assertIsNone(error)
        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "https://api.example.com/v1")
        self.assertEqual(config.api_key, "fallback-key")
        self.assertEqual(config.model, "fallback-model")
        self.assertEqual(config.timeout_seconds, 12)
        self.assertEqual(config.source, "fallback")
