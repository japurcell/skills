# Codebase Exploration Summary

## Overall finding

The available repository is not the target application for saved searches and email alerts. It contains Copilot skills, agents, references, hooks, installer scripts, and eval fixtures. No maintained product search UI, account area, user model, notification preferences, database schema, scheduler, background worker, or email provider integration was found. The PRD therefore uses codebase exploration primarily to document this gap and relies on official research plus simulated user decisions for implementation requirements.

## Code-explorer agent: Similar features and user flows

**Lens:** Similar features and user flows, including search-like workflows, account management, alert/notification-like flows, issue/PRD outputs, and eval patterns.

**Key findings:**
- No product search, account, saved-search, or user email alert flows exist in the repository.
- The exact saved-search/email-alert prompt exists as an eval fixture for the PRD skill, confirming this is a workflow benchmark rather than an implemented app feature.
- The repository’s relevant user-flow pattern is PRD generation: explore, research, interview, produce a GitHub issue body, and avoid implementation.
- Generated workspace outputs are not maintained source and should not be treated as app prior art.

**Key files with reasons:**
1. `README.md` — Establishes the repository as a Copilot skills/agents repository rather than a user-facing application.
2. `AGENTS.md` — Documents essential repo constraints, including no repo-wide package manifest/test runner and ignoring workspace outputs.
3. `docs/agent-guides/repo-layout.md` — Confirms maintained directories are skills, agents, references, hooks, scripts, and docs, not product app modules.
4. `skills/prd-create/SKILL.md` — Defines the PRD workflow and required issue template used for this eval.
5. `skills/prd-create/evals/evals.json` — Contains the exact saved-search email-alert eval prompt and expected workflow behaviors.
6. `skills/create-spec/SKILL.md` — Shows adjacent requirements-gathering conventions focused on user outcomes and testable requirements.
7. `skills/create-spec/references/spec-template.md` — Provides user-story, requirement, key-entity, and success-criteria conventions relevant to PRD quality.
8. `skills/create-plan/SKILL.md` — Shows that technical plans and data-model artifacts belong after a validated spec/PRD.
9. `skills/create-tasks/SKILL.md` — Shows later task breakdown conventions for independently testable increments.
10. `docs/agent-guides/validation.md` — Documents targeted validation rather than a single app test suite.

**Relevant tests/patterns:** PRD eval expectations and generic spec evals exist; no feature-specific tests exist for search/account/email alerts.

**Open gaps:** Actual target application, current search behavior, account settings IA, notification preferences, and email delivery stack are unavailable.

## Code-explorer agent: Architecture boundaries, data flow, and extension points

**Lens:** Architecture boundaries, data flow, extension points, persistence/schema, scheduled/background work patterns.

**Key findings:**
- There are no application architecture layers for routes, controllers, services, schemas, migrations, queues, schedulers, or background jobs.
- The only notification-like artifact is a local session-end terminal bell hook, not product email infrastructure.
- The repository’s durable architecture pattern is documentation and workflow separation: PRDs/specs/plans/tasks are separate phases.
- The PRD should not invent routes, models, tables, workers, or email services.

**Key files with reasons:**
1. `README.md` — Summarizes the repository layout and confirms the absence of product architecture.
2. `docs/agent-guides/repo-layout.md` — Lists top-level areas and workspace-directory expectations.
3. `skills/prd-create/SKILL.md` — Requires exploration before decisions and durable citations rather than file-path-specific issue bodies.
4. `skills/create-plan/SKILL.md` — Shows where architecture, storage, API contracts, and data-model details would be produced after requirements.
5. `skills/create-plan/references/plan-template.md` — Demonstrates planning artifacts for data models/contracts without serving as an app schema.
6. `hooks/notify.json` — The only notification-adjacent file; it is a local Copilot hook and not product email prior art.
7. `references/performance-checklist.md` — Provides generic guidance on indexing, pagination, caching, and p95 response targets useful for future app planning.
8. `docs/agent-guides/validation.md` — Confirms validation is targeted by changed area, not a monolithic app build.
9. `skills/create-tasks/SKILL.md` — Shows implementation tasks should be independently testable and TDD-oriented after planning.

**Relevant tests/patterns:** Generic performance and task-generation patterns exist; no app-level persistence or worker tests exist.

**Open gaps:** Data store, schema migration convention, scheduler/queue technology, email provider, and app service boundaries are unknown.

## Code-explorer agent: API contracts, persistence, schema, and integrations

**Lens:** API contracts, persistence/schema, email integrations, account authorization, and data lifecycle patterns.

**Key findings:**
- No API contracts, persistence layer, user/account model, email templates, or email-provider integration were found.
- Generic security references are relevant: authentication, authorization, ownership checks, input validation, sensitive-data handling, and no sensitive logging.
- Generic performance references suggest future saved-search queries should be indexed, paginated, bounded, and protected against unbounded reads.
- App-specific schema and contract decisions must wait for the real application repository.

**Key files with reasons:**
1. `README.md` — Identifies repository purpose and confirms it is not an application stack.
2. `AGENTS.md` — Captures repository-specific validation and workspace-output boundaries.
3. `skills/prd-create/SKILL.md` — Requires implementation decisions to be evidence-cited without adding code.
4. `skills/prd-create/evals/evals.json` — Sets expectations for the exact saved-search PRD eval scenario.
5. `references/security-checklist.md` — Provides relevant security patterns for auth, ownership, validation, IDOR prevention, and sensitive data.
6. `references/testing-patterns.md` — Provides API/integration testing examples for successful creation, validation errors, and unauthenticated access.
7. `references/performance-checklist.md` — Provides general persistence/API performance requirements for pagination, indexes, and avoiding unbounded queries.
8. `references/accessibility-checklist.md` — Provides UI requirements for form labels, errors, dynamic updates, and accessible search.
9. `docs/agent-guides/validation.md` — Defines targeted validation commands for this repo.
10. `skills/addy-security-and-hardening/SKILL.md` — Highlights security-sensitive areas such as user input, auth, data storage, and external integrations.

**Relevant tests/patterns:** Generic API integration tests and security-review criteria exist; no product API tests exist for saved searches or alerts.

**Open gaps:** REST vs GraphQL/RPC style, persistence schema, email provider, suppression state, deletion behavior, and data retention policy are unknown.

## Code-explorer agent: Tests, accessibility, security, and operational constraints

**Lens:** Tests, fixtures, accessibility, security, privacy, operational constraints, and eval output conventions.

**Key findings:**
- No feature-specific app tests exist for saved searches, account settings, notifications, schedules, or email delivery.
- The repository has strong generic testing guidance: behavior-first tests, accessible component queries, API integration tests, boundary mocking, and E2E tests for critical flows.
- Accessibility references cover labels, forms, errors, status messages, keyboard support, and dynamic announcements.
- Security references cover authentication, ownership, input validation, sensitive-data handling, and external integrations.
- The PRD issue body must avoid file paths and code snippets, while exploration summaries may record them.

**Key files with reasons:**
1. `references/testing-patterns.md` — Main generic testing reference for unit/component/API/E2E patterns and boundary mocking.
2. `references/accessibility-checklist.md` — Accessibility checklist for labels, forms, error messages, keyboard navigation, and status announcements.
3. `references/security-checklist.md` — Security checklist for auth, authorization, validation, data protection, and error handling.
4. `skills/fixing-accessibility/SKILL.md` — Skill guidance for auditing and fixing accessible forms, controls, status messages, and errors.
5. `skills/addy-security-and-hardening/SKILL.md` — Security-hardening workflow relevant to user input, storage, auth, sessions, and integrations.
6. `skills/tdd/tests.md` — TDD/testing guidance relevant to future implementation, although not an app test suite.
7. `skills/security-review/SKILL.md` — Shows review expectations for concrete security risks and exploitability.
8. `skills/prd-create/SKILL.md` — Requires testing decisions to focus on external behavior and user-visible outcomes.
9. `skills/prd-create/evals/evals.json` — Defines eval expectations for official research, one-question-at-a-time interview, and durable citations.
10. `docs/agent-guides/validation.md` — Confirms no single repo-wide test command is available.

**Relevant tests/patterns:** API success/validation/auth-failure tests; component tests using accessible roles/labels; E2E tests for critical flows; boundary mocks for time, database, HTTP, and external APIs.

**Open gaps:** App-specific fixtures for users, searches, permissions, alert schedules, email templates, provider webhooks, and account-area flows do not exist.
