# Exploration Summary

## Request framing
Create a PRD for a web-application feature that lets users save a search, choose an email update cadence, and manage existing alerts from their account area. Primary actors are signed-in end users and support/admin staff reviewing account state. Desired outcomes are repeatable search subscriptions, controllable alert frequency, and self-service management. Likely product surfaces are the search results experience, the account/settings area, background alert generation, and email delivery. Obvious non-goals are native mobile, SMS/push notifications, and implementation details. The biggest unknown was whether the current repository is the target application.

## Codebase findings
1. **The current repository is not the target application.**
   - `README.md` describes this repository as publishing custom GitHub Copilot skills, custom agents, and local instructions.
   - `AGENTS.md` repeats that the repo is for skills and agents, not an application surface.
   - `docs/agent-guides/repo-layout.md` shows a repository structure centered on `skills/`, `agents/`, `references/`, and installer scripts.
   - `scripts/copilot-install.sh` copies repository assets into `~/.agents` and `~/.copilot`, confirming the main runtime is local Copilot asset installation rather than a product application.

2. **There is no app-specific prior art for saved searches, account management, background scheduling, or email alerts.**
   - No maintained user-facing application modules, schemas, API contracts, or notification systems were found.
   - The only notification-like artifact is `hooks/notify.json`, which rings the terminal bell at session end.

3. **The exact feature prompt exists only as an evaluation fixture.**
   - `skills/prd-create/evals/evals.json` includes this same saved-search-alerts prompt as a benchmark for the PRD skill.
   - That confirms this repository is evaluating PRD-writing behavior, not implementing the feature.

## Durable codebase patterns still usable for the PRD
Even though the repo is not the target app, it does provide process-level patterns worth preserving:
- Surface assumptions explicitly before implementation.
- Prefer durable citations over brittle file-path-heavy implementation detail.
- Ground testing decisions in observable behavior, not internals.
- Use targeted validation instead of assuming a monorepo-wide command set.

## Gaps the repository could not answer
- What the real target application stack is.
- Whether user accounts, saved filters, or search already exist.
- Whether the application already has an email provider, background jobs, or a notification preference center.
- Region/compliance scope for outbound alerts.
- Any existing admin/support tooling for user communication settings.

## Assumptions used for the offline PRD
Because the benchmark cannot pause for live discovery and the repository is not the target app, the PRD proceeds with explicit assumptions:
1. The target product is a web application with authenticated user accounts.
2. Users manage only their own alerts at launch; shared or workspace-level alerts are out of scope.
3. Alerts are delivered only by email at launch.
4. Launch frequencies are daily, weekly, and paused; immediate alerts are deferred.
5. Emails are sent only when new matching results are found since the last successful send.
6. Users can create alerts from search results and manage them from their account area.
7. Every alert email includes a manage-preferences link and an unsubscribe path that works without requiring a fresh login.
8. Alert criteria changes at launch are handled by creating a new alert rather than editing the underlying search definition in place.
9. Active alerts are capped per user to limit abuse and operational load.

## Resulting PRD posture
The resulting PRD is grounded in:
- repository evidence that this is **not** the target application,
- official research for accessibility, privacy/security, and email compliance,
- and explicit benchmark assumptions recorded in the simulated interview log.

It does **not** claim target-app-specific prior art that is unavailable from the current codebase.
