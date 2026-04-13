from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.medicines.models import Medicine
from apps.reminders.history_models import ReminderHistory
from apps.reminders.models import Reminder
from apps.reminders.notifications import NotificationService
from apps.users.models import PushSubscription


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class FailureFallbackPendingTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="ffp_user",
            password="pass123",
            email="ffp@example.com",
            phone="13800000003",
        )
        self.medicine = Medicine.objects.create(user=self.user, name="维生素K")
        self.reminder = Reminder.objects.create(
            user=self.user,
            medicine=self.medicine,
            reminder_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            start_date=timezone.now().date(),
            frequency="daily",
            dosage=1,
            dosage_unit="tablet",
            is_active=True,
            notification_types=["push", "sms", "email"],
        )

    def test_pending_history_created_when_all_methods_fail(self):
        svc = NotificationService()
        with patch.object(NotificationService, "_send_by_type", return_value=False):
            ok = svc.send_notification(
                user=self.user,
                title="用药提醒",
                message="请按时服用维生素K",
                reminder=self.reminder,
            )
        self.assertFalse(ok)
        qs = ReminderHistory.objects.filter(
            user=self.user, reminder=self.reminder, status="pending"
        )
        self.assertEqual(qs.count(), 1)
        h = qs.first()
        self.assertIn("sms", h.notification_methods)  # 用户有手机号，默认回退短信
        self.assertGreater(h.scheduled_time, timezone.now())

    def test_pending_history_deduplicated_within_window(self):
        svc = NotificationService()
        with patch.object(NotificationService, "_send_by_type", return_value=False):
            ok1 = svc.send_notification(
                user=self.user,
                title="用药提醒",
                message="请按时服用维生素K",
                reminder=self.reminder,
                trace_id="t-dedup-1",
            )
            ok2 = svc.send_notification(
                user=self.user,
                title="用药提醒",
                message="请按时服用维生素K",
                reminder=self.reminder,
                trace_id="t-dedup-2",
            )
        self.assertFalse(ok1)
        self.assertFalse(ok2)
        qs = ReminderHistory.objects.filter(
            user=self.user, reminder=self.reminder, status="pending"
        )
        self.assertEqual(qs.count(), 1)

    def test_send_notification_logs_trace_id_start_and_done(self):
        svc = NotificationService()
        with patch.object(NotificationService, "_send_by_type", return_value=False):
            with self.assertLogs("apps.reminders.notifications", level="INFO") as cm:
                ok = svc.send_notification(
                    user=self.user,
                    title="用药提醒",
                    message="请按时服用维生素K",
                    reminder=self.reminder,
                    trace_id="t-log-1",
                )
        self.assertFalse(ok)
        joined = "\n".join(cm.output)
        self.assertIn("[notify:t-log-1] start", joined)
        self.assertIn("[notify:t-log-1] done sent=False", joined)

    @override_settings(VAPID_PRIVATE_KEY="test-private-key")
    def test_push_notification_returns_false_when_pywebpush_missing(self):
        PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.com/sub-1",
            keys={"p256dh": "k1", "auth": "a1"},
        )
        svc = NotificationService()

        with patch(
            "apps.reminders.notifications._load_webpush",
            return_value=(None, Exception),
        ):
            with self.assertLogs("apps.reminders.notifications", level="ERROR") as cm:
                ok = svc._send_push_notification(
                    self.user,
                    "用药提醒",
                    "请按时服用维生素K",
                    self.reminder,
                    trace_id="t-push-missing",
                )

        self.assertFalse(ok)
        joined = "\n".join(cm.output)
        self.assertIn("[notify:t-push-missing] pywebpush_missing", joined)

    @override_settings(VAPID_PRIVATE_KEY="test-private-key")
    def test_push_notification_marks_subscription_inactive_on_410(self):
        subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.com/sub-2",
            keys={"p256dh": "k2", "auth": "a2"},
        )
        svc = NotificationService()

        class _DummyWebPushException(Exception):
            def __init__(self, response):
                super().__init__("gone")
                self.response = response

        class _DummyResponse:
            status_code = 410

        def _mock_webpush(**kwargs):
            raise _DummyWebPushException(_DummyResponse())

        with patch(
            "apps.reminders.notifications._load_webpush",
            return_value=(_mock_webpush, _DummyWebPushException),
        ):
            ok = svc._send_push_notification(
                self.user,
                "用药提醒",
                "请按时服用维生素K",
                self.reminder,
                trace_id="t-push-410",
            )

        self.assertFalse(ok)
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)

    @override_settings(VAPID_PRIVATE_KEY="")
    def test_push_notification_returns_false_when_vapid_key_missing(self):
        PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.com/sub-3",
            keys={"p256dh": "k3", "auth": "a3"},
        )
        svc = NotificationService()

        with patch(
            "apps.reminders.notifications._load_webpush",
            return_value=(object(), Exception),
        ):
            with self.assertLogs("apps.reminders.notifications", level="ERROR") as cm:
                ok = svc._send_push_notification(
                    self.user,
                    "用药提醒",
                    "请按时服用维生素K",
                    self.reminder,
                    trace_id="t-push-no-vapid",
                )

        self.assertFalse(ok)
        joined = "\n".join(cm.output)
        self.assertIn(
            "[notify:t-push-no-vapid] vapid_private_key_missing",
            joined,
        )

    @override_settings(VAPID_PRIVATE_KEY="test-private-key")
    def test_push_notification_marks_history_failed_when_send_fails(self):
        PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.com/sub-4",
            keys={"p256dh": "k4", "auth": "a4"},
        )
        history = ReminderHistory.objects.create(
            user=self.user,
            reminder=self.reminder,
            title="用药提醒",
            message="请按时服用维生素K",
            notification_methods=["push"],
            scheduled_time=timezone.now(),
            reminder_type="scheduled",
            status="pending",
        )
        svc = NotificationService()

        class _DummyWebPushException(Exception):
            pass

        def _mock_webpush(**kwargs):
            raise _DummyWebPushException("push failed")

        with patch(
            "apps.reminders.notifications._load_webpush",
            return_value=(_mock_webpush, _DummyWebPushException),
        ):
            ok = svc._send_push_notification(
                self.user,
                "用药提醒",
                "请按时服用维生素K",
                self.reminder,
                history=history,
                trace_id="t-push-history-failed",
            )

        self.assertFalse(ok)
        history.refresh_from_db()
        self.assertEqual(history.status, "failed")
        self.assertEqual(history.notification_methods, ["push"])
