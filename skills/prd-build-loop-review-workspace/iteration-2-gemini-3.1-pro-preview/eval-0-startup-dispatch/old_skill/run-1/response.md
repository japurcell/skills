Source of truth: evals/files/startup-fixture/prd.json
Resolved progress_file: evals/files/startup-fixture/progress.txt
Story selection: story-auth-timeout (highest priority with passes: false)
First orchestrator actions:
- Invoke subagent-model-router.
- Read ## Codebase Patterns and latest entries from the existing progress_file.
- Read nearby AGENTS.md.
- Dispatch fresh implementer for story-auth-timeout.
What must happen before any story-specific repo discovery: Orchestrator must read only prd_file, progress_file, and nearby AGENTS.md needed to dispatch work. Orchestrator must not read story-specific repo files, tests, code, or behavior before dispatching the first implementer for the current code-affecting unit.
