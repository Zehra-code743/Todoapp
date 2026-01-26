"""
RecurringTaskService for the Advanced Todo application.
Handles business logic for recurring tasks.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.task import Task
from ..models.recurring_task import create_next_occurrence
from ..models.recurring_task import RecurringTask
from ..models.recurrence_pattern import RecurrencePattern, validate_recurrence_pattern
from ..config.kafka_producer import send_task_event
from ..utils.recurrence_calculator import calculate_next_occurrence


class RecurringTaskService:
    """
    Service class for handling recurring task operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the service with a database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def create_recurring_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        recurrence_pattern: dict = None,
        first_occurrence_date: Optional[datetime] = None
    ) -> Task:
        """
        Create a new recurring task.

        Args:
            user_id: ID of the user creating the task
            title: Task title
            description: Task description
            priority: Task priority
            category: Task category
            due_date: Task due date
            recurrence_pattern: Dictionary containing recurrence pattern
            first_occurrence_date: Date for the first occurrence

        Returns:
            Created recurring task
        """
        if not recurrence_pattern:
            raise ValueError("Recurrence pattern is required for recurring tasks")

        # Validate the recurrence pattern
        validation_errors = validate_recurrence_pattern(
            RecurrencePattern(**recurrence_pattern)
        )
        if validation_errors:
            raise ValueError(f"Invalid recurrence pattern: {', '.join(validation_errors)}")

        # Use first_occurrence_date if provided, otherwise use due_date or current time
        task_due_date = first_occurrence_date or due_date or datetime.utcnow()

        # Create the recurring task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=task_due_date,
            is_recurring=True,
            recurrence_pattern=recurrence_pattern,
            next_occurrence_date=calculate_next_occurrence(
                task_due_date, recurrence_pattern
            )
        )

        # Add to database
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Send event to Kafka
        send_task_event("task.created", {
            "task_id": task.id,
            "user_id": user_id,
            "title": title,
            "is_recurring": True,
            "recurrence_pattern": recurrence_pattern
        })

        return task

    def complete_recurring_task(self, task_id: int) -> Optional[Task]:
        """
        Complete a recurring task and generate the next occurrence.

        Args:
            task_id: ID of the task to complete

        Returns:
            Next occurrence of the task or None if no more occurrences
        """
        # Get the task
        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task or not task.is_recurring:
            return None

        # Mark current task as completed
        task.mark_as_completed()
        self.db_session.commit()

        # Create next occurrence if applicable
        next_task = create_next_occurrence(task)
        if next_task:
            self.db_session.add(next_task)
            self.db_session.commit()
            self.db_session.refresh(next_task)

            # Send event to Kafka
            send_task_event("task.created", {
                "task_id": next_task.id,
                "user_id": next_task.user_id,
                "title": next_task.title,
                "is_recurring": True,
                "recurrence_pattern": next_task.recurrence_pattern,
                "parent_task_id": task.id
            })

            # Update parent task with next occurrence date
            task.next_occurrence_date = next_task.next_occurrence_date
            self.db_session.commit()

            return next_task

        return None

    def get_recurring_tasks(self, user_id: str) -> List[Task]:
        """
        Get all recurring tasks for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of recurring tasks
        """
        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.is_recurring == True
        ).all()

    def update_recurring_task_pattern(
        self,
        task_id: int,
        recurrence_pattern: dict,
        update_future_tasks: bool = False
    ) -> Optional[Task]:
        """
        Update the recurrence pattern for a recurring task.

        Args:
            task_id: ID of the task to update
            recurrence_pattern: New recurrence pattern
            update_future_tasks: Whether to update future occurrences too

        Returns:
            Updated task or None if not found
        """
        # Validate the new recurrence pattern
        validation_errors = validate_recurrence_pattern(
            RecurrencePattern(**recurrence_pattern)
        )
        if validation_errors:
            raise ValueError(f"Invalid recurrence pattern: {', '.join(validation_errors)}")

        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task or not task.is_recurring:
            return None

        # Update the pattern
        task.recurrence_pattern = recurrence_pattern

        # If updating future tasks, find all related future tasks
        if update_future_tasks:
            # This would require more complex logic to update all future occurrences
            # For now, we'll just update the current task
            pass

        # Calculate next occurrence date
        task.next_occurrence_date = calculate_next_occurrence(
            task.next_occurrence_date or datetime.utcnow(),
            recurrence_pattern
        )

        self.db_session.commit()
        self.db_session.refresh(task)

        # Send event to Kafka
        send_task_event("task.pattern.updated", {
            "task_id": task.id,
            "user_id": task.user_id,
            "recurrence_pattern": recurrence_pattern,
            "update_future_tasks": update_future_tasks
        })

        return task

    def delete_recurring_task(
        self,
        task_id: int,
        delete_future_tasks: bool = False
    ) -> bool:
        """
        Delete a recurring task.

        Args:
            task_id: ID of the task to delete
            delete_future_tasks: Whether to delete all future occurrences

        Returns:
            True if task was deleted, False otherwise
        """
        task = self.db_session.query(Task).filter(Task.id == task_id).first()
        if not task or not task.is_recurring:
            return False

        if delete_future_tasks:
            # Delete all future occurrences by traversing the chain
            self._delete_future_occurrences(task)

        # Delete the task
        self.db_session.delete(task)
        self.db_session.commit()

        # Send event to Kafka
        send_task_event("task.deleted", {
            "task_id": task_id,
            "user_id": task.user_id,
            "deleted_future_tasks": delete_future_tasks
        })

        return True

    def _delete_future_occurrences(self, task: Task):
        """
        Helper method to delete all future occurrences of a recurring task.

        Args:
            task: Parent recurring task
        """
        # This would require traversal of the task chain to find and delete all future occurrences
        # Implementation would depend on how the parent-child relationship is maintained
        pass

    def get_next_occurrence_date(self, task: Task) -> Optional[datetime]:
        """
        Get the next occurrence date for a recurring task.

        Args:
            task: Recurring task

        Returns:
            Next occurrence date or None
        """
        if not task.is_recurring or not task.recurrence_pattern:
            return None

        return calculate_next_occurrence(
            task.next_occurrence_date or task.due_date or datetime.utcnow(),
            task.recurrence_pattern
        )

    def get_recurring_tasks_due_soon(
        self,
        user_id: str,
        days_ahead: int = 1
    ) -> List[Task]:
        """
        Get recurring tasks that have occurrences due soon.

        Args:
            user_id: ID of the user
            days_ahead: Number of days ahead to consider

        Returns:
            List of recurring tasks with upcoming occurrences
        """
        from datetime import timedelta

        future_date = datetime.utcnow() + timedelta(days=days_ahead)

        recurring_tasks = self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.is_recurring == True
        ).all()

        due_soon_tasks = []
        for task in recurring_tasks:
            next_occurrence = self.get_next_occurrence_date(task)
            if next_occurrence and next_occurrence <= future_date:
                due_soon_tasks.append(task)

        return due_soon_tasks