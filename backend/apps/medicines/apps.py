from django.apps import AppConfig


class MedicinesConfig(AppConfig):
    """
    药品应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medicines'
    verbose_name = '药品管理'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.medicines.signals  # noqa F401
        except ImportError:
            pass