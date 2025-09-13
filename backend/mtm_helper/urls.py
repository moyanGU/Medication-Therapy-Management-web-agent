"""MTM-用药助手 URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from apps.core.views import api_docs
from apps.reminders.views import ReminderViewSet

# API路由配置（注意顺序）
api_urlpatterns = [
    path('auth/', include('apps.authentication.urls')),
    path('records/', include('apps.records.urls')),
    path('medical-records/', include('apps.medical_records.urls')),
    # 用户资料接口：/api/user/profile
    path('user/', include('apps.users.urls')),
    # 新增：挂载药品管理路由，修复 /api/medicines/ 404
    path('medicines/', include('apps.medicines.urls')),
    # 显式别名：确保 /api/reminders/ 与 /api/reminders/<pk>/ 支持 POST/PUT/PATCH/DELETE
    # 必须放在 include('apps.reminders.urls') 之前，避免被 DRF Router 根视图拦截导致 405
    path('reminders/', ReminderViewSet.as_view({'get': 'list', 'post': 'create'}), name='reminders-list-create'),
    path('reminders/<int:pk>/', ReminderViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='reminders-detail'),
    path('reminders/today/', ReminderViewSet.as_view({'get': 'today'}), name='reminders-today'),
    path('reminders/stats/', ReminderViewSet.as_view({'get': 'stats'}), name='reminders-stats'),
    path('reminders/upcoming/', ReminderViewSet.as_view({'get': 'upcoming'}), name='reminders-upcoming'),
    # 显式注册批量切换激活状态的路由，避免 Router 未注册导致 404
    path('reminders/batch_toggle/', ReminderViewSet.as_view({'post': 'batch_toggle'}), name='reminders-batch-toggle'),
    # 其余 reminders 路由（history、扩展 action 等）
    path('reminders/', include('apps.reminders.urls')),
    path('plans/', include('apps.plans.urls')),
]


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


# 单一定义的 URL 列表
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    # 根路径显示API文档
    path('', api_docs, name='root'),
    # 提供 favicon，避免浏览器控制台 404 噪音
    path('favicon.ico', favicon_view, name='favicon'),
    path('favicon.svg', favicon_view),
]

# 开发环境下提供媒体与静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)