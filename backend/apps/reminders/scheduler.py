import logging
import sys
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from .history_models import ReminderHistory
from .models import Reminder
from .notifications import NotificationService

logger = logging.getLogger(__name__)

# Fallback logging to ensure INFO-level messages from scheduler are visible in container logs
# If Django's LOGGING doesn't attach a handler to this module, we attach one.
if not logger.handlers:
    logger.propagate = False  # avoid duplicate logs if parent handlers exist
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


class ReminderScheduler:
    """
    用药提醒调度器
    负责检查和发送提醒通知
    """

    def __init__(self):
        self.notification_service = NotificationService()

    def check_and_send_reminders(self):
        """
        检查并发送当前时间需要的提醒
        """
        # 统一使用本地时区时间，避免 USE_TZ=True 时出现 UTC 与本地时间不一致导致匹配失败
        now = timezone.localtime()
        current_time = now.time()
        current_date = now.date()

        logger.info(f"开始检查提醒，当前时间: {now}")

        # 获取所有激活的提醒
        active_reminders = (
            Reminder.objects.filter(is_active=True, start_date__lte=current_date)
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=current_date))
            .select_related("user", "medicine")
        )

        logger.info(
            f"激活提醒数量: {active_reminders.count()} (date={current_date}, time={current_time})"
        )

        sent_count = 0

        for reminder in active_reminders:
            try:
                # Snapshot key fields for visibility when evaluating each reminder
                last_local = (
                    timezone.localtime(reminder.last_reminded_at)
                    if reminder.last_reminded_at
                    else None
                )
                logger.info(
                    f"[candidate:{reminder.id}] user={reminder.user_id} time={reminder.reminder_time} "
                    f"advance={reminder.advance_minutes} freq={reminder.frequency} weekdays={getattr(reminder, 'weekdays', None)} "
                    f"start={reminder.start_date} end={reminder.end_date} last={last_local} "
                    f"types={getattr(reminder, 'notification_types', None)} active={reminder.is_active}")
                if self._should_send_reminder(reminder, now):
                    self._send_reminder(reminder)
                    sent_count += 1
            except Exception as e:
                logger.error(f"发送提醒失败 {reminder.id}: {str(e)}")

        # 处理待发送历史（如用户延迟5分钟后的补发）
        try:
            pending_qs = ReminderHistory.objects.filter(
                status="pending", scheduled_time__lte=now
            ).select_related("user", "reminder")
            logger.info(f"待发送历史记录数量: {pending_qs.count()} (<= {now})")
            for h in pending_qs:
                try:
                    trace_id = f"his-{h.id}-{int(now.timestamp())}"
                    ok = self.notification_service.send_notification(
                        user=h.user,
                        title=h.title,
                        message=h.message,
                        reminder=h.reminder,
                        history=h,
                        trace_id=trace_id,
                    )
                    if ok:
                        h.sent_at = timezone.now()
                        h.status = "sent"
                        h.save(update_fields=["sent_at", "status"])
                        if h.reminder:
                            h.reminder.increment_reminder_count()
                        sent_count += 1
                    else:
                        h.status = "failed"
                        h.save(update_fields=["status"])
                        logger.warning(
                            f"[notify:{trace_id}] pending_send_failed history_id={h.id} "
                            f"prev_methods={list(h.notification_methods or [])} reminder_id={getattr(h.reminder, 'id', None)}")
                        # 升级备用通道：根据历史记录的通道与用户设置，创建5分钟后重试的待发送记录
                        try:
                            prev = list(h.notification_methods or [])
                            settings = (
                                self.notification_service.get_notification_settings(
                                    h.user
                                )
                            )
                            # 简单升级策略：push->sms->email->push
                            next_methods = []
                            if "push" in prev:
                                if settings.get("sms_enabled"):
                                    next_methods = ["sms"]
                                elif settings.get("email_enabled"):
                                    next_methods = ["email"]
                            elif "sms" in prev:
                                if settings.get("email_enabled"):
                                    next_methods = ["email"]
                                elif settings.get("push_enabled"):
                                    next_methods = ["push"]
                            elif "email" in prev:
                                if settings.get("push_enabled"):
                                    next_methods = ["push"]
                                elif settings.get("sms_enabled"):
                                    next_methods = ["sms"]

                            if next_methods:
                                # 避免为同一提醒和通道在短时间内创建多条补发记录
                                retry_time = now + timedelta(minutes=5)
                                exists = (
                                    ReminderHistory.objects.filter(
                                        user=h.user,
                                        reminder=h.reminder,
                                        status="pending",
                                        reminder_type="repeat",
                                        notification_methods=next_methods,
                                    )
                                    .filter(
                                        scheduled_time__gte=now,
                                        scheduled_time__lte=retry_time
                                        + timedelta(minutes=5),
                                    )
                                    .exists()
                                )

                                if exists:
                                    logger.info(
                                        f"[notify:{trace_id}] escalation_pending_exists history_id={h.id} "
                                        f"methods={next_methods} retry_time={retry_time}")
                                else:
                                    ReminderHistory.objects.create(
                                        user=h.user,
                                        reminder=h.reminder,
                                        title="补发提醒",
                                        message=h.message,
                                        notification_methods=next_methods,
                                        scheduled_time=retry_time,
                                        reminder_type="repeat",
                                        status="pending",
                                    )
                                    logger.info(
                                        f"[notify:{trace_id}] escalation_pending_created history_id={h.id} "
                                        f"methods={next_methods} retry_time={retry_time}")
                        except Exception as ie:
                            logger.error(
                                f"[notify:{trace_id}] escalation_error history_id={h.id}: {ie}"
                            )
                except Exception as e:
                    logger.error(f"发送待历史提醒失败 history={h.id}: {e}")
        except Exception as e:
            logger.error(f"查询待发送历史失败: {e}")

        logger.info(f"提醒检查完成，发送了 {sent_count} 个提醒")
        return sent_count

    def _should_send_reminder(self, reminder, now):
        """
        判断是否应该发送提醒
        """
        # 确保比较均使用本地时区
        now_local = timezone.localtime(now)
        current_time = now_local.time()
        current_date = now_local.date()
        logger.debug(
            f"[check:{reminder.id}] now_local={now_local} original_time={reminder.reminder_time} advance={reminder.advance_minutes}"
        )

        # 检查今天是否应该提醒
        if not reminder.should_remind_today():
            logger.info(
                f"[skip:{reminder.id}] 今天不需要提醒 (frequency={reminder.frequency}, start={reminder.start_date}, end={reminder.end_date})"
            )
            return False

        # 计算提醒时间（考虑提前提醒）
        reminder_time = reminder.reminder_time
        if reminder.advance_minutes > 0:
            reminder_datetime = timezone.datetime.combine(current_date, reminder_time)
            # 转为本地时区的 aware datetime 再进行提前分钟处理
            reminder_datetime = timezone.localtime(
                timezone.make_aware(reminder_datetime)
            )
            reminder_datetime -= timedelta(minutes=reminder.advance_minutes)
            reminder_time = reminder_datetime.time()
        logger.debug(
            f"[adjusted_time:{reminder.id}] current={current_time} reminder={reminder_time} advance={reminder.advance_minutes}"
        )

        # 检查时间是否匹配（允许1分钟误差）
        time_diff = abs(
            (current_time.hour * 60 + current_time.minute)
            - (reminder_time.hour * 60 + reminder_time.minute)
        )

        if time_diff > 1:  # 超过1分钟误差
            logger.info(
                f"[skip:{reminder.id}] 时间未命中 current={current_time} reminder={reminder_time} diff={time_diff}min advance={reminder.advance_minutes}"
            )
            return False
        else:
            logger.debug(
                f"[hit_time:{reminder.id}] current={current_time} reminder={reminder_time} diff={time_diff}min advance={reminder.advance_minutes}"
            )

        # 检查是否已经在今天发送过
        if reminder.last_reminded_at:
            last_reminded_local = timezone.localtime(reminder.last_reminded_at)
            last_reminded_date = last_reminded_local.date()
            if last_reminded_date == current_date:
                # 如果设置了重复提醒，检查重复间隔
                if reminder.repeat_interval > 0 and reminder.max_repeats > 0:
                    time_since_last = now_local - last_reminded_local
                    if time_since_last.total_seconds() >= reminder.repeat_interval * 60:
                        # 检查今天的重复次数
                        today_count = self._get_today_reminder_count(
                            reminder, current_date
                        )
                        logger.info(
                            f"[repeat:{reminder.id}] last={last_reminded_local}, since={int(time_since_last.total_seconds())}s, today_count={today_count}/{reminder.max_repeats}"
                        )
                        if today_count < reminder.max_repeats:
                            return True
                logger.info(
                    f"[skip:{reminder.id}] 今天已提醒过 (last={last_reminded_local}, repeat_interval={reminder.repeat_interval}, max_repeats={reminder.max_repeats})"
                )
                return False

        return True

    def _get_today_reminder_count(self, reminder, date):
        """
        获取今天已发送的提醒次数
        """
        current_tz = timezone.get_current_timezone()
        start_of_day = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time()),
            current_tz,
        )
        end_of_day = start_of_day + timedelta(days=1)

        return ReminderHistory.objects.filter(
            reminder=reminder,
            status="sent",
            sent_at__gte=start_of_day,
            sent_at__lt=end_of_day,
        ).count()

    def _send_reminder(self, reminder):
        """
        发送提醒通知
        """
        try:
            # 构建提醒消息
            message = reminder.get_default_message()
            title = reminder.title or f"用药提醒 - {reminder.medicine.name}"

            # 发送通知
            success = self.notification_service.send_notification(
                user=reminder.user,
                title=title,
                message=message,
                reminder=reminder,
                trace_id=f"sch-{reminder.id}-{int(timezone.now().timestamp())}",
            )

            if success:
                # 更新提醒统计
                reminder.increment_reminder_count()
                logger.info(f"成功发送提醒 {reminder.id} 给用户 {reminder.user.username}")
            else:
                logger.warning(f"发送提醒失败 {reminder.id}")

            return success

        except Exception as e:
            logger.error(f"发送提醒异常 {reminder.id}: {str(e)}")
            return False

    def get_upcoming_reminders(self, user, hours=24):
        """
        获取用户未来指定小时内的提醒
        """
        now = timezone.now()
        end_time = now + timedelta(hours=hours)

        reminders = (
            Reminder.objects.filter(
                user=user, is_active=True, start_date__lte=end_time.date()
            )
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=now.date()))
            .order_by("reminder_time")
        )

        upcoming = []
        current_date = now.date()

        # 检查今天和明天的提醒
        for days_ahead in range(2):
            check_date = current_date + timedelta(days=days_ahead)

            for reminder in reminders:
                # 模拟检查该日期是否应该提醒
                if self._should_remind_on_date(reminder, check_date):
                    reminder_datetime = timezone.datetime.combine(
                        check_date, reminder.reminder_time
                    )
                    reminder_datetime = timezone.make_aware(reminder_datetime)

                    # 考虑提前提醒时间
                    if reminder.advance_minutes > 0:
                        reminder_datetime -= timedelta(minutes=reminder.advance_minutes)

                    if now <= reminder_datetime <= end_time:
                        upcoming.append(
                            {
                                "reminder": reminder,
                                "datetime": reminder_datetime,
                                "date": check_date,
                            }
                        )

        # 按时间排序
        upcoming.sort(key=lambda x: x["datetime"])
        return upcoming

    def _should_remind_on_date(self, reminder, date):
        """
        检查指定日期是否应该提醒
        """
        # 检查是否在有效期内
        if date < reminder.start_date:
            return False
        if reminder.end_date and date > reminder.end_date:
            return False

        # 根据频率判断
        if reminder.frequency == "daily":
            return True
        elif reminder.frequency == "every_other_day":
            days_diff = (date - reminder.start_date).days
            return days_diff % 2 == 0
        elif reminder.frequency == "weekly":
            days_diff = (date - reminder.start_date).days
            return days_diff % 7 == 0
        elif reminder.frequency == "custom":
            weekday = date.weekday() + 1  # 转换为1-7
            return weekday in reminder.weekdays
        elif reminder.frequency in [
            "twice_daily",
            "three_times_daily",
            "four_times_daily",
        ]:
            return True  # 这些频率每天都需要提醒

        return False

    def cleanup_old_reminders(self, days=30):
        """
        清理过期的提醒
        """
        cutoff_date = timezone.now().date() - timedelta(days=days)

        expired_reminders = Reminder.objects.filter(
            end_date__lt=cutoff_date, is_active=False
        )

        count = expired_reminders.count()
        expired_reminders.delete()

        logger.info(f"清理了 {count} 个过期提醒")
        return count


# 全局调度器实例
scheduler = ReminderScheduler()
