# Exploration Summary

## Framed request

Draft a PRD issue for improving onboarding after a new workspace is created so the user is guided through inviting teammates, connecting integrations, and completing the first useful setup action. Primary actors are the workspace creator and any admin-capable teammates. Desired outcome is faster activation, better collaboration setup, and clearer next steps immediately after workspace creation.

## Repository fit

The provided repository is **not** the target application for the requested onboarding change. It is a GitHub Copilot skills-and-agents repository.

Evidence from the repository:

- The root README says the repository publishes custom GitHub Copilot assets: skills in `skills/`, custom agents in `agents/`, and local Copilot instructions.
- The README also says `skills/*-workspace/` directories are generated eval runs, snapshots, and review artifacts, and that those outputs are benchmark fixtures rather than maintained source.
- `AGENTS.md` repeats that there is no repo-wide product application or single test runner and that workspace output folders are benchmark fixtures.
- `skills/prd-create/evals/evals.json` contains this onboarding prompt as an eval case for the PRD skill itself, which confirms the repository is evaluating documentation workflow behavior rather than hosting the product that needs onboarding.

Resulting implication: there is no trustworthy product code here for workspace creation flows, invitation systems, integration catalogs, onboarding state, analytics taxonomy, or role models. The PRD therefore uses:

1. codebase evidence only for durable process/security/accessibility/testing patterns,
2. official external references for UX, accessibility, OAuth, and analytics constraints, and
3. explicit assumptions for product-specific decisions that cannot be proven from this repository.

## Exploration workflow followed

Per the skill instructions, three parallel `code-explorer` lenses were used:

1. similar flows and repository purpose,
2. architecture boundaries and extension points,
3. evaluation and operational constraints.

The findings were merged and de-duplicated before drafting the PRD.

## Key findings that affect the PRD

### 1. No target-app prior art exists in this repo

There is no application UI, API, database schema, auth model, or onboarding implementation to cite. That blocks any honest claim like “reuse the existing invite drawer” or “follow the current integration callback contract.” Those items must remain product assumptions or follow-up validation points.

### 2. Durable guidance patterns do exist in this repo

While there is no target app, the repository does include durable patterns that are relevant to PRD quality and implementation guardrails:

- existing PRD workflow guidance emphasizes explicit assumptions, evidence-backed decisions, and durable citations rather than brittle file-path references,
- shared accessibility guidance emphasizes visible labels, keyboard operation, status announcements, focus visibility, and text-based errors,
- shared security guidance emphasizes authorization checks, least privilege, input validation, and not exposing secrets or sensitive data,
- shared testing guidance emphasizes external behavior, lowest-sufficient test level, and mocking at system boundaries.

These are cited as “existing repository patterns” where appropriate.

### 3. The onboarding problem is better modeled as a resumable checklist than a product-tour walkthrough

The requested outcomes—invite teammates, connect integrations, complete a first useful action—are discrete tasks that may happen in different orders and across multiple sessions. That makes a resumable task-list/checklist model more defensible than a rigid wizard.

### 4. Product-specific first-value action cannot be hard-coded from this repo

Because the target application is unknown, the PRD cannot honestly assert a specific domain action such as “create first project” or “send first message.” The requirement must be framed as a configurable, product-defined activation action that uses the real product surface.

### 5. Offline benchmark mode changes the delivery mechanism

The skill normally creates a GitHub issue. This run is explicitly offline, so the issue title/body were saved as artifacts instead of filing anything with `gh issue create`.

## Durable codebase patterns preserved

- **Evidence before implementation:** decisions should be backed by exploration or official references, not guesses.
- **Explicit assumptions:** missing product facts should be surfaced and accepted, not hidden.
- **Accessibility by default:** interactive onboarding controls need labels, keyboard support, visible focus, text errors, and status messaging.
- **Security by default:** invite and integration actions require authz checks, validated input, and least-privilege external access.
- **Behavior-first testing:** tests should verify visible outcomes and system behavior rather than implementation details.

## Key files reviewed

- `README.md` — confirms this repository publishes skills, agents, and benchmark workspaces rather than a target application.
- `AGENTS.md` — confirms there is no single app/test harness and that workspace outputs are benchmark fixtures.
- `skills/prd-create/skill.md` equivalent snapshot (`SKILL.md`) — defines the governing PRD workflow.
- `skills/prd-create/evals/evals.json` — confirms this exact onboarding prompt is a skill benchmark case.
- `references/accessibility-checklist.md` — provides durable accessibility constraints relevant to onboarding.
- `references/security-checklist.md` — provides durable security constraints relevant to invitations and integrations.
- `references/testing-patterns.md` — provides durable testing principles for the PRD’s testing section.

## Open gaps that exploration could not answer

These are genuine product questions and were handled in the simulated interview rather than guessed from the repo:

- Which user roles can invite teammates or connect integrations?
- Which existing integrations are actually supported in v1?
- What is the product’s real first useful setup action?
- What analytics and rollout infrastructure already exist in the target application?
- What repository/stack should receive the real issue once offline restrictions are removed?

## Conclusion

This benchmark run produced a **product-agnostic but actionable PRD draft**. It is grounded in repository evidence about process and guardrails, plus official research and explicit assumptions. It intentionally avoids inventing target-app implementation prior art that the provided repository cannot support.
