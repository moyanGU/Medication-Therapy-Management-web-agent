import logging
from typing import Tuple
from .base import BaseSMSProvider

logger = logging.getLogger(__name__)

class MockSMSProvider(BaseSMSProvider):
    """
    开发或测试环境下的 Mock 服务提供商
    不会真正发送短信，只会将短信内容打印到日志中。
    """
    
    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        logger.info(
            f"🟢 [MockSMSProvider] 模拟发送短信成功. "
            f"Phone: {phone}, Template: {template_code}, Params: {template_params}"
        )
        return True, "mock-success-receipt"
