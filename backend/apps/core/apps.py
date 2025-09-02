"""核心应用配置"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    核心应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = '核心模块'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            from . import signals
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
        log_dir = settings.BASE_DIR / 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        logger = logging.getLogger('mtm_helper')
        logger.info('核心应用初始化完成')
    
    def _check_cache_connection(self):
        """
        检查缓存连接
        """
        try:
            from django.core.cache import cache
            cache.get('test_key')
            
            import logging
            logger = logging.getLogger('mtm_helper')
            logger.info('Redis缓存连接正常')
        except Exception as e:
            import logging
            logger = logging.getLogger('mtm_helper')
            logger.warning(f'Redis缓存连接异常: {e}')