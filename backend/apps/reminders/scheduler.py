import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Reminder
from .notifications import NotificationService

logger = logging.getLogger(__name__)


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
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        
        logger.info(f"开始检查提醒，当前时间: {now}")
        
        # 获取所有激活的提醒
        active_reminders = Reminder.objects.filter(
            is_active=True,
            start_date__lte=current_date
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=current_date)
        ).select_related('user', 'medicine')
        
        sent_count = 0
        
        for reminder in active_reminders:
            try:
                if self._should_send_reminder(reminder, now):
                    self._send_reminder(reminder)
                    sent_count += 1
            except Exception as e:
                logger.error(f"发送提醒失败 {reminder.id}: {str(e)}")
        
        logger.info(f"提醒检查完成，发送了 {sent_count} 个提醒")
        return sent_count
    
    def _should_send_reminder(self, reminder, now):
        """
        判断是否应该发送提醒
        """
        current_time = now.time()
        current_date = now.date()
        
        # 检查今天是否应该提醒
        if not reminder.should_remind_today():
            return False
        
        # 计算提醒时间（考虑提前提醒）
        reminder_time = reminder.reminder_time
        if reminder.advance_minutes > 0:
            reminder_datetime = timezone.datetime.combine(current_date, reminder_time)
            reminder_datetime = timezone.make_aware(reminder_datetime)
            reminder_datetime -= timedelta(minutes=reminder.advance_minutes)
            reminder_time = reminder_datetime.time()
        
        # 检查时间是否匹配（允许1分钟误差）
        time_diff = abs(
            (current_time.hour * 60 + current_time.minute) -
            (reminder_time.hour * 60 + reminder_time.minute)
        )
        
        if time_diff > 1:  # 超过1分钟误差
            return False
        
        # 检查是否已经在今天发送过
        if reminder.last_reminded_at:
            last_reminded_date = reminder.last_reminded_at.date()
            if last_reminded_date == current_date:
                # 如果设置了重复提醒，检查重复间隔
                if reminder.repeat_interval > 0 and reminder.max_repeats > 0:
                    time_since_last = now - reminder.last_reminded_at
                    if time_since_last.total_seconds() >= reminder.repeat_interval * 60:
                        # 检查今天的重复次数
                        today_count = self._get_today_reminder_count(reminder, current_date)
                        if today_count < reminder.max_repeats:
                            return True
                return False
        
        return True
    
    def _get_today_reminder_count(self, reminder, date):
        """
        获取今天已发送的提醒次数
        这里简化处理，实际应该有专门的提醒历史记录表
        """
        if not reminder.last_reminded_at:
            return 0
        
        if reminder.last_reminded_at.date() == date:
            # 简化计算，基于最后提醒时间和重复间隔估算
            time_diff = timezone.now() - reminder.last_reminded_at
            return min(
                int(time_diff.total_seconds() / (reminder.repeat_interval * 60)) + 1,
                reminder.max_repeats
            )
        
        return 0
    
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
                reminder=reminder
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
        
        reminders = Reminder.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=end_time.date()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now.date())
        ).order_by('reminder_time')
        
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
                        upcoming.append({
                            'reminder': reminder,
                            'datetime': reminder_datetime,
                            'date': check_date
                        })
        
        # 按时间排序
        upcoming.sort(key=lambda x: x['datetime'])
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
        if reminder.frequency == 'daily':
            return True
        elif reminder.frequency == 'every_other_day':
            days_diff = (date - reminder.start_date).days
            return days_diff % 2 == 0
        elif reminder.frequency == 'weekly':
            days_diff = (date - reminder.start_date).days
            return days_diff % 7 == 0
        elif reminder.frequency == 'custom':
            weekday = date.weekday() + 1  # 转换为1-7
            return weekday in reminder.weekdays
        elif reminder.frequency in ['twice_daily', 'three_times_daily', 'four_times_daily']:
            return True  # 这些频率每天都需要提醒
        
        return False
    
    def cleanup_old_reminders(self, days=30):
        """
        清理过期的提醒
        """
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        expired_reminders = Reminder.objects.filter(
            end_date__lt=cutoff_date,
            is_active=False
        )
        
        count = expired_reminders.count()
        expired_reminders.delete()
        
        logger.info(f"清理了 {count} 个过期提醒")
        return count


# 全局调度器实例
scheduler = ReminderScheduler()