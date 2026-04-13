from django.test import TestCase, RequestFactory, override_settings
from django.core.cache import cache
from apps.core.middleware import RateLimitMiddleware
from django.http import HttpResponse
from unittest.mock import MagicMock, patch

def get_response(request):
    return HttpResponse("Success")

# 使用本地内存缓存来模拟 Redis，确保限流逻辑可测试
@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    },
    API_RATE_LIMIT=5,
    API_RATE_WINDOW=60,
    API_RATE_LIMIT_PER_USER=5,
    API_RATE_LIMIT_PER_PATH=5
)
class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(get_response)
        cache.clear()

    @patch("apps.core.middleware._redis_available", return_value=True)
    def test_ip_rate_limit(self, mock_redis_available):
        """测试基于 IP 的限流"""
        request = self.factory.get("/api/test/")
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # 前5次应该通过 (process_request 返回 None)
        for i in range(5):
            response = self.middleware.process_request(request)
            self.assertIsNone(response, f"Request {i+1} should pass")

        # 第6次应该被限流 (process_request 返回 429 Response)
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)
        self.assertIn("RATE_LIMIT_EXCEEDED", response.content.decode())

    @patch("apps.core.middleware._redis_available", return_value=True)
    def test_user_rate_limit(self, mock_redis_available):
        """测试基于用户的限流"""
        request = self.factory.get("/api/test/")
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.id = 123
        
        # 前5次应该通过
        for i in range(5):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

        # 第6次应该被限流
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)

    @patch("apps.core.middleware._redis_available", return_value=False)
    def test_rate_limit_fallback(self, mock_redis_available):
        """测试 Redis 不可用时的降级策略"""
        request = self.factory.get("/api/test/")
        
        # 即使超过限制，如果 Redis 不可用，也应该放行 (返回 None)
        for i in range(10):
            response = self.middleware.process_request(request)
            self.assertIsNone(response, "Should fallback to allow when Redis is down")
