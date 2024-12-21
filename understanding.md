# Current Understanding
# Current Understanding

- Issue #348 requests a feature to monitor and optionally interrupt long-running commands
- The feature should:
  - Add a message to the conversation log every 10 seconds
  - Provide context about what the command is doing
  - Check if the command is still running
  - Ask whether to kill the command

# Questions to Investigate

- How are shell commands currently executed in the codebase?
- Is there an existing mechanism for monitoring running commands?
- Where in the codebase would be the best place to implement this feature?
- How can we implement a non-blocking way to check if a command is still running?
- How can we safely interrupt a running command?
