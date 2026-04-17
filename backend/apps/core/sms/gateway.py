import logging
from django.conf import settings
from .mock import MockSMSProvider

logger = logging.getLogger(__name__)

class SMSGateway:
    """短信网关，负责根据配置实例化对应的提供商并路由请求"""
    
    _provider = None
    
    @classmethod
    def get_provider(cls):
        if cls._provider is not None:
            return cls._provider
            
        provider_name = getattr(settings, "SMS_PROVIDER", "mock").lower()
        
        try:
            if provider_name == "aliyun":
                from .aliyun import AliyunSMSProvider
                cls._provider = AliyunSMSProvider()
            elif provider_name == "tencent":
                from .tencent import TencentSMSProvider
                cls._provider = TencentSMSProvider()
            elif provider_name == "spug":
                from .spug import SpugSMSProvider
                cls._provider = SpugSMSProvider()
            else:
                cls._provider = MockSMSProvider()
        except Exception as e:
            logger.error(f"初始化 SMS Provider '{provider_name}' 失败: {str(e)}，自动降级为 Mock")
            cls._provider = MockSMSProvider()
            
        return cls._provider

    @classmethod
    def send(cls, phone: str, template_code: str, template_params: dict):
        provider = cls.get_provider()
        return provider.send(phone, template_code, template_params)
