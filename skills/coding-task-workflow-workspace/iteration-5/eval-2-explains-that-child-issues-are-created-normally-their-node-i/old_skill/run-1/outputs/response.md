# Evaluation: Phase 6 Plan Issue and Phase 7 Implementation Task Issue Creation

## Overview

The baseline workflow creates Phase 6 (Plan) and Phase 7 (Implementation Task) issues using a standardized two-step process: **create child issues normally, then attach them to the parent using GitHub's GraphQL sub-issue mutation**. This is the central pattern for all Phase 1–11 issues and is non-negotiable.

---

## Non-Negotiable Rule #3 (SKILL.md line 31)

> "Every child issue is created first, then linked to the appropriate parent issue by resolving parent/child node IDs and calling `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable."

This rule applies to all child issues, including Phase 6 plan issues and Phase 7 implementation task issues.

---

## Phase 6: Plan Issue Creation

### When Phase 6 Runs

Phase 6 begins after Gate C (Clarification) is satisfied and creates **one child issue** per work item that holds the approved implementation plan.

**Workflow specification (references/workflow.md lines 185–192)**:

Step 3: "Create a GitHub child issue labelled `agent:phase` and `phase:plan`. Its body uses `templates/plan.md` and includes goal / non-goals, approach and rationale, alternatives, file-by-file implementation map, and verification guidance."

### Step 1: Create the Phase 6 Issue Normally

The workflow uses `gh issue create` with standard flags:

```bash
gh issue create \
  --title "Plan — 2026-04-23-add-rate-limit-logs" \
  --body-file <(cat <<'EOF'
## Summary

<One sentence describing what this phase produced.>

## Inputs

- Parent: #N
- Depends on: #<prior phase or artifact issues>

## Deliverable

[Plan artifact from templates/plan.md, including goal/non-goals, approach, alternatives, file-by-file map, verification guidance]

## Exit Criteria

- The Phase 6 plan issue is closed.
- The plan issue contains an explicit approval comment from the human.

## Machine Data

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
kind: phase
phase: plan
depends_on: [#N-5]
status: open
\`\`\`
EOF
) \
  --label agent:phase,phase:plan
```

**Expected output**: GitHub returns the new issue number, e.g., `#42`.

### Step 2: Resolve Both Node IDs

The workflow fetches the GitHub global node IDs (not the issue numbers) for both the parent and the Phase 6 issue:

```bash
# Resolve parent issue node ID
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)

# Resolve Phase 6 plan issue node ID
PLAN_NODE_ID=$(gh issue view 42 --json id --jq .id)

echo "Parent node: $PARENT_NODE_ID"
echo "Plan node: $PLAN_NODE_ID"
```

**Expected output** (example):
```
Parent node: I_kwDODXXXXX
Plan node: I_kwDODXXXXY
```

### Step 3: Attach with GraphQL addSubIssue Mutation

The workflow attaches the Phase 6 issue to the parent using the GitHub GraphQL `addSubIssue` mutation:

```bash
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$PLAN_NODE_ID"
```

**Expected output** (success):
```json
{
  "data": {
    "addSubIssue": {
      "issue": {
        "number": 42
      }
    }
  }
}
```

**Failure handling** (issue-hierarchy.md line 327–333):

> If GitHub issues are available but the sub-issue mutation is disabled for the repository:
> 1. Create the child issue normally.
> 2. Add `Parent: #N` in the child issue body as an explicit fallback marker.
> 3. Record the failed mutation attempt in the child issue body or a comment.
> 4. Do **not** fall back to local per-work-item markdown artifacts.

---

## Phase 7: Implementation Task Issues

### When Phase 7 Runs

Phase 7 begins after Gate D (Plan approved) and creates **multiple child issues** — one per vertical TDD slice. Each implementation task issue is a child of the Phase 7 task-graph issue.

**Workflow specification (references/workflow.md lines 208–215)**:

Steps 4–5:
- "Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`. Put the task graph in a fenced `yaml` block..."
- "Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue. Label each `agent:task`, `phase:implement`, plus `parallel` or `sequential` as appropriate. Initialize each task issue with `stage: red`..."

### Phase 7a: Create the Task-Graph Phase Issue

First, the workflow creates the **Phase 7 task-graph issue itself** (the parent of the implementation task issues):

```bash
gh issue create \
  --title "Task Graph — 2026-04-23-add-rate-limit-logs" \
  --body-file <(cat <<'EOF'
## Summary

<One sentence describing the decomposition of the plan into vertical slices.>

## Inputs

- Parent: #N (main parent)
- Depends on: #N-6 (plan issue)

## Deliverable

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
phase: task-graph
status: complete
updated_at: "ISO8601_TIMESTAMP"

tasks:
  - id: t1
    name: "Add rate-limit info field to LogEntry"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/logging/log-entry.test.ts
      - src/logging/log-entry.ts

  - id: t2
    name: "Update RequestLogger to capture rate-limit headers"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/logging/request-logger.test.ts
      - src/logging/request-logger.ts

  - id: t3
    name: "Add rate-limit fields to JSON encoder"
    stage: red
    depends_on: [t1]
    parallelizable: true
    files:
      - src/logging/json-encoder.test.ts
      - src/logging/json-encoder.ts
\`\`\`

## Exit Criteria

- The Phase 7 task-graph issue is closed.
- At least one implementation task issue has \`stage: red\`.
- Every implementation task issue records an explicit dependency list.

## Machine Data

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
kind: phase
phase: task-graph
depends_on: [#N-6]
status: open
\`\`\`
EOF
) \
  --label agent:phase,phase:task-graph
```

**Expected output**: GitHub returns the task-graph issue number, e.g., `#43`.

### Phase 7b: Create Implementation Task Issues

For each task in the task graph YAML, the workflow creates one implementation task issue:

```bash
# Task 1
gh issue create \
  --title "Task t1 — Add rate-limit info field to LogEntry" \
  --body-file <(cat <<'EOF'
## Summary

Add a \`rateLimitInfo\` field to the LogEntry struct to capture rate-limit metadata.

## Task Details

- **Current stage**: red
- **Task ID**: t1
- **Depends on tasks**: (none)

## Files

- src/logging/log-entry.test.ts
- src/logging/log-entry.ts

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
kind: task
phase: implement
task_id: t1
stage: red
parallelizable: false
depends_on: []
files:
  - src/logging/log-entry.test.ts
  - src/logging/log-entry.ts
status: open
\`\`\`
EOF
) \
  --label agent:task,phase:implement,sequential
```

**Expected output**: GitHub returns task issue number, e.g., `#44`.

Repeat for each task (t2, t3, etc.):

```bash
# Task 2 (depends on t1)
gh issue create \
  --title "Task t2 — Update RequestLogger to capture rate-limit headers" \
  --body-file <(cat <<'EOF'
## Summary

Modify RequestLogger to extract rate-limit response headers and populate the LogEntry rateLimitInfo field.

## Task Details

- **Current stage**: red
- **Task ID**: t2
- **Depends on tasks**: t1

## Files

- src/logging/request-logger.test.ts
- src/logging/request-logger.ts

## Progress Log

<!-- Implementation log added as comments -->

## Machine Data

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
kind: task
phase: implement
task_id: t2
stage: red
parallelizable: false
depends_on: [t1]
files:
  - src/logging/request-logger.test.ts
  - src/logging/request-logger.ts
status: open
\`\`\`
EOF
) \
  --label agent:task,phase:implement,sequential
```

Task 3 (depends on t1, parallelizable):

```bash
# Task 3 (depends on t1, parallelizable)
gh issue create \
  --title "Task t3 — Add rate-limit fields to JSON encoder" \
  --body-file <(cat <<'EOF'
## Summary

Extend the JSON encoder to serialize rate-limit fields from LogEntry.

## Task Details

- **Current stage**: red
- **Task ID**: t3
- **Depends on tasks**: t1

## Files

- src/logging/json-encoder.test.ts
- src/logging/json-encoder.ts

## Progress Log

<!-- Implementation log added as comments -->

## Machine Data

\`\`\`yaml
work_id: 2026-04-23-add-rate-limit-logs
kind: task
phase: implement
task_id: t3
stage: red
parallelizable: true
depends_on: [t1]
files:
  - src/logging/json-encoder.test.ts
  - src/logging/json-encoder.ts
status: open
\`\`\`
EOF
) \
  --label agent:task,phase:implement,parallel
```

### Phase 7c: Attach Task Issues to Task-Graph Issue

After creating all implementation task issues, attach each to the task-graph issue using the same GraphQL mutation:

```bash
# Get task-graph issue node ID (created in Phase 7a, e.g., #43)
TASKGRAPH_NODE_ID=$(gh issue view 43 --json id --jq .id)

# Attach task 1
TASK1_NODE_ID=$(gh issue view 44 --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASKGRAPH_NODE_ID" \
  -f subIssueId="$TASK1_NODE_ID"

# Attach task 2
TASK2_NODE_ID=$(gh issue view 45 --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASKGRAPH_NODE_ID" \
  -f subIssueId="$TASK2_NODE_ID"

# Attach task 3
TASK3_NODE_ID=$(gh issue view 46 --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASKGRAPH_NODE_ID" \
  -f subIssueId="$TASK3_NODE_ID"
```

### Phase 7d: Attach Task-Graph Issue to Parent

Finally, attach the Phase 7 task-graph issue to the main parent issue:

```bash
# Get parent issue node ID (from Phase 1)
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)

# Get task-graph node ID (from Phase 7a, e.g., #43)
TASKGRAPH_NODE_ID=$(gh issue view 43 --json id --jq .id)

# Attach task-graph to parent
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$TASKGRAPH_NODE_ID"
```

---

## Complete Attachment Hierarchy

After Phase 6 and Phase 7 complete, the GitHub issue hierarchy looks like this:

```
Parent issue: #N [agent:parent]
├── Phase 1 issue: #N+1 [phase:intake]
├── Phase 2 issue: #N+2 [phase:worktree]
├── Phase 3 issue: #N+3 [phase:exploration]
│   ├── Artifact: #N+3a [artifact] files.csv
│   └── Artifact: #N+3b [artifact] open-questions
├── Phase 4 issue: #N+4 [phase:research]
│   └── Artifact: #N+4a [artifact] sources.md
├── Phase 5 issue: #N+5 [phase:clarification]
├── Phase 6 issue: #N+6 [phase:plan]  ← Created per workflow.md lines 185–192
└── Phase 7 issue: #N+7 [phase:task-graph]  ← Created per workflow.md lines 213–215
    ├── Task 1: #N+8 [agent:task, phase:implement, sequential]  ← Created per workflow.md line 214
    ├── Task 2: #N+9 [agent:task, phase:implement, sequential]
    └── Task 3: #N+10 [agent:task, phase:implement, parallel]
```

All attachments use the GraphQL `addSubIssue` mutation with resolved node IDs.

---

## Key Design Decisions

### 1. No Local Markdown Files

The workflow explicitly forbids creating local markdown files for Phase 6–11 artifacts. Rule #2 (SKILL.md line 30):

> "Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts."

### 2. Issue Creation Always Precedes Linking

The workflow enforces a two-step pattern: create first, link second. This ensures:
- The issue exists and has a valid number before fetching its node ID.
- The mutation can be retried independently if it fails.
- Node IDs are resolved after both issues exist.

### 3. GraphQL Mutation Is the Requirement

The workflow specifies the exact GraphQL mutation signature and expects it to succeed. Issue-hierarchy.md line 50–61 provides the template.

If the mutation fails due to repository settings, the fallback is a plain `Parent: #N` body reference (line 62–63), **not** a local artifact file.

### 4. Label Application

Labels are applied at issue creation time. The workflow expects:

| Phase | Role Label | Phase Label |
|-------|-----------|------------|
| Phase 6 | `agent:phase` | `phase:plan` |
| Phase 7 (task-graph) | `agent:phase` | `phase:task-graph` |
| Phase 7 (task issue) | `agent:task` | `phase:implement` |
| Task concurrency | – | `parallel` or `sequential` |

---

## Summary

The baseline workflow creates Phase 6 and Phase 7 issues through:

1. **Create**: Use `gh issue create` with title, body (from templates), and labels.
2. **Resolve node IDs**: Fetch both parent and child issue node IDs with `gh issue view --json id`.
3. **Attach**: Call the GitHub GraphQL `addSubIssue` mutation with resolved node IDs.
4. **Repeat**: For each implementation task in Phase 7, repeat steps 1–3.

All state persists in GitHub. No local per-work-item files are created. The hierarchy is machine-readable via issue labels and the `## Machine Data` YAML blocks in each issue body.
