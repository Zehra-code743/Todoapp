"""
Notification Service Implementation
Handles reminder scheduling and notification delivery
"""
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .models import Task, ReminderSettings, Notification, NotificationChannelEnum
from .database import get_db_context
from .event_publisher import event_publisher

# Configure logging
logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for handling notification operations"""

    def __init__(self, db_session):
        """
        Initialize the NotificationService

        Args:
            db_session: Database session to use for operations
        """
        self.db = db_session
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def schedule_reminder(self, task: Task) -> Optional[Notification]:
        """
        Schedule a reminder based on task reminder settings

        Args:
            task: The task for which to schedule a reminder

        Returns:
            Notification: Scheduled notification or None if no reminder needed
        """
        try:
            if not task.reminder_settings or not task.due_date:
                logger.debug(f"No reminder settings or due date for task {task.id}, skipping scheduling")
                return None

            reminder_settings = task.reminder_settings
            due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))

            # Calculate when to send the reminder based on offset
            reminder_time = due_date - timedelta(minutes=reminder_settings.offset_minutes)

            # Check if the reminder time is in the past
            now = datetime.utcnow()
            if reminder_time <= now:
                logger.warning(f"Reminder time for task {task.id} is in the past, not scheduling")
                return None

            # Create notification record
            notification_data = {
                "task_id": task.id,
                "user_id": task.user_id,
                "title": f"Reminder: {task.title}",
                "message": f"Your task '{task.title}' is due soon!",
                "channel": reminder_settings.channel,
                "scheduled_at": reminder_time.isoformat(),
                "status": "pending",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }

            # In a real implementation, this would create the notification in the database
            # For now, we'll simulate it with our in-memory approach
            from .main import notifications_db
            notification_id = len(notifications_db) + 1

            notification = Notification(
                id=notification_id,
                **notification_data
            )

            notifications_db.append(notification)

            # Schedule the reminder using APScheduler
            self.scheduler.add_job(
                self._send_notification,
                'date',
                run_date=reminder_time,
                id=f'reminder_{notification_id}',
                args=[notification]
            )

            logger.info(f"Scheduled reminder for task {task.id} at {reminder_time}")

            # Publish reminder scheduled event
            event_publisher.publish_reminder_scheduled(
                task_id=task.id,
                user_id=task.user_id,
                scheduled_time=reminder_time.isoformat(),
                channel=reminder_settings.channel
            )

            return notification

        except Exception as e:
            logger.error(f"Error scheduling reminder for task {task.id}: {str(e)}")
            raise

    async def _send_notification(self, notification: Notification):
        """
        Send a notification via the specified channel

        Args:
            notification: The notification to send
        """
        try:
            # Update notification status to sending
            notification.status = "sending"
            notification.updated_at = datetime.utcnow().isoformat()

            # Simulate sending notification based on channel
            success = await self._deliver_notification(notification)

            if success:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow().isoformat()

                logger.info(f"Notification {notification.id} sent successfully via {notification.channel}")

                # Publish reminder triggered event
                event_publisher.publish_reminder_triggered(
                    task_id=notification.task_id,
                    user_id=notification.user_id,
                    channel=notification.channel
                )
            else:
                notification.status = "failed"
                logger.error(f"Failed to send notification {notification.id} via {notification.channel}")

            notification.updated_at = datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
            notification.status = "failed"
            notification.updated_at = datetime.utcnow().isoformat()

    async def _deliver_notification(self, notification: Notification) -> bool:
        """
        Deliver notification via the appropriate channel

        Args:
            notification: The notification to deliver

        Returns:
            bool: True if delivered successfully, False otherwise
        """
        try:
            channel = notification.channel

            if channel == NotificationChannelEnum.IN_APP:
                # Simulate in-app notification delivery
                logger.info(f"Delivering in-app notification: {notification.title}")
                # In a real implementation, this would save to a user's notification feed
                return True

            elif channel == NotificationChannelEnum.EMAIL:
                # Simulate email delivery
                logger.info(f"Sending email notification: {notification.title}")
                # In a real implementation, this would send an actual email
                return True

            elif channel == NotificationChannelEnum.PUSH:
                # Simulate push notification delivery
                logger.info(f"Sending push notification: {notification.title}")
                # In a real implementation, this would send to a push notification service
                return True

            elif channel == NotificationChannelEnum.SMS:
                # Simulate SMS delivery
                logger.info(f"Sending SMS notification: {notification.title}")
                # In a real implementation, this would send to an SMS service
                return True

            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False

        except Exception as e:
            logger.error(f"Error delivering notification via {notification.channel}: {str(e)}")
            return False

    def cancel_reminder(self, task_id: int, user_id: str) -> bool:
        """
        Cancel a scheduled reminder for a task

        Args:
            task_id: ID of the task
            user_id: ID of the user

        Returns:
            bool: True if canceled successfully, False otherwise
        """
        try:
            # In a real implementation, this would query the database
            # For now, we'll simulate it with our in-memory approach
            from .main import notifications_db

            # Find the notification for this task
            for notification in notifications_db:
                if notification.task_id == task_id and notification.user_id == user_id and notification.status == "pending":
                    # Remove from scheduler
                    job_id = f'reminder_{notification.id}'

                    if self.scheduler.get_job(job_id):
                        self.scheduler.remove_job(job_id)

                    # Update notification status
                    notification.status = "cancelled"
                    notification.updated_at = datetime.utcnow().isoformat()

                    logger.info(f"Cancelled reminder for task {task_id}")
                    return True

            logger.warning(f"No pending reminder found for task {task_id} to cancel")
            return False

        except Exception as e:
            logger.error(f"Error cancelling reminder for task {task_id}: {str(e)}")
            return False

    def get_pending_notifications(self, user_id: str) -> List[Notification]:
        """
        Get all pending notifications for a user

        Args:
            user_id: ID of the user

        Returns:
            List[Notification]: List of pending notifications
        """
        try:
            from .main import notifications_db

            pending_notifications = [
                notification for notification in notifications_db
                if notification.user_id == user_id and notification.status == "pending"
            ]

            return pending_notifications

        except Exception as e:
            logger.error(f"Error getting pending notifications for user {user_id}: {str(e)}")
            raise

    def process_reminder_event(self, task_id: int, user_id: str, due_date: str, reminder_settings_dict: dict):
        """
        Process a reminder event (e.g., when a task is created or updated with reminder settings)

        Args:
            task_id: ID of the task
            user_id: ID of the user
            due_date: Due date of the task
            reminder_settings_dict: Reminder settings as dictionary
        """
        try:
            # In a real implementation, this would fetch the task from the database
            # For now, we'll create a minimal task object for the reminder scheduling
            from .models import ReminderSettings

            reminder_settings = ReminderSettings(**reminder_settings_dict)

            # Create a minimal task object for reminder scheduling
            temp_task = Task(
                id=task_id,
                title=f"Task {task_id}",
                user_id=user_id,
                due_date=due_date,
                reminder_settings=reminder_settings,
                status="pending",
                priority="medium",
                tags=[],
                is_recurring=False,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )

            # Schedule the reminder
            notification = self.schedule_reminder(temp_task)

            if notification:
                logger.info(f"Processed reminder event for task {task_id}, notification {notification.id} scheduled")
            else:
                logger.info(f"No reminder scheduled for task {task_id} (may be in the past or no settings)")

        except Exception as e:
            logger.error(f"Error processing reminder event for task {task_id}: {str(e)}")
            raise

    def shutdown(self):
        """Clean shutdown of the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Example of how to use the NotificationService
    # Note: This is just an example - in practice, you'd get a real database session
    print("NotificationService implementation created successfully")

    # In a real scenario, you would initialize the service like:
    # with get_db_context() as db:
    #     notification_service = NotificationService(db)
    #
    #     # Schedule a reminder for a task
    #     # notification_service.schedule_reminder(task)
    #
    #     # Don't forget to shut down the scheduler when done
    #     # notification_service.shutdown()