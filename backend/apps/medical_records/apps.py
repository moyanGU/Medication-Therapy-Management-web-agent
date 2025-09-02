from django.apps import AppConfig


class MedicalRecordsConfig(AppConfig):
    """
    就医记录应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medical_records'
    verbose_name = '就医记录'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            import apps.medical_records.signals  # noqa F401
        except ImportError:
            pass