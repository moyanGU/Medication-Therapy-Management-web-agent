"""核心应用配置"""

import importlib

from django.apps import AppConfig


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
            import socket
            from urllib.parse import urlparse

            from django.conf import settings
            from django.core.cache import cache

            backend = (
                getattr(settings, "CACHES", {}).get("default", {}).get("BACKEND", "")
            )
            if "django_redis" in str(backend):
                loc = getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION")
                if isinstance(loc, (list, tuple)):
                    loc = loc[0] if loc else None
                parsed = urlparse(loc) if isinstance(loc, str) else None
                host = parsed.hostname if parsed else None
                port = parsed.port if parsed else None
                if host and port:
                    try:
                        with socket.create_connection((host, int(port)), timeout=0.2):
                            pass
                    except Exception:
                        import logging

                        logger = logging.getLogger("mtm_helper")
                        logger.warning("Redis缓存连接异常: Redis 不可用，启动阶段跳过连通性检查")
                        return

            cache.get("test_key")

            import logging

            logger = logging.getLogger("mtm_helper")
            logger.info("Redis缓存连接正常")
        except Exception as e:
            import logging

            logger = logging.getLogger("mtm_helper")
            logger.warning(f"Redis缓存连接异常: {e}")
