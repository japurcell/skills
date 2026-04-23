# Delegation Rules

This document defines when and how to use subagents in each phase of the workflow. Follow these rules to ensure consistent, non-overlapping delegation.

---

## General Principles

- **Non-overlapping scope**: when multiple agents run in parallel, each agent must cover a distinct, non-overlapping area. Overlapping scopes lead to conflicting writes and duplicated work.
- **Full context in prompt**: each subagent is stateless. Include all necessary context in the launch prompt — do not rely on shared state between agents.
- **Read findings directly**: after agents complete, always read the key files they identify. Do not act solely on agent summaries.
- **Scale to complexity**: launch the minimum number of agents needed for the task complexity. Do not launch agents speculatively.

---

## Phase 3 — Codebase Exploration Agents

### When to use

Always. Scale to track (see [workflow.md](workflow.md) Phase 3 track selection table).

### Agent prompts

**Agent A — Similar features and patterns**

```
Explore the codebase to find existing features similar to: [WORK_ITEM_SUMMARY].
Focus on:
1. Files that implement similar functionality.
2. Patterns used: data structures, error handling, naming, testing.
3. Anti-patterns or legacy approaches that new code should avoid.

Return:
- List of 5–10 key files (path + one-line reason).
- Summary of observed patterns (2–5 bullet points).
- Any open questions about the codebase.
```

**Agent B — Architecture and data flow**

```
Explore the codebase architecture relevant to: [WORK_ITEM_SUMMARY].
Focus on:
1. Module boundaries and dependencies.
2. Data flow from entry point to persistence (or from API call to response).
3. Extension points relevant to this change.
4. Any architectural constraints or decisions recorded in docs/.

Return:
- List of 5–10 key files (path + one-line reason).
- Architecture summary (2–5 bullet points).
- Any open questions about integration points.
```

**Agent C — Test infrastructure and build system** _(Deep track only)_

```
Explore the test infrastructure and build system for: [REPOSITORY_NAME].
Focus on:
1. Test framework, test file locations, naming conventions.
2. Fixture or factory patterns used for test data.
3. Build and CI commands (from Makefile, package.json, .github/workflows/).
4. Any known flaky tests or test helpers that new tests should use.

Return:
- List of 5–10 key files (path + one-line reason).
- Test and build summary.
- Any open questions about the test setup.
```

---

## Phase 4 — Online Research Agents

### When to use

Always, for any question in `open-questions.md`. Group questions by domain to avoid redundant searches.

### Agent prompt template

```
Research question: [QUESTION]
Repository context: [LANGUAGE], [FRAMEWORK], [VERSION]

1. Find the official documentation for [TOPIC] at the version used in this repo.
2. Check for any known issues, deprecations, or best-practice changes in recent versions.
3. Find one or two high-quality secondary sources if the official docs are insufficient.

Return for each source:
- URL
- Date accessed
- Key finding relevant to the question
- Confidence: high | medium | low
- Decision: how this finding should influence the implementation

Do not return generic summaries. Return only findings directly applicable to: [REPOSITORY_CONTEXT].
```

---

## Phase 8 — Implementation Agents _(parallel groups only)_

### When to use

Only for tasks marked `parallelizable: true` in `06-task-graph.yaml`. Sequential tasks are always executed by the primary agent.

### How to partition

1. Read `06-task-graph.yaml`.
2. Identify tasks whose `depends_on` are all already completed.
3. From those ready tasks, select all `parallelizable: true` tasks.
4. Each agent handles exactly one parallelizable task.
5. Agents must not write to the same files. If a file overlap is detected, convert the tasks to sequential.

### Agent prompt template

```
You are implementing task [TASK_ID]: [TASK_NAME].
Stage: [red | green | refactor]

Context files to read first:
- [LIST OF FILES FROM files.csv RELEVANT TO THIS TASK]
- .coding-workflow/work/[SLUG]/05-plan.md (sections: [RELEVANT SECTIONS])

Instructions:
1. Write the failing test first (RED).
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN).
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
[EXPLICIT LIST — do not write outside this list]

When done, append to .coding-workflow/work/[SLUG]/07-implementation-log.md:
- slice_id: [TASK_ID]
- status: complete
- files_changed: [LIST]
- test_result: pass
```

---

## Phase 9 — Review Agents

### When to use

Always — all three review agents run after Phase 8 completes.

### Partitioning changed files

1. List all files changed in Phase 8.
2. Partition into groups by module or directory (non-overlapping).
3. Assign each partition to both the code-review and tech-debt agents. The security agent always reviews all changed files (security issues do not respect module boundaries).

### Code review agent prompt

```
Perform a code review of the following files changed in this work item:
[LIST OF FILES WITH DIFFS OR PATHS]

Review criteria:
1. Conventions: does the code match existing patterns in the codebase?
2. Correctness: are there obvious logic errors or missing edge-case handling?
3. Clarity: are names clear? Is the code readable without comments?
4. DRY: is there unnecessary duplication?
5. Dead code: are there unused variables, unreachable branches, or obsolete comments?

For each finding: file, line range, severity (High|Medium|Low|Info), description, suggested fix.
Write findings to: .coding-workflow/work/[SLUG]/08-review/code-review.md
```

### Security review agent prompt

```
Perform a security review of ALL files changed in this work item:
[LIST OF ALL CHANGED FILES]

Check for (OWASP Top 10 and beyond):
1. Injection (SQL, command, template, LDAP).
2. Hardcoded secrets or credentials.
3. Insecure defaults (weak crypto, missing TLS, debug flags).
4. Authentication and session issues.
5. Broken access control (missing authorisation checks).
6. Unvalidated or unsanitised input.
7. Sensitive data exposure (logging PII, unencrypted storage).
8. Dependency vulnerabilities (note any newly added dependencies).
9. Race conditions or TOCTOU issues.
10. Path traversal or unsafe file operations.

For each finding: file, line range, severity (High|Medium|Low|Info), CWE if applicable, description, remediation.
Write findings to: .coding-workflow/work/[SLUG]/08-review/security-review.md
```

### Tech-debt review agent prompt

```
Perform a tech-debt review of the following files:
[LIST OF FILES]

Assess:
1. Duplication: are there blocks that could be extracted?
2. High coupling: does this code depend on too many other modules?
3. Complexity: are there functions with high cyclomatic complexity (>10 branches)?
4. Missing abstractions: are there opportunities to introduce a simpler interface?
5. Known anti-patterns for [LANGUAGE/FRAMEWORK]: list any detected.
6. Test coverage gaps: are there important behaviours not covered by tests?

For each finding: file, line range, severity (High|Medium|Low|Info), description, suggested improvement.
Write findings to: .coding-workflow/work/[SLUG]/08-review/tech-debt.md
```

---

## Agents Not to Use as Subagents

- Do not launch a subagent to perform git operations (commit, push, PR creation). Always do these in the primary context.
- Do not launch a subagent for the clarification phase — human communication must be in the primary context.
- Do not launch a subagent for the plan approval gate — that conversation requires direct human interaction.

---

## Subagent Output Format

All subagents must return findings in a structured format that can be written directly to the artifact files. Agents must not return prose-only summaries that require interpretation. Use the templates in [`templates/`](templates/) as output targets.
