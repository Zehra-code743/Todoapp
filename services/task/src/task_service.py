"""
Task Service Implementation
Implements CRUD operations for tasks with advanced features
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json

from .models import Task, TaskUpdate, RecurrenceSettings, ReminderSettings, PriorityEnum, TaskStatusEnum
from .database import get_db_context
from .event_publisher import event_publisher

# Import dateutil for date calculations
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # If dateutil is not available, we'll define a simplified version for demo purposes
    class relativedelta:
        def __init__(self, days=0, weeks=0, months=0, years=0):
            self.days = days
            self.weeks = weeks
            self.months = months
            self.years = years

# Configure logging
logger = logging.getLogger(__name__)


class TaskService:
    """Service class for handling task operations"""

    def __init__(self, db_session: Session):
        """
        Initialize the TaskService

        Args:
            db_session: Database session to use for operations
        """
        self.db = db_session

    def create_task(self, user_id: str, title: str, description: Optional[str] = None,
                   priority: PriorityEnum = PriorityEnum.MEDIUM, tags: Optional[List[str]] = None,
                   due_date: Optional[str] = None, is_recurring: bool = False,
                   recurrence_settings: Optional[RecurrenceSettings] = None,
                   reminder_settings: Optional[ReminderSettings] = None) -> Task:
        """
        Create a new task with advanced features

        Args:
            user_id: ID of the user creating the task
            title: Title of the task
            description: Optional description
            priority: Task priority
            tags: List of tags
            due_date: Due date in ISO format
            is_recurring: Whether the task is recurring
            recurrence_settings: Recurrence settings if recurring
            reminder_settings: Reminder settings

        Returns:
            Task: Created task object
        """
        try:
            # Prepare the current timestamp
            now = datetime.utcnow().isoformat()

            # Create the task object
            task_data = {
                "title": title,
                "description": description,
                "priority": priority.value if isinstance(priority, PriorityEnum) else priority,
                "tags": tags or [],
                "due_date": due_date,
                "is_recurring": is_recurring,
                "user_id": user_id,
                "status": TaskStatusEnum.PENDING.value,
                "created_at": now,
                "updated_at": now
            }

            # Add recurrence settings if provided
            if recurrence_settings:
                task_data["recurrence_settings"] = recurrence_settings.dict()

            # Add reminder settings if provided
            if reminder_settings:
                task_data["reminder_settings"] = reminder_settings.dict()

            # Create the task record in the database
            # In a real implementation, this would be an actual database insert
            # For now, we'll simulate it with an in-memory approach
            from .main import tasks_db  # Import from main for simulation
            task_id = len(tasks_db) + 1

            task_obj = Task(
                id=task_id,
                **task_data
            )

            tasks_db.append(task_obj)

            # Publish task created event
            event_publisher.publish_task_created(
                task_id=task_id,
                user_id=user_id,
                title=title
            )

            logger.info(f"Task created successfully: ID {task_id}, User {user_id}")

            return task_obj

        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task: The retrieved task or None if not found
        """
        try:
            from .main import tasks_db  # Import from main for simulation
            for task in tasks_db:
                if task.id == task_id:
                    return task

            logger.warning(f"Task not found: ID {task_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            raise

    def get_tasks(self, user_id: str, status: Optional[TaskStatusEnum] = None,
                 priority: Optional[PriorityEnum] = None, tag: Optional[str] = None,
                 created_after: Optional[str] = None, created_before: Optional[str] = None,
                 sort_by: str = "created_at", sort_order: str = "desc",
                 search_query: Optional[str] = None) -> List[Task]:
        """
        Retrieve tasks with filtering, sorting, and search capabilities

        Args:
            user_id: ID of the user whose tasks to retrieve
            status: Filter by task status
            priority: Filter by task priority
            tag: Filter by tag
            created_after: Filter tasks created after this date
            created_before: Filter tasks created before this date
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            search_query: Search query for full-text search

        Returns:
            List[Task]: List of matching tasks
        """
        try:
            from .main import tasks_db  # Import from main for simulation
            filtered_tasks = [task for task in tasks_db if task.user_id == user_id]

            # Apply filters
            if status:
                filtered_tasks = [task for task in filtered_tasks if task.status == status]

            if priority:
                filtered_tasks = [task for task in filtered_tasks if task.priority == priority]

            if tag:
                filtered_tasks = [task for task in filtered_tasks if tag in task.tags]

            if search_query:
                search_lower = search_query.lower()
                filtered_tasks = [
                    task for task in filtered_tasks
                    if search_lower in task.title.lower() or
                       (task.description and search_lower in task.description.lower())
                ]

            # Apply date range filters
            if created_after:
                from datetime import datetime
                after_dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                filtered_tasks = [
                    task for task in filtered_tasks
                    if datetime.fromisoformat(task.created_at.replace('Z', '+00:00')) >= after_dt
                ]

            if created_before:
                from datetime import datetime
                before_dt = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                filtered_tasks = [
                    task for task in filtered_tasks
                    if datetime.fromisoformat(task.created_at.replace('Z', '+00:00')) <= before_dt
                ]

            # Apply sorting
            reverse_sort = sort_order.lower() == 'desc'

            if sort_by == 'created_at':
                filtered_tasks.sort(key=lambda x: x.created_at, reverse=reverse_sort)
            elif sort_by == 'due_date':
                # Sort by due date, with nulls at the end
                filtered_tasks.sort(
                    key=lambda x: (x.due_date is None, x.due_date),
                    reverse=reverse_sort
                )
            elif sort_by == 'priority':
                # Sort by priority, using the enum value order
                priority_order = {PriorityEnum.HIGH: 0, PriorityEnum.MEDIUM: 1, PriorityEnum.LOW: 2}
                filtered_tasks.sort(
                    key=lambda x: priority_order.get(PriorityEnum(x.priority), 1),
                    reverse=reverse_sort
                )
            elif sort_by == 'title':
                filtered_tasks.sort(key=lambda x: x.title.lower(), reverse=reverse_sort)
            else:
                # Default to created_at
                filtered_tasks.sort(key=lambda x: x.created_at, reverse=reverse_sort)

            logger.info(f"Retrieved {len(filtered_tasks)} tasks for user {user_id}")
            return filtered_tasks

        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
            raise

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """
        Update an existing task

        Args:
            task_id: ID of the task to update
            task_update: Update data

        Returns:
            Task: Updated task object or None if not found
        """
        try:
            from .main import tasks_db  # Import from main for simulation
            for i, task in enumerate(tasks_db):
                if task.id == task_id:
                    # Create a copy of the task with updated values
                    update_data = task_update.dict(exclude_unset=True)

                    # Handle nested objects separately
                    if 'reminder_settings' in update_data and update_data['reminder_settings']:
                        update_data['reminder_settings'] = update_data['reminder_settings'].dict()

                    # Update the task
                    updated_fields = task.dict()
                    updated_fields.update(update_data)
                    updated_fields['updated_at'] = datetime.utcnow().isoformat()

                    # Create new task object with updated data
                    updated_task = Task(**updated_fields)
                    tasks_db[i] = updated_task

                    # Publish task updated event
                    event_publisher.publish_task_updated(
                        task_id=task_id,
                        user_id=task.user_id,
                        changes=update_data
                    )

                    logger.info(f"Task updated successfully: ID {task_id}")
                    return updated_task

            logger.warning(f"Task not found for update: ID {task_id}")
            return None

        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task

        Args:
            task_id: ID of the task to delete

        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            from .main import tasks_db  # Import from main for simulation
            initial_length = len(tasks_db)
            tasks_db[:] = [task for task in tasks_db if task.id != task_id]
            deleted = len(tasks_db) < initial_length

            if deleted:
                logger.info(f"Task deleted successfully: ID {task_id}")
            else:
                logger.warning(f"Task not found for deletion: ID {task_id}")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise

    def complete_task(self, task_id: int) -> Optional[Task]:
        """
        Mark a task as completed

        Args:
            task_id: ID of the task to mark as completed

        Returns:
            Task: Updated task object or None if not found
        """
        try:
            from .main import tasks_db  # Import from main for simulation
            for i, task in enumerate(tasks_db):
                if task.id == task_id:
                    # Update task status and completion time
                    completed_task = task.copy(update={
                        "status": TaskStatusEnum.COMPLETED.value,
                        "completed_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    })

                    tasks_db[i] = completed_task

                    # Publish task completed event
                    event_publisher.publish_task_completed(
                        task_id=task_id,
                        user_id=task.user_id
                    )

                    # If the task is recurring, create a new instance
                    if task.is_recurring and task.recurrence_settings:
                        self._handle_recurring_task_completion(task)

                    logger.info(f"Task completed successfully: ID {task_id}")
                    return completed_task

            logger.warning(f"Task not found for completion: ID {task_id}")
            return None

        except Exception as e:
            logger.error(f"Error completing task {task_id}: {str(e)}")
            raise

    def _handle_recurring_task_completion(self, completed_task: Task):
        """
        Handle the completion of a recurring task by creating a new instance

        Args:
            completed_task: The completed recurring task
        """
        try:
            if not completed_task.is_recurring or not completed_task.recurrence_settings:
                logger.warning(f"Task {completed_task.id} is not recurring, skipping recurrence logic")
                return

            recurrence_settings = completed_task.recurrence_settings
            now = datetime.utcnow()

            # Check if the recurrence should end
            if recurrence_settings.end_date:
                from datetime import datetime as dt
                end_dt = dt.fromisoformat(recurrence_settings.end_date.replace('Z', '+00:00'))
                if now.date() >= end_dt.date():
                    logger.info(f"Recurrence ended for task {completed_task.id}, not creating new instance")
                    return

            # Calculate the next due date based on recurrence pattern
            next_due_date = self._calculate_next_due_date(
                completed_task.due_date,
                recurrence_settings
            )

            # Create a new task based on the completed task
            new_task_data = {
                "title": completed_task.title,
                "description": completed_task.description,
                "priority": completed_task.priority,
                "tags": completed_task.tags,
                "due_date": next_due_date.isoformat() if next_due_date else None,
                "is_recurring": completed_task.is_recurring,
                "recurrence_settings": completed_task.recurrence_settings,
                "reminder_settings": completed_task.reminder_settings,
                "user_id": completed_task.user_id,
                "status": "pending",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }

            # In a real implementation, this would create the new task in the database
            # For now, we'll simulate it with our in-memory approach
            from .main import tasks_db
            new_task_id = len(tasks_db) + 1

            new_task = Task(
                id=new_task_id,
                **new_task_data
            )

            tasks_db.append(new_task)

            logger.info(f"Created new recurring task instance: {new_task_id} from parent {completed_task.id}")

            # Publish recurring task created event
            event_publisher.publish_recurring_task_created(
                parent_task_id=completed_task.id,
                new_task_id=new_task_id,
                user_id=completed_task.user_id
            )

        except Exception as e:
            logger.error(f"Error handling recurring task completion: {str(e)}")

    def _calculate_next_due_date(self, current_due_date: Optional[str], recurrence_settings: RecurrenceSettings):
        """
        Calculate the next due date based on the recurrence settings

        Args:
            current_due_date: Current due date of the task
            recurrence_settings: Recurrence settings

        Returns:
            datetime: Next due date
        """
        if not current_due_date:
            # If no current due date, use current time
            from datetime import datetime
            current_dt = datetime.utcnow()
        else:
            from datetime import datetime
            current_dt = datetime.fromisoformat(current_due_date.replace('Z', '+00:00'))

        import calendar
        from dateutil.relativedelta import relativedelta

        pattern = recurrence_settings.pattern
        interval = recurrence_settings.interval

        if pattern == "daily":
            next_dt = current_dt + relativedelta(days=interval)
        elif pattern == "weekly":
            next_dt = current_dt + relativedelta(weeks=interval)
            # Adjust to specific days if specified
            if recurrence_settings.days:
                # Find the next occurrence of one of the specified days
                next_dt = self._adjust_to_specific_days(next_dt, recurrence_settings.days)
        elif pattern == "monthly":
            next_dt = current_dt + relativedelta(months=interval)
        elif pattern == "yearly":
            next_dt = current_dt + relativedelta(years=interval)
        else:
            # Default to daily if pattern is unknown
            next_dt = current_dt + relativedelta(days=interval)

        return next_dt

    def _adjust_to_specific_days(self, start_date, days_of_week):
        """
        Adjust the date to the next occurrence of one of the specified days

        Args:
            start_date: Starting date
            days_of_week: List of days (e.g., ['Mon', 'Wed', 'Fri'])

        Returns:
            datetime: Adjusted date
        """
        # Map day abbreviations to weekday numbers (Monday=0, Sunday=6)
        day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

        # Convert day names to numbers
        target_days = [day_map[day] for day in days_of_week if day in day_map]

        if not target_days:
            return start_date

        # Find the next occurrence
        current_day = start_date.weekday()
        min_days_ahead = 7  # Start with a week ahead

        for day in target_days:
            days_ahead = day - current_day
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            min_days_ahead = min(min_days_ahead, days_ahead)

        return start_date + relativedelta(days=min_days_ahead)


# Example usage
if __name__ == "__main__":
    # Example of how to use the TaskService
    # Note: This is just an example - in practice, you'd get a real database session
    print("TaskService implementation created successfully")

    # In a real scenario, you would initialize the service like:
    # with get_db_context() as db:
    #     task_service = TaskService(db)
    #     task = task_service.create_task(
    #         user_id="user123",
    #         title="Test Task",
    #         priority=PriorityEnum.HIGH,
    #         tags=["test", "important"]
    #     )