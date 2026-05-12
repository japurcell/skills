---
name: create-plan
description: Build complete implementation plans from a feature spec using the plan template, producing phase artifacts and a readiness report. Use this whenever the user asks for implementation planning, architecture planning, research-before-build, or preparation for task breakdown (even if they do not explicitly say "create-plan").
argument-hint: "spec_file: .agents/scratchpad/<feature>/spec.md"
disable-model-invocation: true
---

# Create implementation plan

Turn a feature spec into implementation-ready planning artifacts that `/create-tasks` can consume directly.

## Input

- `spec_file` (optional): path to the spec file.

If `spec_file` is omitted, first reuse a spec path created or mentioned earlier in the session (for example from `create-spec` or `issue-to-spec`). Otherwise ask the user. If the resolved file is unreadable or lacks actionable requirements, stop with a blocking error.

## Workflow

1. **Load context**
   - Read `spec_file`.
   - Read the IMPL_PLAN template from [references/plan-template.md](references/plan-template.md).
   - Treat the directory containing `spec_file` as the feature workspace.
   - Write outputs there: `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/` when external interfaces are in scope.

2. **Draft `plan.md`**
   - Start from the template.
   - Fill the summary and Technical Context from the spec and repository.
   - Use `NEEDS CLARIFICATION` only for true unknowns that block confident implementation decisions.
   - Fill AGENTS.md checks by reading the relevant AGENTS/instruction files in scope.
   - Replace placeholder structure examples with real repository paths only.

3. **Run the pre-research gate**
   - If AGENTS.md checks reveal hard violations, stop and report the blocker.
   - Otherwise record a pre-research pass and continue.

4. **Create `research.md`**
   - Turn every `NEEDS CLARIFICATION`, major technology choice, integration, protocol, or contract standard into a concrete research question.
   - For every language, framework, library, platform, infrastructure service, or contract standard that affects the plan, check the latest official web documentation before finalizing decisions.
   - Treat official/vendor/framework docs as the primary source; use repository context only to adapt them.
   - Record each decision using this exact structure:
     - `Decision:`
     - `Rationale:`
     - `Official docs reviewed:` one bullet per cited official web source, with title and URL
     - `Version/context checked:`
     - `Alternatives considered:`
   - Propagate resolved research decisions back into Technical Context, contracts, quickstart commands, and risk notes.
   - Resolve each plan-critical unknown or mark it as an explicit follow-up/risk.
   - Do not treat local installs, cached docs, or copied references as proof of current guidance unless they were verified against official web docs during this run.
   - If required official docs are unavailable on the web, stop with a blocker instead of claiming current best practices.

5. **Create design artifacts**
   - Create `data-model.md` from entities, validation rules, relationships, and lifecycle/state transitions in the spec.
   - Create `contracts/` only when external interfaces are in scope, using the contract format that fits the project.
   - Create `quickstart.md` with this exact structure:
     - `# Quickstart: <feature name>`
     - `## Prerequisites`
     - `## 1. Implement`
     - `## 2. Validate`
     - `## 3. Rollout/Operate`
   - `Implement` and `Validate` must each include at least one concrete command and expected outcome. Anchor every section to real plan/research decisions; do not emit placeholders or a shallow checklist.
   - Update agent context only for net-new technology introduced by this plan, using `agents-md-refactor`.

6. **Run the post-design gate**
   - Re-check AGENTS.md constraints after design decisions are written.
   - Verify artifact completeness and internal consistency:
     - `quickstart.md` contains all required headings
     - `Implement` and `Validate` each include a concrete command and expected result
     - quickstart steps align with contracts and data model
     - notable constraints from `research.md` appear in the design artifacts
   - Verify the final report matches the exact output contract before returning.

7. **Return**
   - Stop after the planning artifacts are complete.
   - Return the readiness report using the exact contract below.

## Output contract

Return `ERROR` instead of a partial report if any required section is missing. Use this exact section order and labels:

1. `Plan path`: absolute path to `plan.md`
2. `Artifacts generated`: bullet list of generated files/directories
3. `Gate results`: include both `Pre-research` and `Post-design` results with PASS/FAIL and brief reasons
4. `Open risks`: unresolved items, or `none`
5. `Next command`: `/create-tasks` or one blocking remediation instruction

Always include all five sections, even when a section is empty. `Next command` must be a single actionable command or one blocking remediation step.

## Key rules

- Use absolute paths in reports and when writing output locations.
- Do not invent repository structure; read existing paths and align with current layout.
- Do not claim that a decision reflects latest/current best practices unless the relevant official documentation was checked during this run and captured in `research.md`.
- Prefer explicit decisions and trade-offs over vague recommendations.
- Keep artifacts implementation-oriented; avoid abstract prose with no engineering actionability.
