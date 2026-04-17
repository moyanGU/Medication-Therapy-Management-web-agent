import logging
import os
import requests
from typing import Tuple
from django.conf import settings
from .base import BaseSMSProvider

logger = logging.getLogger(__name__)

class SpugSMSProvider(BaseSMSProvider):
    """
    兼容现有 Spug 通道的短信发送器。
    从 Django settings 中获取 `SPUG_PUSH_URL` 和 `SPUG_PUSH_TOKEN` 进行鉴权与发送。
    """
    
    def __init__(self):
        self.base_url = getattr(
            settings, "SPUG_PUSH_URL", os.getenv("SPUG_PUSH_URL", "https://push.spug.cc")
        ).rstrip("/")
        self.token = getattr(settings, "SPUG_PUSH_TOKEN", "")
        self.app_name = getattr(settings, "SPUG_APP_NAME", os.getenv("SPUG_APP_NAME", "MTM用药助手"))
        self.timeout = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))

    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        if not template_code:
            return False, "SPUG_TEMPLATE_ID 未配置"

        url = f"{self.base_url}/send/{template_code}"
        # 假设 Spug 短信模板里需要的主要是验证码参数，名为 'code'
        code = template_params.get("code", "")
        
        payload = {
            "name": self.app_name,
            "targets": phone,
            "code": code,
        }
        # 将额外的模板参数合并进去（如果有的话）
        for k, v in template_params.items():
            if k not in payload:
                payload[k] = v

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        masked_phone = (
            (phone[:3] + "****" + phone[-4:]) if len(phone) == 11 else "[masked]"
        )
        masked_payload = {**payload, "code": "****", "targets": masked_phone}
        
        logger.info(f"调用Spug发送验证码: url={url}, payload={masked_payload}")

        try:
            r = requests.post(url, data=payload, headers=headers, timeout=self.timeout)
            logger.info(f"Spug响应: status={r.status_code}, text={r.text[:200]}")
            r.raise_for_status()
            return True, r.text
        except Exception as e:
            logger.error(f"Spug 短信发送失败: {str(e)}")
            return False, f"Request Failed: {str(e)}"
