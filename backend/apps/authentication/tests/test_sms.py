from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.core.cache import cache
import datetime

@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class SMSAntiSpamTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.phone = "13800138000"

    def test_send_verification_code_success(self):
        """测试正常发送短信"""
        response = self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_rate_limit_60_seconds(self):
        """测试60秒内防并发"""
        # 第一次发送
        self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        # 立即发送第二次
        response2 = self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        self.assertEqual(response2.status_code, 429)
        self.assertIn("频繁", response2.json()["message"])

    @override_settings(SMS_DAILY_PHONE_LIMIT=2, SMS_RATE_LIMIT_SECONDS=0)
    def test_daily_phone_limit(self):
        """测试单日手机号超限"""
        # 发送2次
        self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        
        # 第3次应该被拦截
        response3 = self.client.post("/api/auth/send-code/", {"phone": self.phone}, format="json")
        self.assertEqual(response3.status_code, 429)
        self.assertIn("手机号今日发送次数已达上限", response3.json()["message"])

    @override_settings(SMS_DAILY_IP_LIMIT=2, SMS_RATE_LIMIT_SECONDS=0, SMS_DAILY_PHONE_LIMIT=10)
    def test_daily_ip_limit(self):
        """测试单日IP超限"""
        # 使用不同手机号，但同一个IP（测试客户端默认 IP 相同）
        self.client.post("/api/auth/send-code/", {"phone": "13800138001"}, format="json")
        self.client.post("/api/auth/send-code/", {"phone": "13800138002"}, format="json")
        
        # 第3次应该被拦截
        response3 = self.client.post("/api/auth/send-code/", {"phone": "13800138003"}, format="json")
        self.assertEqual(response3.status_code, 429)
        self.assertIn("该设备今日发送次数过多", response3.json()["message"])
