# coding-task-workflow Phase 10 Verification Step 1 Evaluation

## Scenario

- **Phase**: 10 (Verification)
- **test-commands.yaml** lists:
  - `npm test`
  - `npm run lint`
  - `npm run typecheck`
  - `npm run build`

## What Phase 10 Step 1 Must Do

**From workflow.md, Phase 10 — Verification, Step 1:**

> Launch verification subagents to run the test suite, linter, type-checker, and build commands from `.coding-workflow/overrides/test-commands.yaml`. If the file does not exist, use the commands inferred during bootstrap or from repo scripts. Run independent checks in parallel subagents when the repo supports concurrent execution; otherwise run one verification subagent at a time. Each subagent reports command, exit code, output summary, and any failure details.

**From SKILL.md, Non-negotiable rule #6:**

> Phase 10 verification step 1 is always performed by verification subagents. Split independent checks across parallel subagents when the repo supports concurrent execution; otherwise run one verification subagent at a time.

## Phase 10 Step 1: Primary Agent Actions

The primary agent does **NOT** directly run the verification commands. Instead:

1. **Read test-commands.yaml**: Load all commands (`npm test`, `npm run lint`, `npm run typecheck`, `npm run build`)

2. **Partition into independent checks**: Determine which commands can run in parallel and which must run sequentially

3. **Launch verification subagents**: Delegate each command or command group to a subagent

4. **Collect results**: Gather all subagent reports

5. **Record in Phase 10 issue**: Consolidate results in the verification GitHub issue

---

## Partitioning Strategy: Parallel vs Sequential

**From delegation-rules.md, Phase 10 — Verification Agents:**

> 2. Group commands by resource needs and dependency order:
>    - independent checks such as lint, type-check, unit tests, and build may run in parallel subagents when the repo supports concurrent execution;
>    - checks that share mutable state, require a server/database, or depend on build artifacts run sequentially, one verification subagent at a time.

### For the Given Commands

**Independent (can run in parallel)**:
- `npm run lint` — no dependencies, read-only file analysis
- `npm run typecheck` — no dependencies, static analysis

**Potentially dependent/sequential**:
- `npm test` — may depend on build artifacts or shared test state
- `npm run build` — produces artifacts that tests may depend on

### Recommended Partitioning Strategy

**Option A: Repo supports concurrent execution**
```
Parallel Group 1:  npm run lint
Parallel Group 2:  npm run typecheck
Sequential after build artifacts ready:
  npm run build
  npm test (depends on build artifacts)
```

**Option B: Repo does NOT support concurrent execution**
```
Sequential:
  npm run lint
  npm run typecheck
  npm run build
  npm test
```

**Key principle**: The primary agent checks repo capabilities. From delegation-rules.md:
> When the repo supports concurrent execution, run independent checks in parallel; otherwise run verification subagents sequentially.

---

## What Each Verification Subagent Must Report

**From workflow.md, Phase 10 Step 1:**

> Each subagent reports command, exit code, output summary, and any failure details.

### Required Report Fields

Each verification subagent that runs a command or command group must return:

#### **1. Command**
- Exact command executed (e.g., `npm run lint`)
- Full command with all arguments and flags used

#### **2. Exit Code**
- Numeric exit code (0 = success, non-zero = failure)
- Must be explicit; don't infer from output

#### **3. Pass/Fail**
- Pass if exit code is 0
- Fail if exit code is non-zero
- Clear binary status

#### **4. Output Summary**
- Concise summary of what passed or failed
- Examples:
  - `npm run lint`: "All 247 files passed linting; 0 new warnings"
  - `npm run typecheck`: "TypeScript check passed; 0 errors"
  - `npm test`: "44 tests passed, 0 failed"
  - `npm run build`: "Build successful; 3 bundles generated, 2.4 MB total"

#### **5. Failure Details**
- If exit code is non-zero, include failure details:
  - File paths with errors
  - Test names that failed
  - Error messages and stack traces (relevant portions)
  - Which lines are affected

#### **6. Environment Assumptions**
- Node version, npm version, or other runtime requirements
- Whether the command was run in a clean environment or with cached artifacts
- Any environment variables set
- Skipped checks and why (e.g., "skipped integration tests because no database server running")

### Agent Prompt Template

**From delegation-rules.md, Phase 10:**

```text
You are running Phase 10 verification for work item [WORK_ID].
Command group: [NAME]

Context:
- Acceptance criteria issue: [SUMMARY OR LINK]
- Plan verification guidance: [SUMMARY OR LINK]
- Review issue: [SUMMARY OR LINK]
- Changed files: [LIST]

Run exactly these commands:
[COMMANDS]

Return:
- command
- exit code
- pass/fail
- concise output summary
- failure details with file paths or test names when applicable
- any environment assumptions or skipped checks
```

---

## Consolidation: Recording in Phase 10 Issue

After all verification subagents complete, the primary agent consolidates results into a GitHub `phase:verify` issue using the template from `references/templates/verification.md`.

### Template Structure

**Automated Checks Table**:
```markdown
| Command | Exit code | Notes |
|---------|-----------|-------|
| npm test | 0 | 44 tests, 0 failures |
| npm run lint | 0 | 247 files, 0 new warnings |
| npm run typecheck | 0 | 0 TypeScript errors |
| npm run build | 0 | Build successful |
```

**Acceptance Criteria Table**:
```markdown
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Retry succeeds after 429 response | pass | test_retry_429: PASS |
| 2 | Exponential backoff applied correctly | pass | test_backoff_timing: PASS |
| 3 | Max retries capped at 5 | pass | test_max_retries: PASS |
```

**Review Clearance Table**:
```markdown
| Review type | High findings | Status |
|-------------|--------------|--------|
| Code review | 0 | Cleared |
| Security review | 0 | Cleared |
| Tech-debt review | 0 | Cleared |
```

**Machine Data**:
```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: verify
status: open
depends_on:
  - review
all_criteria_pass: true
```

---

## Primary Agent Responsibility

The primary agent must:

1. **Do NOT directly run commands** — always use verification subagents

2. **Partition intelligently**: Determine parallelism based on repo capabilities and command dependencies

3. **Review every result** — do not rely on subagent summaries alone. From workflow.md Phase 10:
   > After each subagent finishes, inspect its changed files and test output before updating or closing the task issue.

   (This applies to implementation; Phase 10 inspection means reviewing reported results.)

4. **Consolidate into the verification issue**: Combine all subagent reports into the GitHub issue

5. **Check acceptance criteria**: For each criterion from the intake issue, record `pass` or `fail` with evidence from subagent output

6. **Verify review clearance**: Confirm no `High` severity issue remains open from Phase 9 review

7. **Decision point**: 
   - If any criterion fails → return to Phase 8 for fixes, then re-run verification
   - If all criteria pass and all checks exit 0 → proceed to close the verification issue and Gate F

---

## Gate F Requirements

**From workflow.md, Gate F (line 301):**

> the verification issue is closed, every acceptance criterion is marked `pass`, all automated checks exit 0, and no `High` review finding remains open before Phase 11 begins.

Before closing the verification issue, ensure:
- ✓ All automated commands (lint, typecheck, test, build) exit with code 0
- ✓ All acceptance criteria from intake issue are marked `pass`
- ✓ Review issue has no open `High` severity findings
- ✓ Verification issue body is complete and accurate

---

## Example: 4 Commands → Subagent Delegation

Given `test-commands.yaml` with 4 commands:

### Scenario 1: Repo supports concurrent execution

**Parallel batch 1** (lint + typecheck can run simultaneously):
- Subagent A: runs `npm run lint` → reports exit code 0, "All 247 files passed", environment notes
- Subagent B: runs `npm run typecheck` → reports exit code 0, "0 TypeScript errors", environment notes

**Sequential batch 2** (build must complete before test):
- Subagent C: runs `npm run build` → reports exit code 0, "Build successful", 3 bundles generated
- Subagent D: runs `npm test` (after build ready) → reports exit code 0, "44 tests passed, 0 failed"

**Primary agent**: Collects A, B, C, D results → consolidates into verification issue

### Scenario 2: Repo does NOT support concurrent execution

**Sequential**:
- Subagent A: `npm run lint` → reports results
- Subagent B: `npm run typecheck` → reports results
- Subagent C: `npm run build` → reports results
- Subagent D: `npm test` → reports results

**Primary agent**: Collects A→B→C→D results in order → consolidates into verification issue

---

## Key Rules for Phase 10 Step 1

| Rule | Detail |
|------|--------|
| **Always use subagents** | Never directly run verification commands from primary context |
| **Partition by independence** | Lint, typecheck, unit tests in parallel when safe; sequential when dependent |
| **Read test-commands.yaml** | Source of truth for which commands to run |
| **Fallback to bootstrap** | If test-commands.yaml missing, use commands inferred during Phase 0 |
| **Report all 6 fields** | command, exit code, pass/fail, output summary, failure details, environment assumptions |
| **Primary agent consolidates** | Don't close verification issue until primary agent reviews all results |
| **Gate F requirement** | All commands exit 0 before verification issue closes |

---

## Specification References

| What | Where |
|------|-------|
| Phase 10 Step 1 overview | `workflow.md:292` |
| Non-negotiable rule #6 | `SKILL.md:34` |
| Parallelism rules | `workflow.md:303` |
| Delegation partitioning | `delegation-rules.md` (Phase 10 section) |
| Agent prompt template | `delegation-rules.md` (Phase 10 section) |
| Verification template | `references/templates/verification.md` |
| Gate F requirements | `workflow.md:301` |
| Acceptance criteria | `workflow.md:293` |
| Review clearance | `workflow.md:294` |
