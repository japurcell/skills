---
name: code-review
description: Strict review of a PR, diff, commit range, branch, staged/unstaged changes, or AI patch. Finds only high-confidence issues introduced or exposed by the reviewed change.
disable-model-invocation: true
---

# Code Review

Review only the requested change. Report only high-confidence, change-linked findings.

## Core rules

- Use distinct subagents for required roles; do not merge roles.
- Do not run the review yourself in the main thread.
- Do not expand scope beyond the requested PR, diff, commit range, branch, or local changes.
- If the review target is unclear, ask one clarifying question and stop.
- Do not run builds, tests, linters, typechecks, benchmarks, or broad validation unless asked.
- Do not report unrelated pre-existing issues unless the change makes them reachable or worse.
- Do not report style preferences, speculation, generic test/doc requests, or issues tooling should catch.
- Standards findings require an explicit cited repo rule.
- Keep findings only if they score 80+ under `references/false-positive-rubric.md`.
- If a required skill, subagent, intake source, or reference file is unavailable, stop and explain.

## Workflow

1. **Setup**
   - Invoke the `addy-code-review-and-quality` skill.
   - Invoke the `subagent-model-router` skill and delegate tasks to the most suitable subagents.

2. **Lock target**
   - PR: review that PR.
   - Local: review staged, unstaged, or both exactly as requested.
   - Fixed point: review against the named branch, commit, or base.
   - If user says `review since X` and X is not fixed, ask exactly: `Review against what — a branch, a commit, or main?`. Then stop.

3. **Collect intake**
   - PR: follow `references/pr-protocol.md`.
   - Local: collect the requested `git diff --cached`, `git diff`, or both separately.
   - Fixed point: collect `git diff <target>...HEAD` and `git log <target>..HEAD --oneline`.

4. **Gather coding standards**
   - Read relevant repo instructions, standards, ADRs, contribution docs, and configs from repo root and touched-path ancestors - anything in the repo that documents how code should be written.
   - Prefer snippets over full files.
   - Common context files are listed in `references/standards-files.md`.

5. **Find spec**
   - Use PR metadata, linked issues, commits, user-supplied paths, or obvious files under `docs/`, `specs/`, `.scratch/`, `.agents/scratchpad/**`.
   - If none exists, record `no spec available` and skip spec compliance review.

6. **Review**
   Spawn distinct, parallel subagents for each required role:
   - `addy-code-reviewer`: correctness, regressions, edge cases, architecture boundaries
   - `addy-security-auditor`: vuln, unsafe data handling, auth/authz, injection, secrets, attack surface
   - `addy-test-engineer`: inadequate, misleading, or broken tests for changed behavior
   - `general`: maintainability review using `references/maintainability-criteria.md`
   - `general`: standards review using explicit repo rules
   - `general`: code-smell review using `references/code-smells.md`
   - `general`: spec compliance review, if a spec exists
   - `general`: PR-only checks from `references/pr-protocol.md`, if reviewing a PR

7. **Each subagent result must include**
   - role
   - file and line
   - issue
   - why it is introduced, exposed, or made reachable by the change
   - evidence
   - practical impact
   - severity
   - specific fix
   - preliminary confidence

8. **Filter false positives with fast-tier subagents**
   - Apply `references/false-positive-rubric.md`.
   - Keep only findings scoring 80+.
   - Assign final severity.

9. **Output**
   - Use the user’s requested mode.
   - For PR comment or machine-readable output, use `references/output-formats.md`.
   - Normal format:
     - severity
     - file/line
     - issue
     - impact
     - suggested fix
   - If no findings survive, say:
     `No change-linked issues were found.`

## Tone

Be brief, direct, and serious. Do not soften important correctness, security, or maintainability problems.

## Final checklist

- [ ] Target is fixed or clarified.
- [ ] PR eligibility was checked, if applicable.
- [ ] Relevant context and standards were reviewed.
- [ ] Spec review ran or `no spec available` was recorded.
- [ ] Required review passes stayed distinct.
- [ ] Every kept finding is change-linked and has concrete evidence.
- [ ] Standards findings cite explicit repo rules.
- [ ] Parallel review subagents were spawned for each required role.
- [ ] False-positive score is 80+ for every kept finding.
- [ ] Output matches the requested mode.
