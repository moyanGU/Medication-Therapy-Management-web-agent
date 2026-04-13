from django.apps import AppConfig


class RemindersConfig(AppConfig):
    """
    用药提醒应用配置类
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reminders"
    verbose_name = "用药提醒"

    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.reminders.signals  # noqa F401
        except ImportError:
            pass
