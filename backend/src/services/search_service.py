"""
SearchService for the Advanced Todo application.
Handles searching and filtering tasks.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from ..models.task import Task, PriorityEnum


class SearchService:
    """
    Service class for searching and filtering tasks.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the service with a database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def search_tasks(
        self,
        user_id: str,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Search tasks by various criteria.

        Args:
            user_id: ID of the user performing the search
            keyword: Search term to match in title or description
            status: Task status filter ('all', 'pending', 'completed')
            priority: Priority filter ('low', 'medium', 'high', 'urgent')
            tags: List of tags to filter by
            due_date_start: Start date for due date range
            due_date_end: End date for due date range
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of matching tasks
        """
        query = self.db_session.query(Task).filter(Task.user_id == user_id)

        # Apply keyword search
        if keyword:
            keyword = f"%{keyword}%"
            query = query.filter(
                or_(
                    Task.title.ilike(keyword),
                    Task.description.ilike(keyword)
                )
            )

        # Apply status filter
        if status and status.lower() != 'all':
            if status.lower() == 'pending':
                query = query.filter(Task.completed == False)
            elif status.lower() == 'completed':
                query = query.filter(Task.completed == True)

        # Apply priority filter
        if priority:
            try:
                priority_enum = PriorityEnum(priority.lower())
                query = query.filter(Task.priority == priority_enum)
            except ValueError:
                # Invalid priority - ignore the filter
                pass

        # Apply due date range filter
        if due_date_start:
            query = query.filter(Task.due_date >= due_date_start)
        if due_date_end:
            query = query.filter(Task.due_date <= due_date_end)

        # Apply tag filter (simplified - in a real app this would be more complex with many-to-many relationship)
        if tags:
            # For simplicity, we'll just check if any of the tags are in the task's tags array
            # This assumes tags are stored as a text array column in the Task model
            for tag in tags:
                query = query.filter(Task.tags.any(tag))

        # Apply sorting and pagination
        query = query.order_by(Task.created_at.desc())
        query = query.offset(offset).limit(limit)

        return query.all()

    def filter_tasks_by_multiple_criteria(
        self,
        user_id: str,
        filters: dict
    ) -> List[Task]:
        """
        Filter tasks by multiple criteria specified in a dictionary.

        Args:
            user_id: ID of the user performing the search
            filters: Dictionary with filter criteria

        Returns:
            List of matching tasks
        """
        query = self.db_session.query(Task).filter(Task.user_id == user_id)

        # Apply filters based on the dictionary
        for key, value in filters.items():
            if key == 'status':
                if value.lower() == 'pending':
                    query = query.filter(Task.completed == False)
                elif value.lower() == 'completed':
                    query = query.filter(Task.completed == True)
            elif key == 'priority':
                try:
                    priority_enum = PriorityEnum(value.lower())
                    query = query.filter(Task.priority == priority_enum)
                except ValueError:
                    # Invalid priority - skip this filter
                    continue
            elif key == 'category':
                query = query.filter(Task.category == value)
            elif key == 'completed':
                query = query.filter(Task.completed == bool(value))
            elif key == 'due_date_after':
                query = query.filter(Task.due_date >= value)
            elif key == 'due_date_before':
                query = query.filter(Task.due_date <= value)
            elif key == 'created_after':
                query = query.filter(Task.created_at >= value)
            elif key == 'created_before':
                query = query.filter(Task.created_at <= value)

        return query.all()

    def get_tasks_by_priority(
        self,
        user_id: str,
        priority: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Get tasks filtered by priority.

        Args:
            user_id: ID of the user
            priority: Priority level ('low', 'medium', 'high', 'urgent')
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of tasks with the specified priority
        """
        try:
            priority_enum = PriorityEnum(priority.lower())
        except ValueError:
            raise ValueError(f"Invalid priority: {priority}. Must be one of {list(PriorityEnum)}")

        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.priority == priority_enum
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    def get_tasks_by_tag(
        self,
        user_id: str,
        tag: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Get tasks filtered by a specific tag.

        Args:
            user_id: ID of the user
            tag: Tag to filter by
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of tasks with the specified tag
        """
        # Note: This implementation assumes tags are stored as an array in the Task model
        # In a real implementation with many-to-many relationships, this would be different
        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.tags.any(tag)
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """
        Get all overdue tasks for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of overdue tasks
        """
        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).order_by(Task.due_date.asc()).all()

    def get_tasks_due_today(self, user_id: str) -> List[Task]:
        """
        Get all tasks due today for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of tasks due today
        """
        from datetime import date
        today = date.today()

        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date >= datetime.combine(today, datetime.min.time()),
            Task.due_date < datetime.combine(today, datetime.max.time())
        ).order_by(Task.due_date.asc()).all()

    def get_tasks_due_soon(self, user_id: str, days_ahead: int = 7) -> List[Task]:
        """
        Get all tasks due within the next N days for a user.

        Args:
            user_id: ID of the user
            days_ahead: Number of days ahead to check for due tasks

        Returns:
            List of tasks due soon
        """
        from datetime import timedelta
        today = datetime.utcnow()
        future_date = today + timedelta(days=days_ahead)

        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date >= today,
            Task.due_date <= future_date
        ).order_by(Task.due_date.asc()).all()

    def get_tasks_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Get tasks within a specific date range.

        Args:
            user_id: ID of the user
            start_date: Start date for the range
            end_date: End date for the range
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of tasks within the date range
        """
        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.due_date >= start_date,
            Task.due_date <= end_date
        ).order_by(Task.due_date.asc()).offset(offset).limit(limit).all()

    def get_tasks_statistics(self, user_id: str) -> dict:
        """
        Get statistics about a user's tasks.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with task statistics
        """
        total_tasks = self.db_session.query(Task).filter(Task.user_id == user_id).count()
        completed_tasks = self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == True
        ).count()
        pending_tasks = total_tasks - completed_tasks

        # Get counts by priority
        priority_counts = {}
        for priority in PriorityEnum:
            count = self.db_session.query(Task).filter(
                Task.user_id == user_id,
                Task.priority == priority
            ).count()
            priority_counts[priority.value] = count

        # Get overdue count
        overdue_count = self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).count()

        return {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "overdue": overdue_count,
            "by_priority": priority_counts
        }

    def fuzzy_search_tasks(self, user_id: str, query: str, threshold: float = 0.6) -> List[Task]:
        """
        Perform a fuzzy search on tasks.

        Args:
            user_id: ID of the user
            query: Search query string
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of tasks matching the fuzzy search
        """
        # For now, we'll do a simple keyword search
        # In a real implementation, this would use fuzzy string matching algorithms
        return self.search_tasks(user_id, keyword=query)

    def get_tasks_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Get tasks filtered by category.

        Args:
            user_id: ID of the user
            category: Category to filter by
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of tasks with the specified category
        """
        return self.db_session.query(Task).filter(
            Task.user_id == user_id,
            Task.category == category
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    def get_all_tags_for_user(self, user_id: str) -> List[str]:
        """
        Get all unique tags used by a user.

        Args:
            user_id: ID of the user

        Returns:
            List of unique tags
        """
        # This would be more complex in a real implementation with a separate tags table
        # For now, we'll return an empty list since our current model doesn't support tags properly
        # In a real implementation, this would aggregate tags from all tasks for the user
        tasks = self.db_session.query(Task).filter(Task.user_id == user_id).all()

        all_tags = set()
        for task in tasks:
            if task.tags:
                all_tags.update(task.tags)

        return list(all_tags)