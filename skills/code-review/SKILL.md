---
name: code-review
description: Strict review of a PR, diff, commit range, branch, staged/unstaged changes, or AI patch. Finds only high-confidence issues introduced or exposed by the reviewed change.
disable-model-invocation: true
---

# Code Review

Review only the requested change. Report only high-confidence, change-linked findings.

## Core rules

- Do not run the review yourself in the main thread. Spawning subagents preserves your context window from large diff files and runs deep specialist logic.
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
   Before continuing, ensure the following skills are activated or loaded:
   - `addy-code-review-and-quality`
   - `subagent-model-router`: delegate tasks to the most suitable subagents

2. **Lock target**
   - PR: review that PR.
   - Local: review staged, unstaged, or both exactly as requested.
   - Fixed point: review against the named branch, commit, or base.
   - If user says `review since X` and X is not fixed, ask exactly: `Review against what — a branch, a commit, or main?`. Then stop.

3. **Collect intake**
   - PR: follow `references/pr-protocol.md`.
   - Local: collect the requested `git diff --cached`, `git diff`, or both separately.
   - Fixed point: collect `git diff <target>...HEAD` and `git log <target>..HEAD --oneline`.

4. **Triage large changes**
   If the change exceeds 1000 changed lines or 15 files, follow `references/large-change-triage.md`.

5. **Gather coding standards**
   - Read relevant repo instructions, standards, ADRs, contribution docs, and configs from repo root and touched-path ancestors.
   - Prefer snippets over full files.
   - Skip standards enforced mechanically by tooling unless the change bypasses or weakens that tooling.
   - Common context files are listed in `references/standards-files.md`.

6. **Find spec**
   - Use PR metadata, linked issues, commits, user-supplied paths, or obvious files under `docs/`, `specs/`, `.scratch/`, `.agents/scratchpad/**`.
   - If none exists, record `no spec available` and skip spec compliance review.

7. **Review**
   Spawn parallel subagents using available catalog names:
   - `addy-code-reviewer`: correctness, regressions, edge cases, architecture boundaries
   - `addy-security-auditor`: vuln, unsafe data handling, auth/authz, injection, secrets, attack surface
   - `addy-test-engineer`: inadequate, misleading, or broken tests for changed behavior
   - `generalist`: quality review covering maintainability, standards, code smells, spec compliance if available, and PR-only checks if reviewing a PR

   Prompt the `generalist` with:
   - `references/maintainability-criteria.md`
   - `references/code-smells.md`
   - explicit repo standards only
   - spec, if available
   - `references/pr-protocol.md`, if reviewing a PR

   For all reviews, run the four required subagents unless the user explicitly asks for a lightweight review. For large changes, chunk input per `references/large-change-triage.md`.

8. **Each subagent result must include**
   - role
   - file and line
   - issue
   - why it is introduced, exposed, or made reachable by the change
   - evidence
   - practical impact
   - severity
   - specific fix
   - preliminary confidence

9. **Filter false positives with fast-tier subagents**
   - Apply `references/false-positive-rubric.md`.
   - Verify each finding against the exact diff hunk.
   - Keep only findings on changed lines, or unchanged lines directly reached/exposed by changed hunks with explicit evidence.
   - Drop findings that rely only on nearby unchanged context.
   - Keep only findings scoring 80+.
   - Assign final severity.

10. **Output**
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

- [ ] Prerequisite skills (`addy-code-review-and-quality` and `subagent-model-router`) were successfully activated.
- [ ] Target is fixed or clarified.
- [ ] PR eligibility was checked, if applicable.
- [ ] Relevant context and standards were reviewed.
- [ ] Spec review ran or `no spec available` was recorded.
- [ ] Required catalog subagents ran for correctness, security, tests, and general quality.
- [ ] Large-change triage ran if thresholds were exceeded.
- [ ] Every kept finding is change-linked and verified against an exact diff hunk.
- [ ] Standards findings cite explicit repo rules.
- [ ] False-positive score is 80+ for every kept finding.
- [ ] Findings cite code, standards, specs, or diff evidence as applicable.
- [ ] Output matches the requested mode.
