import logging
import json
from typing import Tuple
from django.conf import settings

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models

from .base import BaseSMSProvider

logger = logging.getLogger(__name__)

class TencentSMSProvider(BaseSMSProvider):
    """腾讯云短信服务提供商"""
    
    def __init__(self):
        self.secret_id = getattr(settings, "TENCENT_SECRET_ID", "")
        self.secret_key = getattr(settings, "TENCENT_SECRET_KEY", "")
        self.sms_app_id = getattr(settings, "TENCENT_SMS_APP_ID", "")
        self.sign_name = getattr(settings, "TENCENT_SMS_SIGN_NAME", "")
        
        if not self.secret_id or not self.secret_key or not self.sms_app_id:
            raise ValueError("缺少腾讯云短信必要配置: TENCENT_SECRET_ID, TENCENT_SECRET_KEY, 或 TENCENT_SMS_APP_ID")
            
        cred = credential.Credential(self.secret_id, self.secret_key)
        self.client = sms_client.SmsClient(cred, "ap-guangzhou")

    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        if not self.sign_name:
            return False, "未配置 TENCENT_SMS_SIGN_NAME"
            
        try:
            req = models.SendSmsRequest()
            
            # 腾讯云要求手机号以 +86 开头
            if not phone.startswith("+"):
                phone = f"+86{phone}"
                
            req.PhoneNumberSet = [phone]
            req.SmsSdkAppId = self.sms_app_id
            req.SignName = self.sign_name
            req.TemplateId = template_code
            
            # 腾讯云 SDK 模板参数为列表形式，需确保按模板定义的顺序传入
            # 这里简单将字典的 value 转为 list，但实际使用时通常需要保持顺序
            # 推荐在外层包装时按照参数位置传递列表，如果传入 dict 则默认按 key 排序（可能有风险）
            if isinstance(template_params, dict):
                req.TemplateParamSet = [str(v) for k, v in sorted(template_params.items())]
            elif isinstance(template_params, list):
                req.TemplateParamSet = [str(v) for v in template_params]
            else:
                req.TemplateParamSet = []
                
            resp = self.client.SendSms(req)
            
            # SendStatusSet[0] 表示第一个手机号的发送结果
            if resp.SendStatusSet and len(resp.SendStatusSet) > 0:
                status = resp.SendStatusSet[0]
                if status.Code == "Ok":
                    return True, status.SerialNo or "OK"
                else:
                    logger.error(f"腾讯云短信发送失败: Code={status.Code}, Message={status.Message}")
                    return False, status.Message
            return False, "腾讯云返回了空的发送结果"
            
        except TencentCloudSDKException as err:
            logger.error(f"腾讯云短信请求异常: {str(err)}")
            return False, str(err)
        except Exception as e:
            logger.error(f"腾讯云短信未知异常: {str(e)}")
            return False, str(e)
