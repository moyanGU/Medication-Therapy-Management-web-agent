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

        try:
            db_timeout = min(float(getattr(settings, "DB_CONNECT_TIMEOUT", 5)), 1.0)

            def _db_check():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True

            ok, _, err = _run_with_timeout(_db_check, db_timeout)
            if ok:
                health_status["services"]["database"] = "healthy"
            else:
                health_status["services"]["database"] = "unhealthy"
                health_status["status"] = "degraded"
                logger.error(f"数据库健康检查失败: {err}")
        except Exception as e:
            health_status["services"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
            logger.error(f"数据库健康检查异常: {e}")

        try:
            if not _redis_tcp_probe():
                health_status["services"]["cache"] = "unhealthy"
                health_status["status"] = "degraded"
            else:
                cache_timeout = min(
                    float(getattr(settings, "REDIS_SOCKET_TIMEOUT", 2)), 0.5
                )

                def _cache_check():
                    cache.set("health_check", "ok", 10)
                    return cache.get("health_check")

                ok, value, err = _run_with_timeout(_cache_check, cache_timeout)
                if ok and value == "ok":
                    health_status["services"]["cache"] = "healthy"
                else:
                    health_status["services"]["cache"] = "unhealthy"
                    health_status["status"] = "degraded"
                    if err:
                        logger.error(f"缓存健康检查失败: {err}")
        except Exception as e:
            logger.error(f"缓存健康检查异常: {e}")
            health_status["services"]["cache"] = "unhealthy"
            health_status["status"] = "degraded"

        if all(service == "unhealthy" for service in health_status["services"].values()):
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

        details["env"] = {
            "python_version": _sys.version,
            "debug": bool(getattr(_settings, "DEBUG", False)),
            "django_settings_module": getattr(_sys.modules.get("os"), "environ", {}).get(
                "DJANGO_SETTINGS_MODULE", "mtm_helper.settings"
            ),
        }

        try:
            import django as _dj

            details["dependencies"]["django"] = _dj.get_version()
        except Exception:
            problems.append("Django 未安装或版本不可用")

        try:
            import rest_framework as _drf

            details["dependencies"]["drf"] = getattr(_drf, "__version__", "available")
        except Exception:
            problems.append("Django REST Framework 未安装")

        try:
            import corsheaders as _ch

            details["dependencies"]["corsheaders"] = getattr(_ch, "__version__", "available")
        except Exception:
            problems.append("django-cors-headers 未安装")

        try:
            import pywebpush as _pwp

            details["dependencies"]["pywebpush"] = getattr(_pwp, "__version__", "available")
        except Exception:
            details["dependencies"]["pywebpush"] = "missing"

        try:
            db_timeout = min(float(getattr(settings, "DB_CONNECT_TIMEOUT", 5)), 1.0)

            def _db_check():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True

            ok, _, err = _run_with_timeout(_db_check, db_timeout)
            if ok:
                details["database"] = {"status": "healthy"}
            else:
                details["database"] = {"status": "unhealthy", "error": err}
                problems.append("数据库连接失败")
        except Exception as e:
            details["database"] = {"status": "unhealthy", "error": str(e)}
            problems.append("数据库连接异常")

        try:
            if not _redis_tcp_probe():
                details["cache"] = {"status": "unhealthy", "error": "tcp probe failed"}
                problems.append("Redis 不可达")
            else:
                details["cache"] = {"status": "healthy"}
        except Exception as e:
            details["cache"] = {"status": "unhealthy", "error": str(e)}
            problems.append("Redis 探活异常")

        notifications = {}
        if getattr(settings, "VAPID_PRIVATE_KEY", None):
            notifications["webpush"] = "configured"
        else:
            notifications["webpush"] = "missing"
            problems.append("WebPush 未配置 VAPID_PRIVATE_KEY")

        spug_enabled = bool(getattr(settings, "SPUG_PUSH_ENABLED", False))
        notifications["sms"] = "configured" if spug_enabled else "disabled"
        details["notifications"] = notifications

        return Response(
            {
                "success": True,
                "message": "ok",
                "data": {"problems": problems, "details": details},
            }
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

