"""CLI for PostgreSQL database schema migration agent."""

import asyncio
import time
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agents.postgres_agent import create_agent


class TodoTracker:
    """Track and display todos from the agent."""

    def __init__(self):
        self.todos: list[dict[str, Any]] = []
        self.task_start_times: dict[int, float] = {}
        self.task_end_times: dict[int, float] = {}
        self.agent_start_time: float | None = None
        self.current_message_type: str = ""
        self.current_message_preview: str = ""

    def update_todos(self, todos: list[dict[str, Any]]) -> None:
        """Update the todo list from the agent.

        Args:
            todos: List of todo items from the agent
        """
        current_time = time.time()

        # Track when tasks start
        for i, todo in enumerate(todos):
            status = todo.get("status", "pending")

            # Mark start time for newly in-progress tasks
            if status == "in_progress" and i not in self.task_start_times:
                self.task_start_times[i] = current_time

            # Mark end time for newly completed tasks
            if status == "completed" and i not in self.task_end_times:
                self.task_end_times[i] = current_time

        self.todos = todos

    def update_message(self, msg_type: str, msg_preview: str) -> None:
        """Update the current message being processed.

        Args:
            msg_type: Type of message (e.g., "AssistantMessage")
            msg_preview: Preview of the message content
        """
        self.current_message_type = msg_type
        # Clean up preview: strip whitespace, ensure single line
        self.current_message_preview = msg_preview.strip() if msg_preview else ""

    def get_task_time(self, index: int) -> float:
        """Get the elapsed time for a task.

        Args:
            index: Index of the task

        Returns:
            Elapsed time in seconds
        """
        current_time = time.time()

        if index in self.task_end_times:
            # Task completed - return duration
            start = self.task_start_times.get(index, self.agent_start_time or current_time)
            return self.task_end_times[index] - start
        elif index in self.task_start_times:
            # Task in progress - return current duration
            return current_time - self.task_start_times[index]
        else:
            # Task not started
            return 0.0

    def create_table(self, agent_elapsed: float, spinner_state: str = "⠋") -> Table:
        """Create a rich table displaying the current todos.

        Args:
            agent_elapsed: Time elapsed since agent started
            spinner_state: Current spinner character

        Returns:
            Rich Table object
        """
        table = Table(show_header=False, box=None, padding=(0, 0))

        # First row: Timer and message on same line, left-aligned
        # Always show message, truncate to fit (max 80 chars total)
        if self.current_message_preview:
            # Take only first line and truncate if needed
            msg = self.current_message_preview.split('\n')[0][:70]
        else:
            msg = "Waiting for response..."

        header_line = Text()
        header_line.append(f"Agent Execution ({agent_elapsed:.1f}s) - ", style="bold")
        header_line.append(msg, style="dim")
        table.add_row(header_line)

        # Add separator
        table.add_row("")

        # If no todos yet, show a waiting message
        if not self.todos:
            table.add_row(Text(f"{spinner_state} Starting agent...", style="cyan"))
            return table

        for i, todo in enumerate(self.todos):
            status = todo.get("status", "pending")
            content = todo.get("content", "")
            task_time = self.get_task_time(i)

            # Determine icon based on status
            if status == "completed":
                icon = Text("[✓]", style="green bold")
                time_text = f"({task_time:.1f}s)"
            elif status == "in_progress":
                icon = Text(f"[{spinner_state}]", style="cyan bold")
                time_text = f"({task_time:.1f}s)"
            else:  # pending
                icon = Text("[ ]", style="dim")
                time_text = ""

            # Combine icon, content, and time
            row_text = Text()
            row_text.append(icon)
            row_text.append(f" {content} ")
            if time_text:
                row_text.append(time_text, style="dim")

            table.add_row(row_text)

        return table


async def run_agent_with_ui(project_path: Path, user_idea: str, console: Console) -> None:
    """Run the agent with live UI updates.

    Args:
        project_path: Path where migrations and seeds will be created
        user_idea: The user's application idea
        console: Rich console for output
    """
    tracker = TodoTracker()
    tracker.agent_start_time = time.time()

    # Create agent with todo and message callbacks
    agent = create_agent(
        project_path,
        todo_callback=tracker.update_todos,
        message_callback=tracker.update_message,
    )

    # Run agent in background task
    agent_task = asyncio.create_task(agent.run(user_idea))

    # Spinner frames for animation
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_idx = 0

    # Live update the UI while agent runs
    with Live(console=console, refresh_per_second=4) as live:
        while not agent_task.done():
            elapsed = time.time() - tracker.agent_start_time
            spinner_state = spinner_frames[frame_idx % len(spinner_frames)]
            table = tracker.create_table(elapsed, spinner_state)
            live.update(table)
            frame_idx += 1
            await asyncio.sleep(0.25)

        # Final update
        elapsed = time.time() - tracker.agent_start_time
        table = tracker.create_table(elapsed, "✓")
        live.update(table)

    # Get the result
    result = await agent_task

    # Display final result message
    console.print()
    if result.is_error:
        # Error message in a red panel
        error_panel = Panel(
            result.result or "Agent execution failed",
            title="[bold red]Error[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
    else:
        # Success - render markdown result
        if result.result:
            # Render the markdown content
            md = Markdown(result.result)
            console.print(md)
        else:
            console.print("[bold green]Success![/bold green]")

    # Display stats in a subtle way
    console.print()
    stats_text = f"Duration: {result.duration_ms / 1000:.1f}s | Turns: {result.num_turns}"
    if result.total_cost_usd:
        stats_text += f" | Cost: ${result.total_cost_usd:.4f}"
    console.print(f"[dim]{stats_text}[/dim]")


@click.command()
@click.option(
    "-p",
    "--project-path",
    type=click.Path(path_type=Path),
    required=True,
    help="Path where migrations and seeds will be created",
)
def build_idea(project_path: Path) -> None:
    """Build PostgreSQL migrations and seeds from your app idea.

    This tool uses Claude to convert your application idea into executable
    PostgreSQL database schema migrations and seed data.
    """
    console = Console()

    # Ensure project path exists
    project_path.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]{project_path} created[/green]")
    console.print()

    # Get user idea
    user_idea = click.prompt("Describe your idea", type=str)
    console.print()

    # Run the agent
    asyncio.run(run_agent_with_ui(project_path, user_idea, console))


if __name__ == "__main__":
    build_idea()
