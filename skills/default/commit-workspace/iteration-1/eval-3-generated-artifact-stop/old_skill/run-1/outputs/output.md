# Commit Skill Dry-Run: generated-artifact-stop

## Scenario
User request: "Commit what I already staged."

Staged files:
- `src/audit/session_log.py` (source code)
- `playwright-report/index.html` (generated artifact)
- `test-results/session-flow/video.mp4` (generated artifact)

Current branch: `feat/session-audit`

## Reasoning

### Guardrail Triggered: Generated Artifacts

The SKILL.md guardrails explicitly state:
> "never ... commit ... tool-generated artifacts, local state files, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks for them to be versioned"

and

> "if staged changes include ignored-looking or generated artifacts, stop and ask before committing"

### Analysis
The staged set contains:
1. **Source code** (`src/audit/session_log.py`) — appropriate to commit
2. **Generated browser artifacts** (`playwright-report/index.html`, `test-results/session-flow/video.mp4`) — typically not versioned

The user's request "Commit what I already staged" is ambiguous:
- It could mean: commit everything literally staged
- OR it could mean: I staged what I want to commit (assuming they didn't intend to stage artifacts)

Given the change summary states "Adds session audit logging, but the staged set also includes generated browser artifacts," the skill should **stop and ask for clarification** rather than blindly committing the artifacts.

### Decision
- **Status:** stop
- **Stop Reason:** generated_artifacts_staged
- **Next Action:** Ask user to clarify whether to commit only source code or include all staged files
- **Branch Action:** keep (no branch creation needed, already on feature branch)
- **Selected Paths:** empty (no files selected due to ambiguity)

## Output
- `result.json`: Contains detailed decision data with all required keys
- `next_action`: Provides clear guidance on how to proceed
