"""核心应用视图"""

import json
import logging
import re
import socket
import threading
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .utils import error_response, success_response

logger = logging.getLogger("mtm_helper")


def _run_with_timeout(func, timeout_seconds: float):
    """在独立线程中执行函数并支持超时，超时返回 (False, None, "timeout")."""

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
    """从 Django CACHES 配置中解析 Redis host/port，解析失败返回 None。"""

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
    """使用 TCP 探活 Redis，避免 cache.get/set 在不可用时阻塞。"""

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
    """
    健康检查接口
    检查系统各组件的运行状态

    Returns:
        Response: 健康检查结果
    """
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
        from datetime import datetime

        health_status["timestamp"] = datetime.now().isoformat()

        # 检查数据库连接
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

        # 检查缓存连接
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

        # 如果所有服务都不健康，标记为不健康
        if all(
            service == "unhealthy" for service in health_status["services"].values()
        ):
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
    """
    系统诊断接口
    汇总环境、依赖、数据库、缓存与通知配置的诊断信息，并输出问题列表
    """
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
            "django_settings_module": getattr(
                _sys.modules.get("os"), "environ", {}
            ).get("DJANGO_SETTINGS_MODULE", "mtm_helper.settings"),
        }

        # 依赖检查
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

            details["dependencies"]["corsheaders"] = getattr(
                _ch, "__version__", "available"
            )
        except Exception:
            problems.append("django-cors-headers 未安装")

        try:
            import pywebpush as _pwp

            details["dependencies"]["pywebpush"] = getattr(
                _pwp, "__version__", "available"
            )
        except Exception:
            details["dependencies"]["pywebpush"] = "missing"

        # 数据库连接
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
            problems.append("数据库连接失败")

        # 缓存连接
        try:
            if not _redis_tcp_probe():
                details["cache"] = {"status": "unhealthy", "error": "redis unavailable"}
                problems.append("缓存连接失败")
            else:
                cache_timeout = min(
                    float(getattr(settings, "REDIS_SOCKET_TIMEOUT", 2)), 0.5
                )

                def _cache_check():
                    cache.set("diagnostics", "ok", 10)
                    return cache.get("diagnostics")

                ok, value, err = _run_with_timeout(_cache_check, cache_timeout)
                ok_rw = ok and value == "ok"
                details["cache"] = {"status": "healthy" if ok_rw else "degraded"}
                if not ok_rw:
                    problems.append("缓存读写失败")
                    if err:
                        details["cache"]["error"] = err
        except Exception as e:
            details["cache"] = {"status": "unhealthy", "error": str(e)}
            problems.append("缓存连接失败")

        # 通知配置检查
        vapid_private = getattr(_settings, "VAPID_PRIVATE_KEY", None)
        vapid_subject = getattr(_settings, "VAPID_SUBJECT", None)
        spug_enabled = bool(getattr(_settings, "SPUG_PUSH_ENABLED", False))
        spug_template = str(getattr(_settings, "SPUG_TEMPLATE_ID", "")).strip()
        spug_url = str(getattr(_settings, "SPUG_PUSH_URL", "https://push.spug.cc"))
        spug_token = str(getattr(_settings, "SPUG_PUSH_TOKEN", "")).strip()
        spug_timeout = int(getattr(_settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))
        details["notifications"] = {
            "webpush": {
                "vapid_private_key_configured": bool(vapid_private),
                "vapid_subject": bool(vapid_subject),
            },
            "sms_spug": {
                "enabled": spug_enabled,
                "template_configured": bool(spug_template),
                "url": spug_url,
                "token_configured": bool(spug_token),
                "timeout_seconds": spug_timeout,
            },
        }
        if not vapid_private:
            problems.append("缺少 VAPID_PRIVATE_KEY 配置，Web Push 将不可用")
        if spug_enabled and not spug_template:
            problems.append("SPUG_PUSH_ENABLED 已开启但缺少 SPUG_TEMPLATE_ID")

        status_code = 200 if not problems else 206
        return Response(
            {"success": True, "data": {"problems": problems, "diagnostics": details}},
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
    """
    系统信息接口
    返回系统基本信息

    Returns:
        Response: 系统信息
    """
    try:
        import platform
        import sys

        from django import get_version
        from django.conf import settings

        system_info = {
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

        # 获取数据库版本
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                db_version = cursor.fetchone()[0]
                system_info["database"]["version"] = db_version
        except Exception as e:
            logger.warning(f"获取数据库版本失败: {e}")

        # 获取Redis版本
        try:
            import redis
            from django.conf import settings as django_settings

            # 从缓存配置中获取Redis连接信息
            cache_config = django_settings.CACHES["default"]
            location = cache_config["LOCATION"]

            # 解析Redis连接URL
            if location.startswith("redis://"):
                import re

                match = re.match(
                    r"redis://(?::([^@]+)@)?([^:]+):([^/]+)/(.+)", location
                )
                if match:
                    password, host, port, db = match.groups()
                    r = redis.Redis(
                        host=host, port=int(port), db=int(db), password=password
                    )
                    redis_info = r.info()
                    system_info["cache"]["version"] = redis_info.get("redis_version")
        except Exception as e:
            logger.warning(f"获取Redis版本失败: {e}")

        return success_response(system_info, "系统信息获取成功")

    except Exception as e:
        logger.error(f"获取系统信息异常: {e}")
        return error_response("系统信息获取失败", "SYSTEM_INFO_ERROR", 500)


@csrf_exempt
@require_http_methods(["GET"])
def ping(request):
    """
    简单的ping接口
    用于快速检查服务是否可用

    Returns:
        JsonResponse: ping响应
    """
    from datetime import datetime

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
    """
    API文档接口
    返回API文档信息

    Returns:
        Response: API文档信息
    """
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
            # 与实际路由一致，使用 /api/user/profile/
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
            # 修正 records 文档端点，准确反映 DRF Router 挂载的 medication-records 子路由
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
    # 统一返回格式：success/data/message
    return success_response(docs_info, "API文档获取成功")


def _build_dashboard_adherence_summary(request):
    """
    复用 records 中的依从性聚合逻辑，生成首页摘要
    """
    from apps.records.views import MedicationRecordViewSet

    today = timezone.now().date()
    viewset = MedicationRecordViewSet()
    viewset.request = request

    summary_7d_start = today - timedelta(days=6)
    summary_30d_start = today - timedelta(days=29)

    summary_7d = viewset._build_adherence_summary(
        viewset._get_adherence_records_queryset(
            start_date=summary_7d_start,
            end_date=today,
        ),
        viewset._get_reminder_history_queryset(
            start_date=summary_7d_start,
            end_date=today,
        ),
    )
    summary_30d = viewset._build_adherence_summary(
        viewset._get_adherence_records_queryset(
            start_date=summary_30d_start,
            end_date=today,
        ),
        viewset._get_reminder_history_queryset(
            start_date=summary_30d_start,
            end_date=today,
        ),
    )

    return {
        "summary_7d": summary_7d,
        "summary_30d": summary_30d,
        "current_period": summary_7d,
    }


def _build_dashboard_today_tasks(reminders, processed_records, today):
    """
    构造首页今日任务摘要
    """
    processed_by_reminder = {}
    for record in processed_records:
        if record.reminder_id and record.reminder_id not in processed_by_reminder:
            processed_by_reminder[record.reminder_id] = record

    items = []
    completed = 0
    for reminder in reminders:
        record = processed_by_reminder.get(reminder.id)
        is_completed = record is not None
        if is_completed:
            completed += 1

        items.append(
            {
                "reminder_id": reminder.id,
                "medicine_id": reminder.medicine_id,
                "medicine_name": reminder.medicine.name,
                "title": reminder.title or f"{reminder.medicine.name} 用药提醒",
                "reminder_time": reminder.reminder_time.strftime("%H:%M"),
                "dosage": reminder.dosage,
                "dosage_unit": reminder.dosage_unit,
                "meal_timing": reminder.meal_timing,
                "is_completed": is_completed,
                "record_status": record.status if record else None,
                "scheduled_date": today.isoformat(),
            }
        )

    return {
        "date": today.isoformat(),
        "total": len(items),
        "completed": completed,
        "pending": max(len(items) - completed, 0),
        "items": items,
    }


def _build_dashboard_risk_alerts(
    low_stock_items, expiring_soon_items, followup_due_items, adherence_summary
):
    """
    构造首页风险提醒列表
    """
    alerts = []

    if low_stock_items:
        alerts.append(
            {
                "type": "low_stock",
                "level": "medium",
                "title": "库存偏低",
                "count": len(low_stock_items),
                "message": f"有 {len(low_stock_items)} 种药品库存偏低，建议尽快补充",
            }
        )

    if expiring_soon_items:
        alerts.append(
            {
                "type": "expiring_soon",
                "level": "medium",
                "title": "药品临期",
                "count": len(expiring_soon_items),
                "message": f"有 {len(expiring_soon_items)} 种药品将在 30 天内到期",
            }
        )

    if followup_due_items:
        alerts.append(
            {
                "type": "followup_due",
                "level": "high",
                "title": "复诊到期",
                "count": len(followup_due_items),
                "message": f"有 {len(followup_due_items)} 条复诊已到期，建议尽快安排就诊",
            }
        )

    summary_7d = adherence_summary["summary_7d"]
    if summary_7d["total_records"] > 0 and summary_7d["risk_level"] in ["medium", "high"]:
        alerts.append(
            {
                "type": "adherence_risk",
                "level": summary_7d["risk_level"],
                "title": "依从性风险",
                "count": summary_7d["missed_count"] + summary_7d["delayed_count"],
                "message": "近 7 天存在漏服或延迟情况，建议及时关注用药执行",
            }
        )

    return alerts


def _serialize_dashboard_medicine_item(medicine):
    """
    序列化首页药品摘要项
    """
    return {
        "id": medicine.id,
        "name": medicine.name,
        "quantity": medicine.quantity,
        "expiry_date": medicine.expiry_date.isoformat() if medicine.expiry_date else None,
        "days_until_expiry": medicine.days_until_expiry,
        "is_low_stock": medicine.is_low_stock,
    }


def _serialize_dashboard_followup_item(record):
    """
    序列化首页复诊摘要项
    """
    return {
        "id": record.id,
        "hospital": record.hospital,
        "department": record.department,
        "doctor": record.doctor,
        "visit_date": record.visit_date.isoformat(),
        "follow_up_date": record.follow_up_date.isoformat() if record.follow_up_date else None,
        "days_until_follow_up": record.days_until_follow_up,
        "is_follow_up_due": record.is_follow_up_due(),
    }


def _build_dashboard_mtm_hint(
    total_medicines, adherence_summary, followup_due_count, risk_alerts
):
    """
    基于首页风险生成 MTM 专业服务入口提示
    """
    reasons = []
    summary_7d = adherence_summary["summary_7d"]

    if total_medicines >= 5:
        reasons.append("当前管理药品较多，建议做一次专业梳理")
    if summary_7d["total_records"] > 0 and summary_7d["adherence_rate"] < 70:
        reasons.append("近 7 天依从性偏低，建议获取专业用药指导")
    if followup_due_count > 0:
        reasons.append("存在到期复诊，建议同步梳理当前用药与复诊安排")
    if len(risk_alerts) >= 2:
        reasons.append("当前存在多项风险提醒，建议进入专业服务进一步评估")

    recommended = len(reasons) > 0
    return {
        "recommended": recommended,
        "reason_count": len(reasons),
        "reasons": reasons,
        "message": (
            "建议进入专业用药指导，帮助你更系统地梳理当前用药情况"
            if recommended
            else "当前日常管理整体稳定，如需更深入评估也可进入专业用药指导"
        ),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    首页聚合摘要接口
    """
    from apps.medical_records.models import MedicalRecord
    from apps.medicines.models import Medicine
    from apps.records.models import MedicationRecord
    from apps.reminders.models import Reminder

    try:
        today = timezone.localtime().date()
        next_seven_days = today + timedelta(days=7)
        next_thirty_days = today + timedelta(days=30)

        logger.info(
            "首页聚合摘要请求，user=%s, date=%s",
            request.user.username,
            today.isoformat(),
        )

        reminders_queryset = (
            Reminder.objects.filter(
                user=request.user,
                is_active=True,
                start_date__lte=today,
            )
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            .select_related("medicine")
        )
        today_reminders = [item for item in reminders_queryset if item.should_remind_today()]
        today_records = list(
            MedicationRecord.objects.filter(
                user=request.user,
                scheduled_time__date=today,
            )
            .filter(Q(source="reminder") | Q(reminder__isnull=False))
            .select_related("medicine", "reminder")
            .order_by("-updated_at")
        )

        medicines_queryset = Medicine.objects.filter(user=request.user)
        low_stock_items = list(
            medicines_queryset.filter(quantity__lte=5).order_by("quantity", "name")[:5]
        )
        expiring_soon_items = list(
            medicines_queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=next_thirty_days,
            )
            .order_by("expiry_date", "name")[:5]
        )

        medical_records_queryset = MedicalRecord.objects.filter(user=request.user)
        followup_due_qs = medical_records_queryset.filter(
            follow_up_date__isnull=False,
            follow_up_date__lte=today,
            status="completed",
        ).order_by("follow_up_date", "-visit_date")
        upcoming_followup_qs = medical_records_queryset.filter(
            follow_up_date__isnull=False,
            follow_up_date__gt=today,
            follow_up_date__lte=next_seven_days,
            status="completed",
        ).order_by("follow_up_date", "-visit_date")
        followup_due_items = list(followup_due_qs[:5])
        upcoming_followup_items = list(upcoming_followup_qs[:5])
        next_followup = (
            medical_records_queryset.filter(
                follow_up_date__isnull=False,
                follow_up_date__gte=today,
                status="completed",
            )
            .order_by("follow_up_date", "-visit_date")
            .first()
        )

        adherence_summary = _build_dashboard_adherence_summary(request)
        risk_alerts = _build_dashboard_risk_alerts(
            low_stock_items=low_stock_items,
            expiring_soon_items=expiring_soon_items,
            followup_due_items=followup_due_items,
            adherence_summary=adherence_summary,
        )

        data = {
            "today_tasks": _build_dashboard_today_tasks(
                reminders=today_reminders,
                processed_records=today_records,
                today=today,
            ),
            "risk_alerts": risk_alerts,
            "medication_summary": {
                "total_medicines": medicines_queryset.count(),
                "active_reminders": reminders_queryset.count(),
                "low_stock_count": medicines_queryset.filter(quantity__lte=5).count(),
                "expiring_soon_count": medicines_queryset.filter(
                    expiry_date__isnull=False,
                    expiry_date__gte=today,
                    expiry_date__lte=next_thirty_days,
                ).count(),
                "low_stock_items": [
                    _serialize_dashboard_medicine_item(item) for item in low_stock_items
                ],
                "expiring_soon_items": [
                    _serialize_dashboard_medicine_item(item) for item in expiring_soon_items
                ],
            },
            "followup_summary": {
                "due_count": followup_due_qs.count(),
                "upcoming_count": upcoming_followup_qs.count(),
                "next_followup": (
                    _serialize_dashboard_followup_item(next_followup) if next_followup else None
                ),
                "due_items": [
                    _serialize_dashboard_followup_item(item) for item in followup_due_items
                ],
                "upcoming_items": [
                    _serialize_dashboard_followup_item(item) for item in upcoming_followup_items
                ],
            },
            "adherence_summary": adherence_summary,
            "mtm_entry_hint": _build_dashboard_mtm_hint(
                total_medicines=medicines_queryset.count(),
                adherence_summary=adherence_summary,
                followup_due_count=followup_due_qs.count(),
                risk_alerts=risk_alerts,
            ),
        }

        return success_response(data, "获取首页聚合摘要成功")
    except Exception as exc:
        logger.error(f"获取首页聚合摘要失败: {exc}")
        return error_response("获取首页聚合摘要失败", "DASHBOARD_SUMMARY_ERROR", 500)


def _normalize_openai_base_url(raw: str) -> str:
    """规范化 OpenAI 兼容服务的 base_url，确保以 /v1 结尾。"""

    base = (raw or "").strip().rstrip("/")
    if not base:
        return ""
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


def _build_openai_chat_completion_urls(raw: str) -> list[str]:
    base = (raw or "").strip().rstrip("/")
    if not base:
        return []
    if base.endswith("/v1"):
        candidates = [f"{base}/chat/completions", f"{base[:-3]}/chat/completions"]
    else:
        candidates = [f"{base}/v1/chat/completions", f"{base}/chat/completions"]
    deduped: list[str] = []
    for url in candidates:
        if url and url not in deduped:
            deduped.append(url)
    return deduped


def _extract_json_object(text: str) -> dict | None:
    """从任意文本中提取第一个 JSON 对象并解析，失败返回 None。"""

    if not text:
        return None
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _openai_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
    response_format: dict | None = None,
) -> str:
    """调用 OpenAI 兼容 /chat/completions 接口并返回消息文本。

    优先返回 message.content；当其为空时回退到 message.reasoning_content（部分模型会将内容输出到该字段）。
    """

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    urls = _build_openai_chat_completion_urls(base_url)
    if not urls:
        raise RuntimeError("llm_invalid_base_url")

    last_error: str | None = None
    for index, url in enumerate(urls):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
        except Exception as exc:
            last_error = f"llm_request_exception:{type(exc).__name__}:{str(exc)[:120]}"
            continue

        body_text = str(getattr(resp, "text", "") or "")
        if resp.status_code >= 300:
            last_error = f"llm_http_error:{resp.status_code}:{body_text[:200]}"
            continue

        try:
            data = resp.json()
        except Exception as exc:
            last_error = f"llm_invalid_json:{type(exc).__name__}"
            continue

        choices = data.get("choices") if isinstance(data, dict) else None
        if not isinstance(choices, list) or not choices:
            fallback_hint = json.dumps(data, ensure_ascii=False)[:300] if isinstance(data, dict) else ""
            if index < len(urls) - 1:
                logger.warning(
                    "[LLMProxy] empty choices on primary endpoint, retrying fallback",
                    extra={"url": url, "response_preview": fallback_hint},
                )
            last_error = f"llm_empty_choices:{fallback_hint}"
            continue
        msg = (choices[0] or {}).get("message") or {}

        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content

        reasoning_content = msg.get("reasoning_content")
        if isinstance(reasoning_content, str) and reasoning_content.strip():
            return reasoning_content

        if isinstance(content, str):
            last_error = "llm_empty_content"
            continue
        last_error = "llm_invalid_content"

    raise RuntimeError(last_error or "llm_invalid_response")


def _normalize_llm_answer(text: str) -> str:
    """规范化模型输出，去掉常见包裹并清理明显的格式噪音。"""

    t = (text or "").strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", t).strip()
    t = re.sub(r"\n```$", "", t).strip()
    if t.startswith("**") and t.count("**") == 1:
        t = t[2:].lstrip()
    return t


def _looks_unhelpful_answer(text: str) -> bool:
    """识别明显不可用/拒答类输出，用于触发兜底返回。"""

    t = (text or "").strip()
    if not t:
        return True
    t2 = re.sub(r"[\*`\s]", "", t)
    refusal_markers = [
        "无法直接提供",
        "无法提供",
        "不能提供",
        "不便提供",
        "无法回答",
        "我不能",
        "我无法",
    ]
    if len(t2) <= 40 and any(m in t2 for m in refusal_markers):
        return True

    # 句子明显未完结（常见截断/中途停止）
    if t.rstrip().endswith(("，", "、", ",", ";", "：", ":", "（", "(")):
        return True

    # 涉及剂量但没给任何可执行信息（常见只说“剂量取决于年龄体重”然后停住）
    has_number = bool(re.search(r"\d", t))
    mentions_dose = any(k in t for k in ("剂量", "用量", "mg", "毫克"))
    mentions_age_weight = bool(re.search(r"(根据|取决于).{0,12}(年龄|体重)", t))
    if len(t2) <= 200 and (mentions_age_weight or mentions_dose) and not has_number:
        return True
    return False


def _is_probably_medication_question(question: str, medicine_context: dict | None) -> bool:
    q = (question or "").strip()
    if not q:
        return False
    if isinstance(medicine_context, dict) and medicine_context:
        return True

    q_compact = re.sub(r"\s+", "", q).lower()
    keyword_hits = [
        "药",
        "用药",
        "服用",
        "剂量",
        "用法",
        "用量",
        "禁忌",
        "副作用",
        "相互作用",
        "饭前",
        "饭后",
        "一次",
        "每日",
        "多久",
        "aspirin",
        "amoxicillin",
        "ibuprofen",
        "paracetamol",
        "acetaminophen",
        "阿司匹林",
        "阿莫西林",
        "布洛芬",
        "头孢",
        "对乙酰氨基酚",
    ]
    return any(k in q_compact for k in keyword_hits)


def _fallback_medication_guidance_answer(
    question: str, medicine_context: dict | None
) -> str:
    """当模型返回不可用内容时，提供可执行的用药指导兜底回复。"""

    drug_name = None
    if isinstance(medicine_context, dict):
        name = medicine_context.get("name")
        if isinstance(name, str) and name.strip():
            drug_name = name.strip()

    q = (question or "").strip()
    q_compact = re.sub(r"\s+", "", q)
    is_ibuprofen = ("布洛芬" in q_compact) or ("ibuprofen" in q.lower())

    if is_ibuprofen:
        return (
            "我可以给你布洛芬（Ibuprofen）的通用用药指导，但需要先确认几个关键信息，避免给出不合适的剂量：\n"
            "1）使用者年龄/体重（儿童剂量按体重计算）\n"
            "2）药品规格与剂型（如 0.2g 片、缓释、混悬液等）\n"
            "3）用途（退烧/止痛）与是否合并胃病、肾病、哮喘、正在备孕/怀孕等\n\n"
            "一般用法要点（请以说明书为准）：\n"
            "- 成人常见 OTC 剂量：200–400mg/次，间隔约 6–8 小时按需；24 小时内不建议超过 1200mg（处方可更高需医生指导）。\n"
            "- 尽量随餐或餐后服用，减少胃部刺激；避免与其他 NSAIDs（如双氯芬酸、萘普生）同服。\n"
            "- 慎用/避免：消化道溃疡或出血史、严重肾功能不全、对阿司匹林/NSAIDs 过敏、妊娠晚期等。\n"
            "- 何时就医：黑便/呕血、严重腹痛、呼吸困难/皮疹肿胀、持续高热或疼痛不缓解。\n\n"
            "你把“规格（比如 0.2g/片）+ 年龄/体重 + 主要症状（退烧/止痛）”告诉我，我再按更贴近说明书的方式给出服用建议。"
        )

    drug_tip = f"（{drug_name}）" if drug_name else ""
    return (
        f"我可以提供药物{drug_tip}的用药指导，但需要你补充信息后才能更准确：\n"
        "1）药品名称/规格/剂型（如 0.25g 胶囊、缓释片、口服液等）\n"
        "2）使用者年龄/体重，是否怀孕/哺乳\n"
        "3）用途（退烧/止痛/抗过敏等）与既往病史（胃病、肝肾功能、哮喘、出血倾向）\n"
        "4）正在使用的其他药物（尤其抗凝药、其他止痛药、激素、降压药等）\n\n"
        "先给通用安全要点：尽量按说明书剂量与间隔服用，避免重复成分/同类药叠加；若出现过敏、严重胃痛/黑便、头晕乏力明显或症状持续不缓解，请及时就医。"
    )


def _build_page_agent_proxy_payload(data: dict) -> dict:
    """构造 Page Agent 代理请求负载，并做必要边界控制。"""

    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages 必须为非空数组")
    if len(messages) > 20:
        raise ValueError("messages 数量超过限制")

    tools = data.get("tools")
    if tools is not None and not isinstance(tools, list):
        raise ValueError("tools 必须为数组")
    if isinstance(tools, list) and len(tools) > 20:
        raise ValueError("tools 数量超过限制")

    payload = {
        "model": getattr(settings, "BAICHUAN_M3_MODEL", ""),
        "messages": messages,
        "temperature": data.get("temperature", 0.1),
        "tool_choice": data.get("tool_choice", "required"),
        "parallel_tool_calls": bool(data.get("parallel_tool_calls", False)),
    }

    if tools:
        payload["tools"] = tools

    max_tokens = data.get("max_tokens")
    if isinstance(max_tokens, int) and max_tokens > 0:
        max_limit = int(getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024))
        payload["max_tokens"] = min(max_tokens, max_limit)

    return payload


def _extract_page_agent_tool_name(tool_choice) -> str:
    if isinstance(tool_choice, dict):
        function = tool_choice.get("function")
        if (
            tool_choice.get("type") == "function"
            and isinstance(function, dict)
            and isinstance(function.get("name"), str)
        ):
            return function["name"].strip()
    return ""


def _select_page_agent_tool(payload: dict) -> dict | None:
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools:
        return None

    selected_name = _extract_page_agent_tool_name(payload.get("tool_choice"))
    if selected_name:
        for tool in tools:
            function = tool.get("function") if isinstance(tool, dict) else None
            if isinstance(function, dict) and function.get("name") == selected_name:
                return tool
        raise ValueError(f"未找到 tool_choice 指定的工具：{selected_name}")

    first_tool = tools[0]
    return first_tool if isinstance(first_tool, dict) else None


def _build_page_agent_fallback_messages(messages: list[dict], tool_spec: dict) -> list[dict]:
    function = tool_spec.get("function") if isinstance(tool_spec, dict) else {}
    tool_name = str(function.get("name") or "AgentOutput").strip() or "AgentOutput"
    description = str(function.get("description") or "").strip()
    parameters = function.get("parameters")
    if not isinstance(parameters, dict):
        parameters = {"type": "object"}

    instruction = (
        "你当前运行在一个不支持 function calling 的模型兼容层。"
        f"请直接模拟一次对工具 {tool_name} 的调用，并只输出该工具参数对应的 JSON 对象。"
        "禁止输出 markdown、代码块、解释、前后缀、思考过程或任何非 JSON 内容。"
        "输出的第一个字符必须是 {，最后一个字符必须是 }。"
        f"\n工具描述：{description or '无'}"
        f"\n参数 JSON Schema：{json.dumps(parameters, ensure_ascii=False)}"
        "\n如果字段无法确定，请给出最保守、最可执行且满足 schema 的值。"
    )
    system_parts = [instruction]
    normalized_messages = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        if role == "system":
            if content:
                system_parts.append(str(content))
            continue
        normalized_messages.append(message)
    return [
        {"role": "system", "content": "\n\n".join(part for part in system_parts if part)},
        *normalized_messages,
    ]


def _build_page_agent_fallback_response(
    *,
    model: str,
    tool_name: str,
    arguments: dict,
    upstream_text: str,
) -> dict:
    return {
        "id": f"chatcmpl-page-agent-fallback-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": upstream_text,
                    "tool_calls": [
                        {
                            "id": "call_page_agent_fallback",
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(arguments, ensure_ascii=False),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
    }


def _execute_page_agent_fallback(
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout_seconds: float,
    payload: dict,
) -> dict:
    tool_spec = _select_page_agent_tool(payload)
    if not tool_spec:
        raise ValueError("未找到可用工具")

    function = tool_spec.get("function") if isinstance(tool_spec, dict) else {}
    tool_name = str(function.get("name") or "AgentOutput").strip() or "AgentOutput"
    fallback_messages = _build_page_agent_fallback_messages(payload["messages"], tool_spec)
    max_tokens = int(
        payload.get("max_tokens")
        or getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024)
    )
    upstream_text = _openai_chat_completion(
        base_url=base_url,
        api_key=api_key,
        model=model,
        messages=fallback_messages,
        temperature=float(payload.get("temperature", 0.1)),
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )
    arguments = _extract_json_object(upstream_text)
    if not isinstance(arguments, dict):
        raise ValueError("上游模型未返回可解析的 JSON 工具参数")
    return _build_page_agent_fallback_response(
        model=model,
        tool_name=tool_name,
        arguments=arguments,
        upstream_text=upstream_text,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def page_agent_chat_completions(request):
    """为前端 Page Agent 提供受保护的 OpenAI 兼容代理接口。"""

    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return JsonResponse(
            {"error": {"message": "AI 服务未启用", "type": "service_unavailable"}},
            status=503,
        )

    base_url = getattr(settings, "BAICHUAN_M3_API_BASE_URL", "")
    api_key = getattr(settings, "BAICHUAN_M3_API_KEY", "")
    model = getattr(settings, "BAICHUAN_M3_MODEL", "")
    timeout_seconds = float(getattr(settings, "BAICHUAN_M3_TIMEOUT_SECONDS", 30))

    if not base_url or not model:
        logger.warning(
            "[PageAgentProxy] missing config",
            extra={"base_url_configured": bool(base_url), "model": model},
        )
        return JsonResponse(
            {"error": {"message": "AI 服务配置缺失", "type": "config_error"}},
            status=503,
        )

    try:
        payload = _build_page_agent_proxy_payload(request.data or {})
    except ValueError as exc:
        logger.warning(
            "[PageAgentProxy] invalid payload",
            extra={"user_id": getattr(request.user, "id", None), "error": str(exc)},
        )
        return JsonResponse(
            {"error": {"message": str(exc), "type": "invalid_request_error"}},
            status=400,
        )

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = f"{_normalize_openai_base_url(base_url)}/chat/completions"
    logger.info(
        "[PageAgentProxy] forwarding request",
        extra={
            "user_id": getattr(request.user, "id", None),
            "message_count": len(payload.get("messages", [])),
            "tool_count": len(payload.get("tools", [])),
        },
    )

    if payload.get("tools"):
        logger.info(
            "[PageAgentProxy] using json fallback",
            extra={
                "user_id": getattr(request.user, "id", None),
                "tool_name": _extract_page_agent_tool_name(payload.get("tool_choice"))
                or "first_tool",
            },
        )
        try:
            body = _execute_page_agent_fallback(
                base_url=base_url,
                api_key=api_key,
                model=model,
                timeout_seconds=timeout_seconds,
                payload=payload,
            )
        except requests.RequestException as exc:
            logger.error(
                "[PageAgentProxy] fallback upstream request failed",
                extra={"user_id": getattr(request.user, "id", None), "error": str(exc)},
            )
            return JsonResponse(
                {"error": {"message": "上游模型服务请求失败", "type": "upstream_error"}},
                status=502,
            )
        except RuntimeError as exc:
            logger.error(
                "[PageAgentProxy] fallback upstream returned error",
                extra={"user_id": getattr(request.user, "id", None), "error": str(exc)},
            )
            return JsonResponse(
                {"error": {"message": "上游模型返回错误", "type": "upstream_error"}},
                status=502,
            )
        except ValueError as exc:
            logger.error(
                "[PageAgentProxy] fallback produced invalid output",
                extra={"user_id": getattr(request.user, "id", None), "error": str(exc)},
            )
            return JsonResponse(
                {"error": {"message": str(exc), "type": "invalid_response_error"}},
                status=502,
            )
        return JsonResponse(body, status=200, safe=isinstance(body, dict))

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    except requests.RequestException as exc:
        logger.error(
            "[PageAgentProxy] upstream request failed",
            extra={"user_id": getattr(request.user, "id", None), "error": str(exc)},
        )
        return JsonResponse(
            {"error": {"message": "上游模型服务请求失败", "type": "upstream_error"}},
            status=502,
        )

    try:
        body = resp.json()
    except ValueError:
        logger.error(
            "[PageAgentProxy] upstream returned non-json",
            extra={
                "user_id": getattr(request.user, "id", None),
                "status_code": resp.status_code,
            },
        )
        return JsonResponse(
            {"error": {"message": "上游模型响应格式错误", "type": "bad_gateway"}},
            status=502,
        )

    return JsonResponse(body, status=resp.status_code, safe=isinstance(body, dict))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def medication_guidance(request):
    """用药咨询接口：仅允许药物/用药指导相关问题。"""

    question = str((request.data or {}).get("question", "")).strip()
    medicine_id = (request.data or {}).get("medicine_id")

    logger.info(
        "[AI] medication_guidance request",
        extra={
            "user_id": getattr(request.user, "id", None),
            "has_question": bool(question),
            "medicine_id": medicine_id,
        },
    )

    if not question:
        return error_response("请提供问题", "VALIDATION_ERROR", 400)
    if len(question) > 2000:
        return error_response("问题过长，请精简后再试", "VALIDATION_ERROR", 400)

    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return error_response("AI 服务未启用", "AI_DISABLED", 503)

    base_url = getattr(settings, "BAICHUAN_M3_API_BASE_URL", "")
    api_key = getattr(settings, "BAICHUAN_M3_API_KEY", "")
    model = getattr(settings, "BAICHUAN_M3_MODEL", "")
    timeout_seconds = float(getattr(settings, "BAICHUAN_M3_TIMEOUT_SECONDS", 30))
    max_tokens = int(getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024))
    cls_max_tokens = int(getattr(settings, "BAICHUAN_M3_CLASSIFIER_MAX_TOKENS", 256))

    if not base_url or not model:
        logger.warning(
            "[AI] missing config",
            extra={"base_url_configured": bool(base_url), "model": model},
        )
        return error_response("AI 服务配置缺失", "AI_CONFIG_MISSING", 503)

    medicine_context = None
    if medicine_id is not None and str(medicine_id).strip() != "":
        try:
            from apps.medicines.models import Medicine

            med = Medicine.objects.filter(id=medicine_id, user=request.user).first()
            if med:
                medicine_context = {
                    "id": med.id,
                    "name": med.name,
                    "specification": med.specification,
                    "manufacturer": med.manufacturer,
                    "medicine_type": med.medicine_type,
                    "is_prescription": bool(med.is_prescription),
                    "storage_conditions": med.storage_conditions,
                    "description": med.description,
                }
        except Exception as e:
            logger.warning(f"[AI] medicine_context load failed: {e}")

    classifier_messages = [
        {
            "role": "system",
            "content": (
                "You are a strict content classifier for a medication guidance app. "
                "Decide whether the user request is ONLY about medications and medication use guidance. "
                "Allowed: drug names, dosage, frequency, timing, interactions, contraindications, side effects, "
                "missed dose, storage, pregnancy/children/elderly precautions related to a medication. "
                "Disallowed: diagnosis, differential diagnosis, lab/imaging, treatment plan for diseases, "
                "medical record interpretation, emergency triage, prognosis. "
                "Answer directly. Do not include analysis. "
                "Return ONLY a JSON object with keys: allowed (boolean), reason (string). "
                "No markdown. No code fences. "
                'Example allowed: {"allowed": true, "reason": ""}. '
                'Example disallowed: {"allowed": false, "reason": "short reason"}.'
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": question,
                    "medicine_context": medicine_context,
                },
                ensure_ascii=False,
            ),
        },
    ]

    try:
        try:
            cls_text = _openai_chat_completion(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=classifier_messages,
                temperature=0.0,
                max_tokens=cls_max_tokens,
                timeout_seconds=timeout_seconds,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            logger.info(f"[AI] classifier response_format fallback: {e}")
            cls_text = _openai_chat_completion(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=classifier_messages,
                temperature=0.0,
                max_tokens=cls_max_tokens,
                timeout_seconds=timeout_seconds,
            )

        logger.info(f"[AI] classifier raw len={len(cls_text)} head={cls_text[:180]!r}")
        cls_obj = _extract_json_object(cls_text) or {}
        allowed = bool(cls_obj.get("allowed"))
        reason = str(cls_obj.get("reason", "")).strip() or ""
    except Exception as e:
        logger.warning(f"[AI] classifier failed: {e}")
        allowed = _is_probably_medication_question(question, medicine_context)
        reason = "" if allowed else "分类失败，且问题不符合用药咨询范围"

    if not allowed and _is_probably_medication_question(question, medicine_context):
        logger.info(
            "[AI] classifier corrected to allow by heuristic",
            extra={"user_id": getattr(request.user, "id", None)},
        )
        allowed = True
        reason = ""

    if not allowed:
        logger.info(
            "[AI] blocked non-medication request",
            extra={"user_id": getattr(request.user, "id", None), "reason": reason},
        )
        return success_response(
            {
                "blocked": True,
                "reason": reason or "当前仅支持药物信息与用药指导咨询（不支持诊断/检查/疾病治疗方案）。",
                "answer": "当前仅支持药物信息与用药指导咨询。请将问题改为具体药物的用法用量、注意事项、相互作用、不良反应等。",
            },
            "已拦截非用药咨询",
        )

    system_prompt = (
        "你是 MTM-用药助手的用药指导助手。\n"
        "你只能回答药物信息与用药指导相关内容，不做疾病诊断、不判断病情严重程度、不替代医生。\n"
        "如果用户的问题包含疾病诊断/检查/治疗方案请求，请拒绝并引导其改问用药问题。\n"
        "不要仅用一句话拒答（例如‘无法提供/无法直接提供’）；当关键信息不足以给出具体剂量时，请给出通用用药原则并提出澄清问题。\n"
        "回答时请尽量结构化：用法用量（一般信息）、禁忌/慎用人群、相互作用、常见不良反应、漏服/过量处理、储存方式、何时就医（仅基于用药风险）。\n"
        "避免给出超出说明书或权威指南的精确个体化剂量；需要关键信息时，先提出澄清问题。"
    )

    user_payload = {
        "question": question,
        "medicine_context": medicine_context,
        "constraints": {
            "only_medication_guidance": True,
            "no_diagnosis": True,
        },
    }

    fallback_used = False

    try:
        answer = _openai_chat_completion(
            base_url=base_url,
            api_key=api_key,
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False),
                },
            ],
            temperature=0.2,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )
    except Exception as e:
        logger.error(f"[AI] generation failed: {e}")
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        fallback_used = True
        logger.warning(
            "[AI] generation exception -> fallback answer",
            extra={"user_id": getattr(request.user, "id", None)},
        )
        return success_response(
            {"blocked": False, "answer": answer, "fallback_used": fallback_used},
            "模型服务暂不可用，已返回通用用药建议",
        )

    answer = _normalize_llm_answer(answer)
    logger.info(f"[AI] generation raw len={len(answer)} head={answer[:180]!r}")
    if _looks_unhelpful_answer(answer):
        logger.warning(
            "[AI] unhelpful generation answer -> fallback",
            extra={"user_id": getattr(request.user, "id", None)},
        )
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        fallback_used = True

    logger.info(
        "[AI] medication_guidance success",
        extra={
            "user_id": getattr(request.user, "id", None),
            "fallback_used": fallback_used,
        },
    )
    return success_response(
        {"blocked": False, "answer": answer, "fallback_used": fallback_used}, "生成成功"
    )


@api_view(["POST"])
def clear_cache(request):
    """
    清除缓存接口
    需要管理员权限

    Returns:
        Response: 清除结果
    """
    if not request.user.is_staff:
        return error_response("权限不足", "PERMISSION_DENIED", 403)

    try:
        cache.clear()
        logger.info(f"管理员 {request.user.username} 清除了所有缓存")
        return success_response(None, "缓存清除成功")
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return error_response("缓存清除失败", "CACHE_CLEAR_ERROR", 500)
