"""MTM-用药助手 URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse
from apps.reminders.views import ReminderViewSet

# API路由配置
api_urlpatterns = [
    path('', include('apps.core.urls')),
    path('auth/', include('apps.authentication.urls')),
    path('medicines/', include('apps.medicines.urls')),
    path('records/', include('apps.records.urls')),
    path('reminders/', include('apps.reminders.urls')),
    # 别名路由：映射到 ReminderViewSet 对应动作，避免双重前缀导致的404
    path('reminders/today/', ReminderViewSet.as_view({'get': 'today'}), name='reminders-today'),
    path('reminders/stats/', ReminderViewSet.as_view({'get': 'stats'}), name='reminders-stats'),
    path('reminders/upcoming/', ReminderViewSet.as_view({'get': 'upcoming'}), name='reminders-upcoming'),
    path('reminders/active/', ReminderViewSet.as_view({'get': 'active'}), name='reminders-active'),
    path('reminders/expired/', ReminderViewSet.as_view({'get': 'expired'}), name='reminders-expired'),
    path('medical-records/', include('apps.medical_records.urls')),
]

from apps.core.views import api_docs


def favicon_view(request):
    """
    开发环境内联返回一个简单的 SVG favicon，避免浏览器自动请求 /favicon.ico 产生 404。

    Returns:
        HttpResponse: 内联 SVG 图标响应
    """
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="12" fill="#2563eb"/>'
        '<path d="M18 34l10 10 18-24" stroke="#fff" stroke-width="6" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    )
    return HttpResponse(svg, content_type='image/svg+xml')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    # 根路径显示API文档
    path('', api_docs, name='root'),
    # 提供 favicon，避免浏览器控制台 404 噪音
    path('favicon.ico', favicon_view, name='favicon'),
    path('favicon.svg', favicon_view),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)