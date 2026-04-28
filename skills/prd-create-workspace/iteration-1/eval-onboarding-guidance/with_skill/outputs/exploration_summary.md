# Codebase Exploration Summary

The `prd-create` skill requires parallel `code-explorer` agents with complementary lenses. Four agents were launched in read-only mode. All found the same major constraint: this repository is a Copilot skills/agents/evals repository, not the target product application for workspace onboarding. No application workspace creation flow, invite model, integration catalog, onboarding UI, persistence schema, or analytics implementation was available.

## Agent lens 1: Similar features and user flows

**Focus:** Onboarding, workspace creation, team invitations, integrations, first-run setup, PRD/eval workflows, and similar user-flow patterns.

**Key findings:**

- The repository publishes Copilot skills, agents, references, hooks, and helper scripts rather than a SaaS product surface.
- `workspace` directories in this repository are generated skill/eval workspaces, not customer workspaces.
- The exact onboarding prompt appears in the `prd-create` eval suite, confirming this is a benchmark scenario for the skill.
- The PRD workflow requires exploration, research, one-question-at-a-time interviewing, durable citations, and no implementation.
- Existing benchmark output for the same onboarding scenario is useful as a non-authoritative fixture but should not be treated as product source.

**Existing patterns/conventions to preserve:**

- Do PRD work before implementation.
- Explore before asking product questions.
- Keep final PRD issue bodies durable by avoiding file paths and snippets.
- Treat generated workspace outputs as benchmark fixtures, not maintained source.

**Key files with reasons:**

1. `skills/prd-create/SKILL.md` — Defines the authoritative PRD workflow, template, citation rules, interview process, quality gate, and normal GitHub issue filing behavior.
2. `skills/prd-create/evals/evals.json` — Contains the exact onboarding benchmark prompt and expectations.
3. `skills/coding-task-workflow/SKILL.md` — Shows durable GitHub-native workflow tracking and multi-phase gates that inform resumable onboarding thinking.
4. `skills/coding-task-workflow/references/issue-hierarchy.md` — Provides issue/subissue conventions relevant to how PRD issues coexist with implementation planning.
5. `skills/coding-task-workflow/references/artifact-schema.md` — Defines durable issue/comment fields that may influence downstream implementation workflows.
6. `skills/create-spec/SKILL.md` — Shows adjacent requirements-writing practices, including measurable requirements and assumptions.
7. `references/accessibility-checklist.md` — Applies to guided onboarding controls, progress, forms, and dynamic states.
8. `references/security-checklist.md` — Applies to invitations, roles, integration credentials, input validation, and sensitive data handling.
9. `references/testing-patterns.md` — Provides behavior-focused component, API/integration, and E2E testing guidance.
10. `README.md` — Establishes repository purpose, layout, workspace artifact treatment, and validation expectations.

**Relevant tests or test patterns:**

- `skills/prd-create/evals/evals.json` includes this exact PRD case and expects exploration, research, dependent interviewing, durable citations, and out-of-scope clarity.
- Shared testing references favor user-visible behavior, API/integration tests for auth and validation, and E2E coverage for complete user journeys.

**Open gaps:**

- No target product repository, workspace domain model, invite states, integration catalog, onboarding UI, persistence schema, or analytics taxonomy was found.

## Agent lens 2: Architecture boundaries, data flow, and extension points

**Focus:** Architecture boundaries, data flow, extension points, and whether this repository contains application surfaces for workspace onboarding.

**Key findings:**

- The repository architecture is a skill/agent workflow architecture, not a customer-facing app architecture.
- `prd-create` prescribes a sequence: frame request, explore, identify gaps, research, interview, write PRD, quality gate, submit issue.
- Planning guidance emphasizes read-only analysis before implementation.
- Multi-step workflow patterns in the repository use phases, gates, durable artifacts, and resume points.
- Installation scripts separate repository source assets from installed runtime copies and skip generated workspace directories.
- No maintained user/workspace/integration domain model was found.

**Existing patterns/conventions to preserve:**

- Keep PRD generation separate from implementation.
- Use evidence-backed implementation decisions.
- Ask product questions one at a time and in dependency order.
- Use explicit gates and checkpoints for multi-step flows.
- Prefer vertical slices that deliver user-visible value.

**Key files with reasons:**

1. `README.md` — Defines the repository as Copilot skills/agents assets and documents validation and workspace conventions.
2. `AGENTS.md` — Captures core repository constraints: no single test runner, edit source first, and ignore generated workspace outputs during audits.
3. `skills/prd-create/SKILL.md` — Central PRD workflow and evidence/citation requirements.
4. `skills/prd-create/evals/evals.json` — Exact onboarding eval and expectations.
5. `skills/coding-task-workflow/SKILL.md` — Deterministic multi-phase workflow model and durable issue tracking.
6. `skills/coding-task-workflow/references/workflow.md` — Detailed gates for exploration, research, clarification, planning, and task graph creation.
7. `skills/addy-planning-and-task-breakdown/SKILL.md` — Read-only planning, dependency graphing, vertical slicing, and checkpoints.
8. `scripts/copilot-install.sh` — Demonstrates source-to-installed-assets boundaries and exclusion of workspace artifacts.
9. `docs/agent-guides/authoring.md` — Defines authoring conventions for skills, agents, resources, scripts, and workspace outputs.
10. `references/testing-patterns.md` — Testing hierarchy and behavior-focused testing guidance.

**Relevant tests or test patterns:**

- Skill frontmatter validation and packaging validation provide structural testing patterns.
- Shell-script tests use local fixtures and filesystem effects to verify state transitions.
- General testing guidance favors the lowest sufficient test level and behavior-focused assertions.

**Open gaps:**

- The repository cannot answer what `workspace` means in the product domain, who owns onboarding state, which integrations exist, or what persistence/resume behavior the application supports.

## Agent lens 3: API contracts, persistence, schema, and integration patterns

**Focus:** API contracts, persistence, schema, integration patterns, external service configuration, GitHub issue workflows, and workspace/team/integration domain models.

**Key findings:**

- No API layer, database migrations, application schemas, workspace/team models, invitation endpoints, OAuth implementation, webhook handling, or integration settings surfaces were found.
- External integrations in this repository are tooling-oriented, especially GitHub CLI usage and installer/importer scripts, not product integration flows.
- The PRD skill normally infers the repository from git remote and creates a GitHub issue, but this offline eval prohibits real issue creation.
- Issue creation conventions exist for PRDs but should be represented only as an intended command in this run.

**Existing patterns/conventions to preserve:**

- Do not create issues, branches, commits, PRs, or source changes during this offline benchmark.
- Use `gh issue create` with a body file only as the intended filing command.
- Treat external integrations as scope-sensitive and security-sensitive.
- Use current authoritative research when application patterns are unavailable.

**Key files with reasons:**

1. `skills/prd-create/SKILL.md` — States normal issue title/body behavior and fallback handling for failed issue creation.
2. `skills/prd-create/evals/evals.json` — Defines the onboarding PRD scenario and benchmark expectations.
3. `scripts/copilot-install.sh` — Shows external file-copy/install boundaries and workspace exclusion logic.
4. `scripts/addy-install.sh` — Shows external source sync/import behavior and environment override patterns.
5. `skills/coding-task-workflow/references/issue-hierarchy.md` — Documents structured GitHub issue workflow conventions.
6. `skills/coding-task-workflow/references/artifact-schema.md` — Defines durable structured issue/comment artifact fields.
7. `references/security-checklist.md` — Provides authorization, validation, secret-handling, and external integration risk guidance.
8. `skills/addy-security-and-hardening/SKILL.md` — Flags external integrations, sensitive data, PII, auth, and elevated permissions as security-sensitive.
9. `README.md` — Confirms repository scope and lack of product application structure.
10. `AGENTS.md` — Provides repository operating constraints and reminds agents to ignore output fixtures during normal audits.

**Relevant tests or test patterns:**

- Existing shell tests verify installer/importer behavior through boundary effects.
- Security checklist suggests authorization, ownership, input validation, and sensitive-data tests for invite/integration operations.

**Open gaps:**

- No product-specific API contracts, persistence model, integration credentials model, invite expiry behavior, seat/billing constraints, or OAuth provider list is available.

## Agent lens 4: Tests, accessibility, security, privacy, and operational constraints

**Focus:** Tests, fixtures, accessibility, security, privacy, operational constraints, evaluation criteria, and validation commands.

**Key findings:**

- The current PRD skill has a strict template and quality gate.
- The exact eval expects official UX/accessibility research, dependency-aware interviewing, durable citations, explicit out-of-scope boundaries, and normal issue URL reporting.
- Accessibility guidance maps directly to onboarding checklist controls, invite forms, progress updates, and error handling.
- Security guidance is material because invites involve PII/permissions and integrations may involve OAuth, scopes, callbacks, tokens, and external APIs.
- Testing guidance emphasizes external behavior, accessible component queries, API/integration behavior, E2E journeys, and avoiding implementation-detail assertions.
- Repository validation is targeted; there is no single repo-wide test runner.

**Existing patterns/conventions to preserve:**

- PRD-first, no implementation.
- Explore and research before decisions.
- Interview one decision at a time.
- Make out-of-scope items explicit.
- Prefer accessibility-by-default requirements.
- Treat invitations and integrations as security/privacy-sensitive.
- Validate with narrow, relevant checks.

**Key files with reasons:**

1. `skills/prd-create/SKILL.md` — Required PRD structure, quality gate, and issue filing behavior.
2. `skills/prd-create/evals/evals.json` — Exact onboarding eval expectations.
3. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/eval_metadata.json` — Confirms this onboarding scenario exists as an offline eval and has no automated assertions.
4. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/without_skill/outputs/issue_body.md` — Existing baseline output fixture for comparison, not maintained product source.
5. `references/accessibility-checklist.md` — Keyboard, labels, errors, status announcements, focus, and empty-state guidance relevant to onboarding.
6. `skills/fixing-accessibility/SKILL.md` — Accessibility workflow guidance for controls, dialogs, validation, hidden content, and icon-only buttons.
7. `references/security-checklist.md` — Authorization, validation, data protection, and production-safe error handling.
8. `skills/addy-security-and-hardening/SKILL.md` — Security hardening rules for integrations, sensitive data, PII, auth changes, and elevated permissions.
9. `references/testing-patterns.md` — Behavior-level component, API/integration, and E2E testing patterns.
10. `docs/agent-guides/validation.md` — Documents targeted validation commands and no monolithic repo test command.

**Relevant tests or test patterns:**

- PRD eval expectations are qualitative for this scenario.
- Component tests should use accessible roles/labels.
- API/integration tests should cover success, validation, and authorization failures.
- E2E tests should verify the complete onboarding journey from workspace creation through completion/dismissal/resume.
- Accessibility validation should combine automated checks with keyboard and screen-reader review.

**Open gaps:**

- The target product/application repository, supported integrations, permission model, analytics policy, and rollout infrastructure are not available in this repository.

## Consolidated exploration conclusion

This PRD must be product-agnostic enough to remain accurate without target application source, but specific enough to guide a future implementation. The final issue body therefore cites durable repository patterns only at the pattern level and relies on official research for onboarding UX, accessibility, OAuth/security, and analytics decisions. Product-specific work remains a follow-up dependency before implementation: identify the target application repository, existing invite flow, existing integration entry points, permissions model, analytics taxonomy, and the first useful setup action for the initial release.
