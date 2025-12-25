"""Main entry point for Todo Console Application."""

import sys
from src.manager import TaskManager
from src.ui import get_user_input, print_success, print_error, format_task_table, confirm_action


def main_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*50)
    print("Todo Console App")
    print("="*50)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Complete/Incomplete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")
    print("="*50)


def add_task(manager: TaskManager) -> None:
    """
    Add a new task operation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Add New Task ---")

    try:
        title = get_user_input("Enter task title: ")
        description = get_user_input("Enter task description (optional, press Enter to skip): ")

        # If description is empty, set to None
        if not description or not description.strip():
            description = None

        # Create task
        task, error = manager.create_task(title, description)

        if error:
            print_error(f"Error: {error}")
        else:
            print_success(f"Task #{task.id} '{task.title}' created successfully")

    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to main loop


def view_tasks(manager: TaskManager) -> None:
    """
    View all tasks operation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- All Tasks ---")
    tasks = manager.get_all_tasks()
    print(format_task_table(tasks))


def toggle_complete_menu(manager: TaskManager) -> None:
    """
    Toggle task completion status operation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Mark Complete/Incomplete ---")

    try:
        task_id_str = get_user_input("Enter task ID: ")

        # Validate ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print_error("Invalid ID: please enter a number")
            return

        # Toggle completion
        task, error = manager.toggle_complete(task_id)

        if error:
            print_error(f"Error: {error}")
        else:
            status = "completed" if task.completed else "pending"
            print_success(f"Task #{task.id} marked as {status}")

    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to main loop


def update_task_menu(manager: TaskManager) -> None:
    """
    Update task details operation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Update Task ---")

    try:
        task_id_str = get_user_input("Enter task ID: ")

        # Validate ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print_error("Invalid ID: please enter a number")
            return

        # Get current task to show details
        current_task = manager.get_task_by_id(task_id)
        if not current_task:
            print_error(f"Task not found: ID {task_id}")
            return

        print(f"\nCurrent title: {current_task.title}")
        print(f"Current description: {current_task.description or '(none)'}")

        # Get updates
        new_title = get_user_input("\nEnter new title (or press Enter to keep current): ").strip()
        new_description = get_user_input("Enter new description (or press Enter to keep current): ").strip()

        # If both are empty, nothing to update
        if not new_title and not new_description:
            print("No changes made")
            return

        # Prepare update values (None means keep existing)
        title_to_update = new_title if new_title else None
        description_to_update = new_description if new_description else None

        # Update task
        task, error = manager.update_task(task_id, title_to_update, description_to_update)

        if error:
            print_error(f"Error: {error}")
        else:
            print_success(f"Task #{task.id} updated successfully")

    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to main loop


def delete_task_menu(manager: TaskManager) -> None:
    """
    Delete task operation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Delete Task ---")

    try:
        task_id_str = get_user_input("Enter task ID: ")

        # Validate ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print_error("Invalid ID: please enter a number")
            return

        # Get task to show details for confirmation
        task = manager.get_task_by_id(task_id)
        if not task:
            print_error(f"Task not found: ID {task_id}")
            return

        # Show task details and confirm
        print(f"\nTask to delete:")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Description: {task.description or '(none)'}")

        if confirm_action("\nAre you sure you want to delete this task?"):
            deleted_task, error = manager.delete_task(task_id)
            if error:
                print_error(f"Error: {error}")
            else:
                print_success(f"Task #{deleted_task.id} '{deleted_task.title}' deleted successfully")
        else:
            print("Deletion cancelled")

    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to main loop


def run() -> None:
    """
    Main application loop.
    """
    manager = TaskManager()

    # Menu dispatch dictionary
    menu_actions = {
        "1": add_task,
        "2": view_tasks,
        "3": toggle_complete_menu,
        "4": update_task_menu,
        "5": delete_task_menu,
    }

    print("\nWelcome to Todo Console App!")

    try:
        while True:
            main_menu()

            try:
                choice = get_user_input("\nSelect option: ")

                if choice == "6":
                    print("\nApplication closed. Goodbye!")
                    sys.exit(0)

                action = menu_actions.get(choice)
                if action:
                    action(manager)
                else:
                    print_error("Invalid option, please try again")

            except (EOFError, KeyboardInterrupt):
                raise  # Re-raise to outer handler

    except KeyboardInterrupt:
        print("\n\nApplication closed")
        sys.exit(0)
    except EOFError:
        print("\n\nInput terminated. Application closed")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred. Please restart the application.")
        sys.exit(1)


if __name__ == "__main__":
    run()
