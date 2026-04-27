# Evaluation: Phase 1 GitHub Issue Creation (No Existing ISSUE)

## Summary

**Task**: For a new feature request with no existing `ISSUE`, explain exactly what GitHub issues Phase 1 should create now that local per-work-item markdown files are gone.

**Answer**: Phase 1 creates exactly **two GitHub issues** and no local files:

1. **Parent issue** (lightweight index) — labelled `agent:parent`
2. **Intake issue** (structured artifact) — labelled `agent:phase` and `phase:intake`

These are the **only** durable artifacts Phase 1 creates. All workflow state lives in GitHub going forward. Local per-work-item files under `.coding-workflow/work/<slug>/` are no longer used.

---

## What Has Changed

### Before (Legacy)
Phase 1 used to create:
- Parent issue in GitHub
- Intake issue in GitHub
- **Local file**: `.coding-workflow/work/<slug>/01-intake.md` — this is **gone**
- **Local file**: `.coding-workflow/work/<slug>/work.yaml` — this is **gone**

### Now (Current)
Phase 1 creates:
- Parent issue in GitHub ✅
- Intake issue in GitHub ✅
- **NO local per-work-item files** ✅

The key rule from `SKILL.md` Non-negotiable rule #2:

> Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.

And from `workflow.md` Priority rule #2:

> After Bootstrap, do **not** create local per-work-item artifacts under `.coding-workflow/work/<slug>/`. Persist durable state in GitHub parent issues, phase issues, artifact subissues, and issue comments.

---

## Phase 1 Workflow (No Existing ISSUE)

### Input
- `WORK_ITEM`: feature description text or file path (e.g., "Add rate limiting to the API")
- `ISSUE`: not provided (no existing issue number)

### Steps

#### Step 1: Parse and classify the work item

```
WORK_ITEM = "Add rate limiting to the API with per-user quotas. 
             Reject requests over 100 calls per minute with HTTP 429."
```

Classify as:
- `type: feature` (it's a new capability)

Assign deterministic slug:
```
work_id = 2026-04-27-add-rate-limiting
```

(Format: `YYYY-MM-DD-<kebab-title>`, max 50 chars)

#### Step 2: Create the parent issue

```bash
gh issue create \
  --title "2026-04-27-add-rate-limiting" \
  --body-file parent_issue_body.md \
  --label "agent:parent"
```

**Parent issue body** (follows template from `references/issue-hierarchy.md`):

```markdown
## Summary

Add rate limiting to the API with per-user quotas. Reject requests over 100 
calls per minute with HTTP 429. This improves service stability and prevents 
abuse.

## Current Phase

Phase 1: Intake — capturing work item.

## Acceptance Snapshot

1. Requests from the same user over 100/minute return HTTP 429
2. Rate limit headers (X-RateLimit-*) are included in all responses
3. Rate limit state is tracked per-user ID, not per-IP
4. Configuration is read from environment variables

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

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: parent
classification: feature
status: open
current_phase: intake
source_issue: null
```
```

**Result**: Returns parent issue number, e.g., `#100`.

#### Step 3: Create the intake issue

```bash
gh issue create \
  --title "Intake — 2026-04-27-add-rate-limiting" \
  --body-file intake_issue_body.md \
  --label "agent:phase" \
  --label "phase:intake"
```

**Intake issue body** (follows template from `references/templates/intake.md`):

```markdown
## Summary

Add rate limiting to the API with per-user quotas. Reject requests over 100 
calls per minute with HTTP 429. Expected outcome: improved service stability 
and abuse prevention.

## Classification

- **Type**: feature
- **Rationale**: This adds a new capability (rate limiting) to an existing subsystem (API).

## Acceptance Criteria

1. Requests from the same user over 100/minute return HTTP 429
2. Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset) 
   are included in all responses
3. Rate limit state is tracked per-user ID (from auth token or session), not per-IP
4. Rate limit configuration (threshold, window) is read from environment variables 
   at startup
5. Rate limit data is stored in memory with a sliding-window counter

## Known Constraints

- **Language / framework**: TypeScript, Express.js
- **Scope**: affects only API endpoints; does not change service discovery or routing
- **Performance**: rate-limit check must add < 1ms per request
- **Compatibility**: must not break existing public API; 429 is already documented

## References

- Parent issue: #100
- Source issue or spec: none (new feature request)
- Related issues: none
- Prior art: none

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: phase
phase: intake
classification: feature
status: open
source_issue: null
```
```

**Result**: Returns intake issue number, e.g., `#101`.

#### Step 4: Attach intake to parent via GraphQL

```bash
PARENT_NODE_ID=$(gh issue view 100 --json id --jq .id)
INTAKE_NODE_ID=$(gh issue view 101 --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$INTAKE_NODE_ID"
```

**Result**: Intake issue (#101) now appears as a child of parent issue (#100) in GitHub's UI.

#### Step 5: Close the intake issue

```bash
gh issue close 101
```

**Result**: Intake issue is now closed. GitHub sub-issue tree shows:
```
#100 [agent:parent] — 2026-04-27-add-rate-limiting
└── #101 [phase:intake] Intake — 2026-04-27-add-rate-limiting (CLOSED)
```

#### Step 6: No local files created

**CRITICALLY**: Do **not** create:
- ❌ `.coding-workflow/work/2026-04-27-add-rate-limiting/01-intake.md`
- ❌ `.coding-workflow/work/2026-04-27-add-rate-limiting/work.yaml`
- ❌ Any other local per-work-item markdown files

This is a hard rule. From `issue-hierarchy.md`:

> Do **not** fall back to local per-work-item markdown artifacts.

---

## GitHub Issue Structure After Phase 1

```
#100 [agent:parent]
  title: 2026-04-27-add-rate-limiting
  labels: agent:parent
  status: open
  machine_data:
    work_id: 2026-04-27-add-rate-limiting
    kind: parent
    classification: feature
    current_phase: intake
  
  └─ #101 [agent:phase, phase:intake]
     title: Intake — 2026-04-27-add-rate-limiting
     labels: agent:phase, phase:intake
     status: closed
     machine_data:
       work_id: 2026-04-27-add-rate-limiting
       kind: phase
       phase: intake
```

---

## Comparison: With Existing ISSUE vs. Without

### Scenario A: No existing ISSUE (this task)

**Phase 1 actions**:
1. Create **new** parent issue (`gh issue create`)
2. Create intake child issue (`gh issue create`)
3. Link intake to parent (`gh api graphql addSubIssue`)
4. Close intake issue

**Result**: Two new GitHub issues created.

### Scenario B: Existing ISSUE provided (e.g., `ISSUE=42`)

**Phase 1 actions**:
1. Fetch existing issue #42 with `gh issue view 42 --json number,title,body,url,id`
2. Infer `WORK_ITEM` from #42's title/body
3. **Reuse #42 as the parent issue** — refresh its body to match parent template
4. Create intake child issue (`gh issue create`)
5. Link intake to parent #42 (`gh api graphql addSubIssue`)
6. Close intake issue

**Result**: Existing issue #42 becomes the parent; one new intake child issue is created.

---

## What Each Issue Contains

### Parent Issue (#100)

| Section | Content |
|---------|---------|
| **Title** | `2026-04-27-add-rate-limiting` |
| **Labels** | `agent:parent` |
| **Summary** | One paragraph work-item description |
| **Current Phase** | Text naming the next phase or blocker |
| **Acceptance Snapshot** | Compact numbered list (copied from intake) |
| **Sub-issues** | Checklist of 10 phase/artifact issues (will be checked off as work progresses) |
| **Machine Data** | YAML with `work_id`, `kind: parent`, `classification`, `status`, `current_phase`, `source_issue` |

**Role**: Lightweight index and progress tracker. It links the workflow together but does not hold detailed phase artifacts.

**Stays open** until the PR is merged. The PR closes it with `Fixes #100`.

### Intake Issue (#101)

| Section | Content |
|---------|---------|
| **Title** | `Intake — 2026-04-27-add-rate-limiting` |
| **Labels** | `agent:phase`, `phase:intake` |
| **Summary** | Full work-item description with context |
| **Classification** | Type (feature/bug/refactor/spec/chore) + rationale |
| **Acceptance Criteria** | 1-5+ independently verifiable criteria |
| **Known Constraints** | Language, scope, deadline, compatibility, performance |
| **References** | Links to parent issue, source specs, related issues |
| **Machine Data** | YAML with `work_id`, `kind: phase`, `phase: intake`, `classification`, `status`, `source_issue` |

**Role**: Durable intake artifact. Records the work-item summary, classification, acceptance criteria, and constraints in structured form. This artifact remains in GitHub for the full workflow lifecycle.

**Closed after creation** because the intake artifact is complete and immutable. Its content does not change; later phases reference it.

---

## Canonical Durable Record

After Phase 1, the canonical workflow state is:

```
GitHub issue hierarchy:
  ✅ Parent issue #100 (open)
  ✅ Intake child issue #101 (closed, but content is immutable and durable)

Local file system:
  ❌ No .coding-workflow/work/<slug>/ files
  ❌ No local intake.md
  ❌ No local work.yaml
```

If the agent is interrupted and the workflow resumes later with `RESUME=2026-04-27-add-rate-limiting`:

```bash
# The new session will:
gh issue view <parent-issue-number> --json number,title,body,id
# Reads parent issue #100

gh issue view <intake-child-number> --json number,title,body,id  
# Reads intake issue #101

# Reconstructs full state from GitHub alone.
# No local files needed; GitHub is authoritative.
```

---

## Key Rules (Non-Negotiable)

From `SKILL.md` and `workflow.md`:

1. **GitHub is canonical** (Phases 1–11) — all durable state lives in GitHub issues and comments, not local files
2. **Phase 0 is special** — only Phase 0 writes repo-local override files
3. **No local per-work-item artifacts** — do not create `.coding-workflow/work/<slug>/` files
4. **Two issues, one workflow** — parent issue (lightweight) + phase issues (detailed artifacts)
5. **Structured Machine Data** — every issue must include a YAML metadata block
6. **GraphQL sub-issue linking** — use `gh api graphql addSubIssue`, not body references

---

## Phase 1 Outputs (Summary)

| Artifact | Type | Status | Location |
|----------|------|--------|----------|
| Parent issue | GitHub issue | Open | #100 |
| Intake issue | GitHub issue | Closed | #101 |
| Local files | None | — | — |

**Next phase**: Phase 2 Worktree Setup begins. It will create a worktree issue and attach it to the parent.

---

## Command Reference (Complete Phase 1)

```bash
#!/bin/bash
set -e

WORK_ITEM="Add rate limiting to the API with per-user quotas..."
WORK_ID="2026-04-27-add-rate-limiting"

# Step 1: Create parent issue
PARENT=$(gh issue create \
  --title "$WORK_ID" \
  --body "## Summary

$WORK_ITEM

## Current Phase

Phase 1: Intake

## Acceptance Snapshot

1. Requests over 100/minute return HTTP 429
2. Rate limit headers included in responses
3. Tracking per-user ID
4. Config via environment

## Sub-issues

- [ ] #N+1 Intake
- [ ] #N+2 Worktree
- [ ] #N+3 Exploration
- [ ] #N+4 Research
- [ ] #N+5 Clarification
- [ ] #N+6 Plan
- [ ] #N+7 Task graph
- [ ] #N+8 Review
- [ ] #N+9 Verification
- [ ] #N+10 PR

## Machine Data

\`\`\`yaml
work_id: $WORK_ID
kind: parent
classification: feature
status: open
current_phase: intake
source_issue: null
\`\`\`
" \
  --label "agent:parent" \
  --json number \
  --jq .number)

# Step 2: Create intake issue
INTAKE=$(gh issue create \
  --title "Intake — $WORK_ID" \
  --body "## Summary

$WORK_ITEM

## Classification

- **Type**: feature
- **Rationale**: New capability for API.

## Acceptance Criteria

1. Requests over 100/minute return HTTP 429
2. Rate limit headers in responses
3. Tracking per-user ID
4. Config via environment

## Known Constraints

- Language: TypeScript, Express.js
- Scope: API endpoints only
- Performance: < 1ms per request
- Compatibility: No breaking changes

## References

- Parent issue: #$PARENT

## Machine Data

\`\`\`yaml
work_id: $WORK_ID
kind: phase
phase: intake
classification: feature
status: open
source_issue: null
\`\`\`
" \
  --label "agent:phase" \
  --label "phase:intake" \
  --json number \
  --jq .number)

# Step 3: Link intake to parent
PARENT_NODE=$(gh issue view $PARENT --json id --jq .id)
INTAKE_NODE=$(gh issue view $INTAKE --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }
' \
  -f parentId="$PARENT_NODE" \
  -f subIssueId="$INTAKE_NODE"

# Step 4: Close intake
gh issue close $INTAKE

echo "Phase 1 complete."
echo "Parent: #$PARENT (open)"
echo "Intake: #$INTAKE (closed)"
echo "Work ID: $WORK_ID"
```

---

## Conclusion

Phase 1, with no existing ISSUE, creates **exactly two GitHub issues**:

1. **Parent issue** — lightweight index tracking all phases
2. **Intake issue** — structured artifact holding summary, classification, acceptance criteria, constraints

**No local files are created.** GitHub is the sole durable workflow record. This design enables:

- ✅ **Resumability** — any agent can resume with `RESUME=<slug>` and read state from GitHub
- ✅ **Durability** — issues are persistent; local files can be lost or corrupted
- ✅ **Traceability** — complete workflow history is visible in GitHub issue comments and state
- ✅ **Collaboration** — human and agent feedback happens directly in issues
