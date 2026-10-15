---
name: code-review
description: Review a pull request, branch, recent commits, staged or unstaged changes, or AI-generated code for correctness, readability, architecture, security, performance, standards/spec adherence, and maintainability. Use when reviewing a PR before merge, reviewing changes since a fixed point, reviewing work-in-progress changes, reviewing another agent's code, asking to "review since X", requesting a thermo-nuclear / thermonuclear / deep code quality / especially harsh maintainability review, or when machine-readable output is needed.
disable-model-invocation: true
---

# Code Review

Review only the requested change scope. Anchor every finding to that change. Prefer behavior-preserving simplification: smaller, clearer, more direct code over cleverness or incidental complexity.

## Scope

Review for correctness, readability, architecture, security, performance, documented standards, spec adherence if a spec exists, and maintainability.

Report only issues introduced by, exposed by, or clearly reachable through the reviewed change.

## Required-agent rule

If this skill requires a dedicated agent, run it. Do not merge, combine, substitute, skip, or manually emulate required agents.

## Process

1. Invoke `subagent-model-router` and `addy-code-review-and-quality`.

2. Make a todo list.

3. Set the review target only. Do not read PR or issue content directly in this step.
   - PR review: target the PR.
   - Fixed-point review: use exactly the user-provided target.
   - If the user says “review since X” but X is not a fixed point, ask: `Review against what — a branch, a commit, or main?` Stop until answered.

4. Follow the main-agent GitHub intake rule:
   - The main agent must not read PR or GitHub issue content directly.
   - All GitHub PR/issue intake must be done by a fast-tier subagent using `gh`, not web fetch.
   - The main agent may use only the subagent summary unless a later required agent needs more detail.

5. Capture inputs with fast-tier subagents.
   - Fixed-point review:
     - `git diff <fixed-point>...HEAD`
     - `git log <fixed-point>..HEAD --oneline`
   - PR review:
     - PR status and early-stop recommendation: open / closed / draft / review not needed / already reviewed by you
     - title, body summary, branch info, changed files, linked issues, referenced specs, notable metadata
     - compact summary of linked or referenced GitHub issues relevant to scope or spec
     - likely spec-source candidates in priority order
   - If not reviewing a PR but GitHub issues are referenced, fetch and summarize them.

6. Stop early if intake says a PR is closed, draft, does not need review, or already has a review from you.

7. Gather only relevant standards/context files via a fast-tier subagent, checking repo root and touched paths as applicable:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `GEMINI.md`
   - `CONTRIBUTING.md`
   - `CONTEXT.md`
   - `CONTEXT-MAP.md`
   - `STYLE.md`
   - `STANDARDS.md`
   - `STYLEGUIDE.md`
   - `docs/adr/*`
   - `.editorconfig`
   - `eslint.config.*`
   - `biome.json`
   - `prettier.config.*`
   - `tsconfig.json`

8. Identify the spec source in this order:
   1. issue references from commit messages or PR metadata
   2. user-supplied path
   3. matching spec / PRD under `docs/`, `specs/`, `.scratch/`, or `.agents/scratchpad/**`
   4. if none is found, ask where the spec is; if there is no spec, record `no spec available` and skip the Spec agent

9. Preflight required agents. Hard stop if any required agent is missing.

   Always required:
   - `addy-code-reviewer`
   - `addy-security-auditor`
   - `addy-test-engineer`
   - Maintainability agent
   - Standards agent

   Required only if a spec exists:
   - Spec agent

   Required only for PR reviews:
   - History agent
   - Related-PR agent
   - Code-comment agent

10. Spawn required agents in parallel.

    PR-only agents:
    - History agent: use `git blame` and modified-code history to identify historically supported issues.
    - Related-PR agent: review prior PRs touching the same files for comments that still apply.
    - Code-comment agent: check whether the change violates guidance in comments within modified files.

    All-review agents:
    - `addy-code-reviewer`: correctness, readability, architecture, security, performance
    - `addy-security-auditor`: OWASP Top 10, secrets, auth/authz, threat model, dependency CVEs
    - `addy-test-engineer`: test gaps in happy path, edge cases, error paths, concurrency
    - Spec agent, if a spec exists: missing or partial requirements, scope creep, incorrect implementation
    - Maintainability agent: apply `MAINTAINABILITY_CRITERIA.md`
    - Standards agent: report only documented standards violations; cite file and rule; skip anything tooling enforces

11. Filter false positives.
    - For each issue, spawn a parallel fast-tier subagent to score whether it is real or a false positive.
    - Use `FALSE_POSITIVE_RUBRIC.md` verbatim.
    - For standards findings, confirm the standards file explicitly supports the finding.
    - Filter out issues with score below 75.

12. Produce output.
    - For PR comment mode, use `OUTPUT_FORMATS.md`, repeat the PR eligibility check before commenting, and post with `gh pr comment` only if still eligible.
    - For machine-readable mode, use `OUTPUT_FORMATS.md`.
    - If the user requested a different output format, satisfy it while preserving the same filtering and evidence requirements.

## Exclusions

Do not report:

- speculative bugs that do not survive light scrutiny
- pedantic nitpicks
- issues tooling should catch
- generic requests for more tests, docs, or security review unless explicitly required by a standards file or clearly broken in the change
- likely intentional functional changes tied to the broader change
- issues on unchanged lines unless the change clearly exposes or activates them

Do not run builds, typechecks, linters, or benchmarks unless the user explicitly asks.

## Review priorities

1. correctness bugs
2. documented repo standards violations
3. spec mismatches
4. structural maintainability regressions
5. missed opportunities for dramatic simplification when a clear path is visible
6. architecture boundary problems
7. security and performance issues supported by the change
8. readability issues that materially affect comprehension

## Primary review questions

- Is there a code-judo move that would make this dramatically simpler?
- Did the diff add branching complexity where a better abstraction should exist?
- Is this logic in the right file and layer?
- Is this abstraction earning its keep, or is it just a wrapper?
- Did the diff introduce casts, optionality, or ad-hoc object shapes that obscure the real invariant?

## Tone

Be direct, serious, and brief. Do not be rude. Do not soften major maintainability or correctness problems into mild suggestions. Do not treat a change as no-issue merely because behavior seems correct if it clearly makes the codebase structurally worse.

## Final checks

Before returning or commenting, verify:

- [ ] every required dedicated agent for this review type was run
- [ ] no required agent was merged, combined, substituted, skipped, or manually emulated
- [ ] every finding is tied to the reviewed change
- [ ] every finding has a concrete file reference
- [ ] every standards-based finding is explicitly supported by a standards file
- [ ] no excluded false positives are included
- [ ] false-positive scoring from `FALSE_POSITIVE_RUBRIC.md` was applied
- [ ] if a plausible restructuring would delete substantial incidental complexity, call it out
- [ ] if a major maintainability problem is present, do not hide it behind minor wording
- [ ] output matches the requested mode exactly
