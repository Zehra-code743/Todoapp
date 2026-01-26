"""
Base service class for the Advanced Todo application.
Provides common functionality for all services.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base class for all services.
    Provides common methods and properties for services.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the service with a database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    @abstractmethod
    def create(self, **kwargs) -> Any:
        """
        Create a new entity.

        Args:
            **kwargs: Entity attributes

        Returns:
            Created entity
        """
        pass

    @abstractmethod
    def get(self, entity_id: int) -> Optional[Any]:
        """
        Get an entity by ID.

        Args:
            entity_id: ID of the entity

        Returns:
            Entity or None if not found
        """
        pass

    @abstractmethod
    def update(self, entity_id: int, **kwargs) -> Optional[Any]:
        """
        Update an entity.

        Args:
            entity_id: ID of the entity
            **kwargs: Attributes to update

        Returns:
            Updated entity or None if not found
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: ID of the entity

        Returns:
            True if deleted, False if not found
        """
        pass

    def commit(self):
        """
        Commit the current transaction.
        """
        try:
            self.db_session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database commit failed: {str(e)}")
            self.db_session.rollback()
            raise

    def rollback(self):
        """
        Rollback the current transaction.
        """
        self.db_session.rollback()

    @contextmanager
    def transaction(self):
        """
        Context manager for handling database transactions.
        Automatically commits on success or rolls back on exception.
        """
        try:
            yield self.db_session
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            self.db_session.rollback()
            raise