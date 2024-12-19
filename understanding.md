# Current Understanding

- Issue 348 is about adding functionality for agents to monitor and interrupt long-running commands.
- The requirement is to add a message to the conversation log every 10 seconds, providing context about the command's status.
- The agent should have the option to kill the command if necessary.

# Questions to Investigate

1. How are shell commands currently executed in the codebase?
2. Where in the code would be the best place to implement this monitoring functionality?
3. How is the conversation log currently managed?
4. What mechanism can we use to periodically check the status of a running command?
5. How can we implement the ability to interrupt a running command?
# Questions to Investigate