# Current understanding

- The `execute_shell` function in `gptme/tools/shell.py` is indeed the main entry point for executing shell commands.
- It accepts the command as part of a `kwargs` dictionary with the key "command".
- The function returns a generator that yields a single Message object.
- The returned Message has a role of "system" and contains the output of the executed command.
- Some commands (like "echo") are considered "allowlisted" and are executed without additional confirmation.

- The `ShellSession` class manages a persistent bash shell process:
  - It uses `subprocess.Popen` to create and interact with the shell process.
  - The `run` method is used to execute commands in the shell.
  - It handles output capturing and return codes.
  - There's a mechanism to restart the shell if it dies unexpectedly.
  - It sets some environment variables to control pager behavior (PAGER, GH_PAGER, GIT_PAGER).

# Questions to investigate

- What is the purpose of the `execute_shell_impl` function?
- How are long-running commands handled?
- Is there a way to interrupt commands?