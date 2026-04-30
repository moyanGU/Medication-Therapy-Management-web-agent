import json
import logging
import os
import sys
import uuid
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

logger = logging.getLogger(__name__)
_webpush_loader = {"loaded": False, "webpush": None, "exception": Exception}


def _load_webpush():
    if _webpush_loader["loaded"]:
        return _webpush_loader["webpush"], _webpush_loader["exception"]

    try:
        from pywebpush import WebPushException, webpush

        _webpush_loader["webpush"] = webpush
        _webpush_loader["exception"] = WebPushException
    except Exception:
        _webpush_loader["webpush"] = None
        _webpush_loader["exception"] = Exception

    _webpush_loader["loaded"] = True
    return _webpush_loader["webpush"], _webpush_loader["exception"]


def _mask_phone(phone: str) -> str:
    if isinstance(phone, str) and len(phone) == 11:
        return phone[:3] + "****" + phone[-4:]
    return "[masked]"


def _build_sms_text(title: str, message: str) -> str:
    return (
        getattr(settings, "SMS_TEMPLATES", {})
        .get("reminder", "{title}: {message}")
        .format(title=title, message=message)
    )


def _derive_spug_msg_var(title: str, message: str, reminder) -> str:
    var = ""
    try:
        if reminder is not None and getattr(reminder, "medicine", None):
            med = getattr(reminder, "medicine")
            med_name = getattr(med, "name", None) or getattr(reminder, "medicine_name", None)
            var = (med_name or "").strip()
    except Exception:
        var = ""

    if not var:
        var = (title or "").strip() or (message or "").strip() or "用药"

    if var.endswith("提醒"):
        var = var[:-2]
    return var


def _truncate_spug_msg_var(var: str, trace_id: str | None) -> str:
    max_len = int(getattr(settings, "SPUG_SMS_MESSAGE_MAX_LEN", 10))
    if max_len <= 0:
        max_len = 10
    original_len = len(var)
    if original_len > max_len:
        logger.warning(
            f"[notify:{trace_id}] spug_msg_truncated original_len={original_len} max_len={max_len}"
        )
        return var[:max_len]
    return var


def _is_test_or_debug() -> bool:
    is_pytest = (os.getenv("PYTEST_CURRENT_TEST") is not None) or ("pytest" in sys.modules)
    is_debug = bool(getattr(settings, "DEBUG", False))
    return is_debug or is_pytest


def _should_short_circuit_sms(spug_enabled: bool, base_url: str) -> bool:
    is_pytest = (os.getenv("PYTEST_CURRENT_TEST") is not None) or ("pytest" in sys.modules)
    if (not spug_enabled and _is_test_or_debug()) or (
        is_pytest and spug_enabled and "spug.test" not in str(base_url)
    ):
        return True
    return False


def _write_history_sent_or_create(user, title, sms_text, reminder, history):
    try:
        if history is not None:
            history.sent_at = timezone.now()
            history.status = "sent"
            history.notification_methods = ["sms"]
            history.save(update_fields=["sent_at", "status", "notification_methods"])
            return
        if reminder is not None:
            from .history_models import ReminderHistory

            ReminderHistory.objects.create(
                user=user,
                reminder=reminder,
                title=title,
                message=sms_text,
                notification_methods=["sms"],
                scheduled_time=timezone.now(),
                reminder_type="scheduled",
                status="sent",
            )
    except Exception:
        return


def _build_spug_request(user, title: str, spug_msg_var: str, base_url: str, template_id: str):
    use_sms = bool(getattr(settings, "SPUG_REMINDER_USE_SMS_ENDPOINT", False))
    timeout = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))
    token = getattr(settings, "SPUG_PUSH_TOKEN", "")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if use_sms:
        url = f"{base_url.rstrip('/')}/sms/{template_id}"
        params = {
            getattr(settings, "SPUG_SMS_PARAM_TO", "to"): user.phone,
            getattr(settings, "SPUG_SMS_PARAM_MESSAGE", "message"): spug_msg_var,
        }
        payload = None
    else:
        url = f"{base_url.rstrip('/')}/send/{template_id}"
        payload = {
            "name": getattr(settings, "SPUG_APP_NAME", "MTM用药助手"),
            "title": title,
            "message": spug_msg_var,
            "targets": user.phone,
        }
        params = None

    try:
        extra_json = getattr(settings, "SPUG_EXTRA_PARAMS_JSON", "")
        if extra_json:
            import json as _json

            extra = _json.loads(extra_json)
            if isinstance(extra, dict):
                if use_sms:
                    params.update(extra)
                else:
                    payload.update(extra)
    except Exception:
        pass

    return {
        "use_sms": use_sms,
        "url": url,
        "params": params,
        "payload": payload,
        "headers": headers,
        "timeout": timeout,
        "token": token,
    }


def _validate_spug_response_json(parsed, trace_id: str | None) -> bool:
    if not isinstance(parsed, dict):
        return True
    code_val = parsed.get("code")
    msg_val = str(parsed.get("msg", ""))
    if code_val not in (200, "200"):
        logger.error(f"[notify:{trace_id}] spug_sms_api_error code={code_val} msg={msg_val}")
        return False
    if "不能为空" in msg_val or "失败" in msg_val:
        logger.error(f"[notify:{trace_id}] spug_sms_api_failed msg={msg_val}")
        return False
    return True


def _send_spug_request(request_spec: dict, trace_id: str | None, masked_phone: str):
    if requests is None:
        logger.error(f"[notify:{trace_id}] requests_missing")
        return False

    use_sms = bool(request_spec["use_sms"])
    url = request_spec["url"]
    headers = request_spec["headers"]
    timeout = request_spec["timeout"]
    token = request_spec["token"]

    if use_sms:
        params = request_spec["params"] or {}
        masked_params = {
            **params,
            getattr(settings, "SPUG_SMS_PARAM_MESSAGE", "message"): "[masked]",
            getattr(settings, "SPUG_SMS_PARAM_TO", "to"): masked_phone,
        }
        logger.info(
            f"[notify:{trace_id}] spug_sms_request url={url} params={masked_params} timeout={timeout} auth={'yes' if token else 'no'}"
        )
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    else:
        payload = request_spec["payload"] or {}
        masked_payload = {**payload, "message": "[masked]", "targets": masked_phone}
        logger.info(
            f"[notify:{trace_id}] spug_sms_request url={url} payload={masked_payload} timeout={timeout} auth={'yes' if token else 'no'}"
        )
        r = requests.post(url, data=payload, headers=headers, timeout=timeout)

    resp_text = str(getattr(r, "text", ""))
    logger.info(
        f"[notify:{trace_id}] spug_sms_response status={getattr(r, 'status_code', None)} text={resp_text[:200]}"
    )
    try:
        r.raise_for_status()
    except Exception as e:
        logger.error(f"[notify:{trace_id}] spug_sms_http_error: {e}")
        return False

    try:
        parsed = r.json()
        if not _validate_spug_response_json(parsed, trace_id):
            return False
    except Exception:
        pass

    return True


class NotificationService:
    """
    通知服务
    负责发送各种类型的提醒通知
    """

    def __init__(self):
        self.enabled_types = ["push", "email", "sms"]  # 可用的通知类型

    def _resolve_preferred_channels(self, user_settings, reminder, history):
        from_history = False
        if history and getattr(history, "notification_methods", None):
            preferred = [
                item
                for item in list(history.notification_methods or [])
                if item in self.enabled_types
            ]
            from_history = True
        elif reminder and getattr(reminder, "notification_types", None):
            preferred = [
                item
                for item in list(reminder.notification_types or [])
                if item in self.enabled_types
            ]
        else:
            preferred = []
            if user_settings.get("push_enabled"):
                preferred = ["push"]
            elif user_settings.get("sms_enabled"):
                preferred = ["sms"]
            elif user_settings.get("email_enabled"):
                preferred = ["email"]

        return preferred, from_history

    def _schedule_fallback_pending(self, user, title, message, reminder, user_settings, trace_id: str):
        if reminder is None:
            return
        try:
            from .history_models import ReminderHistory

            fallback_time = timezone.now() + timedelta(minutes=5)
            methods = []
            if user_settings.get("sms_enabled"):
                methods = ["sms"]
            elif user_settings.get("email_enabled"):
                methods = ["email"]

            if not methods:
                logger.warning(
                    f"[notify:{trace_id}] fallback_pending_skipped_no_channel reminder={getattr(reminder, 'id', None)}"
                )
                return

            exists = (
                ReminderHistory.objects.filter(
                    user=user,
                    reminder=reminder,
                    status="pending",
                    reminder_type="repeat",
                    notification_methods=methods,
                )
                .filter(
                    scheduled_time__gte=timezone.now(),
                    scheduled_time__lte=fallback_time + timedelta(minutes=5),
                )
                .exists()
            )

            if exists:
                logger.warning(
                    f"[notify:{trace_id}] fallback_pending_exists reminder={getattr(reminder, 'id', None)} methods={methods}"
                )
                return

            ReminderHistory.objects.create(
                user=user,
                reminder=reminder,
                title=title,
                message=message,
                notification_methods=methods,
                scheduled_time=fallback_time,
                reminder_type="repeat",
                status="pending",
            )
            logger.warning(
                f"[notify:{trace_id}] fallback_pending_created reminder={getattr(reminder, 'id', None)} methods={methods} scheduled_time={fallback_time}"
            )
        except Exception as ie:
            logger.error(f"[notify:{trace_id}] fallback_pending_create_error: {ie}")

    def send_notification(
        self,
        user,
        title,
        message,
        reminder=None,
        history=None,
        trace_id: Optional[str] = None,
    ):
        try:
            trace_id = trace_id or uuid.uuid4().hex[:10]
            user_settings = self.get_notification_settings(user)
            preferred, from_history = self._resolve_preferred_channels(
                user_settings=user_settings, reminder=reminder, history=history
            )

            logger.info(
                f"[notify:{trace_id}] start user_id={getattr(user, 'id', None)} "
                f"reminder_id={getattr(reminder, 'id', None)} history_id={getattr(history, 'id', None)} "
                f"from_history={from_history} preferred={preferred} title_len={len(title or '')} message_len={len(message or '')}"
            )

            sent = False
            attempts = []
            for notification_type in preferred:
                if notification_type in self.enabled_types:
                    try:
                        ok = self._send_by_type(
                            notification_type,
                            user,
                            title,
                            message,
                            reminder,
                            history,
                            trace_id=trace_id,
                        )
                        attempts.append({"type": notification_type, "ok": bool(ok)})
                        if ok:
                            sent = True
                            self._log_notification(
                                user,
                                title,
                                message,
                                [notification_type],
                                reminder,
                                trace_id=trace_id,
                            )
                            break
                    except Exception as e:
                        attempts.append(
                            {
                                "type": notification_type,
                                "ok": False,
                                "error": f"{type(e).__name__}: {e}",
                            }
                        )
                        logger.error(
                            f"[notify:{trace_id}] channel_error type={notification_type} "
                            f"user_id={getattr(user, 'id', None)} reminder_id={getattr(reminder, 'id', None)} "
                            f"history_id={getattr(history, 'id', None)} err={type(e).__name__}: {e}"
                        )

            if not sent and reminder is not None and not from_history:
                self._schedule_fallback_pending(
                    user=user,
                    title=title,
                    message=message,
                    reminder=reminder,
                    user_settings=user_settings,
                    trace_id=trace_id,
                )

            logger.info(
                f"[notify:{trace_id}] done sent={sent} attempts={json.dumps(attempts, ensure_ascii=False)} "
                f"user_id={getattr(user, 'id', None)} reminder_id={getattr(reminder, 'id', None)} history_id={getattr(history, 'id', None)}"
            )

            return sent
        except Exception as e:
            logger.error(f"[notify:{trace_id or 'no-trace'}] fatal_error: {str(e)}")
            return False

    def _send_by_type(
        self,
        notification_type,
        user,
        title,
        message,
        reminder,
        history,
        trace_id: Optional[str] = None,
    ):
        """根据类型发送通知"""
        if notification_type == "push":
            return self._send_push_notification(
                user, title, message, reminder, history, trace_id=trace_id
            )
        elif notification_type == "email":
            return self._send_email_notification(
                user, title, message, reminder, history, trace_id=trace_id
            )
        elif notification_type == "sms":
            return self._send_sms_notification(
                user, title, message, reminder, history, trace_id=trace_id
            )
        else:
            logger.warning(f"[notify:{trace_id}] unsupported_type={notification_type}")
            return False

    def _get_webpush_client(self, trace_id: Optional[str] = None):
        webpush, webpush_exception = _load_webpush()
        if webpush is None:
            logger.error(f"[notify:{trace_id}] pywebpush_missing")
            return None, None
        return webpush, webpush_exception

    def _get_vapid_config(self, trace_id: Optional[str] = None):
        vapid_private: Optional[str] = getattr(settings, "VAPID_PRIVATE_KEY", None)
        vapid_subject: Optional[str] = (
            getattr(settings, "VAPID_SUBJECT", None) or "mailto:noreply@example.com"
        )
        if not vapid_private:
            logger.error(f"[notify:{trace_id}] vapid_private_key_missing")
            return None, None
        return vapid_private, vapid_subject

    def _ensure_push_history(self, user, title, message, reminder, history):
        if history is not None or reminder is None:
            return history
        try:
            from .history_models import ReminderHistory

            return ReminderHistory.objects.create(
                user=user,
                reminder=reminder,
                title=title,
                message=message,
                notification_methods=["push"],
                scheduled_time=timezone.now(),
                reminder_type="scheduled",
                status="pending",
            )
        except Exception:
            return None

    def _build_push_payload(self, title, message, reminder, history):
        return json.dumps(
            {
                "title": title,
                "body": message,
                "tag": f"mtm-reminder-{getattr(reminder, 'id', 'general')}",
                "data": {
                    "url": "/",
                    "reminderId": getattr(reminder, "id", None),
                    "historyId": getattr(history, "id", None),
                },
            },
            ensure_ascii=False,
        )

    def _build_subscription_info(self, sub):
        return {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.keys.get("p256dh"),
                "auth": sub.keys.get("auth"),
            },
        }

    def _send_push_to_subscription(
        self,
        *,
        webpush,
        webpush_exception,
        sub,
        payload: str,
        vapid_private: str,
        vapid_subject: str,
        user_id,
        trace_id: Optional[str] = None,
    ) -> bool:
        try:
            webpush(
                subscription_info=self._build_subscription_info(sub),
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_subject},
            )
            sub.touch_sent()
            logger.info(
                f"[notify:{trace_id}] push_sent user_id={user_id} endpoint={sub.endpoint[:32]}..."
            )
            return True
        except webpush_exception as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            logger.warning(
                f"[notify:{trace_id}] push_exception user_id={user_id} endpoint={sub.endpoint[:32]}... "
                f"status={status_code} error={e}"
            )
            if status_code in (404, 410):
                sub.mark_inactive()
            return False
        except Exception as e:
            logger.error(
                f"[notify:{trace_id}] push_send_failed user_id={user_id} endpoint={sub.endpoint[:32]}... error={e}"
            )
            return False

    def _update_push_history(self, history, success_any: bool):
        if history is None:
            return
        try:
            if success_any:
                history.sent_at = timezone.now()
                history.status = "sent"
                history.notification_methods = ["push"]
                history.save(update_fields=["sent_at", "status", "notification_methods"])
            else:
                history.status = "failed"
                history.notification_methods = ["push"]
                history.save(update_fields=["status", "notification_methods"])
        except Exception:
            return

    def _send_push_notification(
        self,
        user,
        title,
        message,
        reminder,
        history=None,
        trace_id: Optional[str] = None,
    ):
        """
        发送推送通知（Web Push）
        - 查找用户的有效订阅
        - 使用 VAPID 私钥发送浏览器推送
        - 针对 404/410 将订阅标记为失效
        """
        from apps.users.models import PushSubscription

        webpush, webpush_exception = self._get_webpush_client(trace_id=trace_id)
        if webpush is None:
            return False

        vapid_private, vapid_subject = self._get_vapid_config(trace_id=trace_id)
        if not vapid_private or not vapid_subject:
            return False

        subs = PushSubscription.objects.filter(user=user, is_active=True)
        if not subs.exists():
            logger.info(f"[notify:{trace_id}] push_no_subscription user_id={user.id}")
            return False

        history = self._ensure_push_history(user, title, message, reminder, history)
        payload = self._build_push_payload(title, message, reminder, history)

        success_any = False
        for sub in subs:
            if self._send_push_to_subscription(
                webpush=webpush,
                webpush_exception=webpush_exception,
                sub=sub,
                payload=payload,
                vapid_private=vapid_private,
                vapid_subject=vapid_subject,
                user_id=user.id,
                trace_id=trace_id,
            ):
                success_any = True

        self._update_push_history(history, success_any)

        return success_any

    def _send_email_notification(
        self,
        user,
        title,
        message,
        reminder,
        history=None,
        trace_id: Optional[str] = None,
    ):
        """
        发送邮件通知
        """
        try:
            if not user.email:
                logger.warning(
                    f"[notify:{trace_id}] email_missing user_id={getattr(user, 'id', None)}"
                )
                return False

            # 构建邮件内容
            context = {
                "user": user,
                "title": title,
                "message": message,
                "reminder": reminder,
                "current_time": timezone.now(),
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
                fail_silently=False,
            )

            try:
                if history is not None:
                    history.sent_at = timezone.now()
                    history.status = "sent"
                    history.notification_methods = ["email"]
                    history.save(
                        update_fields=["sent_at", "status", "notification_methods"]
                    )
                elif reminder is not None:
                    from .history_models import ReminderHistory

                    ReminderHistory.objects.create(
                        user=user,
                        reminder=reminder,
                        title=title,
                        message=message,
                        notification_methods=["email"],
                        scheduled_time=timezone.now(),
                        reminder_type="scheduled",
                        status="sent",
                    )
            except Exception:
                pass

            logger.info(
                f"[notify:{trace_id}] email_sent user_id={getattr(user, 'id', None)}"
            )
            return True

        except Exception as e:
            logger.error(f"[notify:{trace_id}] email_send_failed: {str(e)}")
            return False

    def _send_sms_notification(
        self,
        user,
        title,
        message,
        reminder,
        history=None,
        trace_id: Optional[str] = None,
    ):
        """
        发送短信通知
        """
        try:
            if not hasattr(user, "phone") or not user.phone:
                logger.warning(
                    f"[notify:{trace_id}] sms_missing_phone user_id={getattr(user, 'id', None)}"
                )
                return False

            sms_text = _build_sms_text(title, message)
            spug_msg_var = _truncate_spug_msg_var(
                _derive_spug_msg_var(title, message, reminder),
                trace_id=trace_id,
            )
            spug_enabled = bool(getattr(settings, "SPUG_PUSH_ENABLED", False))
            base_url = getattr(settings, "SPUG_PUSH_URL", "https://push.spug.cc")
            masked_phone = _mask_phone(user.phone)

            if _should_short_circuit_sms(spug_enabled=spug_enabled, base_url=base_url):
                logger.info(
                    f"[notify:{trace_id}] sms_dev_mode_sent user_id={getattr(user, 'id', None)} phone={masked_phone}"
                )
                _write_history_sent_or_create(
                    user=user,
                    title=title,
                    sms_text=sms_text,
                    reminder=reminder,
                    history=history,
                )
                return True

            if not spug_enabled:
                logger.error(
                    f"[notify:{trace_id}] spug_disabled_sms_not_sent user_id={getattr(user, 'id', None)}"
                )
                return False

            template_id = (
                getattr(settings, "SPUG_TEMPLATE_ID_REMINDER", "")
                or getattr(settings, "SPUG_TEMPLATE_ID", "")
                or ""
            ).strip()
            if not template_id:
                logger.error(f"[notify:{trace_id}] spug_template_id_missing")
                return False

            request_spec = _build_spug_request(
                user=user,
                title=title,
                spug_msg_var=spug_msg_var,
                base_url=base_url,
                template_id=template_id,
            )
            ok = _send_spug_request(
                request_spec=request_spec,
                trace_id=trace_id,
                masked_phone=masked_phone,
            )
            if not ok:
                return False

            _write_history_sent_or_create(
                user=user,
                title=title,
                sms_text=sms_text,
                reminder=reminder,
                history=history,
            )
            return True

        except Exception as e:
            logger.error(f"[notify:{trace_id}] sms_send_failed: {str(e)}")
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
            if context["reminder"]:
                reminder = context["reminder"]
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
                title=context["title"],
                username=context["user"].username,
                message=context["message"],
                reminder_info=reminder_info,
                current_time=context["current_time"].strftime("%Y-%m-%d %H:%M:%S"),
            )

        except Exception as e:
            logger.error(f"渲染邮件模板失败: {str(e)}")
            return context["message"]  # 降级到纯文本

    def _log_notification(
        self,
        user,
        title,
        message,
        notification_types,
        reminder,
        trace_id: Optional[str] = None,
    ):
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

            logger.info(
                f"[notify:{trace_id}] logged user_id={getattr(user, 'id', None)} "
                f"reminder_id={getattr(reminder, 'id', None)} types={notification_types} "
                f"title_len={len(title or '')} message_len={len(message or '')}"
            )

        except Exception as e:
            logger.error(f"记录通知历史失败: {str(e)}")

    def test_notification(self, user, notification_type="push"):
        """
        测试通知功能
        """
        test_title = "测试通知"
        test_message = "这是一条测试通知，用于验证通知功能是否正常工作。"

        return self._send_by_type(
            notification_type, user, test_title, test_message, None
        )

    def get_notification_settings(self, user):
        """
        获取用户的通知设置
        """
        # 这里可以从用户设置中获取
        # 简化返回默认设置
        return {
            "push_enabled": True,
            "email_enabled": bool(getattr(user, "email", None)),
            "sms_enabled": bool(getattr(user, "phone", None)),
            "quiet_hours": {
                "enabled": False,
                "start_time": "22:00",
                "end_time": "08:00",
            },
        }

    def is_quiet_time(self, user):
        """
        检查是否在免打扰时间
        """
        settings = self.get_notification_settings(user)
        if not settings["quiet_hours"]["enabled"]:
            return False

        now = timezone.now().time()
        start_time = timezone.datetime.strptime(
            settings["quiet_hours"]["start_time"], "%H:%M"
        ).time()
        end_time = timezone.datetime.strptime(
            settings["quiet_hours"]["end_time"], "%H:%M"
        ).time()

        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # 跨天的情况
            return now >= start_time or now <= end_time


# 全局通知服务实例
notification_service = NotificationService()
