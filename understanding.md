# Current Understanding

- Issue 348 is about adding functionality for agents to monitor and interrupt long-running commands
- This is particularly important for debugging commands that may hang
- The proposed solution involves:
  - Adding periodic messages (every 10 seconds) to the conversation log
  - These messages should provide context about what the command is doing
  - The messages should also ask whether the agent wants to kill the command

# Questions to Investigate

- How are shell commands currently executed in the project?
- Is there an existing mechanism for monitoring command execution?
- Where in the codebase would be the best place to implement this new functionality?
- How can we implement a non-blocking way to check the status of a running command?
- What information can we retrieve about a running command to provide context in the log messages?
# Questions to Investigate