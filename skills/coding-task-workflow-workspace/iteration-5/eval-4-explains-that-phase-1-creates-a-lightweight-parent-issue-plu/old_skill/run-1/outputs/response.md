# Evaluation: Phase 1 GitHub Issue Creation (No Existing ISSUE)

## Overview

When using the baseline `coding-task-workflow` skill for a new feature request **without an existing GitHub issue**, Phase 1 (Intake) creates **exactly two GitHub issues**:

1. **A lightweight parent issue** — labeled `agent:parent` (the top-level work item)
2. **A structured intake child issue** — labeled `agent:phase` and `phase:intake` (the detailed artifact)

These are GitHub's durable canonical workflow records. **No local per-work-item markdown files are created.** Rule #2 forbids them: "Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts."

---

## Phase 1 Workflow (When ISSUE is Not Provided)

**Workflow specification** (references/workflow.md lines 42–63):

> **Objective**: capture the work item in GitHub before any code is touched.
> 
> **Inputs**: `WORK_ITEM` text or file path; optional `ISSUE` number.
>
> **Steps**:
> 1. If `ISSUE` is provided, fetch the GitHub issue...
> 2. If `WORK_ITEM` is a file path, read the file.
> 3. Classify the work item as `feature | bug | refactor | spec | chore`.
> 4. Assign a deterministic slug: `YYYY-MM-DD-<kebab-title>` (max 50 chars).
> 5. If `ISSUE` is provided, treat that issue as the lightweight parent issue... **If `ISSUE` is not provided, create a new parent issue labelled `agent:parent`**.
> 6. Create a separate GitHub child issue labelled `agent:phase` and `phase:intake`. Its body is the structured intake artifact based on [templates/intake.md](templates/intake.md).
> 7. Attach the intake issue to the parent issue with `addSubIssue`.
> 8. Close the intake issue once the body contains the accepted summary, classification, acceptance criteria, known constraints, references, and `## Machine Data`.
>
> **Outputs**: lightweight parent issue, closed intake child issue.

---

## Issue 1: Create the Parent Issue

When no `ISSUE` is provided, Phase 1 creates a new lightweight parent issue.

### Command Shape

```bash
gh issue create \
  --title "<work-item-title>" \
  --body-file <(cat <<'EOF'
## Summary

<One paragraph describing the work item, source, and expected outcome.>

## Current Phase

intake

## Acceptance Snapshot

<Short numbered list copied from the intake issue. Keep it compact; the intake issue holds the full artifact.>

## Sub-issues

<!-- Maintained as phases begin -->

- [ ] #N+1 Intake
- [ ] #N+2 Worktree setup
- [ ] #N+3 Codebase exploration
- [ ] #N+4 Online research
- [ ] #N+5 Clarification
- [ ] #N+6 Implementation plan
- [ ] #N+7 TDD task graph
- [ ] #N+8 Review
- [ ] #N+9 Verification
- [ ] #N+10 PR / landing

## Machine Data

\`\`\`yaml
work_id: <slug>
kind: parent
classification: feature | bug | refactor | spec | chore
status: open
current_phase: intake
source_issue: null
\`\`\`
EOF
) \
  --label agent:parent
```

### Expected Output

GitHub returns the parent issue number, e.g., `#42`.

### Body Structure Details

The parent issue body contains:

- **Summary**: One paragraph (work item description, source, expected outcome)
- **Current Phase**: Name the next phase (`intake` initially)
- **Acceptance Snapshot**: Short numbered list copied from the intake issue (compact; full artifact is in the intake issue)
- **Sub-issues**: Checklist of all 10 phases (template; updated as phases complete)
- **Machine Data**: YAML block with:
  - `work_id`: slug (deterministic, `YYYY-MM-DD-<kebab-title>`, max 50 chars)
  - `kind`: `parent` (fixed)
  - `classification`: `feature | bug | refactor | spec | chore` (inferred in Phase 1 step 3)
  - `status`: `open` (initially)
  - `current_phase`: `intake` (initially)
  - `source_issue`: `null` (no pre-existing issue)

---

## Issue 2: Create the Intake Child Issue

Separately, Phase 1 creates a structured intake artifact issue.

### Command Shape

```bash
gh issue create \
  --title "Intake — 2026-04-27-add-retry-mechanism" \
  --body-file <(cat <<'EOF'
## Summary

One paragraph describing the work item: what it is, why it matters, and what the expected outcome is.

## Classification

- **Type**: feature
- **Rationale**: One sentence explaining why this classification was chosen.

## Acceptance Criteria

1. **Criterion 1** — Description of what must be true for the criterion to pass.
2. **Criterion 2** — Description.
3. **Criterion 3** — Description.

## Known Constraints

- **Language / framework**: e.g., TypeScript 5.4, React 18
- **Scope**: e.g., only affects the HTTP client module
- **Deadline**: e.g., must ship before v2.0 release
- **Compatibility**: e.g., must not break existing public API

## References

- Parent issue: #42
- Source issue or spec: (link if applicable)
- Related issues: (if any)
- Prior art: (links to related PRs or issues)

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: intake
classification: feature
status: open
source_issue: null
\`\`\`
EOF
) \
  --label agent:phase,phase:intake
```

### Expected Output

GitHub returns the intake issue number, e.g., `#43`.

### Body Structure Details

The intake issue body contains:

- **Summary**: One paragraph (work item description, why it matters, expected outcome)
- **Classification**: Type and rationale
  - **Type**: `feature | bug | refactor | spec | chore` (inferred in Phase 1)
  - **Rationale**: One sentence explaining the classification choice
- **Acceptance Criteria**: Numbered list (each independently verifiable)
- **Known Constraints**: Language, framework, scope, deadline, compatibility, etc.
- **References**: Parent issue, source issue, related issues, prior art
- **Machine Data**: YAML block with:
  - `work_id`: slug (same as parent)
  - `kind`: `phase` (fixed)
  - `phase`: `intake` (fixed)
  - `classification`: matching the parent's classification
  - `status`: `open` (initially)
  - `source_issue`: `null` (no pre-existing issue)

---

## Step 3: Attach Intake to Parent

After creating both issues, Phase 1 attaches the intake child issue to the parent using the GitHub GraphQL `addSubIssue` mutation.

### Command Shape

```bash
# Resolve parent node ID
PARENT_NODE_ID=$(gh issue view 42 --json id --jq .id)

# Resolve intake node ID
INTAKE_NODE_ID=$(gh issue view 43 --json id --jq .id)

# Attach with GraphQL mutation
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$INTAKE_NODE_ID"
```

### Expected Output

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

---

## Step 4: Close the Intake Issue

Phase 1 step 8 closes the intake issue once its body is complete:

> Close the intake issue once the body contains the accepted summary, classification, acceptance criteria, known constraints, references, and `## Machine Data`.

### Command Shape

```bash
gh issue close 43
```

### Expected Output

```
✓ Closed issue #43
```

---

## Summary of Phase 1 Issues Created (No Pre-Existing ISSUE)

| Issue # | Label | Purpose | Status after Phase 1 |
|---------|-------|---------|----------------------|
| #N | `agent:parent` | Lightweight parent work item | **Open** (remains open through Phase 11) |
| #N+1 | `agent:phase`, `phase:intake` | Structured intake artifact | **Closed** |

### GitHub Hierarchy After Phase 1

```
Parent issue: #N [agent:parent] "Add retry mechanism to HTTP client"
└── Intake issue: #N+1 [phase:intake] "Intake — 2026-04-27-add-retry-mechanism" [CLOSED]
```

---

## Key Differences from Old Workflow

The old workflow (before the change to GitHub-native artifacts) would have created:
- A lightweight parent issue (same as now)
- An intake child issue (same as now)
- **Plus**: Local per-work-item markdown files at `.coding-workflow/work/<slug>/01-intake.md`

**The baseline workflow now forbids the local files.** Rule #2 (SKILL.md line 30):

> "Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts."

---

## Phase 1 Workflow Rule Answer

The workflow includes a direct answer for intake authority (SKILL.md lines 40–42):

> | User asks about | Answer |
> | Intake authority | `The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.` |

And for workflow record (SKILL.md line 44):

> | User asks about | Answer |
> | Workflow record | `Phase 0 keeps repo-local overrides, but Phases 1–11 persist durable state in GitHub issues and comments instead of local per-work-item markdown files.` |

---

## Issue Lifecycle After Phase 1

- **Parent issue (#N)**: Remains open until the PR is merged. The PR body will include `Fixes #N` to close it.
- **Intake issue (#N+1)**: Closed at the end of Phase 1. Its content (acceptance criteria, constraints) is referenced in the parent issue's "Acceptance Snapshot" section.
- **Phase 2–11 issues**: Created sequentially as each phase begins. All are attached to the parent issue (#N) using the same GraphQL mutation.

---

## Command Summary

Phase 1, when no `ISSUE` is provided, executes these commands in order:

1. `gh issue create --title ... --body-file ... --label agent:parent` → returns parent issue number
2. `gh issue create --title ... --body-file ... --label agent:phase,phase:intake` → returns intake issue number
3. `gh issue view <parent> --json id --jq .id` → returns parent node ID
4. `gh issue view <intake> --json id --jq .id` → returns intake node ID
5. `gh api graphql -f query='mutation(...)' -f parentId="..." -f subIssueId="..."` → attaches intake to parent
6. `gh issue close <intake>` → closes the intake issue

---

## No Local Files

To emphasize: Phase 1 does **not** create any of these:

- `.coding-workflow/work/<slug>/01-intake.md`
- `.coding-workflow/work/<slug>/intake-summary.txt`
- `intake.md` anywhere in the repo

All intake data is in the GitHub intake issue body and `## Machine Data` YAML block. The parent issue body holds the "Acceptance Snapshot" as a convenience reference.
