# Evaluation: Phase 3 Exploration Outputs Storage

## Overview

Phase 3 of coding-task-workflow produces **three distinct outputs**, each stored as a separate GitHub issue with explicit parent/child relationships. This evaluation explains where each output lives and how they are linked.

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), Phase 3 produces artifacts that must be stored in GitHub as the durable record, not in local files.

**Key reference**: `references/issue-hierarchy.md` lines 14–17 show the hierarchy structure for Phase 3:

```text
├── Exploration issue:     [phase:exploration]    Exploration summary
│   ├── Artifact issue:    files.csv              files.csv content
│   └── Artifact issue:    open-questions         open/resolved research questions
```

---

## The Three Exploration Outputs

### 1. Exploration Summary (Phase Issue)

**Where it lives**: GitHub issue with labels `agent:phase` and `phase:exploration`

**Parent**: Attached as a sub-issue to the top-level parent issue (e.g., `#42`)

**Body format**: Uses `references/templates/exploration-summary.md` as specified in Phase 3 step 5:
- One-paragraph summary of exploration outcome
- Track selected (light | standard | deep) with rationale
- Key findings (3–5 important insights)
- Anti-patterns to avoid
- Relevant files snapshot (high-level; full list in `files.csv` subissue)
- Open questions snapshot (high-level; full ledger in `open-questions` subissue)
- `## Machine Data` YAML block with `work_id`, `kind: phase`, `phase: exploration`, `track`, `agents_launched`, and `depends_on`

**Status**: **Closed** when the summary is complete (Phase 3 step 9)

**Purpose**: The primary durable record of codebase exploration findings. Other agents resume from GitHub by reading this issue.

**Example issue title**: `Exploration — 2026-04-27-add-retry-mechanism`

---

### 2. Files CSV Artifact Subissue

**Where it lives**: GitHub issue with labels `agent:artifact` (and optionally `phase:exploration` for consistency)

**Parent**: Attached as a sub-issue to the Exploration phase issue (not the top-level parent)

**Body format**: Uses `references/artifact-schema.md` artifact subissue template (lines 195–220):
- `## Summary`: Describe the secondary durable artifact (file ledger)
- `## Parent`: Reference to the Exploration phase issue
- `## Artifact`: Fenced `csv` block containing the file list
  - Each row: `file_path`, `reason_for_inclusion`, `touched_by_agent`, `line_count` (or similar fields)
  - Stored as a direct CSV block so other agents can parse it programmatically
- `## Machine Data` YAML block with `artifact_name: files.csv`, `format: csv`, `status: closed`

**Status**: **Closed** as soon as the file ledger is complete (Phase 3 step 7)

**Purpose**: Provides a resumable, machine-readable list of key files for later phases (research, planning, implementation). Other agents can read this CSV from GitHub alone without needing to re-explore.

**Example issue title**: `Artifact — files.csv — 2026-04-27-add-retry-mechanism`

**Example CSV content**:
```csv
file_path,reason,touched_by_agent,line_count
src/http/client.ts,existing retry patterns,agent-a,850
src/http/retry.ts,current retry implementation,agent-a,320
tests/http/retry.test.ts,test structure and patterns,agent-c,500
src/utils/backoff.ts,exponential backoff implementation,agent-b,200
docs/http-client.md,API documentation,agent-b,450
```

---

### 3. Open Questions Artifact Subissue

**Where it lives**: GitHub issue with labels `agent:artifact` (and optionally `phase:exploration` for consistency)

**Parent**: Attached as a sub-issue to the Exploration phase issue (not the top-level parent)

**Body format**: Uses `references/artifact-schema.md` artifact subissue template with a ledger format:
- `## Summary`: Describe the question ledger (e.g., "Unresolved questions from Phase 3 exploration")
- `## Parent`: Reference to the Exploration phase issue
- `## Artifact`: Markdown table or checklist with columns:
  - `id`: Unique question identifier (e.g., `EXP-001`, `EXP-002`)
  - `question`: The open question text
  - `status`: `open | resolved | needs-human` (Phase 3 only uses `open` or `needs-human`)
  - `resolved_by`: (empty during Phase 3; filled by Phase 4 research or Phase 5 clarification)
  - `answer`: (empty during Phase 3; filled later)
- `## Machine Data` YAML block with `artifact_name: open-questions`, `format: markdown`, `status: open`

**Status**: **Kept open** across Phases 3, 4, and 5 until every question is resolved or explicitly marked `needs-human` (Phase 3 step 9, Phase 5 step 8)

**Purpose**: Durable question ledger that Phase 4 (Research) and Phase 5 (Clarification) update in place. This is the single source of truth for unresolved questions. Artifact stays open until all questions are finalized.

**Example issue title**: `Artifact — open-questions — 2026-04-27-add-retry-mechanism`

**Example content**:
```markdown
## Artifact

| id  | question | status | resolved_by | answer |
|-----|----------|--------|-------------|--------|
| EXP-001 | What's the current retry logic in the HTTP client? | open | — | — |
| EXP-002 | Are there existing backoff utilities in the codebase? | open | — | — |
| EXP-003 | How should retries interact with circuit breakers? | needs-human | — | — |
| EXP-004 | What status codes should trigger retries? | open | — | — |
```

---

## GitHub Issue Hierarchy Diagram

For a work item with parent issue `#42`:

```
Parent issue #42  [agent:parent]
│
├─ #43  [agent:phase] [phase:intake]          — Intake
│
├─ #44  [agent:phase] [phase:worktree]        — Worktree setup
│
└─ #45  [agent:phase] [phase:exploration]     ← Exploration summary
   │
   ├─ #46  [agent:artifact] [phase:exploration]  ← files.csv
   │        Title: "Artifact — files.csv — ..."
   │        Body: fenced CSV block
   │        Status: CLOSED when complete
   │
   └─ #47  [agent:artifact] [phase:exploration]  ← open-questions
            Title: "Artifact — open-questions — ..."
            Body: markdown table with id, question, status, etc.
            Status: OPEN (kept open through Phases 3–5)
```

### Sub-issue Linking Process (Non-negotiable)

From `references/issue-hierarchy.md` lines 34–65:

1. **Create the Exploration phase issue** with `gh issue create`
2. **Attach it to the parent issue** using the GraphQL `addSubIssue` mutation
3. **Create artifact subissues** (`files.csv` and `open-questions`) normally
4. **Attach each artifact subissue to the Exploration phase issue** using the GraphQL mutation

Example linking command:
```bash
EXPLORATION_NODE_ID=$(gh issue view 45 --json id --jq .id)
FILES_CSV_NODE_ID=$(gh issue view 46 --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$EXPLORATION_NODE_ID" \
  -f subIssueId="$FILES_CSV_NODE_ID"
```

---

## When to Close Which Issues

From Phase 3 workflow specification (`references/workflow.md` lines 103–117) and issue lifecycle (`references/issue-hierarchy.md` lines 305–306):

| Artifact | Close When | Stays Open Until |
|----------|-----------|-----------------|
| **Exploration summary** | The summary is complete | Never (closed after Phase 3) |
| **files.csv** | File ledger is complete | Never (closed after Phase 3) |
| **open-questions** | (Stays open) | Every question is finalized (Phase 5) |

---

## Why GitHub Issues, Not Local Files?

From `SKILL.md` non-negotiable rule #2:
> Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.

**Benefits of GitHub storage**:
1. **Resumability**: Fresh session can load the entire Phase 3 state from GitHub alone
2. **Auditability**: All exploration findings are visible in GitHub history
3. **Collaboration**: Multiple agents can read and update the same artifacts
4. **Durability**: Parent issue and all child issues remain after the workflow session ends
5. **Traceability**: Each issue has a permanent URL for linking from other phases

---

## Phase 4 and Beyond

Phase 4 (Research) consumes the `open-questions` artifact subissue and updates it with answers. Phase 5 (Clarification) does the same. The artifact subissue remains open across these phases, acting as a durable ledger.

**Example Phase 4 update to the open-questions issue**:
- Agent marks `EXP-001` as `resolved` and fills in the answer
- Agent marks `EXP-003` as `needs-human` (escalation)
- Keeps all entries visible for Phase 5 to process

---

## Summary: The Three Locations

| Output | GitHub Issue Type | Parent | Labels | Status | Purpose |
|--------|---|---|---|---|---|
| **Exploration summary** | Phase issue | Parent issue | `agent:phase`, `phase:exploration` | Closed | Primary exploration findings |
| **files.csv** | Artifact subissue | Exploration issue | `agent:artifact` | Closed | Machine-readable file ledger |
| **open-questions** | Artifact subissue | Exploration issue | `agent:artifact` | Open (until Phase 5) | Durable question ledger for research |

All three issues are created, linked, and persisted in GitHub. None are written to local `.coding-workflow/work/<slug>/` directories.
