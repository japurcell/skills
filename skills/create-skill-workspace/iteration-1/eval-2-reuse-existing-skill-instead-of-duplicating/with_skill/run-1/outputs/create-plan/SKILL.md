---
name: create-plan
description: Turn a feature spec into concrete implementation-planning artifacts — `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/` when needed — by reading the repo's planning conventions and returning a strict readiness report for `/create-tasks`. Use this whenever the user asks for `plan.md`, research notes, architecture or implementation planning, design artifacts before coding, or wants a spec made ready for task breakdown, even if they do not explicitly say "create-plan".
---

# Create implementation plan

## Overview

Turn a feature spec into implementation-ready planning artifacts that `/create-tasks` can consume directly. Read the spec, the local planning template, and the in-scope AGENTS or instruction files first; then write concrete docs in the spec workspace instead of returning a vague planning summary.

## When to Use

- The user already has a spec file and wants `plan.md`
- The user asks for implementation planning, architecture planning, research before building, or design artifacts before code
- The user wants `research.md`, `data-model.md`, `quickstart.md`, contracts, or a plan that is ready for task breakdown
- The user asks to read repo planning conventions and turn a spec into concrete next-step docs
- The user wants clear validation guidance and a strict planning handoff
- Not for drafting the spec itself from a vague request; use `create-spec` or `issue-to-spec`
- Not for breaking an existing plan into `tasks.md`; use `create-tasks`

## Workflow

1. **Resolve the spec and workspace**
   - Use `spec_file` if provided.
   - If `spec_file` is omitted, reuse a spec path created or mentioned earlier in the session, such as output from `create-spec` or `issue-to-spec`.
   - If the resolved file is unreadable or lacks actionable requirements, stop with `ERROR`.
   - Treat the directory containing `spec_file` as the feature workspace.

2. **Load planning conventions before drafting**
   - Read `spec_file`.
   - Read [references/plan-template.md](references/plan-template.md).
   - Read the relevant AGENTS or instruction files in scope and capture any constraints that affect planning output.
   - Inspect the real repository layout before naming paths. Do not invent directories or carry placeholder trees into the final plan.

3. **Draft `plan.md`**
   - Start from the template structure.
   - Fill `Summary`, `Technical Context`, `AGENTS.md Check`, `Project Structure`, and other required sections with concrete repository details.
   - Use `NEEDS CLARIFICATION` only for true blockers that prevent confident planning decisions.
   - Replace placeholder structure examples with real repository paths only.

4. **Create `research.md`**
   - Turn every blocking unknown, major technology choice, external integration, protocol, or contract standard into a research question.
   - For every language, framework, library, platform, infrastructure service, or standard that materially affects the plan, verify current guidance in official web docs before finalizing decisions.
   - Record each decision using this exact structure:
     - `Decision:`
     - `Rationale:`
     - `Official docs reviewed:` one bullet per cited official web source with title and URL
     - `Version/context checked:`
     - `Alternatives considered:`
   - If required official docs are unavailable, stop with a blocker instead of claiming current best practice.

5. **Create design artifacts**
   - Write `data-model.md` from entities, validation rules, relationships, and lifecycle or state transitions in the spec.
   - Create `contracts/` only when external interfaces are in scope.
   - Write `quickstart.md` with this exact structure:
     - `# Quickstart: <feature name>`
     - `## Prerequisites`
     - `## 1. Implement`
     - `## 2. Validate`
     - `## 3. Rollout/Operate`
   - `Implement` and `Validate` must each include at least one concrete command plus the expected outcome. Prefer the narrowest repo-specific validation guidance over vague phrases like "run the usual tests."

6. **Run gates and consistency checks**
   - Record a `Pre-research` gate result after the first AGENTS or instructions review.
   - Re-check constraints after design decisions and record a `Post-design` result.
   - Verify artifact completeness and internal consistency:
     - `plan.md` uses the template sections with concrete content
     - `research.md` decisions are reflected back into the plan and quickstart
     - `quickstart.md` contains all required headings
     - `Implement` and `Validate` each include a concrete command and expected result
     - contracts and data model align with the plan

7. **Return the strict readiness report**
   - Stop after the planning artifacts are complete.
   - Return `ERROR` instead of a partial report if any required section is missing.
   - Use this exact section order and labels:
     1. `Plan path`
     2. `Artifacts generated`
     3. `Gate results`
     4. `Open risks`
     5. `Next command`
   - `Next command` must be a single actionable command: `/create-tasks` or one blocking remediation step.

## Specific Techniques

### Output discipline

- Write artifacts into the same workspace as the spec: `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/` only when needed.
- Keep the final response tight and structured. Do not substitute a narrative summary for the required output contract.
- Use absolute paths in the report and when naming written artifacts.

### Validation guidance

- Make the `Validate` section concrete. Name the exact narrowest command or commands that fit the repository and note the expected outcome.
- If validation cannot yet run, say what blocks it; do not hide the gap behind generic language like "verify everything works."

### Planning conventions

- Planning output must reflect the repository's real structure, AGENTS guidance, and current docs, not a generic template copy.
- When the repository already has a downstream planning step, optimize for that handoff. Here, the target is `/create-tasks`.

### Blocking behavior

- If the spec is missing, unreadable, or too thin to plan against, stop with a blocking error.
- If official documentation is required to support a decision and cannot be verified, stop instead of guessing.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "This sounds like a new `plan-maker` skill." | The repository already has `create-plan`, which covers spec-to-plan artifacts and `/create-tasks` handoff. Tighten that skill instead of creating a duplicate. |
| "I can just summarize what should happen." | The user asked for concrete planning artifacts. Write the files, not just a prose recap. |
| "I'll leave the template paths as examples." | Placeholder paths make the plan unusable for implementation and task breakdown. Replace them with real repository paths. |
| "Quickstart can say 'run the usual tests'." | Vague validation guidance is exactly what makes planning outputs unreliable. Name concrete commands and expected results. |

## Red Flags

- The response suggests creating a brand-new planning skill when the workflow already matches `create-plan`.
- The final answer omits one of the required artifacts or the 5-section readiness report.
- `quickstart.md` lacks concrete commands and expected outcomes.
- The plan invents repo structure instead of reading real paths.
- Research claims "current best practice" without citing official docs.

## Verification

After completing the workflow, confirm:

- [ ] The request was handled as a `create-plan` run, not a duplicate skill proposal.
- [ ] `spec_file`, the plan template, and relevant AGENTS or instruction files were read before drafting.
- [ ] `plan.md`, `research.md`, `data-model.md`, and `quickstart.md` were written in the spec workspace, with `contracts/` only when in scope.
- [ ] `research.md` records official docs reviewed and version or context checked for plan-shaping decisions.
- [ ] `quickstart.md` includes `Prerequisites`, `1. Implement`, `2. Validate`, and `3. Rollout/Operate`, with concrete commands and expected outcomes.
- [ ] The final response uses exactly `Plan path`, `Artifacts generated`, `Gate results`, `Open risks`, and `Next command`.
