"""字段级加密实现"""

import base64
import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger("mtm_helper")


def get_encryption_key():
    """
    获取或生成加密密钥
    优先使用 settings.ENCRYPTION_KEY，如果未设置则从 SECRET_KEY 派生
    """
    key = getattr(settings, "ENCRYPTION_KEY", None)
    if key:
        return key

    # 从 SECRET_KEY 派生一个 Fernet 密钥 (需要 32 url-safe base64-encoded bytes)
    secret = settings.SECRET_KEY
    # 简单的派生逻辑，生产环境建议配置独立的 ENCRYPTION_KEY
    if len(secret) < 32:
        secret = secret.ljust(32, "0")
    key_bytes = secret[:32].encode("utf-8")
    return base64.urlsafe_b64encode(key_bytes)


class EncryptedTextField(models.TextField):
    """
    加密文本字段
    存储时自动加密，读取时自动解密
    """

    description = "Encrypted Text Field"

    def __init__(self, *args, **kwargs):
        self._cipher = None
        super().__init__(*args, **kwargs)

    def _get_cipher(self):
        if self._cipher is not None:
            return self._cipher

        try:
            from cryptography.fernet import Fernet

            self._cipher = Fernet(get_encryption_key())
            return self._cipher
        except Exception as exc:
            if getattr(settings, "IS_TESTING", False):
                logger.warning(
                    "EncryptedTextField fallback enabled during tests: %s", exc
                )
                self._cipher = _PassthroughCipher()
                return self._cipher
            raise

    def get_prep_value(self, value):
        """
        准备存入数据库的值：加密
        """
        value = super().get_prep_value(value)
        if value is None or value == "":
            return value
        
        # 如果已经是 bytes，先解码为字符串（虽然通常这里是 str）
        if isinstance(value, bytes):
            value = value.decode('utf-8')
            
        encrypted_value = self._get_cipher().encrypt(value.encode("utf-8"))
        return encrypted_value.decode("utf-8")

    def from_db_value(self, value, expression, connection):
        """
        从数据库读取的值：解密
        """
        if value is None or value == "":
            return value

        try:
            decrypted_value = self._get_cipher().decrypt(value.encode("utf-8"))
            return decrypted_value.decode("utf-8")
        except Exception:
            # 如果解密失败（可能是旧数据未加密），返回原始值
            # 这是一个简单的迁移策略，允许逐渐过渡
            return value

    def to_python(self, value):
        """
        转换为 Python 对象
        """
        if value is None:
            return value
        return value


class _PassthroughCipher:
    def encrypt(self, value):
        return value

    def decrypt(self, value):
        return value
