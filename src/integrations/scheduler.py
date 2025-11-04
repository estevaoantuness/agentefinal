"""Task scheduler for reminders using APScheduler."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pytz

from src.config.settings import settings
from src.database.session import get_db_context
from src.database.models import Reminder, Task, User
from src.integrations.evolution_api import evolution_client
from src.utils.logger import logger


class ReminderScheduler:
    """Scheduler for managing task reminders."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        self.scheduler.start()
        logger.info("Reminder scheduler started")

    def schedule_reminder(self, reminder_id: int, scheduled_time: datetime):
        """
        Schedule a reminder to be sent.

        Args:
            reminder_id: Reminder ID
            scheduled_time: When to send the reminder
        """
        # Convert to timezone-aware datetime
        tz = pytz.timezone(settings.TIMEZONE)
        if scheduled_time.tzinfo is None:
            scheduled_time = tz.localize(scheduled_time)

        # Schedule job
        self.scheduler.add_job(
            func=self._send_reminder,
            trigger=DateTrigger(run_date=scheduled_time),
            args=[reminder_id],
            id=f"reminder_{reminder_id}",
            replace_existing=True
        )

        logger.info(f"Reminder {reminder_id} scheduled for {scheduled_time}")

    def cancel_reminder(self, reminder_id: int):
        """
        Cancel a scheduled reminder.

        Args:
            reminder_id: Reminder ID
        """
        try:
            self.scheduler.remove_job(f"reminder_{reminder_id}")
            logger.info(f"Reminder {reminder_id} cancelled")
        except Exception as e:
            logger.warning(f"Could not cancel reminder {reminder_id}: {e}")

    async def _send_reminder(self, reminder_id: int):
        """
        Send a reminder notification.

        Args:
            reminder_id: Reminder ID
        """
        with get_db_context() as db:
            try:
                # Get reminder with related data
                reminder = db.query(Reminder).filter(
                    Reminder.id == reminder_id
                ).first()

                if not reminder or reminder.sent:
                    logger.warning(f"Reminder {reminder_id} not found or already sent")
                    return

                # Get task and user
                task = db.query(Task).filter(Task.id == reminder.task_id).first()
                user = db.query(User).filter(User.id == reminder.user_id).first()

                if not task or not user:
                    logger.error(f"Task or user not found for reminder {reminder_id}")
                    return

                # Build reminder message
                message = f"⏰ *Lembrete*\n\n"
                message += f"📋 *Tarefa:* {task.title}\n"

                if task.description:
                    message += f"📝 *Descrição:* {task.description}\n"

                if task.due_date:
                    due_str = task.due_date.strftime("%d/%m/%Y às %H:%M")
                    message += f"📅 *Prazo:* {due_str}\n"

                priority_emoji = {
                    "low": "🔵",
                    "medium": "🟡",
                    "high": "🟠",
                    "urgent": "🔴"
                }.get(task.priority, "⚪")
                message += f"{priority_emoji} *Prioridade:* {task.priority.upper()}\n"

                if reminder.message:
                    message += f"\n💬 {reminder.message}"

                # Send via Evolution API
                evolution_client.send_text_message(
                    phone_number=user.phone_number,
                    message=message
                )

                # Mark as sent
                reminder.sent = True
                reminder.sent_at = datetime.utcnow()
                db.commit()

                logger.info(f"Reminder {reminder_id} sent to {user.phone_number}")

            except Exception as e:
                logger.error(f"Error sending reminder {reminder_id}: {e}", exc_info=True)
                db.rollback()

    def load_pending_reminders(self):
        """
        Load all pending reminders from database and schedule them.
        Call this on startup.
        """
        with get_db_context() as db:
            try:
                # Get all pending reminders
                now = datetime.utcnow()
                pending_reminders = db.query(Reminder).filter(
                    Reminder.sent == False,
                    Reminder.scheduled_time > now
                ).all()

                for reminder in pending_reminders:
                    self.schedule_reminder(reminder.id, reminder.scheduled_time)

                logger.info(f"Loaded {len(pending_reminders)} pending reminders")

            except Exception as e:
                logger.error(f"Error loading pending reminders: {e}")

    def schedule_daily_sync(self):
        """
        Schedule daily Notion sync for all users.
        Runs every day at 3 AM.
        """
        from apscheduler.triggers.cron import CronTrigger

        self.scheduler.add_job(
            func=self._daily_notion_sync,
            trigger=CronTrigger(hour=3, minute=0),
            id="daily_notion_sync",
            replace_existing=True
        )

        logger.info("Daily Notion sync scheduled for 3 AM")

    async def _daily_notion_sync(self):
        """
        Perform daily Notion sync for all active users.
        """
        with get_db_context() as db:
            try:
                from src.integrations.notion_sync import notion_sync

                users = db.query(User).filter(
                    User.is_active == True,
                    User.notion_database_id.isnot(None)
                ).all()

                for user in users:
                    try:
                        stats = notion_sync.bidirectional_sync(user, db)
                        logger.info(f"Daily sync for user {user.id}: {stats}")
                    except Exception as e:
                        logger.error(f"Error syncing user {user.id}: {e}")

                logger.info(f"Daily sync completed for {len(users)} users")

            except Exception as e:
                logger.error(f"Error in daily sync: {e}")

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Reminder scheduler shutdown")


# Global scheduler instance
reminder_scheduler = ReminderScheduler()
