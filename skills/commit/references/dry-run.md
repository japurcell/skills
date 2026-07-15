# Dry run output

Use only when the user asks for a dry run.

```text
status: commit|stop
branch_action: create|keep
branch: <branch>
scope:
- <file>
subject: <commit subject>
push_requested: true|false
should_push: true|false
pr_requested: true|false
blocker: <reason, if stopped>
next_action: <what user should do next, if stopped>
```

Definitions:

- `push_requested`: user explicitly asked to push.
- `should_push`: push is required now because the user asked or PR creation needs it.
