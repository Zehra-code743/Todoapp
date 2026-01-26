"""
Recurring Task Service Implementation
Handles the creation of new task instances based on recurrence patterns
"""
from typing import List, Optional
from datetime import datetime
import logging
from croniter import croniter
from dateutil.relativedelta import relativedelta

from .models import Task, RecurrenceSettings, TaskStatusEnum
from .database import get_db_context
from .event_publisher import event_publisher

# Configure logging
logger = logging.getLogger(__name__)


class RecurringTaskService:
    """Service class for handling recurring task operations"""

    def __init__(self, db_session):
        """
        Initialize the RecurringTaskService

        Args:
            db_session: Database session to use for operations
        """
        self.db = db_session

    def create_recurring_task_instance(self, parent_task: Task) -> Optional[Task]:
        """
        Create a new task instance based on the recurrence pattern of the parent task

        Args:
            parent_task: The parent recurring task

        Returns:
            Task: New task instance or None if not created
        """
        try:
            if not parent_task.is_recurring or not parent_task.recurrence_settings:
                logger.warning(f"Task {parent_task.id} is not recurring, skipping instance creation")
                return None

            recurrence_settings = parent_task.recurrence_settings

            # Check if the recurrence should end
            if self._should_end_recurrence(parent_task, recurrence_settings):
                logger.info(f"Recurrence ended for task {parent_task.id}, not creating new instance")
                return None

            # Calculate the next due date
            next_due_date = self._calculate_next_due_date(parent_task, recurrence_settings)

            # Create a new task based on the parent
            new_task_data = {
                "title": parent_task.title,
                "description": parent_task.description,
                "status": TaskStatusEnum.PENDING.value,
                "priority": parent_task.priority,
                "tags": parent_task.tags,
                "due_date": next_due_date.isoformat() if next_due_date else None,
                "is_recurring": parent_task.is_recurring,
                "recurrence_settings": parent_task.recurrence_settings.dict() if parent_task.recurrence_settings else None,
                "reminder_settings": parent_task.reminder_settings.dict() if parent_task.reminder_settings else None,
                "user_id": parent_task.user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
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

            logger.info(f"Created new recurring task instance: {new_task_id} from parent {parent_task.id}")

            # Publish recurring task created event
            event_publisher.publish_recurring_task_created(
                parent_task_id=parent_task.id,
                new_task_id=new_task_id,
                user_id=parent_task.user_id
            )

            return new_task

        except Exception as e:
            logger.error(f"Error creating recurring task instance from parent {parent_task.id}: {str(e)}")
            raise

    def _should_end_recurrence(self, task: Task, recurrence_settings: RecurrenceSettings) -> bool:
        """
        Check if the recurrence should end based on end date or occurrence limit

        Args:
            task: The recurring task
            recurrence_settings: Recurrence settings

        Returns:
            bool: True if recurrence should end, False otherwise
        """
        # Check if there's an end date
        if recurrence_settings.end_date:
            from datetime import datetime as dt
            end_dt = dt.fromisoformat(recurrence_settings.end_date.replace('Z', '+00:00'))
            now = datetime.utcnow()
            if now.date() >= end_dt.date():
                return True

        # In a full implementation, we might also check occurrence limits
        # if hasattr(recurrence_settings, 'occurrence_limit'):
        #     # Logic to check if the occurrence limit has been reached
        #     pass

        return False

    def _calculate_next_due_date(self, parent_task: Task, recurrence_settings: RecurrenceSettings):
        """
        Calculate the next due date based on the recurrence settings

        Args:
            parent_task: The parent task
            recurrence_settings: Recurrence settings

        Returns:
            datetime: Next due date
        """
        if not parent_task.due_date:
            # If no current due date, use current time
            current_dt = datetime.utcnow()
        else:
            current_dt = datetime.fromisoformat(parent_task.due_date.replace('Z', '+00:00'))

        pattern = recurrence_settings.pattern
        interval = recurrence_settings.interval

        if pattern == "daily":
            next_dt = current_dt + relativedelta(days=interval)
        elif pattern == "weekly":
            next_dt = current_dt + relativedelta(weeks=interval)
            # Adjust to specific days if specified
            if recurrence_settings.days:
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

    def process_task_completion_event(self, task_id: int, user_id: str):
        """
        Process a task completion event and create a new recurring instance if needed

        Args:
            task_id: ID of the completed task
            user_id: ID of the user who completed the task
        """
        try:
            # In a real implementation, this would fetch the task from the database
            # For now, we'll simulate it with our in-memory approach
            from .main import tasks_db
            completed_task = None
            for task in tasks_db:
                if task.id == task_id:
                    completed_task = task
                    break

            if not completed_task:
                logger.warning(f"Task {task_id} not found for completion processing")
                return

            if completed_task.is_recurring and completed_task.recurrence_settings:
                new_task = self.create_recurring_task_instance(completed_task)
                if new_task:
                    logger.info(f"Successfully created recurring task instance {new_task.id} from completed task {task_id}")
                else:
                    logger.info(f"No recurring instance created for task {task_id} (recurrence may have ended)")
            else:
                logger.debug(f"Task {task_id} is not recurring, no new instance created")

        except Exception as e:
            logger.error(f"Error processing task completion event for task {task_id}: {str(e)}")
            raise

    def get_upcoming_recurring_tasks(self, user_id: str, days_ahead: int = 7) -> List[Task]:
        """
        Get upcoming recurring tasks that will be created in the next N days

        Args:
            user_id: ID of the user
            days_ahead: Number of days to look ahead

        Returns:
            List[Task]: List of upcoming recurring tasks
        """
        try:
            from .main import tasks_db
            # Find all recurring tasks for the user
            recurring_tasks = [
                task for task in tasks_db
                if task.user_id == user_id and task.is_recurring and task.recurrence_settings
            ]

            upcoming_instances = []
            for task in recurring_tasks:
                # Calculate if the next instance would be within the specified timeframe
                next_due = self._calculate_next_due_date(task, task.recurrence_settings)
                if next_due and (next_due - datetime.utcnow()).days <= days_ahead:
                    # Create a simulated upcoming instance
                    upcoming_instance = Task(
                        id=-1,  # Placeholder ID
                        title=task.title,
                        description=task.description,
                        status=TaskStatusEnum.PENDING.value,
                        priority=task.priority,
                        tags=task.tags,
                        due_date=next_due.isoformat(),
                        is_recurring=task.is_recurring,
                        recurrence_settings=task.recurrence_settings,
                        reminder_settings=task.reminder_settings,
                        user_id=task.user_id,
                        created_at=datetime.utcnow().isoformat(),
                        updated_at=datetime.utcnow().isoformat()
                    )
                    upcoming_instances.append(upcoming_instance)

            return upcoming_instances

        except Exception as e:
            logger.error(f"Error getting upcoming recurring tasks for user {user_id}: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Example of how to use the RecurringTaskService
    # Note: This is just an example - in practice, you'd get a real database session
    print("RecurringTaskService implementation created successfully")

    # In a real scenario, you would initialize the service like:
    # with get_db_context() as db:
    #     recurring_service = RecurringTaskService(db)
    #     # Process a task completion event
    #     recurring_service.process_task_completion_event(123, "user456")