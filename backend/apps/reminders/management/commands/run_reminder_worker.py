import os
import time
import logging
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from django_redis import get_redis_connection

from apps.reminders.scheduler import ReminderScheduler


logger = logging.getLogger(__name__)

# Fallback logging to ensure INFO-level messages are visible in container logs
# If Django's LOGGING doesn't attach a handler to this module, we attach one.
if not logger.handlers:
    logger.propagate = False  # avoid duplicate logs if parent handlers exist
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "运行用药提醒独立 Worker：定期扫描并发送到期提醒（支持 Redis 分布式锁防重）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=int(os.getenv("REMINDER_WORKER_INTERVAL", "60")),
            help="循环间隔秒数（默认 60）",
        )
        parser.add_argument(
            "--lock-timeout",
            type=int,
            default=int(os.getenv("REMINDER_WORKER_LOCK_TIMEOUT", "120")),
            help="Redis 锁的过期时间（秒，默认 120）",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="只运行一次扫描后退出（用于调试/健康检查）",
        )

    def handle(self, *args, **options):
        interval: int = max(1, int(options.get("interval", 60)))
        lock_timeout: int = max(10, int(options.get("lock_timeout", 120)))
        run_once: bool = bool(options.get("once", False))

        scheduler = ReminderScheduler()

        # 准备 Redis 分布式锁；不可用时降级为无锁运行
        lock = None
        try:
            conn = get_redis_connection("default")
            # 简单连接探测
            conn.ping()
            lock_name = f"{getattr(settings, 'REDIS_KEY_PREFIX', 'mtm-helper')}:reminder_worker_lock"
            lock = conn.lock(lock_name, timeout=lock_timeout, blocking=False)
            logger.info("Redis连接正常，启用分布式锁防重：%s", lock_name)
        except Exception as e:
            logger.warning("Redis不可用或未正确配置，Worker 将以无锁模式运行：%s", e)

        def run_iteration():
            try:
                sent = scheduler.check_and_send_reminders()
                logger.info("本次提醒扫描完成，发送数量：%s", sent)
            except Exception as e:
                logger.error("提醒调度循环发生错误：%s", e, exc_info=True)

        while True:
            acquired = True  # 默认允许运行（无锁模式）
            if lock is not None:
                try:
                    acquired = lock.acquire(blocking=False)
                except Exception as e:
                    logger.warning("获取 Redis 锁失败，按无锁模式继续：%s", e)
                    acquired = True

            if acquired:
                try:
                    run_iteration()
                finally:
                    if lock is not None:
                        try:
                            lock.release()
                        except Exception:
                            # 忽略锁释放异常避免影响后续循环
                            pass
            else:
                logger.info("已有其他 Worker 正在运行，跳过本轮扫描（等待下一次尝试）")

            if run_once:
                break

            time.sleep(interval)