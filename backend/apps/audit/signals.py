import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from apps.audit.models import AuditLog
from apps.audit.middleware import get_current_request
from apps.medical_records.models import MedicalRecord
from apps.medicines.models import Medicine
from apps.reminders.models import Reminder

# 仅监听核心业务模型，避免日志过多
WATCHED_MODELS = [
    MedicalRecord,
    Medicine,
    Reminder,
    get_user_model(),
]

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _serialize_instance(instance):
    """简单的模型序列化"""
    try:
        # 尝试只保留主要字段，避免过大
        d = model_to_dict(instance)
        # 移除不可序列化的字段
        for k, v in list(d.items()):
            if k in ['password', 'groups', 'user_permissions']:
                del d[k]
            # 处理日期时间等特殊类型
            if hasattr(v, 'isoformat'):
                d[k] = v.isoformat()
        return json.dumps(d, default=str)
    except Exception:
        return str(instance)


def _resolve_audit_user(sender, instance, user):
    if not user or not getattr(user, "is_authenticated", False):
        return None
    try:
        user_model = get_user_model()
        if sender == user_model and instance.pk == user.pk:
            return None
        if user.pk and user_model.objects.filter(pk=user.pk).exists():
            return user
    except Exception:
        return None
    return None


def _build_delete_details(sender, instance, user, audit_user):
    details = {"model": sender.__name__, "pk": instance.pk}
    if user and not audit_user:
        details["operator_username"] = getattr(user, "username", "unknown")
    return details


def _create_delete_audit_log(sender, instance, request, audit_user, details):
    try:
        AuditLog.objects.create(
            user=audit_user,
            action="DELETE",
            resource_type=str(sender._meta.verbose_name),
            resource_id=str(instance.pk),
            details=details,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        return
    except Exception as e:
        if "foreign key constraint" in str(e).lower():
            AuditLog.objects.create(
                user=None,
                action="DELETE",
                resource_type=str(sender._meta.verbose_name),
                resource_id=str(instance.pk),
                details=details,
                ip_address=_get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            )
            return
        logger.error(f"Failed to create audit log for DELETE: {e}")


@receiver(post_save)
def audit_log_save(sender, instance, created, **kwargs):
    if sender not in WATCHED_MODELS:
        return

    request = get_current_request()
    if not request:
        return

    # 忽略非登录用户的操作（或者是系统后台任务，视需求而定）
    # 但通常我们也想记录系统操作，这里暂时只记录有 request 上下文的操作
    
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        # 匿名操作或系统操作，user 设为 None
        user = None

    action = 'CREATE' if created else 'UPDATE'
    resource_type = str(sender._meta.verbose_name)
    resource_id = str(instance.pk)
    
    # 构建详情
    details = {
        'model': sender.__name__,
        'pk': instance.pk,
    }

    AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )


@receiver(post_delete)
def audit_log_delete(sender, instance, **kwargs):
    if sender not in WATCHED_MODELS:
        return

    request = get_current_request()
    if not request:
        return

    user = getattr(request, 'user', None)

    audit_user = _resolve_audit_user(sender, instance, user)
    details = _build_delete_details(sender, instance, user, audit_user)
    _create_delete_audit_log(sender, instance, request, audit_user, details)
