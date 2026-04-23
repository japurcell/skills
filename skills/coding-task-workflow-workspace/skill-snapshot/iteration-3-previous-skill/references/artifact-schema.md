# artifact Schema

Every artifact file produced by the `coding-task-workflow` skill must include YAML frontmatter and follow the structural rules in this document.

---

## Common Frontmatter Fields

All artifact files must start with:

```yaml
---
work_id: <slug> # e.g., 2026-04-23-add-retry-mechanism
phase:
  <phase-name> # intake | worktree | exploration | research |
  # clarification | plan | task-graph |
  # implementation-log | review | verification | pr
status: <status> # open | in-progress | complete | partial | blocked
updated_at: <ISO8601> # e.g., 2026-04-23T15:30:00Z
depends_on: # list of phases that must be complete before this one
  - <phase-name>
---
```

Optional fields:

```yaml
github_issue: <number> # GitHub issue number linked to this artifact
github_pr: <number> # GitHub PR number (for 10-pr.md only)
plan_approved: true # Only in 00-intake.md, after Gate D
plan_approved_at: <ISO8601> # Only in 00-intake.md, after Gate D
```

---

## Per-artifact Schemas

### `00-intake.md`

```yaml
---
work_id: <slug>
phase: intake
status: open
updated_at: <ISO8601>
depends_on: []
classification: feature | bug | refactor | spec | chore
github_issue: <number>
plan_approved: false
---
```

Body sections (required):

- `## Summary` — one paragraph restating the work item.
- `## Classification` — type and rationale.
- `## Acceptance Criteria` — numbered list; each criterion should be verifiable.
- `## Known Constraints` — language, framework, deadline, scope limits.
- `## References` — links to issues, specs, or related PRs.

---

### `01-worktree.md`

```yaml
---
work_id: <slug>
phase: worktree
status: complete
updated_at: <ISO8601>
depends_on: [intake]
---
```

Body sections (required):

- `## Worktree` — path, branch name, base commit SHA.
- `## Commands Run` — exact commands used to create the worktree.

---

### `02-exploration/summary.md`

```yaml
---
work_id: <slug>
phase: exploration
status: complete | partial
updated_at: <ISO8601>
depends_on: [worktree]
track: light | standard | deep
agents_launched: <number>
---
```

Body sections (required):

- `## Track Selected` — track name and rationale.
- `## Key Findings` — consolidated patterns, architectural insights, constraints.
- `## Anti-patterns to Avoid` — patterns observed that new code should not use.
- `## Relevant Files` — brief list; full list is in `files.csv`.
- `## Open Questions` — brief list; full details in `open-questions.md`.

---

### `02-exploration/files.csv`

Plain CSV; no frontmatter.

```
path,reason,phase_relevance
src/http/client.go,Existing HTTP client to extend,implementation
src/http/client_test.go,Test pattern to follow,implementation
docs/architecture.md,Context for HTTP layer design,plan
```

---

### `02-exploration/open-questions.md`

```yaml
---
work_id: <slug>
phase: exploration
status: complete
updated_at: <ISO8601>
depends_on: [exploration]
---
```

Body: a YAML list embedded in Markdown:

```markdown
## Questions

- id: q1
  question: "Which backoff algorithm does the existing retry helper use?"
  status: open # open | resolved | needs-human
  resolved_by: "" # phase that resolved it, or "human"
  answer: ""
```

---

### `03-research/findings.md`

```yaml
---
work_id: <slug>
phase: research
status: complete
updated_at: <ISO8601>
depends_on: [exploration]
---
```

Body: one section per question answered.

```markdown
## q1 — Which backoff algorithm to use?

- **Source**: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- **Date**: 2026-04-23
- **Finding**: Full jitter is recommended for high-concurrency scenarios.
- **Confidence**: high
- **Applicability**: directly applicable; our retry helper is used by multiple concurrent workers.
- **Decision**: use full-jitter exponential backoff (base 100 ms, max 30 s, cap 5 retries).
```

---

### `03-research/sources.md`

Plain Markdown table; no frontmatter.

```markdown
| id  | url         | date       | status      | notes                                |
| --- | ----------- | ---------- | ----------- | ------------------------------------ |
| s1  | https://... | 2026-04-23 | used        | Primary source for backoff algorithm |
| s2  | https://... | 2026-04-23 | unavailable | Behind paywall                       |
```

---

### `04-clarifications.md`

```yaml
---
work_id: <slug>
phase: clarification
status: complete
updated_at: <ISO8601>
depends_on: [research]
---
```

Body: one entry per question.

```markdown
## q3 — Should the retry limit be configurable per call-site?

- **blocking**: true
- **status**: answered
- **asked_at**: 2026-04-23T14:00:00Z
- **answered_at**: 2026-04-23T14:05:00Z
- **answer**: "Yes, accept an optional max_retries parameter, defaulting to 5."

## q4 — Should we log every retry attempt?

- **blocking**: false
- **status**: assumption
- **assumption**: "Log at DEBUG level to avoid noise in production logs."
```

---

### `05-plan.md`

```yaml
---
work_id: <slug>
phase: plan
status: approved
updated_at: <ISO8601>
depends_on: [clarification]
---
```

Body sections (required):

- `## Goal / Non-Goals`
- `## Recommended Approach`
- `## Alternatives Considered` _(if a meaningful trade-off exists)_
- `## File-by-File Implementation Map` — `path: exact change and purpose`
- `## Verification Guidance` — test commands and manual checks
- `## Revision History` _(added if plan is revised after initial draft)_

---

### `06-task-graph.yaml`

```yaml
work_id: <slug>
phase: task-graph
status: complete
updated_at: "2026-04-23T15:00:00Z"

tasks:
  - id: t1
    name: "Add failing test for single retry on 500"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/http/client_test.go

  - id: t2
    name: "Implement single retry on 500"
    stage: green
    depends_on: [t1]
    parallelizable: false
    files:
      - src/http/client.go

  - id: t3
    name: "Add failing test for retry count limit"
    stage: red
    depends_on: [t2]
    parallelizable: false
    files:
      - src/http/client_test.go

  - id: t4
    name: "Add failing test for jitter"
    stage: red
    depends_on: [t2]
    parallelizable: true
    files:
      - src/http/retry_test.go

  - id: t5
    name: "Implement retry count limit and jitter"
    stage: green
    depends_on: [t3, t4]
    parallelizable: false
    files:
      - src/http/client.go
      - src/http/retry.go

  - id: t6
    name: "Refactor: extract retry policy struct"
    stage: refactor
    depends_on: [t5]
    parallelizable: false
    files:
      - src/http/retry.go
      - src/http/client.go
```

---

### `07-implementation-log.md`

```yaml
---
work_id: <slug>
phase: implementation-log
status: in-progress
updated_at: <ISO8601>
depends_on: [task-graph]
---
```

Body: one entry appended per completed slice.

```markdown
## t1 — 2026-04-23T15:05:00Z

- **status**: complete
- **files_changed**: src/http/client_test.go
- **test_result**: pass (1 new test added, existing tests unaffected)
- **notes**: Test correctly fails before implementation.
```

---

### `08-review/code-review.md` / `security-review.md` / `tech-debt.md`

```yaml
---
work_id: <slug>
phase: review
review_type: code | security | tech-debt
status: complete
updated_at: <ISO8601>
depends_on: [implementation-log]
high_severity_count: 0
---
```

Body: one section per finding.

```markdown
## Finding 1

- **file**: src/http/client.go
- **lines**: 45–52
- **severity**: High
- **status**: open | resolved
- **description**: Retry loop does not cap total elapsed time, risking indefinite blocking.
- **suggestion**: Add a context deadline check inside the retry loop.
- **cwe**: CWE-400 (Uncontrolled Resource Consumption) _(security review only)_
```

---

### `09-verification.md`

```yaml
---
work_id: <slug>
phase: verification
status: complete
updated_at: <ISO8601>
depends_on: [review]
all_criteria_pass: true
---
```

Body sections:

```markdown
## Automated Checks

| Command             | Exit code | Notes                |
| ------------------- | --------- | -------------------- |
| `go test ./...`     | 0         | 42 tests, 0 failures |
| `golangci-lint run` | 0         | No new warnings      |

## Acceptance Criteria

| Criterion      | Result | Evidence                     |
| -------------- | ------ | ---------------------------- |
| Retry on 500   | pass   | TestRetryOn500: PASS         |
| Max 5 retries  | pass   | TestMaxRetries: PASS         |
| Jitter applied | pass   | TestJitterDistribution: PASS |

## Limitations

_(Omit this section if none.)_

- Manual smoke test against staging not performed (no staging environment available).
```

---

### `10-pr.md`

```yaml
---
work_id: <slug>
phase: pr
status: complete
updated_at: <ISO8601>
depends_on: [verification]
github_pr: <number>
github_issue: <number>
---
```

Body sections:

```markdown
## PR

- **Number**: #47
- **URL**: https://github.com/org/repo/pull/47
- **Branch**: feat/2026-04-23-add-retry-mechanism
- **Closes**: #42

## Follow-up Issues

- #48 [tech-debt]: Extract retry policy configuration into a dedicated config struct.
- #49 [tech-debt]: Add integration test against a real HTTP server.
```
