from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    认证应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = '用户认证'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.authentication.signals  # noqa F401
        except ImportError:
            pass