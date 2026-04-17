from abc import ABC, abstractmethod
from typing import Tuple

class BaseSMSProvider(ABC):
    """短信服务提供商基类"""
    
    @abstractmethod
    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        """
        发送短信
        :param phone: 手机号
        :param template_code: 模板ID或编码
        :param template_params: 模板变量参数字典
        :return: (是否发送成功, 错误信息/响应回执)
        """
        pass
