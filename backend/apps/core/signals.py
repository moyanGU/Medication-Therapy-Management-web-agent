"""核心应用信号处理器"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import Signal, receiver

logger = logging.getLogger("mtm_helper")
User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    用户登录成功信号处理器

    Args:
        sender: 信号发送者
        request: 请求对象
        user: 用户对象
        **kwargs: 其他参数
    """
    from .utils import get_client_ip, log_user_action

    client_ip = get_client_ip(request)

    # 记录登录日志
    logger.info(f"用户登录成功: {user.username} - IP: {client_ip}")

    # 记录用户操作
    log_user_action(
        user,
        "LOGIN",
        {
            "ip_address": client_ip,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )

    # 更新用户最后登录时间缓存（容错）
    try:
        cache.set(f"user_last_login:{user.id}", user.last_login, 3600 * 24)  # 缓存24小时
    except Exception as e:
        logger.warning(f"[Signals] 设置用户最后登录缓存失败，降级忽略: {e}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    用户登出信号处理器

    Args:
        sender: 信号发送者
        request: 请求对象
        user: 用户对象
        **kwargs: 其他参数
    """
    if user:
        from .utils import get_client_ip, log_user_action

        client_ip = get_client_ip(request)

        # 记录登出日志
        logger.info(f"用户登出: {user.username} - IP: {client_ip}")

        # 记录用户操作
        log_user_action(
            user,
            "LOGOUT",
            {
                "ip_address": client_ip,
            },
        )

        # 清除用户相关缓存（容错）
        try:
            cache.delete(f"user_last_login:{user.id}")
            cache.delete(f"user_profile:{user.id}")
        except Exception as e:
            logger.warning(f"[Signals] 清理用户缓存失败，降级忽略: {e}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    用户登录失败信号处理器

    Args:
        sender: 信号发送者
        credentials: 登录凭据
        request: 请求对象
        **kwargs: 其他参数
    """
    from .utils import get_client_ip

    client_ip = get_client_ip(request)
    username = credentials.get("username", "Unknown")

    # 记录登录失败日志
    logger.warning(f"用户登录失败: {username} - IP: {client_ip}")

    # 增加失败计数（用于防暴力破解）- 容错
    fail_key = f"login_fail:{client_ip}"
    try:
        fail_count = cache.get(fail_key, 0)
    except Exception as e:
        logger.warning(f"[Signals] 读取登录失败计数缓存失败，降级使用0: {e}")
        fail_count = 0
    try:
        cache.set(fail_key, fail_count + 1, 3600)  # 缓存1小时
    except Exception as e:
        logger.warning(f"[Signals] 写入登录失败计数缓存失败，降级忽略: {e}")

    # 如果失败次数过多，记录警告（仅日志，不依赖缓存）
    if fail_count >= 5:
        logger.error(f"IP {client_ip} 登录失败次数过多，可能存在暴力破解行为")


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    """
    用户保存后信号处理器

    Args:
        sender: 信号发送者
        instance: 用户实例
        created: 是否为新创建
        **kwargs: 其他参数
    """
    if created:
        # 新用户创建
        logger.info(f"新用户创建: {instance.username} (ID: {instance.id})")
        # 初始化逻辑（无需缓存）
    else:
        # 用户信息更新
        logger.info(f"用户信息更新: {instance.username} (ID: {instance.id})")

        # 清除用户相关缓存（容错）
        try:
            cache.delete(f"user_profile:{instance.id}")
        except Exception as e:
            logger.warning(f"[Signals] 清理用户资料缓存失败，降级忽略: {e}")


@receiver(post_delete, sender=User)
def user_post_delete_handler(sender, instance, **kwargs):
    """
    用户删除后信号处理器

    Args:
        sender: 信号发送者
        instance: 用户实例
        **kwargs: 其他参数
    """
    logger.info(f"用户删除: {instance.username} (ID: {instance.id})")

    # 清除用户相关缓存（容错）
    try:
        cache.delete(f"user_profile:{instance.id}")
        cache.delete(f"user_last_login:{instance.id}")
    except Exception as e:
        logger.warning(f"[Signals] 清理用户删除缓存失败，降级忽略: {e}")


def clear_model_cache(sender, instance, **kwargs):
    """
    通用模型缓存清理函数

    Args:
        sender: 信号发送者
        instance: 模型实例
        **kwargs: 其他参数
    """
    model_name = sender._meta.label_lower

    # 清除模型相关的缓存（容错）
    cache_keys = [
        f"{model_name}:list",
        f"{model_name}:{instance.pk}",
        f"{model_name}:count",
    ]

    for key in cache_keys:
        try:
            cache.delete(key)
        except Exception as e:
            logger.warning(f"[Signals] 清理模型缓存失败 key={key}，降级忽略: {e}")

    logger.debug(f"清除模型缓存: {model_name} - {instance.pk}")


def setup_model_cache_signals():
    """
    设置模型缓存信号
    为所有模型注册缓存清理信号
    """
    from django.apps import apps

    # 获取所有已安装应用的模型
    for model in apps.get_models():
        # 跳过Django内置模型
        if model._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]:
            continue

        # 注册信号
        # ... 保持原样，若有使用请确保调用处也做好容错 ...


# 在应用启动时设置模型缓存信号
setup_model_cache_signals()


class SignalLogger:
    """
    信号日志记录器
    用于记录各种信号的触发情况
    """

    @staticmethod
    def log_signal(signal_name, sender, instance=None, **kwargs):
        """
        记录信号日志

        Args:
            signal_name: 信号名称
            sender: 信号发送者
            instance: 实例对象
            **kwargs: 其他参数
        """
        log_data = {
            "signal": signal_name,
            "sender": sender.__name__ if hasattr(sender, "__name__") else str(sender),
            "instance_id": getattr(instance, "pk", None) if instance else None,
        }

        logger.debug(f"信号触发: {log_data}")


# 定义自定义信号
user_profile_updated = Signal()
data_export_completed = Signal()
notification_sent = Signal()


@receiver(user_profile_updated)
def handle_user_profile_updated(sender, user, changes, **kwargs):
    """
    用户资料更新信号处理器

    Args:
        sender: 信号发送者
        user: 用户对象
        changes: 变更内容
        **kwargs: 其他参数
    """
    logger.info(f"用户资料更新: {user.username} - 变更: {changes}")

    # 清除用户缓存
    cache.delete(f"user_profile:{user.id}")


@receiver(data_export_completed)
def handle_data_export_completed(sender, user, export_type, file_path, **kwargs):
    """
    数据导出完成信号处理器

    Args:
        sender: 信号发送者
        user: 用户对象
        export_type: 导出类型
        file_path: 文件路径
        **kwargs: 其他参数
    """
    logger.info(f"数据导出完成: {user.username} - 类型: {export_type} - 文件: {file_path}")

    # 可以在这里添加导出完成后的处理逻辑
    # 例如：发送通知、清理临时文件等


@receiver(notification_sent)
def handle_notification_sent(sender, user, notification_type, content, **kwargs):
    """
    通知发送信号处理器

    Args:
        sender: 信号发送者
        user: 用户对象
        notification_type: 通知类型
        content: 通知内容
        **kwargs: 其他参数
    """
    logger.info(f"通知发送: {user.username} - 类型: {notification_type}")

    # 记录通知发送历史
    # 可以在这里添加通知统计
