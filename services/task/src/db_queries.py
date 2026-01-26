"""
Database Queries for Task Service
Contains SQLAlchemy queries for the new task attributes
"""
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .models import Task, TaskStatusEnum, PriorityEnum
from .database import Base


class TaskQueries:
    """Class containing database queries for task operations"""

    @staticmethod
    def get_tasks_by_filters(
        db: Session,
        user_id: str,
        status: Optional[TaskStatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        tag: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        due_after: Optional[str] = None,
        due_before: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        """
        Get tasks with various filters and sorting options

        Args:
            db: Database session
            user_id: User ID to filter tasks
            status: Filter by task status
            priority: Filter by task priority
            tag: Filter by tag
            created_after: Filter tasks created after this date
            created_before: Filter tasks created before this date
            due_after: Filter tasks with due date after this date
            due_before: Filter tasks with due date before this date
            search_query: Search query for full-text search
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            List of Task objects
        """
        from .main import tasks_db  # Using in-memory simulation for now
        # In a real implementation, this would be a SQLAlchemy query

        # For demonstration purposes, returning a filtered list from our in-memory store
        filtered_tasks = [task for task in tasks_db if task.user_id == user_id]

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

        # Apply sorting
        reverse_sort = sort_order.lower() == 'desc'

        if sort_by == 'created_at':
            filtered_tasks.sort(key=lambda x: x.created_at, reverse=reverse_sort)
        elif sort_by == 'due_date':
            filtered_tasks.sort(
                key=lambda x: (x.due_date is None, x.due_date),
                reverse=reverse_sort
            )
        elif sort_by == 'priority':
            priority_order = {PriorityEnum.HIGH: 0, PriorityEnum.MEDIUM: 1, PriorityEnum.LOW: 2}
            filtered_tasks.sort(
                key=lambda x: priority_order.get(PriorityEnum(x.priority), 1),
                reverse=reverse_sort
            )
        elif sort_by == 'title':
            filtered_tasks.sort(key=lambda x: x.title.lower(), reverse=reverse_sort)
        else:
            filtered_tasks.sort(key=lambda x: x.created_at, reverse=reverse_sort)

        return filtered_tasks

    @staticmethod
    def get_overdue_tasks(db: Session, user_id: str = None):
        """
        Get all overdue tasks (tasks with due date in the past that are not completed)

        Args:
            db: Database session
            user_id: Optional user ID to filter

        Returns:
            List of overdue Task objects
        """
        from .main import tasks_db  # Using in-memory simulation for now
        from datetime import datetime

        now = datetime.utcnow()
        overdue_tasks = []

        for task in tasks_db:
            if task.due_date and task.status == TaskStatusEnum.PENDING:
                due_dt = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                if due_dt < now:
                    if not user_id or task.user_id == user_id:
                        overdue_tasks.append(task)

        return overdue_tasks

    @staticmethod
    def get_tasks_by_priority(db: Session, user_id: str, priority: PriorityEnum):
        """
        Get tasks filtered by priority

        Args:
            db: Database session
            user_id: User ID
            priority: Priority level

        Returns:
            List of Task objects with specified priority
        """
        from .main import tasks_db  # Using in-memory simulation for now
        return [task for task in tasks_db
                if task.user_id == user_id and task.priority == priority]

    @staticmethod
    def get_tasks_by_tag(db: Session, user_id: str, tag: str):
        """
        Get tasks filtered by tag

        Args:
            db: Database session
            user_id: User ID
            tag: Tag to filter by

        Returns:
            List of Task objects with specified tag
        """
        from .main import tasks_db  # Using in-memory simulation for now
        return [task for task in tasks_db
                if task.user_id == user_id and tag in task.tags]

    @staticmethod
    def get_recurring_tasks(db: Session, user_id: str):
        """
        Get all recurring tasks

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of recurring Task objects
        """
        from .main import tasks_db  # Using in-memory simulation for now
        return [task for task in tasks_db
                if task.user_id == user_id and task.is_recurring]

    @staticmethod
    def get_tasks_with_reminders(db: Session, user_id: str):
        """
        Get all tasks that have reminders configured

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of Task objects with reminder settings
        """
        from .main import tasks_db  # Using in-memory simulation for now
        return [task for task in tasks_db
                if task.user_id == user_id and task.reminder_settings is not None]

    @staticmethod
    def search_tasks_by_keyword(db: Session, user_id: str, keyword: str):
        """
        Full-text search for tasks by keyword in title and description

        Args:
            db: Database session
            user_id: User ID
            keyword: Keyword to search for

        Returns:
            List of matching Task objects
        """
        from .main import tasks_db  # Using in-memory simulation for now
        keyword_lower = keyword.lower()
        return [
            task for task in tasks_db
            if task.user_id == user_id and
               (keyword_lower in task.title.lower() or
                (task.description and keyword_lower in task.description.lower()))
        ]

    @staticmethod
    def get_task_statistics(db: Session, user_id: str):
        """
        Get statistics for a user's tasks

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with task statistics
        """
        from .main import tasks_db  # Using in-memory simulation for now
        user_tasks = [task for task in tasks_db if task.user_id == user_id]

        total_tasks = len(user_tasks)
        completed_tasks = len([task for task in user_tasks if task.status == TaskStatusEnum.COMPLETED])
        pending_tasks = len([task for task in user_tasks if task.status == TaskStatusEnum.PENDING])
        high_priority_tasks = len([task for task in user_tasks if task.priority == PriorityEnum.HIGH])
        overdue_tasks = len(TaskQueries.get_overdue_tasks(db, user_id))
        recurring_tasks = len([task for task in user_tasks if task.is_recurring])

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "high_priority_tasks": high_priority_tasks,
            "overdue_tasks": overdue_tasks,
            "recurring_tasks": recurring_tasks
        }


# Real SQLAlchemy implementation (commented out as we're using in-memory for now)
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

class TaskEntity(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='pending')
    priority = Column(String(10), default='medium')  # high, medium, low
    tags = Column(JSONB, default=list)  # Array of strings
    due_date = Column(DateTime(timezone=True))  # Date and time when the task is due
    is_recurring = Column(Boolean, default=False)  # Whether this task is recurring
    recurrence_settings = Column(JSONB)  # Configuration for recurrence patterns
    reminder_settings = Column(JSONB)  # Configuration for reminder notifications
    user_id = Column(String(255), nullable=False)  # Identifier of the user who owns the task
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    def to_domain_model(self) -> Task:
        '''Convert SQLAlchemy model to Pydantic model'''
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            status=TaskStatusEnum(self.status),
            priority=PriorityEnum(self.priority),
            tags=self.tags or [],
            due_date=self.due_date.isoformat() if self.due_date else None,
            is_recurring=self.is_recurring,
            recurrence_settings=None,  # Would convert from JSONB
            reminder_settings=None,  # Would convert from JSONB
            user_id=self.user_id,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            completed_at=self.completed_at.isoformat() if self.completed_at else None
        )
"""