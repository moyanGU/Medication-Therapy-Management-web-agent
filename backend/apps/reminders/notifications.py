import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import json
from typing import Optional
from datetime import timedelta

try:
    # 运行环境未安装时避免导入错误，具体发送时再做校验
    from pywebpush import webpush, WebPushException
except Exception:  # pragma: no cover
    webpush = None
    WebPushException = Exception

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务
    负责发送各种类型的提醒通知
    """
    
    def __init__(self):
        self.enabled_types = ['push', 'email', 'sms']  # 可用的通知类型
    
    def send_notification(self, user, title, message, reminder=None, history=None):
        try:
            user_settings = self.get_notification_settings(user)
            # 优先尊重历史记录指定的通道顺序，其次使用提醒的偏好，否则按用户设置推断
            from_history = False
            if history and getattr(history, 'notification_methods', None):
                preferred = list(history.notification_methods or [])
                from_history = True
            else:
                preferred = reminder.notification_types if reminder else ['push']
            if not preferred:
                preferred = []
                if user_settings.get('push_enabled'):
                    preferred.append('push')
                if user_settings.get('sms_enabled'):
                    preferred.append('sms')
                if user_settings.get('email_enabled'):
                    preferred.append('email')
            elif not from_history:
                if user_settings.get('sms_enabled') and 'sms' not in preferred:
                    preferred.append('sms')
                if user_settings.get('email_enabled') and 'email' not in preferred:
                    preferred.append('email')

            sent = False
            for notification_type in preferred:
                if notification_type in self.enabled_types:
                    if self._send_by_type(notification_type, user, title, message, reminder, history):
                        sent = True
                        self._log_notification(user, title, message, [notification_type], reminder)
                        break

            if not sent and reminder is not None and not from_history:
                try:
                    from .history_models import ReminderHistory
                    fallback_time = timezone.now() + timedelta(minutes=5)
                    ReminderHistory.objects.create(
                        user=user,
                        reminder=reminder,
                        title=title,
                        message=message,
                        notification_methods=['sms'] if user_settings.get('sms_enabled') else ['email'] if user_settings.get('email_enabled') else [],
                        scheduled_time=fallback_time,
                        reminder_type='repeat',
                        status='pending',
                    )
                    logger.warning(f"所有通知方式发送失败，已创建5分钟后重试的待发送记录: reminder={getattr(reminder, 'id', None)}")
                except Exception as ie:
                    logger.error(f"创建待发送记录失败: {ie}")

            return sent
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            return False
    
    def _send_by_type(self, notification_type, user, title, message, reminder, history):
        """
        根据类型发送通知
        """
        try:
            if notification_type == 'push':
                return self._send_push_notification(user, title, message, reminder, history)
            elif notification_type == 'email':
                return self._send_email_notification(user, title, message, reminder, history)
            elif notification_type == 'sms':
                return self._send_sms_notification(user, title, message, reminder, history)
            else:
                logger.warning(f"不支持的通知类型: {notification_type}")
                return False
        except Exception as e:
            logger.error(f"发送 {notification_type} 通知失败: {str(e)}")
            return False
    
    def _send_push_notification(self, user, title, message, reminder, history=None):
        """
        发送推送通知（Web Push）
        - 查找用户的有效订阅
        - 使用 VAPID 私钥发送浏览器推送
        - 针对 404/410 将订阅标记为失效
        """
        from apps.users.models import PushSubscription

        # 校验依赖
        if webpush is None:
            logger.error("pywebpush 未安装，无法发送 Web Push。请在 requirements.txt 中添加 pywebpush 并安装。")
            return False

        vapid_private: Optional[str] = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        vapid_subject: Optional[str] = getattr(settings, 'VAPID_SUBJECT', None) or 'mailto:noreply@example.com'
        if not vapid_private:
            logger.error("缺少 VAPID_PRIVATE_KEY 配置，无法发送 Web Push。请在 .env 设置 VAPID_PRIVATE_KEY。")
            return False

        subs = PushSubscription.objects.filter(user=user, is_active=True)
        if not subs.exists():
            logger.info(f"用户 {user.id} 暂无有效 Push 订阅，跳过推送")
            return False

        if history is None and reminder is not None:
            try:
                from .history_models import ReminderHistory
                history = ReminderHistory.objects.create(
                    user=user,
                    reminder=reminder,
                    title=title,
                    message=message,
                    notification_methods=['push'],
                    scheduled_time=timezone.now(),
                    reminder_type='scheduled',
                    status='sent',
                )
            except Exception:
                history = None

        payload = json.dumps({
            'title': title,
            'body': message,
            'tag': f"mtm-reminder-{getattr(reminder, 'id', 'general')}",
            'data': {
                'url': '/',
                'reminderId': getattr(reminder, 'id', None),
                'historyId': getattr(history, 'id', None),
            }
        }, ensure_ascii=False)

        success_any = False
        for sub in subs:
            try:
                webpush(
                    subscription_info={
                        'endpoint': sub.endpoint,
                        'keys': {
                            'p256dh': sub.keys.get('p256dh'),
                            'auth': sub.keys.get('auth'),
                        }
                    },
                    data=payload,
                    vapid_private_key=vapid_private,
                    vapid_claims={'sub': vapid_subject}
                )
                sub.touch_sent()
                success_any = True
                logger.info(f"Web Push 已发送: user={user.id} endpoint={sub.endpoint[:32]}...")
                if history is not None:
                    try:
                        history.sent_at = timezone.now()
                        history.status = 'sent'
                        history.save(update_fields=['sent_at', 'status'])
                    except Exception:
                        pass
            except WebPushException as e:
                # 404/410 表示订阅失效
                status_code = getattr(getattr(e, 'response', None), 'status_code', None)
                logger.warning(f"WebPushException user={user.id} endpoint={sub.endpoint[:32]}... status={status_code} error={e}")
                if status_code in (404, 410):
                    sub.mark_inactive()
            except Exception as e:
                logger.error(f"Web Push 发送失败 user={user.id} endpoint={sub.endpoint[:32]}... error={e}")

        return success_any
    
    def _send_email_notification(self, user, title, message, reminder, history=None):
        """
        发送邮件通知
        """
        try:
            if not user.email:
                logger.warning(f"用户 {user.username} 没有邮箱地址")
                return False
            
            # 构建邮件内容
            context = {
                'user': user,
                'title': title,
                'message': message,
                'reminder': reminder,
                'current_time': timezone.now()
            }
            
            # 使用模板渲染邮件内容
            html_content = self._render_email_template(context)
            
            # 发送邮件
            send_mail(
                subject=title,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False
            )
            
            try:
                if history is not None:
                    history.sent_at = timezone.now()
                    history.status = 'sent'
                    history.notification_methods = ['email']
                    history.save(update_fields=['sent_at', 'status', 'notification_methods'])
                elif reminder is not None:
                    from .history_models import ReminderHistory
                    ReminderHistory.objects.create(
                        user=user,
                        reminder=reminder,
                        title=title,
                        message=message,
                        notification_methods=['email'],
                        scheduled_time=timezone.now(),
                        reminder_type='scheduled',
                        status='sent',
                    )
            except Exception:
                pass

            logger.info(f"邮件通知发送成功给 {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件通知失败: {str(e)}")
            return False
    
    def _send_sms_notification(self, user, title, message, reminder, history=None):
        """
        发送短信通知
        """
        try:
            if not hasattr(user, 'phone') or not user.phone:
                logger.warning(f"用户 {user.username} 没有手机号")
                return False
            
            sms_text = getattr(settings, 'SMS_TEMPLATES', {}).get('reminder', '{title}: {message}').format(title=title, message=message)
            spug_msg_var = (title or '').strip() or (message or '').strip() or '用药'
            if spug_msg_var.endswith('提醒'):
                spug_msg_var = spug_msg_var[:-2]
            spug_enabled = getattr(settings, 'SPUG_PUSH_ENABLED', False)

            if spug_enabled:
                base_url = getattr(settings, 'SPUG_PUSH_URL', 'https://push.spug.cc')
                template_id = (getattr(settings, 'SPUG_TEMPLATE_ID_REMINDER', '') or getattr(settings, 'SPUG_TEMPLATE_ID', '')).strip()
                app_name = getattr(settings, 'SPUG_APP_NAME', 'MTM用药助手')
                token = getattr(settings, 'SPUG_PUSH_TOKEN', '')
                timeout = int(getattr(settings, 'SPUG_PUSH_TIMEOUT_SECONDS', 3))

                if requests is None:
                    logger.error('requests 未安装，无法调用Spug推送')
                    return False
                if not template_id:
                    logger.error('SPUG_TEMPLATE_ID 未配置')
                    return False

                use_sms = bool(getattr(settings, 'SPUG_REMINDER_USE_SMS_ENDPOINT', False))
                if use_sms:
                    url = f"{base_url.rstrip('/')}/sms/{template_id}"
                    params = {
                        getattr(settings, 'SPUG_SMS_PARAM_TO', 'to'): user.phone,
                        getattr(settings, 'SPUG_SMS_PARAM_MESSAGE', 'message'): spug_msg_var,
                    }
                else:
                    url = f"{base_url.rstrip('/')}/send/{template_id}"
                    payload = {
                        'name': app_name,
                        'title': title,
                        'message': spug_msg_var,
                        'targets': user.phone,
                    }
                try:
                    extra_json = getattr(settings, 'SPUG_EXTRA_PARAMS_JSON', '')
                    if extra_json:
                        import json as _json
                        extra = _json.loads(extra_json)
                        if isinstance(extra, dict):
                            payload.update(extra)
                    # 验证码模板：若要求数字验证码且尚未提供，则自动生成
                    require_code = bool(getattr(settings, 'SPUG_REQUIRE_NUMERIC_CODE', False))
                    if require_code and 'code' not in payload:
                        try:
                            import random
                            length = int(getattr(settings, 'SPUG_CODE_LENGTH', 6))
                            length = max(4, min(10, length))
                            payload['code'] = ''.join(str(random.randint(0, 9)) for _ in range(length))
                            # 可选传递TTL（分钟）
                            ttl_seconds = int(getattr(settings, 'SMS_CODE_TTL', 300))
                            ttl_minutes = max(1, ttl_seconds // 60)
                            payload.setdefault('ttl', ttl_minutes)
                        except Exception:
                            pass
                except Exception:
                    pass
                headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
                if token:
                    headers['Authorization'] = f"Bearer {token}"

                masked_phone = (user.phone[:3] + '****' + user.phone[-4:]) if isinstance(user.phone, str) and len(user.phone) == 11 else '[masked]'
                if use_sms:
                    masked_params = { **params, getattr(settings, 'SPUG_SMS_PARAM_MESSAGE', 'message'): '[masked]', getattr(settings, 'SPUG_SMS_PARAM_TO', 'to'): masked_phone }
                    logger.info(f"调用Spug发送提醒短信: url={url}, params={masked_params}, timeout={timeout}, auth={'yes' if token else 'no'}")
                    r = requests.get(url, params=params, headers=headers, timeout=timeout)
                else:
                    masked_payload = { **payload, 'message': '[masked]', 'targets': masked_phone }
                    logger.info(f"调用Spug发送提醒短信: url={url}, payload={masked_payload}, timeout={timeout}, auth={'yes' if token else 'no'}")
                    r = requests.post(url, data=payload, headers=headers, timeout=timeout)
                resp_text = str(getattr(r, 'text', ''))
                logger.info(f"Spug响应: status={getattr(r, 'status_code', None)}, text={resp_text[:200]}")
                try:
                    r.raise_for_status()
                except Exception as e:
                    logger.error(f"Spug短信发送失败: {e}")
                    return False
                try:
                    parsed = r.json()
                    if isinstance(parsed, dict):
                        code_val = parsed.get('code')
                        msg_val = str(parsed.get('msg', ''))
                        if code_val not in (200, '200'):
                            logger.error(f"Spug返回错误: code={code_val}, msg={msg_val}")
                            return False
                        if '不能为空' in msg_val or '失败' in msg_val:
                            logger.error(f"Spug返回提示失败: msg={msg_val}")
                            return False
                except Exception:
                    pass

                try:
                    if history is not None:
                        history.sent_at = timezone.now()
                        history.status = 'sent'
                        history.notification_methods = ['sms']
                        history.save(update_fields=['sent_at', 'status', 'notification_methods'])
                    elif reminder is not None:
                        from .history_models import ReminderHistory
                        ReminderHistory.objects.create(
                            user=user,
                            reminder=reminder,
                            title=title,
                            message=sms_text,
                            notification_methods=['sms'],
                            scheduled_time=timezone.now(),
                            reminder_type='scheduled',
                            status='sent',
                        )
                except Exception:
                    pass

                return True
            else:
                logger.info(f"模拟发送短信给 {user.phone}: {sms_text}")

                try:
                    if history is not None:
                        history.sent_at = timezone.now()
                        history.status = 'sent'
                        history.notification_methods = ['sms']
                        history.save(update_fields=['sent_at', 'status', 'notification_methods'])
                    elif reminder is not None:
                        from .history_models import ReminderHistory
                        ReminderHistory.objects.create(
                            user=user,
                            reminder=reminder,
                            title=title,
                            message=sms_text,
                            notification_methods=['sms'],
                            scheduled_time=timezone.now(),
                            reminder_type='scheduled',
                            status='sent',
                        )
                except Exception:
                    pass

                return True
            
        except Exception as e:
            logger.error(f"发送短信通知失败: {str(e)}")
            return False
    
    def _render_email_template(self, context):
        """
        渲染邮件模板
        """
        try:
            # 这里可以使用Django模板
            # return render_to_string('reminders/email_notification.html', context)
            
            # 简化的HTML模板
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>用药提醒</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>{title}</h2>
                </div>
                <div class="content">
                    <p>亲爱的 {username}，</p>
                    <p>{message}</p>
                    {reminder_info}
                    <p>请按时服药，保持健康！</p>
                </div>
                <div class="footer">
                    <p>此邮件由MTM用药助手自动发送，请勿回复。</p>
                    <p>发送时间: {current_time}</p>
                </div>
            </body>
            </html>
            """
            
            reminder_info = ""
            if context['reminder']:
                reminder = context['reminder']
                reminder_info = f"""
                <div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50;">
                    <p><strong>药品信息:</strong></p>
                    <ul>
                        <li>药品名称: {reminder.medicine.name}</li>
                        <li>服用剂量: {reminder.dosage} {reminder.get_dosage_unit_display()}</li>
                        <li>服用时机: {reminder.get_meal_timing_display()}</li>
                        <li>提醒时间: {reminder.reminder_time}</li>
                    </ul>
                </div>
                """
            
            return html_template.format(
                title=context['title'],
                username=context['user'].username,
                message=context['message'],
                reminder_info=reminder_info,
                current_time=context['current_time'].strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"渲染邮件模板失败: {str(e)}")
            return context['message']  # 降级到纯文本
    
    def _log_notification(self, user, title, message, notification_types, reminder):
        """
        记录通知历史
        """
        try:
            # 这里可以记录到数据库
            # NotificationLog.objects.create(
            #     user=user,
            #     reminder=reminder,
            #     title=title,
            #     message=message,
            #     notification_types=notification_types,
            #     sent_at=timezone.now()
            # )
            
            # 简化记录到日志
            logger.info(f"通知记录 - 用户: {user.username}, 标题: {title}, 类型: {notification_types}")
            
        except Exception as e:
            logger.error(f"记录通知历史失败: {str(e)}")
    
    def test_notification(self, user, notification_type='push'):
        """
        测试通知功能
        """
        test_title = "测试通知"
        test_message = "这是一条测试通知，用于验证通知功能是否正常工作。"
        
        return self._send_by_type(notification_type, user, test_title, test_message, None)
    
    def get_notification_settings(self, user):
        """
        获取用户的通知设置
        """
        # 这里可以从用户设置中获取
        # 简化返回默认设置
        return {
            'push_enabled': True,
            'email_enabled': bool(getattr(user, 'email', None)),
            'sms_enabled': bool(getattr(user, 'phone', None)),
            'quiet_hours': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }
    
    def is_quiet_time(self, user):
        """
        检查是否在免打扰时间
        """
        settings = self.get_notification_settings(user)
        if not settings['quiet_hours']['enabled']:
            return False
        
        now = timezone.now().time()
        start_time = timezone.datetime.strptime(settings['quiet_hours']['start_time'], '%H:%M').time()
        end_time = timezone.datetime.strptime(settings['quiet_hours']['end_time'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # 跨天的情况
            return now >= start_time or now <= end_time


# 全局通知服务实例
notification_service = NotificationService()
