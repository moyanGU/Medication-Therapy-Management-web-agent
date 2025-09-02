from django.apps import AppConfig


class PlansConfig(AppConfig):
    """
    用药计划应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.plans'
    verbose_name = '用药计划'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.plans.signals  # noqa F401
        except ImportError:
            pass