"""PostgreSQL database schema migration agent using Claude SDK."""

from pathlib import Path
from typing import Any, Callable

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookContext,
    HookInput,
    HookJSONOutput,
    HookMatcher,
    ResultMessage,
)


class PostgresAgent:
    """Agent for generating PostgreSQL migrations and seeds from app ideas."""

    def __init__(
        self,
        project_path: Path,
        todo_callback: Callable[[list[dict[str, Any]]], None] | None = None,
        message_callback: Callable[[str, str], None] | None = None,
    ):
        """Initialize the PostgreSQL agent.

        Args:
            project_path: Path where migrations and seeds will be created
            todo_callback: Optional callback to receive todo updates from the agent
            message_callback: Optional callback to receive message updates (type, preview)
        """
        self.project_path = project_path
        self.todo_callback = todo_callback
        self.message_callback = message_callback
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from the specs file."""
        prompt_path = Path(__file__).parent.parent / "specs" / "system-prompt.md"
        return prompt_path.read_text()

    async def _post_tool_use_hook(
        self,
        hook_input: HookInput,
        _tool_use_id: str | None,
        _context: HookContext,
    ) -> HookJSONOutput:
        """Hook callback for PostToolUse events.

        Captures TodoWrite tool calls to extract and report todo lists to the CLI.
        """
        # Type guard to check if this is a PostToolUse hook
        if hook_input.get("hook_event_name") != "PostToolUse":
            return {"continue_": True}

        post_tool_use_input = hook_input  # type: ignore[assignment]
        assert isinstance(post_tool_use_input, dict)

        tool_name = post_tool_use_input.get("tool_name")
        tool_input = post_tool_use_input.get("tool_input", {})

        # If this is a TodoWrite call, extract and report the todos
        if tool_name == "TodoWrite" and self.todo_callback:
            todos = tool_input.get("todos", [])
            self.todo_callback(todos)

        # Always allow the tool to proceed
        return {"continue_": True}

    async def run(self, user_idea: str) -> ResultMessage:
        """Run the agent with the user's app idea.

        Args:
            user_idea: The user's description of their application idea

        Returns:
            ResultMessage containing the agent's final result
        """
        # Set up hook for all PostToolUse events to capture TodoWrite
        hooks: dict[str, list[HookMatcher]] = {
            "PostToolUse": [
                HookMatcher(
                    matcher=None,  # Capture all tool calls
                    hooks=[self._post_tool_use_hook],
                )
            ]
        }

        # Configure agent options
        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            cwd=str(self.project_path),
            hooks=hooks,
            permission_mode="bypassPermissions",  # Auto-approve all tools for seamless execution
        )

        # Create client with hooks enabled
        client = ClaudeSDKClient(options=options)

        # Connect and send query
        await client.connect()
        await client.query(user_idea)

        # Receive messages
        result_message: ResultMessage | None = None

        from claude_agent_sdk import AssistantMessage, TextBlock

        async for message in client.receive_messages():
            # Extract message info
            msg_type = type(message).__name__
            msg_preview = ""

            if isinstance(message, AssistantMessage):
                # Extract first text block
                for block in message.content:
                    if isinstance(block, TextBlock):
                        first_line = block.text.split('\n')[0][:60]
                        msg_preview = first_line
                        break

            # Send to callback
            if self.message_callback:
                self.message_callback(msg_type, msg_preview)

            # The last message should be a ResultMessage
            if isinstance(message, ResultMessage):
                result_message = message
                break

        # Disconnect
        await client.disconnect()

        if result_message is None:
            raise RuntimeError("No result message received from agent")

        return result_message


def create_agent(
    project_path: Path,
    todo_callback: Callable[[list[dict[str, Any]]], None] | None = None,
    message_callback: Callable[[str, str], None] | None = None,
) -> PostgresAgent:
    """Create a new PostgreSQL agent instance.

    Args:
        project_path: Path where migrations and seeds will be created
        todo_callback: Optional callback to receive todo updates from the agent
        message_callback: Optional callback to receive message updates (type, preview)

    Returns:
        Configured PostgresAgent instance
    """
    return PostgresAgent(project_path, todo_callback, message_callback)
