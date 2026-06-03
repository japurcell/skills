---
name: code-review
description: Review a pull request, branch, recent commits, staged or unstaged changes, or AI-generated code for correctness, readability, architecture, security, performance, standards, spec adherence, and maintainability. Use when reviewing a PR before merge, reviewing changes since a fixed point, reviewing work-in-progress changes, reviewing another agent's code, asking to "review since X", requesting a thermo-nuclear / thermonuclear / deep code quality / especially harsh maintainability review, or when machine-readable output is needed.
---
# Code Review
Review only the requested change scope and anchor every conclusion to that change. Be ambitious about structural simplification: look for "code judo" moves that preserve behavior while making the code simpler, smaller, more direct, and more maintainable.

## When to use
- Review a pull request before merge
- Review a branch, work-in-progress changes, staged or unstaged changes, recent commits, or AI-generated code
- Review since a fixed point such as a commit, branch, tag, `main`, or `HEAD~N`
- Compare changes against repo standards or a spec / issue / PRD
- Request a thermo-nuclear / thermonuclear / deep code quality / especially harsh maintainability review
- Produce machine-readable findings for another model or script

## Scope
Review for correctness, readability, architecture, security, performance, standards adherence, spec adherence if a spec exists, and maintainability. Report only issues introduced by, exposed by, or clearly reachable through the reviewed change.

## Non-substitution rule
If this skill requires a dedicated agent, run that dedicated agent. Do not merge, combine, substitute, skip, or manually emulate required agents. Manual checking is not a substitute for the Spec agent, History agent, Related-PR agent, or Code-comment agent.

## Process
1. Invoke `subagent-model-router` and `addy-code-review-and-quality`.
2. Make a todo list.
3. Pin scope:
   - If given a PR, review that PR.
   - If asked to review since a fixed point, use exactly what the user provided.
   - If asked to "review since X" without a fixed point, ask: `Review against what — a branch, a commit, or main?` Do not proceed until answered.
   - For fixed-point reviews, capture:
     - `git diff <fixed-point>...HEAD`
     - `git log <fixed-point>..HEAD --oneline`
4. For PRs, use a fast-tier subagent to stop early if the PR is closed, draft, does not need review, or already has a review from you.
5. Gather context:
   - Use `gh` for GitHub interactions, not web fetch.
   - For PRs, use a fast-tier subagent to summarize the PR.
   - Read only relevant standards/context files: root or touched-path `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `CONTEXT.md`, `CONTEXT-MAP.md`, `STYLE.md`, `STANDARDS.md`, `STYLEGUIDE.md`, `docs/adr/*`, `.editorconfig`, `eslint.config.*`, `biome.json`, `prettier.config.*`, `tsconfig.json`.
6. Identify the spec source in this order:
   1. issue references in commit messages or PR metadata
   2. a user-supplied path
   3. a matching spec / PRD under `docs/`, `specs/`, `.scratch/`, or `.agents/scratchpad/**`
   4. if none is found, ask where the spec is; if there is no spec, record `no spec available` and skip the Spec agent
7. Preflight required agents. Complete before synthesis.
   - Always required:
     - [ ] `addy-code-reviewer`
     - [ ] `addy-security-auditor`
     - [ ] `addy-test-engineer`
     - [ ] Maintainability agent
     - [ ] Standards agent
   - Required only if a spec exists:
     - [ ] Spec agent
   - Required only for PR reviews:
     - [ ] History agent
     - [ ] Related-PR agent
     - [ ] Code-comment agent
   - Hard stop: if any required box is unchecked, do not continue to synthesis, output, or commenting.
8. Run agents in parallel.
   - For PRs, run these dedicated agents:
     1. History agent: use git blame and history of modified code to identify historically supported issues.
     2. Related-PR agent: read prior PRs touching the same files for comments that still apply.
     3. Code-comment agent: check whether the change violates guidance in comments within modified files.
   - For all reviews, run these dedicated agents:
     1. `addy-code-reviewer`: correctness, readability, architecture, security, performance.
     2. `addy-security-auditor`: OWASP Top 10, secrets, auth/authz, threat model, dependency CVEs.
     3. `addy-test-engineer`: test gaps in happy path, edge cases, error paths, concurrency.
     4. Spec agent: run only if a spec exists; report missing or partial requirements, scope creep, or incorrect implementation.
     5. Maintainability agent: do a strict maintainability review. Prefer deleting complexity over rearranging it; direct, boring code over hacky or magical code. Aggressively flag:
        - a file growing from under 1000 lines to over 1000 without strong justification
        - new ad-hoc conditionals, spaghetti growth, one-off booleans, nullable modes, or flags that complicate control flow
        - unnecessary wrappers, casts, optionality, indirection, `any`, `unknown`, ad-hoc object shapes, or cast-heavy contracts that obscure invariants
        - hacky or magical behavior, or generic mechanisms hiding simple data-shape assumptions
        - logic in the wrong layer, duplication of canonical helpers, or copy-pasted logic instead of extracted helpers
        - narrow edge-case handling inserted into an already busy function
        - sequential orchestration or non-atomic updates when a cleaner structure is obvious
        Treat unjustified file-size explosions, spaghetti growth, unnecessary abstraction layers, wrong-layer logic, and obvious duplication of canonical helpers as presumptive blockers unless clearly justified. Prefer a small number of high-conviction structural findings over cosmetic notes.
     6. Standards agent: report only documented standards violations; cite file and rule; skip anything tooling enforces.
9. Filter false positives:
   - For each issue, launch a parallel fast-tier subagent to score whether it is real or a false positive using the issue, reviewed change, and relevant standards files.
   - Use this rubric verbatim:
     - 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
     - 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant standards file.
     - 50: Moderately confident. The agent verified this is real, but it may be minor or uncommon.
     - 75: Highly confident. The agent verified it is very likely real and important, will be hit in practice, or is directly mentioned in the relevant standards file.
     - 100: Absolutely certain. The agent confirmed it is definitely real and will happen frequently in practice; the evidence directly confirms this.
   - For standards findings, confirm the standards file explicitly supports the finding.
   - Filter out issues with score below 80.
10. Exclusions:
   - Do not report pre-existing issues, speculative bugs that do not survive light scrutiny, pedantic nitpicks, issues tooling should catch, generic requests for more tests or docs or generic security concerns unless explicitly required by a standards file or clearly broken in the change, likely intentional functional changes tied to the broader change, or issues on unchanged lines unless the change clearly exposes or activates them.
   - Do not run builds, typechecks, linters, or benchmarks unless the user explicitly asks.

## Primary review questions
- Is there a code-judo move that would make this dramatically simpler?
- Did the diff add branching complexity where a better abstraction should exist?
- Is this logic in the right file and layer?
- Is this abstraction earning its keep, or is it just a wrapper?
- Did the diff introduce casts, optionality, or ad-hoc object shapes that obscure the real invariant?

## Output modes
### A. PR comment mode
If reviewing a PR, repeat the PR eligibility check before commenting. If still eligible, post with `gh pr comment`.

If qualifying findings remain, use this format exactly:
---
### Code review
Found <N> issues:
1. <brief description>
<link to file and line with full sha and line range>
2. <brief description>
<link to file and line with full sha and line range>
3. <brief description>
<link to file and line with full sha and line range>
🤖 Generated with [Claude Code](https://claude.ai/code)
<sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>
---

If no qualifying findings remain, use:
---
### Code review
No issues found. Checked for bugs, standards compliance, and maintainability.
🤖 Generated with [Claude Code](https://claude.ai/code)
---

Keep the comment brief:
- no emojis except the required footer line
- cite and link relevant files, code, standards, and URLs
- for code links, use full Git SHA and line ranges
- provide at least 1 line of context before and after when possible

Link format must be exactly:
`https://github.com/OWNER/REPO/blob/FULL_SHA/path/to/file.ext#L10-L15`

Requirements:
- full git sha only
- repository name must match the reviewed repo
- line format `#L[start]-L[end]`

### B. Machine-readable mode
Categorize findings as Critical, Important, or Suggestion. Output a structured review with specific file:line references and fix recommendations.

## Review priorities
1. correctness bugs
2. documented repo standards violations
3. spec mismatches
4. structural maintainability regressions
5. missed opportunities for dramatic simplification when a clear path is visible
6. architecture boundary problems
7. security and performance issues supported by the change
8. readability issues that materially affect comprehension

## Tone
Be direct, serious, and brief. Do not be rude. Do not soften major maintainability or correctness problems into mild suggestions. Do not treat a change as no-issue merely because behavior seems correct if it clearly makes the codebase structurally worse.

## Final checks
Before returning or commenting, verify:
- every required dedicated agent for this review type was run
- no required agent was merged, combined, substituted, skipped, or manually emulated
- the preflight required-agents checklist is fully satisfied
- every finding is tied to the reviewed change
- every finding has a concrete file reference
- every standards-based finding is explicitly supported by a standards file
- no excluded false positives are included
- if a plausible restructuring would delete substantial incidental complexity, call it out
- if a major maintainability problem is present, do not hide it behind minor wording
- output matches the requested mode exactly