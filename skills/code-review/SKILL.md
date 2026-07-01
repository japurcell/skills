---
name: code-review
description: Reviews PRs, diffs, commits, staged or unstaged changes, or another agent's patch for correctness, standards/spec adherence, maintainability, architecture, security, performance, and readability. Use whenever the user asks to review code, inspect a PR/branch/diff, audit staged or work-in-progress changes, review AI-generated code, say `review since main` or `review since this commit`, ask `find issues in this patch`, request a harsh/deep/thermonuclear maintainability pass, or want PR-comment / machine-readable review output—even if they never say `code review` explicitly.
disable-model-invocation: true
---

# Code Review

Review only the requested scope. Report only issues introduced by, exposed by, or clearly reachable through the change. Be brief, direct, and evidence-backed.

## Required Setup

1. Invoke `subagent-model-router` and `addy-code-review-and-quality`.
2. Create a todo list.
3. Use fast-tier subagents for GitHub/git intake.
4. Main agent must not read PR or issue content directly.
5. Use `gh` for GitHub intake, not web fetch.
6. Stop if any required role, subagent, or required external file cannot be used.

## Scope

- PR: review the PR diff and relevant metadata.
- Local changes: review staged, unstaged, or both exactly as requested.
- Fixed/base review: review `target...HEAD` plus `git log target..HEAD --oneline`.
- If the user says `review since` without a clear base, ask exactly: `Review against what — a branch, a commit, or main?` Then stop.

Do not expand scope, run builds/tests/linters/benchmarks, or fix code unless asked.

## Intake

Use fast-tier subagents to gather only needed context.

### Local changes

- staged: `git diff --cached`
- unstaged: `git diff`
- both: capture both

### Fixed/base review

- `git diff <target>...HEAD`
- `git log <target>..HEAD --oneline`

### PR review

Capture:

- eligibility: `open`, `closed`, `draft`, or `review not needed` based on explicit PR labels/body/repo convention
- title/body summary
- branch/base info
- changed files
- linked issues/specs
- compact linked-issue summaries

Stop early if PR is closed, draft, or marked review-not-needed. Before `gh pr comment`, repeat the eligibility check.

## Context and Standards

Spawn a subagent to gather only relevant standards/context files from global, repo root, and touched paths:

- `~/.copilot/copilot-instructions.md`
- `~/.gemini/GEMINI.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `CONTRIBUTING.md`
- `CONTEXT*.md`
- `STYLE*.md`
- `STANDARDS.md`
- `.github/*.md`
- `.gemini/*.md`
- `docs/adr/*`
- `.editorconfig`
- `eslint.config.*`
- `biome.json`
- `prettier.config.*`
- `tsconfig.json`

Standards findings must cite the exact standards file and rule.

## Spec Discovery

Find the spec in this order:

1. issue references from commit messages or PR metadata
2. user-supplied path
3. matching spec/PRD under `docs/`, `specs/`, `.scratch/`, or `.agents/scratchpad/**`
4. if none exists, record `no spec available` and skip spec review

## Required Review Roles

Run each role distinctly in parallel. Do not merge them into one generic pass.

Always run:

- `addy-code-reviewer`
- `addy-security-auditor`
- `addy-test-engineer`
- maintainability review using `MAINTAINABILITY_CRITERIA.md`
- standards review limited to explicit documented rules; skip anything tooling already enforces

Also run:

- spec review if a spec exists
- for PRs: history review using `git blame` and modified-code history
- for PRs: related-PR review
- for PRs: code-comment review

Stop if any required role cannot be assigned.

## Review Priorities

1. correctness
2. explicit repo standards
3. spec mismatches
4. maintainability regressions
5. obvious simplification opportunities
6. architecture/layering problems
7. security or performance issues caused by the change
8. readability issues that materially hurt comprehension

## Finding Rules

Keep a finding only if it has:

- concrete file/line or code reference
- clear link to the reviewed change
- specific impact
- actionable recommendation
- low false-positive risk

Filter findings with fast-tier subagents using `FALSE_POSITIVE_RUBRIC.md` verbatim. Keep only findings scoring `80` or higher.

Do not report:

- speculative issues
- pedantic nits
- generic requests for tests, docs, or security review
- issues tooling should catch
- unchanged-code problems unless activated by the change
- likely intentional product changes unless they contradict an explicit spec

## Output

Use the requested output mode.

- PR comment mode and machine-readable mode must follow `OUTPUT_FORMATS.md`.
- Different output formats are allowed only if scope, filtering, evidence, and role requirements remain intact.

Default format:

## Findings

### High

- `file:line` — Issue. Impact. Recommendation.

### Medium

- `file:line` — Issue. Impact. Recommendation.

### Low

- `file:line` — Issue. Impact. Recommendation.

## Notes

- Scope reviewed: ...
- Spec: found / not found
- Validation not run unless requested.
- Roles run: ...

If no findings:

No issues found in the requested scope.

## Verification

Before final output, verify:

- [ ] Review target is fixed or clarified
- [ ] PR eligibility was checked, if applicable
- [ ] Relevant standards/context files were gathered
- [ ] Spec review ran or `no spec available` was recorded
- [ ] Every required role ran distinctly
- [ ] Findings are tied to the change with concrete file references
- [ ] Findings survived `FALSE_POSITIVE_RUBRIC.md` filtering with score `80+`
- [ ] Standards findings cite an explicit standards file/rule
- [ ] Requested output mode follows `OUTPUT_FORMATS.md`

Tone: concise, serious, and direct.
