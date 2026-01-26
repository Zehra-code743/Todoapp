"""
Database migration scripts for the Advanced Todo application.
Handles database schema creation and updates.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import settings
import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


def create_initial_tables():
    """
    Create initial database tables for the application.
    """
    engine = create_engine(settings.database_url)

    # SQL statements to create tables
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            timezone VARCHAR(50) DEFAULT 'UTC',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(255) NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            priority VARCHAR(20) DEFAULT 'medium',
            tags TEXT,
            category VARCHAR(100),
            due_date TIMESTAMP,
            reminder_settings TEXT,
            reminder_sent BOOLEAN DEFAULT 0,
            is_recurring BOOLEAN DEFAULT 0,
            recurrence_pattern TEXT,
            parent_task_id INTEGER,
            next_occurrence_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            scheduled_for TIMESTAMP NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            user_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    ]

    # Index statements (separate for SQLite compatibility)
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_is_recurring ON tasks(is_recurring);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);",
        "CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_reminders_scheduled_for ON reminders(scheduled_for);",
        "CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);"
    ]

    try:
        with engine.connect() as conn:
            # Create tables if they don't exist
            for stmt in create_statements:
                conn.execute(text(stmt))

            # Add missing columns to tasks table if they don't exist
            # Check if priority column exists, if not add it
            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN tags TEXT;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN category VARCHAR(100);"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN reminder_settings TEXT;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN reminder_sent BOOLEAN DEFAULT 0;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT 0;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence_pattern TEXT;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN next_occurrence_date TIMESTAMP;"))
            except:
                pass  # Column already exists

            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP;"))
            except:
                pass  # Column already exists

            # Execute index statements separately for SQLite compatibility
            for stmt in index_statements:
                try:
                    conn.execute(text(stmt))
                except:
                    pass  # Index may already exist

            conn.commit()

        logger.info("Initial database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False


def migrate_database():
    """
    Run database migrations to update schema to current version.
    """
    logger.info("Starting database migration...")

    # For now, just run the initial table creation
    # In a real application, you'd have versioned migrations
    success = create_initial_tables()

    if success:
        logger.info("Database migration completed successfully")
    else:
        logger.error("Database migration failed")

    return success


def rollback_migration(version: str):
    """
    Rollback database to a previous version.

    Args:
        version: Version to rollback to
    """
    logger.warning(f"Rolling back to version {version} - not implemented")
    # In a real application, you would implement rollback logic here


def get_current_version():
    """
    Get the current database schema version.

    Returns:
        Current version string
    """
    # For now, we'll return a simple version
    # In a real application, you'd have a version tracking table
    return "1.0.0"


def check_migration_status():
    """
    Check the status of database migrations.

    Returns:
        Dictionary with migration status information
    """
    engine = create_engine(settings.database_url)

    try:
        with engine.connect() as conn:
            # Check if tables exist (using sqlite_master for SQLite)
            result = conn.execute(text("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name IN ('users', 'tasks', 'reminders', 'tags');
            """))

            existing_tables = [row[0] for row in result]

            required_tables = ['users', 'tasks', 'reminders', 'tags']
            missing_tables = [table for table in required_tables if table not in existing_tables]

            return {
                "current_version": get_current_version(),
                "tables_exist": len(existing_tables) == len(required_tables),
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "status": "OK" if not missing_tables else "INCOMPLETE"
            }
    except Exception as e:
        logger.error(f"Error checking migration status: {str(e)}")
        return {
            "current_version": "UNKNOWN",
            "tables_exist": False,
            "existing_tables": [],
            "missing_tables": ['users', 'tasks', 'reminders', 'tags'],
            "status": "ERROR",
            "error": str(e)
        }


def seed_initial_data():
    """
    Seed the database with initial data if needed.
    """
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if users table is empty
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        if user_count == 0:
            # Insert default user for testing
            session.execute(text("""
                INSERT INTO users (id, timezone)
                VALUES ('default_user', 'UTC');
            """))
            session.commit()
            logger.info("Seeded default user data")

        session.close()
        return True
    except Exception as e:
        logger.error(f"Error seeding initial data: {str(e)}")
        if session:
            session.rollback()
            session.close()
        return False


if __name__ == "__main__":
    # If run directly, perform the migration
    migrate_database()
    status = check_migration_status()
    print(f"Migration status: {status}")