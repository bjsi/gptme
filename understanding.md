# Current Understanding
## Issue Overview
- Issue #348: Add a way for agents to monitor and optionally interrupt long-running commands
- Problem: Some GitHub issues involve debugging commands that hang
- Proposed solution: 
  - After running a shell command, add a message to the conversation log every 10 seconds
  - Message should provide context about the command's status
  - Ask whether to kill the command
# Questions to Investigate