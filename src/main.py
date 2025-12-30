"""Main entry point for Todo Console Application."""

import sys
from src.manager import TaskManager
from src.ui import (
    get_user_input,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_sub_header,
    print_divider,
    print_banner,
    print_menu,
    print_task_details,
    confirm_action,
    format_task_table,
    console,
)


def main_menu() -> None:
    """Display the main menu using rich styling."""
    console.clear()
    print_banner()
    print_divider("magenta")

    print_menu({
        "1": "Add a new task",
        "2": "View all tasks",
        "3": "Mark task as complete/incomplete",
        "4": "Update task details",
        "5": "Delete a task",
        "6": "Exit application",
    })

    print_divider("magenta")


def add_task(manager: TaskManager) -> None:
    """
    Add a new task operation.

    Args:
        manager: TaskManager instance
    """
    print_sub_header("Add New Task")

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
    print_sub_header("All Tasks")
    tasks = manager.get_all_tasks()
    table = format_task_table(tasks)
    if isinstance(table, str):
        print(table)
    else:
        console.print(table)


def toggle_complete_menu(manager: TaskManager) -> None:
    """
    Toggle task completion status operation.

    Args:
        manager: TaskManager instance
    """
    print_sub_header("Mark Complete/Incomplete")

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
    print_sub_header("Update Task")

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

        # Show current task details
        print_task_details(current_task)

        # Get updates
        new_title = get_user_input("\nEnter new title (or press Enter to keep current): ").strip()
        new_description = get_user_input("Enter new description (or press Enter to keep current): ").strip()

        # If both are empty, nothing to update
        if not new_title and not new_description:
            print_warning("No changes made")
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
    print_sub_header("Delete Task")

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

        # Show task details
        print_task_details(task)

        if confirm_action("Are you sure you want to delete this task?"):
            deleted_task, error = manager.delete_task(task_id)
            if error:
                print_error(f"Error: {error}")
            else:
                print_success(f"Task #{deleted_task.id} '{deleted_task.title}' deleted successfully")
        else:
            print_info("Deletion cancelled")

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

    try:
        while True:
            main_menu()

            try:
                choice = get_user_input("\nSelect option: ")

                if choice == "6":
                    console.clear()
                    print_banner()
                    print_success("Thank you for using Todo App! Goodbye!")
                    print_divider("magenta")
                    sys.exit(0)

                action = menu_actions.get(choice)
                if action:
                    action(manager)
                else:
                    print_error("Invalid option, please try again")

                # Add a small pause and prompt to continue
                if choice in ["1", "2", "3", "4", "5"]:
                    print_info("Press Enter to continue...")
                    input()

            except (EOFError, KeyboardInterrupt):
                raise  # Re-raise to outer handler

    except KeyboardInterrupt:
        console.clear()
        print_banner()
        print_info("Application closed by user")
        print_divider("magenta")
        sys.exit(0)
    except EOFError:
        console.clear()
        print_banner()
        print_info("Input terminated. Application closed")
        print_divider("magenta")
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
