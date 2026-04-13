from django.apps import AppConfig


class RecordsConfig(AppConfig):
    """
    用药记录应用配置类
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.records"
    verbose_name = "用药记录"

    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.records.signals  # noqa F401
        except ImportError:
            pass
