# Current understanding

- The `execute_shell` function in `gptme/tools/shell.py` is indeed the main entry point for executing shell commands.
- It accepts the command as part of a `kwargs` dictionary with the key "command".
- The function returns a generator that yields a single Message object.
- The returned Message has a role of "system" and contains the output of the executed command.
- Some commands (like "echo") are considered "allowlisted" and are executed without additional confirmation.

# Questions to investigate

- How does the `ShellSession` class work?
- What is the purpose of the `execute_shell_impl` function?
- How are long-running commands handled?
- Is there a way to interrupt commands?