**Before the implementer runs:** Because this task is already the next plan item and you already have acceptance criteria, validation commands, and likely file hints, the manager should invoke `addy-context-engineering` and `subagent-model-selection`, confirm there’s no ambiguity or plan conflict, and then **dispatch immediately**. The manager should **not** pre-read the likely files, explore the repo, draft the pagination approach, or sketch patches first.

**What belongs in the handoff:** Keep it lean and limited to already-known context:
1. The task text: add pagination to `GET /api/issues`
2. The acceptance/success criteria
3. Known constraints and relevant repo rules
4. Known validation commands
5. Only the file hints already named in the plan

**What must stay with the implementer:** Repo discovery, reading the hinted files and related tests, pattern lookup, first-pass design, loading the minimum needed context, writing the failing test first, making the code change, choosing the narrowest applicable validations from the known commands, running verification, and debugging failures. Verification ownership stays with the implementer, and ordinary repo exploration is explicitly **not** a valid `NEEDS_CONTEXT`.
