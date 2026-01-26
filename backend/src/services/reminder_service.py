"""
ReminderService for the Advanced Todo application.
Handles business logic for task reminders.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.task import Task
from ..models.reminder import Reminder, ReminderStatusEnum
from ..config.kafka_producer import send_reminder_event
from ..utils.datetime_utils import get_time_until


class ReminderService:
    """
    Service class for handling reminder operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the service with a database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def create_reminder(
        self,
        task_id: int,
        user_id: str,
        scheduled_for: datetime,
        reminder_advance_minutes: int = 60,
        notification_channels: Optional[List[str]] = None
    ) -> Reminder:
        """
        Create a new reminder for a task.

        Args:
            task_id: ID of the task to create reminder for
            user_id: ID of the user
            scheduled_for: When the reminder should be sent
            reminder_advance_minutes: Minutes before due date to send reminder
            notification_channels: List of notification channels

        Returns:
            Created reminder
        """
        # Check if task exists
        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Create reminder
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            scheduled_for=scheduled_for,
            status=ReminderStatusEnum.PENDING
        )

        # Add to database
        self.db_session.add(reminder)
        self.db_session.commit()
        self.db_session.refresh(reminder)

        # Update task with reminder settings
        if not hasattr(task, 'reminder_settings') or task.reminder_settings is None:
            task.reminder_settings = {}
        task.reminder_settings.update({
            "enabled": True,
            "advance_notice": reminder_advance_minutes,
            "notification_channels": notification_channels or ["push", "email"]
        })
        task.reminder_sent = False
        self.db_session.commit()

        # Send event to Kafka
        send_reminder_event("reminder.scheduled", {
            "reminder_id": reminder.id,
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_for": scheduled_for.isoformat(),
            "channels": notification_channels or ["push", "email"]
        })

        return reminder

    def set_due_date_with_reminder(
        self,
        task_id: int,
        due_date: datetime,
        reminder_enabled: bool = True,
        reminder_advance_minutes: int = 60
    ) -> Task:
        """
        Set a due date for a task and schedule a reminder.

        Args:
            task_id: ID of the task
            due_date: Due date for the task
            reminder_enabled: Whether to schedule a reminder
            reminder_advance_minutes: Minutes before due date to send reminder

        Returns:
            Updated task
        """
        # Get the task
        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Update due date
        task.due_date = due_date

        if reminder_enabled:
            # Calculate when to schedule the reminder
            scheduled_for = due_date - timedelta(minutes=reminder_advance_minutes)

            # Create reminder
            reminder = self.create_reminder(
                task_id=task_id,
                user_id=task.user_id,
                scheduled_for=scheduled_for,
                reminder_advance_minutes=reminder_advance_minutes
            )

        self.db_session.commit()
        self.db_session.refresh(task)

        return task

    def get_pending_reminders(self) -> List[Reminder]:
        """
        Get all pending reminders.

        Returns:
            List of pending reminders
        """
        return self.db_session.query(Reminder).filter(
            Reminder.status == ReminderStatusEnum.PENDING
        ).all()

    def get_reminders_for_user(self, user_id: str) -> List[Reminder]:
        """
        Get all reminders for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of user's reminders
        """
        return self.db_session.query(Reminder).filter(
            Reminder.user_id == user_id
        ).all()

    def get_overdue_reminders(self) -> List[Reminder]:
        """
        Get all overdue reminders (should have been sent).

        Returns:
            List of overdue reminders
        """
        return self.db_session.query(reminder).filter(
            Reminder.status == ReminderStatusEnum.PENDING,
            Reminder.scheduled_for < datetime.utcnow()
        ).all()

    def mark_reminder_as_sent(self, reminder_id: int) -> Optional[Reminder]:
        """
        Mark a reminder as sent.

        Args:
            reminder_id: ID of the reminder

        Returns:
            Updated reminder or None if not found
        """
        reminder = self.db_session.query(Reminder).filter(
            Reminder.id == reminder_id
        ).first()

        if not reminder or reminder.status != ReminderStatusEnum.PENDING:
            return None

        reminder.status = ReminderStatusEnum.SENT
        self.db_session.commit()
        self.db_session.refresh(reminder)

        # Update associated task
        task = self.db_session.query(Task).filter(Task.id == reminder.task_id).first()
        if task:
            task.reminder_sent = True
            self.db_session.commit()

        # Send event to Kafka
        send_reminder_event("reminder.sent", {
            "reminder_id": reminder_id,
            "task_id": reminder.task_id,
            "user_id": reminder.user_id
        })

        return reminder

    def cancel_reminder(self, reminder_id: int) -> bool:
        """
        Cancel a pending reminder.

        Args:
            reminder_id: ID of the reminder

        Returns:
            True if canceled, False if not found or not pending
        """
        reminder = self.db_session.query(Reminder).filter(
            Reminder.id == reminder_id
        ).first()

        if not reminder or reminder.status != ReminderStatusEnum.PENDING:
            return False

        reminder.status = ReminderStatusEnum.CANCELLED
        self.db_session.commit()

        # Send event to Kafka
        send_reminder_event("reminder.cancelled", {
            "reminder_id": reminder_id,
            "task_id": reminder.task_id,
            "user_id": reminder.user_id
        })

        return True

    def snooze_reminder(
        self,
        reminder_id: int,
        snooze_duration_minutes: int
    ) -> Optional[Reminder]:
        """
        Reschedule a reminder for later (snooze functionality).

        Args:
            reminder_id: ID of the reminder
            snooze_duration_minutes: Number of minutes to snooze

        Returns:
            Updated reminder or None if not found or not pending
        """
        reminder = self.db_session.query(Reminder).filter(
            Reminder.id == reminder_id
        ).first()

        if not reminder or reminder.status != ReminderStatusEnum.PENDING:
            return None

        # Reschedule the reminder
        new_schedule_time = datetime.utcnow() + timedelta(minutes=snooze_duration_minutes)
        reminder.scheduled_for = new_schedule_time
        self.db_session.commit()
        self.db_session.refresh(reminder)

        # Send event to Kafka
        send_reminder_event("reminder.snoozed", {
            "reminder_id": reminder_id,
            "task_id": reminder.task_id,
            "user_id": reminder.user_id,
            "new_scheduled_time": new_schedule_time.isoformat(),
            "snooze_duration_minutes": snooze_duration_minutes
        })

        return reminder

    def process_due_reminders(self) -> List[Reminder]:
        """
        Process all reminders that are due to be sent.

        Returns:
            List of reminders that were processed
        """
        due_reminders = self.get_overdue_reminders()
        processed_reminders = []

        for reminder in due_reminders:
            # In a real implementation, this would trigger the actual notification
            # For now, we'll just mark as sent
            updated_reminder = self.mark_reminder_as_sent(reminder.id)
            if updated_reminder:
                processed_reminders.append(updated_reminder)

        return processed_reminders

    def get_reminder_time_remaining(self, reminder: Reminder) -> Optional[timedelta]:
        """
        Get the time remaining until a reminder is scheduled.

        Args:
            reminder: Reminder to check

        Returns:
            Time remaining as timedelta, or None if not pending
        """
        if reminder.status != ReminderStatusEnum.PENDING:
            return None

        return get_time_until(reminder.scheduled_for)

    def is_reminder_due_now(self, reminder: Reminder) -> bool:
        """
        Check if a reminder is due to be sent now.

        Args:
            reminder: Reminder to check

        Returns:
            True if reminder is due now, False otherwise
        """
        if reminder.status != ReminderStatusEnum.PENDING:
            return False

        return datetime.utcnow() >= reminder.scheduled_for

    def get_reminders_by_status(self, status: ReminderStatusEnum) -> List[Reminder]:
        """
        Get all reminders with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of reminders with the specified status
        """
        return self.db_session.query(Reminder).filter(
            Reminder.status == status
        ).all()

    def get_reminders_for_task(self, task_id: int) -> List[Reminder]:
        """
        Get all reminders for a specific task.

        Args:
            task_id: ID of the task

        Returns:
            List of reminders for the task
        """
        return self.db_session.query(Reminder).filter(
            Reminder.task_id == task_id
        ).all()