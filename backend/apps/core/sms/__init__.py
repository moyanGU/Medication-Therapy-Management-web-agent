from .gateway import SMSGateway

def send_sms(phone: str, template_code: str, template_params: dict):
    """
    统一短信发送入口
    :param phone: 手机号
    :param template_code: 模板编码/ID
    :param template_params: 模板变量
    :return: Tuple[bool, str]
    """
    return SMSGateway.send(phone, template_code, template_params)
