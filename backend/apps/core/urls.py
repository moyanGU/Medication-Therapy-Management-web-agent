"""核心应用URL配置"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 健康检查相关
    path('health/', views.health_check, name='health_check'),
    path('ping/', views.ping, name='ping'),
    path('system-info/', views.system_info, name='system_info'),
    path('diagnostics/', views.diagnostics, name='diagnostics'),
    
    # API文档
    path('docs/', views.api_docs, name='api_docs'),
    
    # 管理功能
    path('clear-cache/', views.clear_cache, name='clear_cache'),
]
