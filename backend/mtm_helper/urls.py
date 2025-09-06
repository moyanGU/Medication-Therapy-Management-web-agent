"""MTM-用药助手 URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# API路由配置
api_urlpatterns = [
    path('', include('apps.core.urls')),
    path('auth/', include('apps.authentication.urls')),
    path('medicines/', include('apps.medicines.urls')),
    path('records/', include('apps.records.urls')),
    path('reminders/', include('apps.reminders.urls')),
    path('medical-records/', include('apps.medical_records.urls')),
    # 其他应用URL配置将在后续任务中添加
    # path('users/', include('apps.users.urls')),
    # path('plans/', include('apps.plans.urls')),
]

from apps.core.views import api_docs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    # 根路径显示API文档
    path('', api_docs, name='root'),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)