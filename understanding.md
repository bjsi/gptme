# Current Understanding
## Issue #348: Add a way for agents to monitor and optionally interrupt long-running commands

- The issue is about implementing a mechanism for agents to monitor and potentially interrupt long-running shell commands.
- This is particularly important for debugging commands that might hang.
- The proposed solution involves adding a message to the conversation log every 10 seconds, providing:
  - Context about what the command is doing
  - Whether the command is still running
  - An option to kill the command
# Questions to Investigate