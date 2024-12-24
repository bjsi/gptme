# Current Understanding

- The `execute_shell` function in `gptme/tools/shell.py` is the main entry point for executing shell commands.
- It uses `get_shell_command` to construct the command string.
- The `execute_shell_impl` function handles the execution of the shell command using a `ShellSession` object.
- It captures the output, standard error, and return code of the command.
- The function formats the output and yields a `Message` object containing the results of the command execution.
- The `ShellSession` class manages the shell session, including running commands and capturing their output.
  - The `run` method in the `ShellSession` class executes the command and captures its output, standard error, and return code.
  - It uses `select.select` to read from the command's stdout and stderr file descriptors.
  - The method constructs a full command by appending a return code echo and a delimiter.
  - It handles the case where the shell process dies by restarting the session and retrying the command once.
  - After running the command, it checks if the command is a `cd` command and changes the directory if successful.

# Questions to Investigate
- How can we modify the `run` method in the `ShellSession` class to periodically check the status of a running command?
- What mechanism can be used to implement a timeout for long-running commands?
- How can we add an option to interrupt a long-running command from the `execute_shell_impl` function?
- Are there existing mechanisms in the codebase for handling timeouts or interruptions that we can leverage?
