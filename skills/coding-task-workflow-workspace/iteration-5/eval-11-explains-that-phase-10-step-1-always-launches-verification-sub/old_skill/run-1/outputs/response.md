# Evaluation: Phase 10 Verification Step 1 — Running Automated Checks

## Test Case

- **Phase**: Phase 10 (Verification)
- **Test commands**: `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`
- **Goal**: Understand what Step 1 must do, when to use parallel subagents, and what each reports

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), Phase 10 Step 1 is explicitly defined.

**Reference**: `references/workflow.md` Phase 10 lines 289–300:
> **Steps:**
> 1. Run the test suite, linter, type-checker, and build commands from `.coding-workflow/overrides/test-commands.yaml`. If the file does not exist, run the commands inferred during bootstrap or from repo scripts.
> 
> **Parallelism**: test-suite steps may run in parallel subagents if the test framework supports it.

---

## What Phase 10 Step 1 Must Do

### Primary Responsibility

**Run all four automated check commands:**
1. Test suite: `npm test`
2. Linter: `npm run lint`
3. Type checker: `npm run typecheck`
4. Build: `npm run build`

### Source of Truth

**Where commands come from** (in priority order):
1. **`.coding-workflow/overrides/test-commands.yaml`** (if file exists)
   - This file was created during Phase 0 (Bootstrap) and contains the authoritative command list
   - Example content:
     ```yaml
     test: npm test
     lint: npm run lint
     typecheck: npm run typecheck
     build: npm run build
     ```

2. **Commands inferred during bootstrap** (if the override file does not exist)
   - Inferred from `package.json` scripts, `Makefile`, `.github/workflows/`, CI configuration

3. **Repo scripts as fallback** (if both above are unavailable)
   - Discovered during Phase 0 analysis

### Execution Model

**Sequential by default, parallel when framework supports it:**

From workflow.md Phase 10 line 300:
> **Parallelism**: test-suite steps may run in parallel subagents if the test framework supports it.

**When to run sequentially:**
- Most NPM-based projects: run all four commands sequentially in the primary context
- Reason: each command typically must complete before the next can run cleanly

**When to use parallel subagents:**
- The test framework explicitly supports parallel test execution (e.g., Jest with `--maxWorkers=4`, Mocha with `--parallel`)
- Multiple test suites or check commands don't share state and won't conflict
- Each subagent runs exactly one command independently

---

## Parallel Subagent Model (If Applicable)

### When to Launch Parallel Subagents

**Condition 1: Test framework supports parallelization**
- Check for parallel test runner configuration (jest.config.js, mocha.opts, etc.)
- If `npm test` can run multiple test files concurrently without conflicts

**Condition 2: Commands are independent**
- `npm test` does not depend on `npm run build` completing first
- `npm run lint`, `npm run typecheck`, and `npm run build` can run in parallel if they don't share state

**Condition 3: Linter and type-checker can run in parallel**
- Static analysis tools (ESLint, TypeScript) typically don't conflict
- Can run `npm run lint` and `npm run typecheck` concurrently

### Subagent Launch Strategy

**Option A: Sequential (Default)**
```
Primary agent:
  1. Run: npm test → record exit code and output
  2. Run: npm run lint → record exit code and output
  3. Run: npm run typecheck → record exit code and output
  4. Run: npm run build → record exit code and output
```

**Option B: Partial Parallelism (Common)**
```
Primary agent:
  1. Launch Agent 1: npm run lint
  2. Launch Agent 2: npm run typecheck
  3. Wait for both to complete → record results
  4. Run: npm test (must run after build-like deps resolve)
  5. Run: npm run build → record results
```

**Option C: Full Parallelism (Rare, only if tests support it)**
```
Primary agent:
  1. Launch Agent 1: npm test
  2. Launch Agent 2: npm run lint
  3. Launch Agent 3: npm run typecheck
  4. Launch Agent 4: npm run build
  5. Wait for all to complete → aggregate results
```

### Each Subagent Must Report

**Standard report structure** (for any parallel subagent running a check command):

```
## Execution Report — <command>

- **Command**: npm test | npm run lint | npm run typecheck | npm run build
- **Exit code**: 0 | non-zero
- **Status**: PASS | FAIL
- **Output summary**: (first 500 chars of stdout)
- **Error summary**: (first 500 chars of stderr if exit code != 0)
- **Files affected**: (list of files changed or checked)
- **Duration**: (elapsed time in seconds)
- **Warnings/Errors count**: N (for lint/typecheck)
- **Test results**: (for npm test: N tests, N passed, N failed)
```

**Required fields in every report:**
1. **Command executed** — exact npm command run
2. **Exit code** — 0 for success, non-zero for failure
3. **Status** — PASS or FAIL (primary agent uses this for gate check)
4. **Output** — stdout and stderr (primary agent records in verification issue)
5. **Failure details** — if exit code != 0, include exact error messages

**Example report for `npm test`:**
```
## Execution Report — npm test

- **Command**: npm test
- **Exit code**: 0
- **Status**: PASS
- **Test results**: 247 tests, 247 passed, 0 failed
- **Duration**: 42.3 seconds
- **Coverage**: 94.2% statements, 88.1% branches
```

**Example report for `npm run lint` (with failures):**
```
## Execution Report — npm run lint

- **Command**: npm run lint
- **Exit code**: 1
- **Status**: FAIL
- **Linter**: ESLint 8.47.0
- **Issues found**: 3 errors, 12 warnings
- **Errors**:
  - src/http/client.ts:42: Missing semicolon
  - src/http/client.ts:89: Unused variable 'tempResult'
  - tests/http.test.ts:105: 'x' is defined but never used
- **Warnings**: (12 style warnings)
- **Duration**: 8.2 seconds
```

---

## Primary Agent Integration

### What the Primary Agent Does with Subagent Reports

**Step 1 summary**:
1. **Determine parallelism strategy** based on repo configuration
2. **Launch subagents** for each command (or run sequentially if no parallelism)
3. **Wait for all to complete**
4. **Aggregate results** into the verification artifact

### Recording Results in the Verification Issue

After Step 1, the primary agent records results in a table format (from `references/templates/verification.md`):

```markdown
## Automated Checks

| Command | Exit code | Notes |
|---------|-----------|-------|
| `npm test` | 0 | 247 tests, 0 failures |
| `npm run lint` | 0 | No new warnings |
| `npm run typecheck` | 0 | No errors |
| `npm run build` | 0 | Build successful |
```

**Exit code interpretation**:
- `0` = PASS (command succeeded)
- non-zero = FAIL (command failed)

**Early failure handling** (Steps 3–5):
- If any check fails in Step 1, the verification issue is created as `open`
- Steps 2–3 continue to completion for diagnosis
- Step 5: Return to Phase 8 to fix the failing behavior

---

## The Four Commands in Sequence

### Command 1: npm test

**Runs**: Test suite (Jest, Mocha, Vitest, or configured test runner)

**Subagent must report:**
- Exit code (0 = all tests pass)
- Total tests run
- Passed vs. failed count
- Coverage metrics (if configured)
- Failed test names and stack traces (if failures)

**Primary agent records**:
```
| `npm test` | 0 | 247 tests, 0 failures |
```

### Command 2: npm run lint

**Runs**: Code linter (ESLint, Prettier, or configured)

**Subagent must report:**
- Exit code (0 = no linting issues, or warnings allowed)
- Linter name and version
- Error count (must be 0)
- Warning count
- Each error and its location (file:line)

**Primary agent records**:
```
| `npm run lint` | 0 | No new warnings |
```

### Command 3: npm run typecheck

**Runs**: TypeScript type checker or equivalent

**Subagent must report:**
- Exit code (0 = no type errors)
- Type checker name and version
- Error count (must be 0)
- Each error location and message

**Primary agent records**:
```
| `npm run typecheck` | 0 | No errors |
```

### Command 4: npm run build

**Runs**: Build process (webpack, tsc, rollup, esbuild, etc.)

**Subagent must report:**
- Exit code (0 = build successful)
- Build tool and version
- Output directory
- Bundle size (if applicable)
- Build time

**Primary agent records**:
```
| `npm run build` | 0 | Build successful |
```

---

## Gate F Exit Criteria (After All Checks)

From `references/workflow.md` Phase 10 line 298 and Gate F (`references/stop-gates.md`):

**All four commands must exit with code 0** before Phase 11 can begin:
- ✅ `npm test` exit code = 0
- ✅ `npm run lint` exit code = 0
- ✅ `npm run typecheck` exit code = 0
- ✅ `npm run build` exit code = 0

If any check fails:
- Step 5: Return to Phase 8 to fix the failing behavior
- Re-run Phase 10 (Verification) from Step 1
- Record previous attempt in verification issue comments

---

## Key Decisions for Phase 10 Step 1

| Decision | Default | When to Vary |
|----------|---------|--------------|
| Sequential vs. parallel | Sequential (primary agent) | Launch subagents only if test framework explicitly supports parallelization |
| Test commands source | `.coding-workflow/overrides/test-commands.yaml` | Use bootstrap inferred if file doesn't exist |
| Failure handling | Stop and diagnose | Don't stop; continue to completion for full picture if time allows |
| Command order | npm test → lint → typecheck → build | Can reorder to lint/typecheck first (faster feedback) |

---

## Summary: Phase 10 Step 1 Algorithm

```
Phase 10 Step 1: Run Automated Checks

Input: test-commands.yaml or inferred commands
Output: exit codes and output for all four commands

1. Check if .coding-workflow/overrides/test-commands.yaml exists
   If yes: Read commands from file
   If no: Use bootstrap-inferred or repo-discovered commands

2. Determine parallelism strategy
   If test framework supports parallel execution:
     Launch up to 4 subagents (one per command)
   Else:
     Run all commands sequentially in primary agent

3. Execute all four commands:
   - npm test
   - npm run lint
   - npm run typecheck
   - npm run build

4. If parallel subagents:
   Each subagent reports: command, exit code, status, output
   Primary agent waits for all to complete

5. Record results in verification artifact template:
   Command | Exit code | Notes

6. Check exit codes:
   If all are 0:
     Proceed to Step 2 (acceptance criteria check)
   If any non-zero:
     Create verification issue with FAIL status
     Steps 2–3 continue for diagnosis
     Step 5: Return to Phase 8
```
