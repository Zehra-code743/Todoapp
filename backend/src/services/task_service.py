"""
Task Service
Business logic for task CRUD operations
"""

from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from src.models.task import Task
from src.schemas.task_schemas import TaskCreate, TaskUpdate


class TaskService:
    """Service class for task operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_tasks_by_user(
        self, user_id: str, status_filter: Optional[str] = None
    ) -> List[Task]:
        """
        Get all tasks for a user, optionally filtered by completion status

        Args:
            user_id: User ID to filter tasks
            status_filter: Optional filter ('all', 'pending', 'completed')

        Returns:
            List of Task objects sorted by creation date (newest first)
        """
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status_filter == "pending":
            query = query.where(Task.completed == False)
        elif status_filter == "completed":
            query = query.where(Task.completed == True)
        # 'all' or None = no filter

        # Sort by creation date (newest first)
        query = query.order_by(Task.created_at.desc())

        tasks = self.db.exec(query).all()
        return list(tasks)

    def create_task(self, user_id: str, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task for a user

        Args:
            user_id: Owner user ID
            title: Task title (1-200 characters)
            description: Optional description (max 1000 characters)

        Returns:
            Created Task object

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not title or len(title.strip()) < 1:
            raise ValueError("Title must be at least 1 character")
        if len(title) > 200:
            raise ValueError("Title must not exceed 200 characters")
        if description and len(description) > 1000:
            raise ValueError("Description must not exceed 1000 characters")

        # Create task
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def get_task_by_id(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID, ensuring it belongs to the user

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            Task object or None if not found or not owned by user
        """
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(query).first()
        return task

    def update_task(
        self, task_id: int, user_id: str, title: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update task title and/or description

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated Task object or None if not found

        Raises:
            ValueError: If validation fails
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        # Update fields if provided
        if title is not None:
            if len(title.strip()) < 1:
                raise ValueError("Title must be at least 1 character")
            if len(title) > 200:
                raise ValueError("Title must not exceed 200 characters")
            task.title = title.strip()

        if description is not None:
            if len(description) > 1000:
                raise ValueError("Description must not exceed 1000 characters")
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def toggle_task_completion(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Toggle task completion status

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            Updated Task object or None if not found
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def delete_task(self, task_id: int, user_id: str) -> bool:
        """
        Delete a task

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()

        return True

    def count_tasks_by_status(self, user_id: str) -> dict:
        """
        Count pending and completed tasks for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with 'pending' and 'completed' counts
        """
        all_tasks = self.get_tasks_by_user(user_id)

        pending = sum(1 for task in all_tasks if not task.completed)
        completed = sum(1 for task in all_tasks if task.completed)

        return {"pending": pending, "completed": completed, "total": len(all_tasks)}
