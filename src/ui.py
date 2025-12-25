"""UI helper functions for console input/output."""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.task import Task


def get_user_input(prompt: str) -> str:
    """
    Wrap input() with error handling.

    Args:
        prompt: Prompt message to display

    Returns:
        User input string

    Raises:
        EOFError: If input is terminated (Ctrl+D)
        KeyboardInterrupt: If user interrupts (Ctrl+C)
    """
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to be handled by main loop


def print_success(message: str) -> None:
    """
    Display success message.

    Args:
        message: Success message to display
    """
    # Try to use green color if terminal supports it
    try:
        print(f"\033[92m✓ {message}\033[0m")
    except Exception:
        print(f"✓ {message}")


def print_error(message: str) -> None:
    """
    Display error message.

    Args:
        message: Error message to display
    """
    # Try to use red color if terminal supports it
    try:
        print(f"\033[91m✗ {message}\033[0m", file=sys.stderr)
    except Exception:
        print(f"✗ {message}", file=sys.stderr)


def format_task_table(tasks: list["Task"]) -> str:
    """
    Format tasks as a readable table.

    Args:
        tasks: List of Task objects to format

    Returns:
        Formatted string (table view) or "No tasks yet" if empty
    """
    if not tasks:
        return "No tasks yet"

    lines = []
    lines.append("\n" + "="*80)
    lines.append(f"{'ID':<4} | {'Status':<8} | {'Title':<25} | {'Description':<30}")
    lines.append("-"*80)

    for task in tasks:
        status = "✓ Done" if task.completed else "○ Pending"
        title = task.title[:25]  # Truncate if too long
        description = (task.description or "—")[:30]  # Truncate if too long

        lines.append(f"{task.id:<4} | {status:<8} | {title:<25} | {description:<30}")

    lines.append("="*80 + "\n")

    return "\n".join(lines)


def confirm_action(prompt: str) -> bool:
    """
    Get yes/no confirmation from user.

    Args:
        prompt: Confirmation prompt message

    Returns:
        True if user confirms (yes/y), False otherwise
    """
    response = get_user_input(f"{prompt} (yes/no): ").strip().lower()
    return response in ["yes", "y"]
