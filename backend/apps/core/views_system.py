"""核心应用系统视图"""

import logging
import socket
import threading
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .utils import error_response, success_response

logger = logging.getLogger("mtm_helper")


def _set_service_status(health_status: dict, service: str, ok: bool, err: str | None = None):
    health_status["services"][service] = "healthy" if ok else "unhealthy"
    if not ok:
        health_status["status"] = "degraded"
        if err:
            logger.error(f"{service} 健康检查失败: {err}")


def _db_health_check():
    db_timeout = min(float(getattr(settings, "DB_CONNECT_TIMEOUT", 5)), 1.0)

    def _db_check():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True

    ok, _, err = _run_with_timeout(_db_check, db_timeout)
    return ok, err


def _cache_health_check():
    if not _redis_tcp_probe():
        return False, "tcp probe failed"

    cache_timeout = min(float(getattr(settings, "REDIS_SOCKET_TIMEOUT", 2)), 0.5)

    def _cache_check():
        cache.set("health_check", "ok", 10)
        return cache.get("health_check")

    ok, value, err = _run_with_timeout(_cache_check, cache_timeout)
    return bool(ok and value == "ok"), err


def _is_all_services_unhealthy(services: dict) -> bool:
    return all(service == "unhealthy" for service in services.values())


def _safe_get_module_version(importer, module_name: str, default=None):
    try:
        mod = importer(module_name)
        return getattr(mod, "__version__", "available")
    except Exception:
        return default


def _safe_get_django_version(importer):
    try:
        dj = importer("django")
        return dj.get_version()
    except Exception:
        return None


def _build_diagnostics_env(_sys, _settings):
    return {
        "python_version": _sys.version,
        "debug": bool(getattr(_settings, "DEBUG", False)),
        "django_settings_module": getattr(_sys.modules.get("os"), "environ", {}).get(
            "DJANGO_SETTINGS_MODULE", "mtm_helper.settings"
        ),
    }


def _collect_dependency_versions(importer, problems: list[str]):
    dependencies = {}
    django_version = _safe_get_django_version(importer)
    if django_version is None:
        problems.append("Django 未安装或版本不可用")
    else:
        dependencies["django"] = django_version

    drf_version = _safe_get_module_version(importer, "rest_framework")
    if drf_version is None:
        problems.append("Django REST Framework 未安装")
    else:
        dependencies["drf"] = drf_version

    cors_version = _safe_get_module_version(importer, "corsheaders")
    if cors_version is None:
        problems.append("django-cors-headers 未安装")
    else:
        dependencies["corsheaders"] = cors_version

    dependencies["pywebpush"] = (
        _safe_get_module_version(importer, "pywebpush", default="missing") or "missing"
    )
    return dependencies


def _collect_database_diagnostics(problems: list[str]):
    db_ok, db_err = _db_health_check()
    if db_ok:
        return {"status": "healthy"}
    problems.append("数据库连接失败")
    return {"status": "unhealthy", "error": db_err}


def _collect_cache_diagnostics(problems: list[str]):
    try:
        cache_ok = _redis_tcp_probe()
        payload = {"status": "healthy" if cache_ok else "unhealthy"}
        if not cache_ok:
            payload["error"] = "tcp probe failed"
            problems.append("Redis 不可达")
        return payload
    except Exception as e:
        problems.append("Redis 探活异常")
        return {"status": "unhealthy", "error": str(e)}


def _collect_notification_diagnostics(problems: list[str]):
    notifications = {}
    if getattr(settings, "VAPID_PRIVATE_KEY", None):
        notifications["webpush"] = "configured"
    else:
        notifications["webpush"] = "missing"
        problems.append("WebPush 未配置 VAPID_PRIVATE_KEY")

    spug_enabled = bool(getattr(settings, "SPUG_PUSH_ENABLED", False))
    template_id = str(getattr(settings, "SPUG_TEMPLATE_ID", "") or "").strip()
    spug_url = str(getattr(settings, "SPUG_PUSH_URL", "") or "").strip()
    spug_token = str(getattr(settings, "SPUG_PUSH_TOKEN", "") or "").strip()
    timeout_seconds = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3) or 3)

    if spug_enabled and not template_id:
        problems.append("SPUG_PUSH_ENABLED 已开启但缺少 SPUG_TEMPLATE_ID")

    notifications["sms_spug"] = {
        "enabled": spug_enabled,
        "template_configured": bool(template_id),
        "url": spug_url,
        "token_configured": bool(spug_token),
        "timeout_seconds": timeout_seconds,
    }
    return notifications


def _run_with_timeout(func, timeout_seconds: float):
    result = {"ok": False, "value": None, "error": None}

    def _target():
        try:
            result["value"] = func()
            result["ok"] = True
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout_seconds)
    if t.is_alive():
        return False, None, "timeout"
    if result["ok"]:
        return True, result["value"], None
    return False, None, result["error"] or "error"


def _parse_redis_host_port_from_cache():
    try:
        cache_config = getattr(settings, "CACHES", {}).get("default", {})
        loc = cache_config.get("LOCATION")
        if isinstance(loc, (list, tuple)):
            loc = loc[0] if loc else None
        if not isinstance(loc, str) or not loc:
            return None
        parsed = urlparse(loc)
        if not parsed.hostname or not parsed.port:
            return None
        return parsed.hostname, int(parsed.port)
    except Exception:
        return None


def _redis_tcp_probe(timeout_seconds: float = 0.2) -> bool:
    hp = _parse_redis_host_port_from_cache()
    if not hp:
        return False
    host, port = hp
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except Exception:
        return False


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "services": {
            "database": "unknown",
            "cache": "unknown",
            "application": "healthy",
        },
        "version": "1.0.0",
    }

    try:
        health_status["timestamp"] = datetime.now().isoformat()

        db_ok, db_err = _db_health_check()
        _set_service_status(health_status, "database", db_ok, db_err)

        cache_ok, cache_err = _cache_health_check()
        _set_service_status(health_status, "cache", cache_ok, cache_err)

        if _is_all_services_unhealthy(health_status["services"]):
            health_status["status"] = "unhealthy"

        status_code = 200 if health_status["status"] == "healthy" else 503

        return Response(
            {"success": True, "data": health_status, "message": "健康检查完成"},
            status=status_code,
        )
    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        return Response(
            {
                "success": False,
                "data": {"status": "unhealthy", "error": str(e)},
                "message": "健康检查失败",
            },
            status=500,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def diagnostics(request):
    problems = []
    details = {
        "env": {},
        "dependencies": {},
        "database": {},
        "cache": {},
        "notifications": {},
    }

    try:
        import sys as _sys

        from django.conf import settings as _settings
        importer = __import__

        details["env"] = _build_diagnostics_env(_sys, _settings)
        details["dependencies"] = _collect_dependency_versions(importer, problems)
        details["database"] = _collect_database_diagnostics(problems)
        details["cache"] = _collect_cache_diagnostics(problems)
        details["notifications"] = _collect_notification_diagnostics(problems)

        diagnostics_payload = {
            "env": details.get("env") or {},
            "dependencies": details.get("dependencies") or {},
            "database": details.get("database") or {},
            "cache": details.get("cache") or {},
            "notifications": details.get("notifications") or {},
        }

        status_code = 206 if problems else 200
        return Response(
            {
                "success": True,
                "message": "ok",
                "data": {
                    "diagnostics": diagnostics_payload,
                    "problems": problems,
                    "details": details,
                },
            },
            status=status_code,
        )
    except Exception as e:
        logger.error(f"系统诊断异常: {e}")
        return Response(
            {"success": False, "message": str(e), "data": {"problems": ["诊断执行失败"]}},
            status=500,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def system_info(request):
    try:
        import platform
        import sys

        from django import get_version

        system_info_payload = {
            "application": {
                "name": "MTM-用药助手",
                "version": "1.0.0",
                "environment": "development" if settings.DEBUG else "production",
            },
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "django_version": get_version(),
            },
            "database": {"engine": "MySQL", "version": None},
            "cache": {"backend": "Redis", "version": None},
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                db_version = cursor.fetchone()[0]
                system_info_payload["database"]["version"] = db_version
        except Exception as e:
            logger.warning(f"获取数据库版本失败: {e}")

        try:
            import redis

            cache_config = settings.CACHES["default"]
            location = cache_config["LOCATION"]
            if isinstance(location, str) and location.startswith("redis://"):
                import re

                match = re.match(r"redis://(?::([^@]+)@)?([^:]+):([^/]+)/(.+)", location)
                if match:
                    password, host, port, db = match.groups()
                    r = redis.Redis(host=host, port=int(port), db=int(db), password=password)
                    redis_info = r.info()
                    system_info_payload["cache"]["version"] = redis_info.get("redis_version")
        except Exception as e:
            logger.warning(f"获取Redis版本失败: {e}")

        return success_response(system_info_payload, "系统信息获取成功")
    except Exception as e:
        logger.error(f"获取系统信息异常: {e}")
        return error_response("系统信息获取失败", "SYSTEM_INFO_ERROR", 500)


@csrf_exempt
@require_http_methods(["GET"])
def ping(request):
    return JsonResponse(
        {
            "success": True,
            "data": {"message": "pong", "timestamp": datetime.now().isoformat()},
            "message": "服务正常",
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_docs(request):
    docs_info = {
        "title": "MTM-用药助手 API Documentation",
        "version": "1.0.0",
        "description": "MTM-用药助手药品管理系统API文档",
        "base_url": request.build_absolute_uri("/api/"),
        "endpoints": {
            "authentication": {
                "login": "POST /api/auth/login/",
                "register": "POST /api/auth/register/",
                "refresh": "POST /api/auth/refresh/",
                "logout": "POST /api/auth/logout/",
            },
            "user": {
                "profile": "GET /api/user/profile/",
                "update_profile": "PUT /api/user/profile/",
                "change_password": "POST /api/user/change-password/",
            },
            "medicines": {
                "list": "GET /api/medicines/",
                "create": "POST /api/medicines/",
                "detail": "GET /api/medicines/{id}/",
                "update": "PUT /api/medicines/{id}/",
                "delete": "DELETE /api/medicines/{id}/",
                "search": "GET /api/medicines/search/",
            },
            "records": {
                "list": "GET /api/records/medication-records/",
                "create": "POST /api/records/medication-records/",
                "detail": "GET /api/records/medication-records/{id}/",
                "update": "PUT /api/records/medication-records/{id}/",
                "delete": "DELETE /api/records/medication-records/{id}/",
                "statistics": "GET /api/records/medication-records/statistics/",
                "trends": "GET /api/records/medication-records/trends/",
                "export": "GET /api/records/medication-records/export/",
                "recent": "GET /api/records/medication-records/recent/",
            },
            "reminders": {
                "list": "GET /api/reminders/",
                "create": "POST /api/reminders/",
                "detail": "GET /api/reminders/{id}/",
                "update": "PUT /api/reminders/{id}/",
                "delete": "DELETE /api/reminders/{id}/",
                "today": "GET /api/reminders/today/",
                "stats": "GET /api/reminders/stats/",
                "upcoming": "GET /api/reminders/upcoming/",
            },
            "ai": {
                "medication_guidance": "POST /api/ai/medication-guidance/",
            },
        },
    }
    return success_response(docs_info, "API文档获取成功")


@api_view(["POST"])
def clear_cache(request):
    if not request.user.is_staff:
        return error_response("权限不足", "PERMISSION_DENIED", 403)

    try:
        cache.clear()
        logger.info(f"管理员 {request.user.username} 清除了所有缓存")
        return success_response(None, "缓存清除成功")
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return error_response("缓存清除失败", "CACHE_CLEAR_ERROR", 500)
