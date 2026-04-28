# Exploration Summary

## Request framing

The requested PRD is for improving onboarding after a new workspace is created so the user is guided through:

1. inviting teammates,
2. connecting integrations, and
3. completing the first useful setup action.

Primary actor: likely the workspace creator.
Desired outcome: faster activation for new workspaces.
Likely product surface: post-creation onboarding UI plus existing invite, integration, and setup entry points.
Known constraints: offline benchmark mode, no live GitHub issue creation, no live interview answers, and no target application repository was provided.
Obvious non-goals: implementation, new integration development, or app-specific design details not supported by evidence.
Unknowns exploration needed to answer: whether this repository is the target app, what product/domain evidence exists, and what stable conventions can still inform the PRD.

## Repository reality

This repository is **not the target application**. It is a repository of Copilot skills, agents, references, and benchmark workspaces.

### Codebase evidence

- `README.md` describes the repo as publishing custom coding skills from `skills/` and custom agent definitions from `agents/`, not as a product application.
- `AGENTS.md` states that this repository publishes custom coding skills and custom agent definitions and explicitly calls out `skills/*-workspace/` as generated evaluation runs and review artifacts.
- `skills/prd-create/SKILL.md` is the governing source for PRD creation workflow and confirms that this task should produce a PRD issue rather than application code.
- `skills/prd-create/evals/evals.json` contains this exact onboarding prompt as an offline benchmark scenario, confirming the repository is evaluating PRD workflow quality rather than hosting the target onboarding product.
- Prior benchmark fixtures under `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/with_skill/outputs/` show how the skill handled this prompt before, but they are benchmark outputs rather than product prior art.

## What exploration found

### Material findings

1. There is no trustworthy product-app evidence here for real workspace creation, teammate invitation flows, integration catalogs, setup actions, permissions, schemas, analytics taxonomy, or onboarding UI.
2. The strongest reliable codebase evidence is about **how to write the PRD**, not **how the product currently works**.
3. The governing skill requires exploration first, targeted research before decisions, explicit assumptions, one-question-at-a-time interviewing, durable citations, and a PRD body with fixed section order.
4. Shared reference material in the repo provides reusable guidance for accessibility, security, and testing quality, which is relevant to invite flows, integration setup, progress/status messaging, and rollout.
5. Because the target app is missing, the final PRD must rely on:
   - explicit assumptions,
   - official research,
   - stable process/architecture patterns from this repo when they are genuinely relevant,
   - and clear statements about what must be validated in the real product repository before implementation.

### Existing patterns/conventions worth preserving

- Multi-step work should be resumable and explicit rather than hidden or implicit.
- Assumptions should be surfaced instead of silently filled in.
- Outputs should use durable language and avoid brittle implementation details.
- Testing language should focus on external behavior and user-visible outcomes.
- Accessibility and security should be treated as first-class requirements, not afterthoughts.

## Key files reviewed

1. `skills/prd-create/SKILL.md` — source of truth for the workflow, interview expectations, PRD template, and citation rules.
2. `skills/prd-create/evals/evals.json` — contains the exact onboarding benchmark prompt and its expectations.
3. `skills/prd-create-workspace/iteration-1/benchmark.md` — confirms offline benchmark mode blocks real issue creation.
4. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/eval_metadata.json` — lists what this benchmark run must demonstrate.
5. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/with_skill/grading.json` — shows what the grader considers a pass.
6. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/with_skill/outputs/interview_log.md` — prior example of the required dependency-ordered question flow.
7. `skills/prd-create-workspace/iteration-1/eval-onboarding-guidance/with_skill/outputs/issue_body.md` — prior example of a durable PRD issue body for the same prompt.
8. `references/testing-patterns.md` — repo prior art for behavior-focused testing language.
9. `references/accessibility-checklist.md` — repo prior art for labels, errors, keyboard support, and status messaging.
10. `references/security-checklist.md` — repo prior art for authorization, safe redirects, input validation, and sensitive-data handling.

## Gaps exploration could not answer

Exploration could not answer the following because the target application is absent from this repository:

- what a workspace represents in the actual product,
- which integrations already exist,
- which roles can invite teammates or connect integrations,
- what the real “first useful setup action” should be,
- where onboarding should resume in the live UI,
- what analytics/events already exist,
- and what rollout constraints the product team already has.

## Explicit assumptions carried forward

Because the target app is unavailable, the PRD proceeds with these assumptions unless the real product repository later disproves them:

1. The product is a web SaaS application with workspace-based collaboration.
2. The first-run user is usually the workspace creator, typically with owner/admin capability.
3. Existing invite and integration entry points already exist in the product, and onboarding should guide users into them rather than invent net-new providers.
4. Onboarding should be non-blocking, dismissible, resumable, and measurable.
5. The first useful setup action must be product-defined and configurable by workspace type or product area.
