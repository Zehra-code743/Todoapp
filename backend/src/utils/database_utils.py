"""
Database utility functions for the Advanced Todo application.
Provides common database operations and helpers.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List, Optional
import logging


logger = logging.getLogger(__name__)


def execute_raw_sql(db_session: Session, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Execute raw SQL query and return results as list of dictionaries.

    Args:
        db_session: SQLAlchemy database session
        query: SQL query string
        params: Parameters for the query

    Returns:
        List of dictionaries representing rows
    """
    try:
        if params is None:
            params = {}

        result = db_session.execute(text(query), params)
        rows = result.fetchall()

        # Convert Row objects to dictionaries
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except SQLAlchemyError as e:
        logger.error(f"Raw SQL execution failed: {str(e)}")
        raise


def bulk_insert(db_session: Session, table_name: str, data: List[Dict[str, Any]]) -> int:
    """
    Perform bulk insert operation.

    Args:
        db_session: SQLAlchemy database session
        table_name: Name of the table to insert into
        data: List of dictionaries containing data to insert

    Returns:
        Number of rows inserted
    """
    if not data:
        return 0

    try:
        # Build column names from the first record
        columns = list(data[0].keys())
        column_names = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in columns])

        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        result = db_session.execute(text(query), data)
        db_session.commit()

        return result.rowcount
    except SQLAlchemyError as e:
        logger.error(f"Bulk insert failed: {str(e)}")
        db_session.rollback()
        raise


def get_table_row_count(db_session: Session, table_name: str) -> int:
    """
    Get the total number of rows in a table.

    Args:
        db_session: SQLAlchemy database session
        table_name: Name of the table

    Returns:
        Number of rows in the table
    """
    try:
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = db_session.execute(text(query))
        count = result.scalar()
        return count
    except SQLAlchemyError as e:
        logger.error(f"Row count query failed: {str(e)}")
        raise


def table_exists(db_session: Session, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        db_session: SQLAlchemy database session
        table_name: Name of the table to check

    Returns:
        True if table exists, False otherwise
    """
    try:
        # Different databases have different ways to check for table existence
        # This approach works for PostgreSQL
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            )
        """
        result = db_session.execute(text(query), {"table_name": table_name})
        exists = result.scalar()
        return exists
    except SQLAlchemyError as e:
        logger.error(f"Table existence check failed: {str(e)}")
        raise


def create_index_if_not_exists(db_session: Session, table_name: str, column_name: str, index_name: Optional[str] = None) -> bool:
    """
    Create an index on a column if it doesn't already exist.

    Args:
        db_session: SQLAlchemy database session
        table_name: Name of the table
        column_name: Name of the column to index
        index_name: Optional custom name for the index

    Returns:
        True if index was created, False if it already existed
    """
    if index_name is None:
        index_name = f"idx_{table_name}_{column_name}"

    try:
        # Check if index exists
        check_query = """
            SELECT EXISTS (
                SELECT FROM pg_indexes
                WHERE tablename = :table_name
                AND indexname = :index_name
            )
        """
        result = db_session.execute(text(check_query), {
            "table_name": table_name,
            "index_name": index_name
        })
        index_exists = result.scalar()

        if not index_exists:
            create_query = f"CREATE INDEX {index_name} ON {table_name} ({column_name})"
            db_session.execute(text(create_query))
            db_session.commit()
            logger.info(f"Created index {index_name} on {table_name}.{column_name}")
            return True
        else:
            logger.info(f"Index {index_name} already exists on {table_name}.{column_name}")
            return False
    except SQLAlchemyError as e:
        logger.error(f"Index creation failed: {str(e)}")
        db_session.rollback()
        raise


def get_column_info(db_session: Session, table_name: str) -> List[Dict[str, Any]]:
    """
    Get information about columns in a table.

    Args:
        db_session: SQLAlchemy database session
        table_name: Name of the table

    Returns:
        List of dictionaries containing column information
    """
    try:
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                is_primary_key
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """
        # Also get primary key info from constraint information
        pk_query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_name = :table_name
        """

        result = db_session.execute(text(query), {"table_name": table_name})
        columns = []
        for row in result:
            col_dict = dict(row._mapping)
            columns.append(col_dict)

        # Add primary key info to each column
        pk_result = db_session.execute(text(pk_query), {"table_name": table_name})
        pk_columns = [row[0] for row in pk_result]

        for col in columns:
            col['is_primary_key'] = col['column_name'] in pk_columns

        return columns
    except SQLAlchemyError as e:
        logger.error(f"Column info query failed: {str(e)}")
        raise