---
name: code-review
description: Reviews PRs, diffs, commits, staged or unstaged changes, or another agent's patch for correctness, standards/spec adherence, maintainability, architecture, security, performance, and readability. Use whenever the user asks to review code, inspect a PR/branch/diff, audit staged or work-in-progress changes, review AI-generated code, say `review since main` or `review since this commit`, ask `find issues in this patch`, request a harsh/deep/thermonuclear maintainability pass, or want PR-comment / machine-readable review output—even if they never say `code review` explicitly.
disable-model-invocation: true
---

# Code Review

## Overview

Review only the requested change scope. Report only issues introduced by, exposed by, or clearly reachable through that change. Prefer simplification over cleverness, and keep findings brief, direct, and evidence-backed.

## When to Use

- PR, branch, commit-range, staged/unstaged, or AI-generated change review
- Requests like `review since main`, `find issues in this diff`, `be harsh`, `thermonuclear`, `maintainability review`, `security review`, or `machine-readable review`
- Not for writing/fixing code, broad architecture design, or running validation the user did not ask for

## Workflow

1. Invoke `subagent-model-router` and `addy-code-review-and-quality`. Make a todo list.
2. Lock the target:
   - PR review: target the PR.
   - Fixed-point review: use exactly the user-provided branch, commit, or base.
   - Local-change review: target staged changes, unstaged changes, or both exactly as requested.
   - If the user says `review since X` and `X` is not a fixed point, ask exactly: `Review against what — a branch, a commit, or main?` Stop.
3. Do GitHub intake through fast subagents only.
   - Main agent must not read PR or issue content directly.
   - Use `gh`, not web fetch.
   - Local-change intake: capture `git diff --cached`, `git diff`, or both, matching the requested scope.
   - Fixed-point intake: capture `git diff <target>...HEAD` and `git log <target>..HEAD --oneline`.
   - PR intake: capture eligibility (`open`, `closed`, `draft`, `review not needed`, `already reviewed by you`), title/body summary, branch info, changed files, linked issues/specs, and compact summaries of linked issues.
   - If intake says `closed`, `draft`, `review not needed`, or `already reviewed by you`, stop early.
4. Gather only relevant standards/context files from global, repo root and touched paths: `~/.copilot/copilot-instructions.md`, `~/.gemini/GEMINI.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `CONTEXT*.md`, `STYLE*.md`, `STANDARDS.md`, `.github/*.md`, `.gemini/*.md`, `docs/adr/*`, `.editorconfig`, `eslint.config.*`, `biome.json`, `prettier.config.*`, and `tsconfig.json`.
5. Find the spec in this order:
   1. issue references from commit messages or PR metadata
   2. user-supplied path
   3. matching spec/PRD under `docs/`, `specs/`, `.scratch/`, or `.agents/scratchpad/**`
   4. if none exists, record `no spec available` and skip spec review
6. Preflight required review roles. Stop if any required role cannot be assigned.
   - Always: `addy-code-reviewer`, `addy-security-auditor`, `addy-test-engineer`
   - Always: maintainability review using `MAINTAINABILITY_CRITERIA.md`
   - Always: standards review limited to explicit documented rules; skip anything tooling already enforces
   - If a spec exists: spec review
   - If reviewing a PR: history review (`git blame` + modified-code history), related-PR review, and code-comment review
7. Run required review roles in parallel. Keep each role distinct; do not merge them into one generic pass.
8. Filter false positives with fast subagents.
   - Use `FALSE_POSITIVE_RUBRIC.md` verbatim.
   - Keep only scores `80` or higher.
   - Standards findings need explicit file-plus-rule support.
9. Produce the requested output.
   - PR comment mode and machine-readable mode must follow `OUTPUT_FORMATS.md`.
   - Before `gh pr comment`, repeat the PR eligibility check.
   - Different output formats are fine only if the same scope, filtering, and evidence rules remain intact.

## Specific Techniques

### Review priorities

1. correctness
2. explicit repo standards
3. spec mismatches
4. maintainability regressions
5. obvious simplification opportunities
6. architecture boundary problems
7. security/performance issues supported by the change
8. readability issues that materially hurt comprehension

### Maintainability lens

Ask:

- Can a code-judo move delete incidental complexity?
- Did the change add branching or flags where a simpler shape exists?
- Is the logic in the right file or layer?
- Is an abstraction earning its keep?
- Did the change add casts, optionality, or ad-hoc shapes that hide invariants?

### Exclusions

Do not report:

- speculative bugs that fail light scrutiny
- pedantic nits
- issues tooling should catch
- generic asks for more tests, docs, or security review unless a rule explicitly requires them or the change is clearly broken
- likely intentional product changes tied to the broader diff
- issues on unchanged lines unless the reviewed change clearly exposes or activates them

Do not run builds, typechecks, linters, or benchmarks unless the user explicitly asks.

### Tone

Be brief, direct, and serious. Do not hide major correctness or maintainability problems behind soft wording.

## Common Rationalizations

| Rationalization                             | Reality                                                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| "I can read the PR and issues myself."      | Main-agent GitHub intake stays in fast subagents using `gh`; the review should consume summaries, not raw PR/issue pages. |
| "One broad review pass is enough."          | This skill requires distinct review roles; collapsing them loses coverage and breaks the workflow.                        |
| "This probably counts as an issue."         | Findings survive only with change linkage, concrete file evidence, and a false-positive score of at least 80.             |
| "We should run tests or builds to be safe." | Not here unless the user asked. This skill reviews code; it does not expand scope on its own.                             |

## Red Flags

- Review scope drifts beyond the requested PR, diff, or fixed point
- Main agent reads GitHub PR or issue content directly
- Required review roles are skipped, merged, or hand-waved
- Standards findings cite no explicit rule
- Findings are not tied to the reviewed change
- Machine-readable or PR-comment output ignores `OUTPUT_FORMATS.md`

## Verification

- [ ] Review target is fixed or clarified exactly
- [ ] Early-stop eligibility was checked for PR reviews
- [ ] Relevant standards/context files were gathered
- [ ] Spec review ran or `no spec available` was recorded
- [ ] Every required review role ran distinctly
- [ ] Every kept finding is tied to the change, has a concrete file reference, and survives false-positive filtering
- [ ] Standards findings cite an explicit standards file
- [ ] Output matches the requested mode exactly
