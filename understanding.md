# Current Understanding
## Issue #348: Add a way for agents to monitor and optionally interrupt long-running commands

- The issue is about implementing a mechanism for agents to monitor and potentially interrupt long-running shell commands.
- This is particularly important for debugging commands that might hang.
- The proposed solution involves adding a message to the conversation log every 10 seconds, providing:
  - Context about what the command is doing
  - Whether the command is still running
  - An option to kill the command
## Current Implementation

- The `execute_shell` function in `gptme/tools/shell.py` is the main entry point for executing shell commands.
- It uses `get_shell_command` to construct the command string from provided code, args, and kwargs.
- The function checks if the command is allowlisted using `is_allowlisted`.
- For non-allowlisted commands, it uses `execute_with_confirmation` to get user confirmation before execution.
- The actual execution is done by `execute_shell_impl`, which:
  - Uses a `ShellSession` to run the command.
  - Captures stdout and stderr.
  - Formats the output into a message.
- The current implementation does not have a mechanism for monitoring long-running commands or interrupting them.

# Questions to Investigate

1. How can we modify `execute_shell_impl` to add periodic status updates?
2. What's the best way to implement a command interruption mechanism?
3. How can we detect if a command is still running?
4. Should we modify the `ShellSession` class to support these new features?
5. How can we integrate the new monitoring and interruption features with the existing confirmation mechanism?