# Current Understanding
## Issue #348: Add a way for agents to monitor and optionally interrupt long-running commands

- The issue is about implementing a mechanism for agents to monitor and potentially interrupt long-running shell commands.
- This is particularly important for debugging commands that might hang.
- The proposed solution involves adding a message to the conversation log every 10 seconds, providing:
  - Context about what the command is doing
  - Whether the command is still running
  - An option to kill the command
# Questions to Investigate

## Current Implementation

- The `execute_shell` function in `gptme/tools/shell.py` is the main entry point for executing shell commands.
- It uses `get_shell_command` to construct the command string from the provided code, args, and kwargs.
- The function uses a `ShellSession` class to manage the shell environment.
- There's an allowlist mechanism (`is_allowlisted`) that determines whether a command needs confirmation before execution.
- The actual execution is handled by `execute_shell_impl`, which runs the command and formats the output.
- The output is shortened using `_shorten_stdout` to limit the number of tokens.
- There's no current mechanism for monitoring long-running commands or interrupting them.

## Questions to Investigate

1. How can we modify the `execute_shell_impl` function to add periodic status updates?
2. What's the best way to implement a timer to check the command status every 10 seconds?
3. How can we add an option to interrupt the command execution?
4. Should we modify the `ShellSession` class to handle long-running commands, or create a new class?
5. How can we integrate the new monitoring feature with the existing confirmation mechanism?
6. What's the best way to add the status updates to the conversation log?
7. How should we handle the case where a command finishes before the 10-second check?
8. Should we implement a timeout feature for commands, and if so, how?