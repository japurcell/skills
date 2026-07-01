---
name: code-review
description: Strict scoped review of PRs, diffs, commits, branches, staged/unstaged changes, or AI patches.
disable-model-invocation: true
---

# Code Review

Review only the requested change scope. Report only change-linked issues that survive false-positive filtering.

## Hard Rules

- Use distinct subagents for required roles; do not merge roles.
- If intake, required role, or required protocol file is unavailable, stop and explain.
- Main agent must not read GitHub PR/issue pages directly; PR intake uses `gh` via fast subagents.
- Do not run builds, tests, linters, typechecks, benchmarks, or broad validation unless asked.
- Do not report unrelated or unchanged-line issues unless the change makes them reachable.

## Workflow

1. Invoke `subagent-model-router` and `addy-code-review-and-quality`. Create todos.

2. Lock target:
   - PR: review that PR.
   - Local: review staged, unstaged, or both exactly as requested.
   - Fixed point: review against provided branch/commit/base.
   - If user says `review since X` and X is not fixed, ask exactly:
     `Review against what — a branch, a commit, or main?`
     Then stop.

3. Intake:
   - PR: use `gh` via fast subagents for status, labels/body conventions, title/body, base/head, files, linked issues/specs, compact issue summaries.
   - Stop if PR is closed, draft, or explicitly review-not-needed.
   - Local: collect `git diff --cached`, `git diff`, or both separately.
   - Fixed point: collect `git diff <target>...HEAD` and `git log <target>..HEAD --oneline`.

4. Spawn a subagent to gather only relevant context:
   - repo/global instructions, standards, style, ADRs, contribution docs, formatter/linter/test/build/language configs from repo root and touched-path ancestors.
   - Include common files:
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
   - Summarize large files; prefer relevant snippets over full documents. Standards findings require exact file/rule citation.
   - Skip standards mechanically enforced by tooling unless the change bypasses or weakens that tooling.

5. Find spec:
   - PR metadata/issues/commits
   - user-supplied path
   - obvious files under `docs/`, `specs/`, `.scratch/`, `.agents/scratchpad/**`
   - otherwise record `no spec available` and skip spec review.

6. Run distinct review subagents in parallel:
   - `addy-code-reviewer`: correctness, regressions, edge cases, architecture boundaries.
   - `addy-security-auditor`: vuln, unsafe data handling, auth/authz, injection, secrets, attack surface.
   - `addy-test-engineer`: inadequate, misleading, or broken tests for changed behavior.
   - Maintainability reviewer using `MAINTAINABILITY_CRITERIA.md`.
   - Standards reviewer for explicit documented repo rules only.
   - If spec exists: spec compliance reviewer.
   - If PR: history reviewer, related-PR reviewer, code-comment reviewer.

7. Each subagent returns only:
   - role
   - file/line
   - issue
   - change linkage
   - evidence
   - impact
   - severity
   - suggested fix
   - preliminary confidence

8. Filter false positives with fast subagents:
   - Apply `FALSE_POSITIVE_RUBRIC.md`.
   - Assign final false-positive score and final severity.
   - Keep only findings scoring `80+`.
   - Drop speculation, pedantry, generic requests for tests/docs/security review, and issues tooling should trivially catch.

9. Output:
   - Use requested mode.
   - PR-comment and machine-readable modes follow `OUTPUT_FORMATS.md`.
   - Before `gh pr comment`, re-check PR eligibility.
   - Normal format:
     - severity
     - file/line
     - issue
     - impact
     - suggested fix
   - If none survive, say: `No change-linked issues were found.`

### Tone

Be brief, direct, and serious. Do not hide major correctness or maintainability problems behind soft wording.

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
