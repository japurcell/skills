---
name: create-plan
description: Build complete implementation plans from a feature spec using the plan template, producing phase artifacts and a readiness report. Use this whenever the user asks for implementation planning, architecture planning, research-before-build, or preparation for task breakdown (even if they do not explicitly say "create-plan").
disable-model-invocation: true
---

# Create implementation plan

Generate a plan package that moves a feature from spec text to implementation-ready design artifacts.
The goal is to reduce ambiguity before coding and produce outputs that can be consumed directly by `/create-tasks`.

## Inputs

You receive these parameters in your prompt:

- **spec_file** (required): The path to the spec file that contains the requirements.

If `spec_file` is missing, unreadable, or does not contain actionable requirements, stop and return a blocking error.

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
   - Resolve each unknown with an explicit decision.
   - Record each decision in this format:
     - Decision
     - Rationale
     - Alternatives considered
   - Ensure every Technical Context unknown is resolved or marked with a justified follow-up.

5. **Phase 1: Design outputs**
   - Create `data-model.md` from entities, invariants, relationships, and lifecycle/state transitions in `spec_file`.
   - Create `contracts/` only when external interfaces are part of scope.
   - Create `quickstart.md` with implementation and validation flow for developers.
   - Update agent context only for net-new technology introduced by this plan.

6. **Run post-design gate**
   - Re-check AGENTS.md constraints after design choices are written.
   - Verify artifact completeness and internal consistency across all outputs.

7. **Stop and report**
   - End after planning artifacts are complete.
   - Report output file paths, gate results, and readiness for `/create-tasks`.

## Output contract

Return a concise status report using this exact section structure:

1. `Plan path`: absolute path to `plan.md`
2. `Artifacts generated`: bullet list of generated files/directories
3. `Gate results`: pass/fail with brief reasons
4. `Open risks`: unresolved items, if any
5. `Next command`: `/create-tasks` or a blocking remediation step

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**
   - For each `NEEDS CLARIFICATION` item, create one research task.
   - For each major dependency choice, create one best-practice check.
   - For each integration, create one implementation pattern check.

2. **Generate and dispatch research agents (or equivalent direct research)**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

4. **Close the loop back to plan.md**
   - Update Technical Context in `plan.md` so resolved unknowns are no longer marked unclear.

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
   - `quickstart.md` steps must align with contracts and data model.
   - Any notable constraint in `research.md` must appear in plan/design artifacts.

**Output**: `data-model.md`, optional `contracts/*`, `quickstart.md`, updated agent context

## Key rules

- Use absolute paths in reports and when writing output locations.
- Return `ERROR` on gate failures that are not justified.
- Do not invent repository structure; read existing paths and align with current layout.
- Prefer explicit trade-offs over vague recommendations.
- Keep artifacts implementation-oriented; avoid abstract prose with no engineering actionability.
