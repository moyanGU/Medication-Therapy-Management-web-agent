import json
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

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"AUDIT-SENSITIVE | Model: {sender.__name__} | ID: {instance.pk} | Action: {action}"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Failed to record audit log for {action} of {sender.__name__} id {instance.pk}: {str(e)}",
            exc_info=True)


@receiver(post_delete)
def audit_log_delete(sender, instance, **kwargs):
    if sender not in WATCHED_MODELS:
        return

    request = get_current_request()
    if not request:
        return

    user = getattr(request, 'user', None)

    # 检查操作用户是否有效
    audit_user = None
    if user and user.is_authenticated:
        try:
            # 1. 检查 user 实例本身是否就是被删除的对象
            if sender == get_user_model() and instance.pk == user.pk:
                audit_user = None
            # 2. 检查 user 是否存在于数据库 (避免外键错误)
            # 注意：如果 user 已经被删除，User.objects.filter(pk=user.pk).exists() 会返回 False
            elif user.pk and get_user_model().objects.filter(pk=user.pk).exists():
                audit_user = user
        except Exception:
            pass

    # 如果此时 audit_user 为 None，但 request.user 是存在的（说明是已登录用户操作，但用户可能刚被删，或者是删除自己的操作）
    # 我们可以选择记录 user_id=None 的审计日志，或者记录在 details 中

    details = {
        'model': sender.__name__,
        'pk': instance.pk,
        'deleted_data': _serialize_instance(instance)
    }
    if user and not audit_user:
        details['operator_username'] = getattr(user, 'username', 'unknown')

    try:
        # 当删除操作发生时，如果外键约束导致无法保存 user，我们尝试将 user 置为 None
        # 或者在创建时捕获 IntegrityError 并重试
        AuditLog.objects.create(
            user=audit_user,
            action='DELETE',
            resource_type=str(sender._meta.verbose_name),
            resource_id=str(instance.pk),
            details=details,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"AUDIT-SENSITIVE | Model: {sender.__name__} | ID: {instance.pk} | Action: DELETE"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        # 如果是因为外键约束失败（例如 audit_user 刚被删），尝试以 user=None 再次记录
        if "foreign key constraint" in str(e).lower():
            try:
                AuditLog.objects.create(
                    user=None,
                    action='DELETE',
                    resource_type=str(sender._meta.verbose_name),
                    resource_id=str(instance.pk),
                    details=details,
                    ip_address=_get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                logger.info(
                    f"AUDIT-SENSITIVE | Model: {sender.__name__} | ID: {instance.pk} | Action: DELETE"
                )
            except Exception as inner_e:
                logger.error(
                    f"Failed to record audit log for deletion of {sender.__name__} id {instance.pk}: {str(inner_e)}",
                    exc_info=True)
        else:
            # 其他错误则记录日志
            logger.error(
                f"Failed to record audit log for deletion of {sender.__name__} id {instance.pk}: {str(e)}",
                exc_info=True)
