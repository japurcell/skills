# Evaluation: GitHub-Native Recording of Plan Approval, Task Graph, and Implementation Log

## Overview

The baseline `coding-task-workflow` skill records Phase 6 approval, Phase 7 task graph, and Phase 8 implementation logs using **GitHub issues and comments instead of local markdown files**. This is the central design change from the old workflow.

Old files that are now **completely gone**:
- `05-plan.md` (approval history)
- `06-task-graph.yaml` (task decomposition)
- `07-implementation-log.md` (RED/GREEN/REFACTOR progress)

New GitHub-native mechanism:
- Phase 6 approval → **explicit comment on the plan issue body**
- Phase 7 task graph → **YAML in the task-graph issue body** (NOT a separate artifact subissue)
- Phase 8 implementation log → **comments on individual task issues** (one comment per RED/GREEN/REFACTOR stage)

---

## Phase 6: Plan Approval

### What Gets Recorded

Phase 6 step 5 (workflow.md line 191):

> "Record approval as an explicit comment on the plan issue."

The plan issue itself contains the implementation plan in its body (see templates/plan.md). When the human approves, that approval is recorded as a **comment on the same issue**, not as a separate file or artifact.

### Phase 6 Workflow Steps

**Phase 6 steps (workflow.md lines 185–192)**:

1. Create a GitHub child issue labelled `agent:phase` and `phase:plan`. Its body uses templates/plan.md.
2. Present a concise plan summary to the human. Gate on explicit approval.
3. **Record approval as an explicit comment on the plan issue.**
4. Close the plan issue immediately after approval.

### Approval Comment Format

The workflow provides a template for the approval comment (issue-hierarchy.md lines 258–273):

```markdown
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```
```

### GitHub Command

After the human approves the plan issue body, the workflow records the approval comment:

```bash
gh issue comment <plan-issue-number> --body <(cat <<'EOF'
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: "2026-04-27T14:32:00Z"
```
EOF
)
```

### Gate D Condition

**Stop-gates.md lines 67–70**:

> **Condition**:
> - The Phase 6 plan issue is closed.
> - The plan issue contains an explicit approval comment from the human.

The gate is verified by checking:
1. Plan issue is in closed state
2. Plan issue has at least one comment (the approval comment)
3. That comment contains the `kind: approval` machine data

### Approval Persistence

The approval comment is permanent and immutable:
- It persists on the plan issue forever
- It is the authoritative record that Gate D was satisfied
- When resuming via `RESUME=<slug>`, Phase 8 loads this issue and checks for the approval comment

---

## Phase 7: Task Graph

### What Gets Recorded

Phase 7 step 4 (workflow.md line 213):

> "Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`. Put the task graph in a fenced `yaml` block using [templates/task-graph.yaml](templates/task-graph.yaml) as the content shape."

The task graph YAML lives **in the task-graph issue body**, not in a separate artifact subissue or file.

**Important constraint (issue-hierarchy.md line 193)**:

> "For Phase 7 specifically, keep the task graph YAML in the phase issue body. Do not create a separate `task-graph.yaml` artifact subissue."

### Task Graph Issue Body

The task-graph issue body contains:

1. Summary section
2. Inputs section
3. **Deliverable section** with the fenced `yaml` block
4. Exit Criteria section
5. Machine Data section

### Task Graph YAML Content

**Templates/task-graph.yaml** defines the exact structure (lines 1–39):

```yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "ISO8601_TIMESTAMP"

tasks:
  - id: t1
    name: "Implement basic exponential backoff"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts

  - id: t2
    name: "Add jitter to backoff calculation"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts

  - id: t3
    name: "Add max-retry enforcement"
    stage: red
    depends_on: [t1]
    parallelizable: true
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts
```

### Gate E Condition

**Stop-gates.md lines 91–96**:

> **Condition**:
> - The Phase 7 task-graph issue is closed.
> - At least one implementation task issue has `stage: red`.
> - Every implementation task issue has an explicit dependency list.
> - No circular dependencies exist in the task graph YAML.

The gate is verified by:
1. Checking that the task-graph issue is closed
2. Parsing the YAML from the task-graph issue body
3. Verifying that each task in the YAML has a corresponding implementation task issue
4. Checking that each implementation task issue has `stage: red` initially
5. Verifying that all dependency lists are present and acyclic

### Task Graph Lifecycle

Once Phase 7 closes the task-graph issue:
- The YAML is locked and immutable
- Each task in the YAML becomes an open implementation task issue (child of the task-graph issue)
- The Phase 8 session loads the task-graph issue, parses the YAML, and uses it to determine execution order
- Implementation tasks inherit their `stage`, `depends_on`, and `parallelizable` fields from the task graph

---

## Phase 8: Implementation Log

### What Gets Recorded

Phase 8 step 3 (workflow.md lines 237–239):

> **RED**: write a failing test that captures the behaviour. Run it and confirm it fails for the expected reason. **Record the result as a comment on the task issue while the issue remains at `stage: red`.**
> 
> **GREEN**: update the same task issue to `stage: green`, write the minimal code to make the test pass, run it, and **record the result as a comment on that issue.**
> 
> **REFACTOR**: update the same task issue to `stage: refactor`, clean up if needed, rerun the relevant tests, and **record the outcome as another comment on that issue.**

The implementation log is **a series of comments on the same task issue**, not a separate file. This replaces `07-implementation-log.md`.

**Key statement (workflow.md line 241)**:

> "The task issue comments replace `07-implementation-log.md`, and the issue body remains the durable record of the slice's current/final stage."

### Implementation Log Comment Format

The workflow provides a template for implementation progress comments (issue-hierarchy.md lines 275–295):

```markdown
## Slice Update — <task_id> / <stage>

- **status**: complete | blocked
- **files_changed**: <paths>
- **test_result**: pass | fail
- **notes**: <short explanation>

## Machine Data

```yaml
work_id: <slug>
kind: implementation-log
task_id: <id>
stage: red | green | refactor
status: complete | blocked
updated_at: <ISO8601>
```
```

### RED Stage Example

When Phase 8 begins work on task `t1`, it writes a failing test, runs it, and records the RED result:

```bash
gh issue comment 44 --body <(cat <<'EOF'
## Slice Update — t1 / red

- **status**: complete
- **files_changed**: src/http/retry.test.ts
- **test_result**: fail (expected)
- **notes**: Test verifies that retry is attempted exactly once for a 500 response. Fails because retry mechanism does not exist yet.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: red
status: complete
updated_at: "2026-04-27T15:00:00Z"
\`\`\`
EOF
)
```

At the same time, the issue's `stage` field is updated (via `gh issue edit` or the workflow keeps it in sync):

```bash
gh issue edit 44 --body-file <(cat <<'EOF'
## Summary

Implement basic exponential backoff for HTTP client retries.

## Task Details

- **Current stage**: red
- **Task ID**: t1
- **Depends on tasks**: (none)

## Files

- src/http/retry.ts
- src/http/retry.test.ts

## Progress Log

<!-- RED / GREEN / REFACTOR comments added below -->

[Previous comments will appear in the timeline]

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t1
stage: red
parallelizable: false
depends_on: []
files:
  - src/http/retry.ts
  - src/http/retry.test.ts
status: open
\`\`\`
EOF
)
```

### GREEN Stage Example

After writing implementation code, Phase 8 records the GREEN result:

```bash
gh issue comment 44 --body <(cat <<'EOF'
## Slice Update — t1 / green

- **status**: complete
- **files_changed**: src/http/retry.ts, src/http/retry.test.ts
- **test_result**: pass
- **notes**: Implemented basic exponential backoff. Test passes. Retry succeeds after 500 response.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: green
status: complete
updated_at: "2026-04-27T15:15:00Z"
\`\`\`
EOF
)
```

And update the issue stage to `green`:

```bash
gh issue edit 44 --body-file <(cat <<'EOF'
## Summary

Implement basic exponential backoff for HTTP client retries.

## Task Details

- **Current stage**: green
- **Task ID**: t1
- **Depends on tasks**: (none)

[Rest of issue body unchanged]
EOF
)
```

### REFACTOR Stage Example

After cleanup, Phase 8 records the REFACTOR result:

```bash
gh issue comment 44 --body <(cat <<'EOF'
## Slice Update — t1 / refactor

- **status**: complete
- **files_changed**: src/http/retry.ts
- **test_result**: pass
- **notes**: Extracted retry delay calculation to separate function for clarity. All tests still pass.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: refactor
status: complete
updated_at: "2026-04-27T15:25:00Z"
\`\`\`
EOF
)
```

Update the issue stage to `refactor` and close it:

```bash
gh issue edit 44 --body-file <(cat <<'EOF'
## Summary

Implement basic exponential backoff for HTTP client retries.

## Task Details

- **Current stage**: refactor
- **Task ID**: t1
- **Depends on tasks**: (none)

[Rest of issue body unchanged]
EOF
)

gh issue close 44
```

---

## Complete Artifact Replacement Summary

### Old Local Files (Forbidden Now)

| Old File | Purpose | Size |
|----------|---------|------|
| `05-plan.md` | Plan text + approval history | Varied |
| `06-task-graph.yaml` | Task decomposition (YAML) | Varied |
| `07-implementation-log.md` | RED/GREEN/REFACTOR log (markdown) | Varies per task |

### New GitHub-Native Equivalents

| Old File | New Location | Mechanism |
|----------|--------------|-----------|
| `05-plan.md` | Phase 6 plan issue (body) | Plan artifact in issue body; approval is a comment |
| `06-task-graph.yaml` | Phase 7 task-graph issue (body, YAML fenced block) | YAML in issue body, NOT a separate artifact subissue |
| `07-implementation-log.md` | Implementation task issue (comments) | One comment per RED/GREEN/REFACTOR stage on the same task issue |

### Query Pattern for Resuming

Phase 8 loads the GitHub state when resuming:

```bash
# Resume with RESUME=<slug>
# Phase 8 loads:
1. Parent issue (#N) → gets work_id, classification
2. Phase 6 plan issue (#N+6) → reads plan body, verifies approval comment exists (Gate D check)
3. Phase 7 task-graph issue (#N+7) → parses YAML, extracts task order and dependencies
4. Implementation task issues (#N+8..#N+X) → loads current stage, loads all previous comments (RED/GREEN/REFACTOR history)
```

The implementation task issue comments form a durable timeline of all work done on that task:

```
Issue timeline (chronological):
- Comment 1: RED result (first attempt, test fails)
- Comment 2: GREEN result (implementation code works)
- Comment 3: REFACTOR result (cleanup, tests still pass)
- [Issue closed]
```

---

## Key Differences from Old Workflow

| Aspect | Old Workflow | New Workflow |
|--------|--------------|-------------|
| Plan approval | Stored in local `05-plan.md` or issue body | Explicit comment on plan issue body |
| Approval verification | Check local file or read issue | Load plan issue, check for approval comment |
| Task graph storage | Local file `06-task-graph.yaml` | YAML in task-graph issue body (fenced block) |
| Task graph parsing | Read from `.coding-workflow/work/<slug>/` | Load from GitHub task-graph issue body |
| Implementation log | Local markdown file `07-implementation-log.md` | Comments on individual task issues |
| Progress tracking | File-based ledger | GitHub issue comment timeline |
| Session resumption | Might load local files (risky) | Always loads from GitHub issues (canonical) |

---

## Rule #2 Enforcement

**SKILL.md line 30**:

> "Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts."

Under this rule:
- ❌ Creating `.coding-workflow/work/<slug>/05-plan.md`
- ❌ Creating `.coding-workflow/work/<slug>/06-task-graph.yaml`
- ❌ Creating `.coding-workflow/work/<slug>/07-implementation-log.md`
- ✅ Recording approval as a comment on the plan issue
- ✅ Storing task graph YAML in the task-graph issue body
- ✅ Recording implementation progress as comments on task issues

---

## Machine Data for Auditability

Every artifact includes a `## Machine Data` YAML block with metadata:

**Approval comment**:
```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```

**Task graph** (in issue body):
```yaml
work_id: <slug>
phase: task-graph
status: complete
updated_at: <ISO8601>
```

**Implementation log comment** (per stage):
```yaml
work_id: <slug>
kind: implementation-log
task_id: <id>
stage: red | green | refactor
status: complete | blocked
updated_at: <ISO8601>
```

This machine data allows downstream tooling to parse and audit workflow state without relying on GitHub UI parsing.

---

## Summary

**Phase 6 Approval**: Explicit comment on the plan issue, containing `kind: approval` machine data.

**Phase 7 Task Graph**: YAML in the task-graph issue body (fenced block), NOT a separate artifact subissue. Contains all task IDs, names, dependencies, parallelizability, and files.

**Phase 8 Implementation Log**: Three comments per task issue (RED, GREEN, REFACTOR), each containing task ID, stage, status, files changed, test result, and `kind: implementation-log` machine data.

All state is GitHub-native. No local per-work-item files are created. Rule #2 is enforced everywhere.
