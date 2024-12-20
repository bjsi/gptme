# Current Understanding

- Issue #348 requests a feature to monitor and optionally interrupt long-running commands
- This is particularly important for debugging commands that may hang
- The proposed solution involves:
  - Monitoring shell commands every 10 seconds
  - Adding context about the command's status to the conversation log
  - Providing an option to kill the command

# Questions to Investigate

- How are shell commands currently executed in the codebase?
- Where in the code would be the best place to implement this monitoring feature?
- How can we periodically check the status of a running command?
- How can we add messages to the conversation log during command execution?
- What's the best way to implement the option to kill a running command?