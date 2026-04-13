from django.apps import AppConfig


class MedicinesConfig(AppConfig):
    """
    药品应用配置类
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.medicines"
    verbose_name = "药品管理"

    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 信号处理器将在需要时添加
        pass
