import logging
import json
from typing import Tuple
from django.conf import settings
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models

from .base import BaseSMSProvider

logger = logging.getLogger(__name__)

class AliyunSMSProvider(BaseSMSProvider):
    """阿里云短信服务提供商"""
    
    def __init__(self):
        self.access_key_id = getattr(settings, "ALIYUN_ACCESS_KEY_ID", "")
        self.access_key_secret = getattr(settings, "ALIYUN_ACCESS_KEY_SECRET", "")
        self.sign_name = getattr(settings, "ALIYUN_SMS_SIGN_NAME", "")
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("缺少阿里云短信必要配置: ALIYUN_ACCESS_KEY_ID 或 ALIYUN_ACCESS_KEY_SECRET")
            
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = 'dysmsapi.aliyuncs.com'
        self.client = Dysmsapi20170525Client(config)

    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        if not self.sign_name:
            return False, "未配置 ALIYUN_SMS_SIGN_NAME"
            
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=self.sign_name,
            template_code=template_code,
            template_param=json.dumps(template_params)
        )
        runtime = util_models.RuntimeOptions()
        
        try:
            response = self.client.send_sms_with_options(send_sms_request, runtime)
            body = response.body
            if body.code == 'OK':
                return True, body.biz_id or "OK"
            else:
                logger.error(f"阿里云短信发送失败: Code={body.code}, Message={body.message}")
                return False, body.message
        except Exception as error:
            logger.error(f"阿里云短信请求异常: {str(error)}")
            return False, str(error)
