# Evaluation: Phase 11 Commit Message Format

## Test Case

- **Work item**: `2026-04-23-add-retry-mechanism`
- **Parent issue**: `#42`
- **Phase**: Phase 11 — Commit / Push / PR

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), Phase 11 commit messages must follow this format:

### Non-Negotiable Rule #5

From `SKILL.md` (line 33):
> Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

### Phase 11 Workflow Specification

From `references/workflow.md` (Phase 11 — Commit / Push / PR, lines 310–314):
> 1. Stage all changed files.
> 2. Write a conventional-commits message: `<type>(<scope>): <subject>`. Include a body linking to the work-item slug and parent issue, then append a `Co-authored-by: NAME <EMAIL>` trailer block separated from that body by a blank line using your own known co-author identity. For GitHub Copilot CLI, use `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

## Required Commit Message Shape

### Structure

```
<type>(<scope>): <subject>

<body>

<trailer>
```

### Components Breakdown

#### 1. Conventional Commits Subject Line

Format: `<type>(<scope>): <subject>`

- **type**: one of `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, etc. based on the work-item classification
- **scope**: optional context for the change (e.g., module name, feature area)
- **subject**: imperative, present-tense, lowercase, no period at end

Example subject lines:
- `feat(retry): add exponential backoff with jitter to HTTP client`
- `fix(csv-import): prevent silent row drops during parsing`
- `refactor(auth): migrate password hashing to Argon2id`

#### 2. Commit Body

Required content:
- A brief description of what changed and why
- Must include explicit reference to the **work-item slug** and **parent issue number**
- May include implementation notes, tradeoffs, or verification summary

Pattern: `This work implements <description>. Addresses work item <slug> (closes #<parent-issue>).`

Example body:
```
This work implements exponential backoff with jitter for HTTP client retries.
It caps retries at 5 attempts and only retries on status codes 429, 500, 502, 503, 504.
Test coverage verified via TDD phases.

Work item: 2026-04-23-add-retry-mechanism
Closes #42
```

#### 3. Blank Line Separator

A blank line (exactly one empty line) separates the body from the trailer block. This is required by Git and most CI systems that parse conventional commits.

#### 4. Co-authored-by Trailer

Format: `Co-authored-by: <NAME> <EMAIL>`

For GitHub Copilot CLI agents, always use:
```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

---

## Complete Example for Test Case

Given:
- Work item: `2026-04-23-add-retry-mechanism`
- Parent issue: `#42`
- Type: `feat` (assuming it's a feature, not a bug fix)
- Scope: `http-client` (assumed)

**Full commit message:**

```
feat(http-client): add exponential backoff with jitter to retry mechanism

This work implements a configurable retry mechanism for the HTTP client with
exponential backoff and jitter. Retries are capped at 5 attempts and only occur
for status codes 429, 500, 502, 503, and 504. All code paths are covered by TDD
test cases written before implementation.

Work item: 2026-04-23-add-retry-mechanism
Closes #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

---

## Formatting Rules (Non-Negotiable)

1. **Subject line must be on line 1**
   - No preamble, no blank lines before it
   - Format: `<type>(<scope>): <subject>`

2. **Blank line after subject (line 2 is blank)**
   - Required separator between subject and body

3. **Body starts on line 3**
   - Describe the change in clear, human-readable language
   - Include both the work-item slug and parent issue reference
   - Keep lines to ~72 characters for readability in terminals

4. **Blank line before trailer block**
   - Exactly one empty line separates body from trailers
   - This is standard Git convention

5. **Trailer block at the end**
   - `Co-authored-by:` must be on its own line
   - Format must be exact: `Co-authored-by: <Name> <email@example.com>`
   - For Copilot CLI: use `223556219+Copilot@users.noreply.github.com`

6. **No trailing blank lines**
   - The commit message should end with the trailer line (no blank lines after)

---

## Validation Checklist

For Phase 11 commits on `coding-task-workflow`:

- [ ] Subject line uses conventional commits format `<type>(<scope>): <subject>`
- [ ] Subject uses imperative, present-tense language
- [ ] Blank line after subject line
- [ ] Body references the work-item slug (e.g., `2026-04-23-add-retry-mechanism`)
- [ ] Body references the parent issue (e.g., `#42` or `Closes #42`)
- [ ] Blank line before trailer block
- [ ] Trailer block includes `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
- [ ] No trailing whitespace or blank lines after trailer

---

## Why This Format Matters

1. **Auditability**: GitHub issues, PRs, and git log remain synchronized via explicit references
2. **Resumability**: work-item slug in commit links back to the GitHub issue hierarchy
3. **Co-authorship**: `Co-authored-by` trailer is GitHub-recognized and credits the AI agent
4. **Tool compatibility**: conventional commits format is parsed by CI systems, release notes generators, and changelog tools
5. **Traceability**: parent issue `#42` appears in the commit, so `git log --grep="#42"` finds all related commits
