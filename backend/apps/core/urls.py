"""核心应用URL配置"""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from . import views

app_name = "core"

urlpatterns = [
    # 健康检查相关
    path("health/", views.health_check, name="health_check"),
    path("ping/", views.ping, name="ping"),
    path("system-info/", views.system_info, name="system_info"),
    path("diagnostics/", views.diagnostics, name="diagnostics"),
    path("dashboard/summary/", views.dashboard_summary, name="dashboard_summary"),
    # API文档
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url="/api/schema/"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url="/api/schema/"),
        name="redoc",
    ),
    path("docs/", views.api_docs, name="api_docs"),
    # AI
    path(
        "ai/medication-guidance/",
        views.medication_guidance,
        name="ai_medication_guidance",
    ),
    path(
        "ai/page-agent/chat/completions/",
        views.page_agent_chat_completions,
        name="ai_page_agent_chat_completions",
    ),
    path(
        "ai/page-agent/chat/completions",
        views.page_agent_chat_completions,
        name="ai_page_agent_chat_completions_no_slash",
    ),
    path(
        "ai/session-memory/",
        views.session_memory,
        name="ai_session_memory",
    ),
    path(
        "ai/session-memory/summarize/",
        views.session_memory_summarize,
        name="ai_session_memory_summarize",
    ),
    path(
        "ai/permissions/",
        views.agent_permission_matrix,
        name="ai_agent_permissions",
    ),
    # 管理功能
    path("clear-cache/", views.clear_cache, name="clear_cache"),
]
