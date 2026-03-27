---
name: issue-to-spec
description: Convert a GitHub issue into a planning-ready spec and requirements checklist by collecting issue context (including comments), extracting problem/constraints, and delegating spec drafting to create-spec. Use this whenever a user asks to turn an issue/ticket into a spec, PRD-style requirements, or planning input, even if they do not explicitly say "spec".
disable-model-invocation: true
---

# Issue to spec

## Inputs

You receive these parameters in your prompt:

- **github_issue** (required): The Github issue number to read and build a spec for.
- **repo** (optional): `owner/repo` to disambiguate issue lookup when current git remote is not the target repository.

## Goal

Produce a high-quality feature spec and checklist from the issue by:

1. Collecting complete issue context (title, body, labels, comments, acceptance notes).
2. Distilling requirements, constraints, and open questions.
3. Passing a clean, structured brief to `create-spec`.
4. Reporting where outputs were written and any unresolved ambiguities.

## Workflow

1. Validate inputs.
2. Retrieve the issue using `gh` (title, body, labels, assignees, milestone, state, and comments).
3. Normalize and summarize issue context into a concise feature brief.
4. Run `create-spec` with that brief as input.
5. Return output paths and readiness status.

## Step-by-step Instructions

1. Validate `github_issue`.
   - If missing, stop and ask for issue number.
   - If non-numeric, fail with a clear message.

2. Retrieve issue content with comments.
   - If `repo` is provided, run commands against that repository.
   - Prefer machine-readable output where possible (for stable parsing).
   - Ensure all comments are included because acceptance criteria often live there.

3. Build a feature brief with these sections:
   - Issue metadata: number, title, labels, milestone, state.
   - Problem statement: what is broken or missing.
   - Desired outcome: user/business value.
   - Requirements signals: explicit requirements from issue text/comments.
   - Constraints: non-functional limits, dependencies, roll-out notes.
   - Open questions: only high-impact uncertainties.

4. Quality-pass the brief before handoff.
   - Keep implementation choices out unless the issue explicitly mandates them.
   - Resolve obvious ambiguity with documented assumptions.
   - Preserve critical quoted constraints verbatim from the issue.

5. Invoke `create-spec` and pass the full brief as arguments.
   - Do not pass raw issue text without structuring; the brief should reduce noise.
   - Include source traceability markers like `Issue #<n>` and key comment references.

6. Return a concise completion report.
   - Include issue reference and repository.
   - Include generated feature short name from `create-spec`.
   - Include spec and checklist file paths.
   - Include readiness for `/create-plan`.
   - Include unresolved blockers (if any).

## Output Contract

Your final response must include:

- `issue`: `<repo>#<number>`
- `feature_name`: short name returned by `create-spec`
- `spec_path`: path to generated spec
- `checklist_path`: path to generated requirements checklist
- `readiness`: `ready` or `needs-clarification`
- `notes`: short bullets for assumptions/blockers

## Failure Handling

- If `gh` cannot access the issue (auth, permissions, not found), stop and report the exact command failure.
- If issue exists but content is insufficient, still proceed with best-effort assumptions and clearly mark assumptions in the brief.
- If `create-spec` fails validation after retries, return partial outputs plus the specific failing checklist items.

### Failure response template (gh access failure)

When issue retrieval fails, use this exact shape and do not continue to spec generation:

- `issue`: `<repo>#<number>`
- `readiness`: `needs-clarification`
- `notes`:
  - attempted gh command
  - exact gh stderr/error text
  - one-line next action required from user (auth/repo access/correct repo)

On this failure path:

- Do not claim `ready`.
- Do not use the phrase "planning-ready" anywhere in the final response.
- Do not invent `spec_path`, `checklist_path`, or `feature_name` values.

## Why This Works

Structuring issue data before spec generation reduces prompt noise, improves requirement extraction quality, and creates more stable outputs across similar issues.
