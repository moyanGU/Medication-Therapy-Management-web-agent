from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    用户应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户管理'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.users.signals  # noqa F401
        except ImportError:
            pass