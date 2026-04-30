"""核心应用配置"""

import importlib
import logging
import socket
from urllib.parse import urlparse

from django.apps import AppConfig


logger = logging.getLogger("mtm_helper")


def _extract_redis_host_port():
    from django.conf import settings

    loc = getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION")
    if isinstance(loc, (list, tuple)):
        loc = loc[0] if loc else None
    if not isinstance(loc, str) or not loc:
        return None
    parsed = urlparse(loc)
    host = parsed.hostname
    port = parsed.port
    if not host or not port:
        return None
    return host, int(port)


def _probe_socket(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except Exception:
        return False


class CoreConfig(AppConfig):
    """
    核心应用配置类
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "核心模块"

    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            importlib.import_module("apps.core.signals")
        except ImportError:
            pass

        # 执行其他初始化操作
        self._setup_logging()
        self._check_cache_connection()

    def _setup_logging(self):
        """
        设置日志配置
        """
        import logging
        import os

        from django.conf import settings

        # 确保日志目录存在
        log_dir = settings.BASE_DIR / "logs"
        os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger("mtm_helper")
        logger.info("核心应用初始化完成")

    def _check_cache_connection(self):
        """
        检查缓存连接
        """
        try:
            from django.conf import settings
            from django.core.cache import cache

            backend = getattr(settings, "CACHES", {}).get("default", {}).get("BACKEND", "")
            if "django_redis" in str(backend):
                hp = _extract_redis_host_port()
                if hp and not _probe_socket(hp[0], hp[1]):
                    logger.warning("Redis缓存连接异常: Redis 不可用，启动阶段跳过连通性检查")
                    return

            cache.get("test_key")
            logger.info("Redis缓存连接正常")
        except Exception as e:
            logger.warning(f"Redis缓存连接异常: {e}")
