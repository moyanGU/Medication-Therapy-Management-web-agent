import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import json
from typing import Optional

try:
    # 运行环境未安装时避免导入错误，具体发送时再做校验
    from pywebpush import webpush, WebPushException
except Exception:  # pragma: no cover
    webpush = None
    WebPushException = Exception

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务
    负责发送各种类型的提醒通知
    """
    
    def __init__(self):
        self.enabled_types = ['push', 'email']  # 可用的通知类型
    
    def send_notification(self, user, title, message, reminder=None):
        """
        发送通知
        """
        try:
            notification_types = reminder.notification_types if reminder else ['push']
            success_count = 0
            
            for notification_type in notification_types:
                if notification_type in self.enabled_types:
                    if self._send_by_type(notification_type, user, title, message, reminder):
                        success_count += 1
            
            # 记录通知历史
            self._log_notification(user, title, message, notification_types, reminder)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            return False
    
    def _send_by_type(self, notification_type, user, title, message, reminder):
        """
        根据类型发送通知
        """
        try:
            if notification_type == 'push':
                return self._send_push_notification(user, title, message, reminder)
            elif notification_type == 'email':
                return self._send_email_notification(user, title, message, reminder)
            elif notification_type == 'sms':
                return self._send_sms_notification(user, title, message, reminder)
            else:
                logger.warning(f"不支持的通知类型: {notification_type}")
                return False
        except Exception as e:
            logger.error(f"发送 {notification_type} 通知失败: {str(e)}")
            return False
    
    def _send_push_notification(self, user, title, message, reminder):
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

        payload = json.dumps({
            'title': title,
            'body': message,
            'data': {
                'url': '/',
                'reminderId': getattr(reminder, 'id', None),
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
            except WebPushException as e:
                # 404/410 表示订阅失效
                status_code = getattr(getattr(e, 'response', None), 'status_code', None)
                logger.warning(f"WebPushException user={user.id} endpoint={sub.endpoint[:32]}... status={status_code} error={e}")
                if status_code in (404, 410):
                    sub.mark_inactive()
            except Exception as e:
                logger.error(f"Web Push 发送失败 user={user.id} endpoint={sub.endpoint[:32]}... error={e}")

        return success_any
    
    def _send_email_notification(self, user, title, message, reminder):
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
            
            logger.info(f"邮件通知发送成功给 {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件通知失败: {str(e)}")
            return False
    
    def _send_sms_notification(self, user, title, message, reminder):
        """
        发送短信通知
        """
        try:
            if not hasattr(user, 'phone') or not user.phone:
                logger.warning(f"用户 {user.username} 没有手机号")
                return False
            
            # 这里应该集成短信服务提供商的API
            # 例如：阿里云短信、腾讯云短信等
            
            # 模拟发送短信
            logger.info(f"模拟发送短信给 {user.phone}: {message}")
            
            # 在实际应用中，这里会调用短信API
            # sms_result = sms_client.send_sms(
            #     phone_number=user.phone,
            #     message=message
            # )
            # return sms_result.success
            
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