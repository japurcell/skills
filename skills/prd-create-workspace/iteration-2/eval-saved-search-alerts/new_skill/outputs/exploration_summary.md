# Exploration Summary

## Request Framing

**Feature request:** Create a PRD for saved searches with email alerts so users can save a search, choose an update frequency, and manage existing alerts from their account area.

**Primary users:** signed-in end users who run repeat searches and want updates without rerunning those searches manually.

**Desired outcome:** a durable PRD issue that defines the feature clearly enough for later planning and implementation.

**Likely product surface:** search/results UI, account-area alert management UI, persistence for saved searches and subscriptions, scheduled delivery, email templates, unsubscribe flow, and observability.

**Known constraints:** offline benchmark mode, no live user interview, no real GitHub issue creation, and the current repository is the PRD-skill repository rather than the target application.

**Obvious non-goals:** implementing the feature, inventing target-app prior art, or pretending the current repository already contains search/account/email-alert code.

## Workflow Followed

I followed `skills/prd-create/SKILL.md` directly:

1. Framed the request.
2. Ran three parallel `code-explorer` subagents with distinct lenses:
   - repository identity / issue-authoring context
   - analogous features and user flows
   - architecture, persistence, integration, testing, accessibility, and security constraints
3. Merged the exploration findings.
4. Performed targeted official-source research in parallel.
5. Simulated the one-question-at-a-time interview with recommendations and assumed accepted answers.
6. Wrote the PRD issue title/body and offline run summary artifacts.

## Repository Reality Check

The current repository is **not** the target application. Codebase evidence consistently shows this is a repository for GitHub Copilot skills, custom agents, references, and benchmark workspaces rather than a production web application:

- `README.md` describes the repo as publishing custom GitHub Copilot assets in `skills/`, `agents/`, `references/`, and `scripts`.
- `AGENTS.md` says this repo publishes custom coding skills and agent definitions and explicitly treats `skills/*-workspace/**/outputs/` as generated benchmark fixtures.
- `docs/agent-guides/validation.md` documents narrow validation commands for skills and scripts instead of any product-app build/test/runtime workflow.
- `skills/prd-create/evals/evals.json` includes this exact saved-search prompt as a benchmark case for the PRD skill, confirming that this repository contains the workflow for authoring PRDs, not the application that would receive the feature.
- `skills/prd-create-workspace/iteration-1/benchmark.md` confirms offline benchmark mode expects saved artifacts instead of a live GitHub issue.

## Merged Findings From Exploration

### 1. There is no trustworthy in-repo prior art for the actual feature

I found no application code for:

- search UI or search APIs
- saved-search persistence
- account settings or profile management
- email delivery infrastructure
- scheduling/background jobs for recurring alerts
- user-level authorization, unsubscribe, or notification preferences

Because those surfaces are absent, the PRD cannot cite app-specific implementation patterns from this repository without inventing them.

### 2. The strongest codebase evidence is process-oriented, not feature-oriented

The repository does provide durable patterns for **how to write the PRD**:

- explore first, then research, then interview, then draft
- separate durable requirements from brittle implementation details
- use targeted validation rather than vague “test everything” language
- keep generated benchmark artifacts in a workspace output directory

These patterns informed the artifact set and the testing guidance language in the PRD, but not the target application’s product behavior.

### 3. Accessibility and testing references exist as generic guidance

The repo’s shared references include accessibility and testing guidance that are useful as durable evidence for the PRD even though they are not product-specific:

- the accessibility checklist covers live regions, status/error messaging, dialogs, and semantic controls
- the testing patterns reference emphasizes accessible-role UI tests, API/auth validation, and end-to-end user journeys

These were safe to reuse as codebase-pattern citations because they are repository-wide guidance rather than invented app behavior.

## Implications For The PRD

Because the repository is not the target app, the PRD had to be grounded in:

1. explicit acknowledgement that no target-app codebase prior art is available here
2. official research for accessibility, email subscription requirements, unsubscribe behavior, and durable web search-state behavior
3. explicit assumptions captured and accepted in the simulated interview

This means the PRD is intentionally **product-directional** and **implementation-aware**, but not tied to any invented file paths, endpoints, schema names, or existing app modules.

## Key Files Reviewed

- `README.md` — confirms the repository publishes skills/agents, not an application.
- `AGENTS.md` — documents repo working rules and the benchmark nature of `*-workspace` outputs.
- `docs/agent-guides/validation.md` — confirms there is no monorepo app test runner.
- `skills/prd-create/SKILL.md` — governing workflow for exploration, research, interviewing, PRD structure, and issue filing.
- `skills/prd-create/evals/evals.json` — benchmark expectations, including parallel exploration, official research, sequential interview logging, and offline issue artifacts.
- `skills/prd-create-workspace/iteration-1/benchmark.md` — confirms offline benchmark mode expects saved issue title/body plus intended `gh issue create` command.
- `references/accessibility-checklist.md` — reusable accessibility prior art for status messages, alerts, dialogs, and control semantics.
- `references/testing-patterns.md` — reusable testing prior art focused on external behavior rather than implementation details.

## Gaps Exploration Could Not Answer

These questions remain unanswered by the repository itself:

- What search experience already exists in the real application?
- Does the real application already have an account/settings area?
- What email provider, scheduler, queue, or notification system exists today?
- Are there privacy, consent, retention, or regional compliance requirements already established in the real application?
- Are saved-search alerts user-only, workspace-scoped, or admin-manageable in the target product?

## Conclusion

The exploration phase completed successfully and produced enough evidence to continue, but only by treating this repository as **workflow prior art** rather than **application prior art**. The resulting PRD therefore relies on codebase evidence for process/testing/accessibility conventions, official research for feature constraints, and explicit assumptions for missing product context.
