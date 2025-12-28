"""UI helper functions for console input/output using Rich."""

import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.style import Style
from rich.color import Color
from rich.markdown import Markdown
from rich.syntax import Syntax

if TYPE_CHECKING:
    from src.task import Task

# Create a single console instance
console = Console()


def get_user_input(prompt: str) -> str:
    """
    Wrap input() with error handling and styled prompt.

    Args:
        prompt: Prompt message to display

    Returns:
        User input string

    Raises:
        EOFError: If input is terminated (Ctrl+D)
        KeyboardInterrupt: If user interrupts (Ctrl+C)
    """
    try:
        styled_prompt = Text(prompt, style="bold cyan")
        return Prompt.ask(styled_prompt)
    except (EOFError, KeyboardInterrupt):
        raise  # Re-raise to be handled by main loop


def print_success(message: str) -> None:
    """
    Display success message in green.

    Args:
        message: Success message to display
    """
    text = Text(f"  [OK] {message}", style="bold green")
    console.print(text)


def print_error(message: str) -> None:
    """
    Display error message in red.

    Args:
        message: Error message to display
    """
    text = Text(f"  [ERROR] {message}", style="bold red")
    console.print(text)


def print_warning(message: str) -> None:
    """
    Display warning message in yellow.

    Args:
        message: Warning message to display
    """
    text = Text(f"  [WARNING] {message}", style="bold yellow")
    console.print(text)


def print_info(message: str) -> None:
    """
    Display info message in blue.

    Args:
        message: Info message to display
    """
    text = Text(f"  [INFO] {message}", style="bold blue")
    console.print(text)


def print_header(title: str) -> None:
    """
    Display a styled header.

    Args:
        title: Header title text
    """
    text = Text(title, style="bold white on blue")
    console.print(Panel(text, expand=False, border_style="blue"))


def print_sub_header(title: str) -> None:
    """
    Display a styled sub-header.

    Args:
        title: Sub-header title text
    """
    text = Text(f"  {title}  ", style="bold white on magenta")
    console.print(text)


def format_task_table(tasks: list["Task"]) -> str:
    """
    Format tasks as a rich colorful table.

    Args:
        tasks: List of Task objects to format

    Returns:
        Formatted string (table view) or "No tasks yet" if empty
    """
    if not tasks:
        return "[yellow]No tasks yet[/yellow]"

    table = Table(
        title="[bold cyan]📋 Your Tasks[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        row_styles=["", "dim"],
        expand=True,
    )

    # Add columns
    table.add_column("ID", width=6, style="cyan bold")
    table.add_column("Status", width=12, style="")
    table.add_column("Title", width=35, style="white")
    table.add_column("Description", width=40, style="dim")
    table.add_column("Created", width=20, style="dim")

    for task in tasks:
        # Status with emoji and color
        if task.completed:
            status = Text("  ✓ Done  ", style="bold green")
        else:
            status = Text("  ○ Pending  ", style="bold yellow")

        # Title - truncate if too long
        title = task.title[:35] if len(task.title) > 35 else task.title
        if task.completed:
            title = Text(title, style="strike green")
        else:
            title = Text(title, style="bold white")

        # Description - truncate if too long
        description = (task.description or "—")[:40]
        if len(str(task.description or "")) > 40:
            description += "..."

        # Created date
        created = task.created_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(
            f"[cyan]{task.id}[/cyan]",
            status,
            title,
            description,
            created,
        )

    return table


def confirm_action(prompt: str) -> bool:
    """
    Get yes/no confirmation from user with styled prompt.

    Args:
        prompt: Confirmation prompt message

    Returns:
        True if user confirms (yes/y), False otherwise
    """
    styled_prompt = Text(f"\n  {prompt} ", style="bold yellow")
    response = Prompt.ask(styled_prompt, choices=["yes", "y", "no", "n"], default="no")
    return response.lower() in ["yes", "y"]


def print_divider(style: str = "cyan") -> None:
    """
    Print a styled divider line.

    Args:
        style: Rich style string for the divider
    """
    console.print("─" * 60, style=style)


def print_loading(message: str) -> None:
    """
    Print a loading/status message.

    Args:
        message: Message to display
    """
    text = Text(f"  {message}", style="cyan")
    console.print(text)


def print_banner() -> None:
    """
    Display the application banner.
    """
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     TODO                                             ║
    ║     ██╗██╗   ██╗███████╗██████╗ ██████╗  ██████╗      ║
    ║     ██║██║   ██║██╔════╝██╔══██╗██╔══██╗██╔═══██╗     ║
    ║     ██║██║   ██║█████╗  ██║  ██║██║  ██║██║   ██║     ║
    ║     ██║╚██╗ ██╔╝██╔══╝  ██║  ██║██║  ██║██║   ██║     ║
    ║     ██║ ╚████╔╝ ███████╗██████╔╝██████╔╝╚██████╔╝     ║
    ║     ╚═╝  ╚═══╝  ╚══════╝╚═════╝ ╚═════╝  ╚═════╝      ║
    ║                                                       ║
    ║           Console Application                        ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, border_style="magenta", expand=False))


def print_menu(options: dict[str, str]) -> None:
    """
    Display a styled menu.

    Args:
        options: Dictionary of option keys and descriptions
    """
    table = Table(show_header=False, border_style="cyan", expand=True, box=None)
    table.add_column("Option", width=10, style="bold cyan")
    table.add_column("Description", style="white")

    for key, description in options.items():
        table.add_row(f"  [{key}]", description)

    console.print(table)


def print_task_details(task: "Task") -> None:
    """
    Display task details in a styled panel.

    Args:
        task: Task object to display
    """
    from rich.text import Text

    status_emoji = "✓" if task.completed else "○"
    status_text = "Completed" if task.completed else "Pending"
    status_color = "green" if task.completed else "yellow"

    # Build status line properly using Text
    status_line = Text()
    status_line.append(status_emoji, style=status_color)
    status_line.append(f" {status_text}", style=f"bold {status_color}")

    details = Text()
    details.append("Task Details\n", style="bold cyan")
    details.append("\n")
    details.append(f"ID:          ", style="white")
    details.append(f"{task.id}\n", style="cyan")
    details.append(f"Title:       ", style="white")
    details.append(f"{task.title}\n", style="white")
    details.append(f"Description: ", style="white")
    details.append(f"{task.description or '(none)'}\n", style="dim")
    details.append(f"Status:      ", style="white")
    details.append(status_line)
    details.append("\n")
    details.append(f"Created:     ", style="white")
    details.append(f"{task.created_at.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")

    console.print(Panel(details, border_style="cyan", expand=False))
