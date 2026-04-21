---
name: create-plan
description: Build complete implementation plans from a feature spec using the plan template, producing phase artifacts and a readiness report. Use this whenever the user asks for implementation planning, architecture planning, research-before-build, or preparation for task breakdown (even if they do not explicitly say "create-plan").
argument-hint: "spec_file: .agents/scratchpad/<feature>/spec.md"
---

# Create implementation plan

Generate a plan package that moves a feature from spec text to implementation-ready design artifacts.
The goal is to reduce ambiguity before coding and produce outputs that can be consumed directly by `/create-tasks`.

## Inputs

You receive these parameters in your prompt:

- **spec_file** (optional): The path to the spec file that contains the requirements.

### Inferring spec_file

When `spec_file` is not explicitly provided, resolve it from context before proceeding:

1. **Conversation context**: Check whether a spec file was recently created or mentioned in the current session (e.g., output from `create-spec` or `issue-to-spec`). Use that path if found.
2. **Ask the user**: If no candidate is found after the steps above, ask which spec file to use.

If the resolved file is unreadable or does not contain actionable requirements, stop and return a blocking error.

## Steps

1. **Load context**
   - Read `spec_file`.
   - Load IMPL_PLAN template from [references/plan-template.md](references/plan-template.md).
   - Determine the feature workspace directory as the directory containing `spec_file`.
   - Set these output paths:
     - `plan.md`
     - `research.md`
     - `data-model.md`
     - `quickstart.md`
     - `contracts/` (if applicable)

2. **Draft plan.md from template**
   - Fill template headers and summary from `spec_file`.
   - Fill Technical Context fields with concrete values when known.
   - Use `NEEDS CLARIFICATION` only for true unknowns that block confident implementation choices.
   - Fill AGENTS.md checks by reading relevant AGENTS/instruction files in scope.
   - Fill Project Structure with real repository paths; remove unused placeholder options.

3. **Run pre-research gate**
   - If AGENTS.md checks reveal hard violations, stop and report with rationale.
   - Otherwise continue to Phase 0.

4. **Phase 0: Research (research.md)**
    - Convert each `NEEDS CLARIFICATION` item into a concrete research question.
    - For every external language, framework, library, platform, infrastructure service, protocol, or contract standard that influences Technical Context or design choices, check the latest official documentation available on the web before finalizing the decision.
    - Treat official/vendor/framework documentation as the primary source for technical context and best-practice guidance; use repository context and secondary sources only to adapt those recommendations to the project.
    - Whenever you reference official documentation in a decision, rationale, trade-off, risk, or best-practice claim, cite the latest official source retrieved from the web during this run.
    - Resolve each unknown with an explicit decision.
    - Record each decision in this format:
      - Decision
      - Rationale
      - Official docs reviewed
      - Version/context checked
      - Alternatives considered
    - Ensure every Technical Context unknown is resolved or marked with a justified follow-up.
    - Do not treat locally installed docs, cached references, or whatever happens to be present in the local environment as sufficient proof of current best practices unless they are verified against the latest official web documentation during this run and cited where referenced.
    - If plan-critical official documentation cannot be reached on the web, stop and report a blocker instead of claiming the outcome reflects latest best practices.

5. **Phase 1: Design outputs**
   - Create `data-model.md` from entities, invariants, relationships, and lifecycle/state transitions in `spec_file`.
   - Create `contracts/` only when external interfaces are part of scope.
   - Create `quickstart.md` with the mandatory structure below; do not emit a placeholder or shallow checklist.
     - `# Quickstart: <feature name>`
     - `## Prerequisites`
     - `## 1. Implement`
     - `## 2. Validate`
     - `## 3. Rollout/Operate`
   - Quickstart depth requirements:
     - Include at least one concrete command in `Implement` and at least one in `Validate`.
     - Include expected outcomes for each command (what success looks like).
     - Map each section back to plan/research decisions so the flow is executable, not generic.
   - Update agent context only for net-new technology introduced by this plan.

6. **Run post-design gate**
   - Re-check AGENTS.md constraints after design choices are written.
   - Verify artifact completeness and internal consistency across all outputs.
   - Verify output report contract conformance before returning: section names and order must match exactly.

7. **Stop and report**
   - End after planning artifacts are complete.
   - Report output file paths, gate results, and readiness for `/create-tasks`.

## Output contract

Return a concise status report using this exact section structure and order. If any required section is missing, return `ERROR` instead of a partial report.

1. `Plan path`: absolute path to `plan.md`
2. `Artifacts generated`: bullet list of generated files/directories
3. `Gate results`: pass/fail with brief reasons
4. `Open risks`: unresolved items, if any
5. `Next command`: `/create-tasks` or a blocking remediation step

Formatting rules for this report:

- Use the section labels exactly as written above.
- Include all 5 sections even when content is empty (`Open risks: none`).
- `Next command` must be one actionable command or one explicit blocking remediation instruction.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**
    - For each `NEEDS CLARIFICATION` item, create one research task.
    - For each major dependency choice, create one best-practice check.
    - For each integration, create one implementation pattern check.
    - Build an explicit list of technologies, standards, and services from the spec/repository context that require an official-documentation pass.

2. **Generate and dispatch research agents (or equivalent direct research)**:

    ```text
    For each unknown in Technical Context:
      Task: "Research {unknown} for {feature context}. Check the latest official documentation on the web for every relevant technology first, cite the official web sources you rely on, then summarize current best-practice implications."
    For each technology choice:
      Task: "Check the latest official documentation on the web for {tech}, cite the official web sources you rely on, and identify current best practices for {domain}"
    ```

    - When researching directly instead of dispatching agents, follow the same documentation-first workflow and fetch the official sources from the web.
    - Prefer official docs that match the version already used in the repository or the version most appropriate for the proposed implementation.
    - Do not rely on local environment artifacts alone (installed packages, vendored docs, copied references, cached files) as the source of truth for "latest" guidance.
    - Every referenced official-doc claim must map to an explicit citation in `Official docs reviewed`; do not mention official guidance without a corresponding cited web source.
    - If official web docs are unavailable, capture that as a blocker or explicit risk; do not present uncited guidance as current best practice.

3. **Consolidate findings** in `research.md` using format:
    - Decision: [what was chosen]
    - Rationale: [why chosen]
    - Official docs reviewed: [one bullet per cited official web source, with doc title + URL]
    - Version/context checked: [version, release, or current-doc context that informed the decision]
    - Alternatives considered: [what else evaluated]

4. **Close the loop back to plan.md**
    - Update Technical Context in `plan.md` so resolved unknowns are no longer marked unclear.
    - Propagate version-specific or best-practice findings from official docs into Technical Context, contracts, quickstart commands, and any notable constraints/risk notes, while keeping the underlying web citations in `research.md`.

**Output**: `research.md` with all important unknowns resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from spec_file** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

3. **Agent context update**:
   - Add only new technology from current plan using the `agents-md-refactor` skill
   - Preserve manual additions between markers

4. **Consistency check**:
   - Quickstart depth gate:
     - Confirm all 5 required quickstart headings exist.
     - Confirm `Implement` and `Validate` each include at least one concrete command and expected result.
     - Fail this gate if quickstart is missing, skeletal, or not anchored to this feature.
   - `quickstart.md` steps must align with contracts and data model.
   - Any notable constraint in `research.md` must appear in plan/design artifacts.

**Output**: `data-model.md`, optional `contracts/*`, `quickstart.md`, updated agent context

## Key rules

- Use absolute paths in reports and when writing output locations.
- Return `ERROR` on gate failures that are not justified.
- Do not invent repository structure; read existing paths and align with current layout.
- Do not claim that a decision reflects latest/current best practices unless the relevant official documentation was checked during this run and captured in `research.md`.
- Prefer explicit trade-offs over vague recommendations.
- Keep artifacts implementation-oriented; avoid abstract prose with no engineering actionability.
