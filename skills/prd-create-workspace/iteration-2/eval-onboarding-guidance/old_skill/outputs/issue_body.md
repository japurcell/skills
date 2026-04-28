# PRD: New Workspace Onboarding Guidance

## Objective

Improve activation for newly created workspaces by guiding the primary setup actor through three outcomes that make the workspace useful quickly: inviting teammates, connecting an existing integration, and completing the first useful setup action. The primary user is the workspace creator, with permission-aware support for other roles. Success means more new workspaces reach collaborative, integrated, first-value use without blocking users who need to move ahead immediately.

## User Stories

1. As a workspace creator, I want onboarding to appear immediately after workspace creation, so that I know what to do next.
2. As a workspace creator, I want onboarding to feel helpful rather than mandatory, so that I can use the workspace right away if needed.
3. As a workspace creator, I want to see the three most important setup outcomes in one place, so that I can understand the path to value quickly.
4. As a workspace creator, I want each onboarding task to explain why it matters, so that I can decide what to do first.
5. As a workspace creator, I want to invite teammates from onboarding, so that the workspace becomes collaborative quickly.
6. As a workspace creator, I want invite entry points to use the normal invitation flow, so that I learn the real product behavior instead of a disconnected tutorial.
7. As a workspace creator, I want clear success, failure, and retry feedback when sending invites, so that I know whether I need to act again.
8. As a workspace creator, I want to connect one existing integration from onboarding, so that the workspace becomes useful with tools my team already relies on.
9. As a workspace creator, I want the integration step to communicate the value and required permissions before I connect, so that I can make an informed decision.
10. As a workspace creator, I want integration connection progress and completion to be visible, so that I understand whether setup succeeded.
11. As a workspace creator, I want the first useful setup action to feel like a real product action, so that onboarding leads directly into normal usage.
12. As a workspace creator, I want the first useful setup action to be specific to the product area, so that onboarding is not generic or misleading.
13. As a workspace creator, I want task completion to persist across sessions, so that I can return later without losing progress.
14. As a workspace creator, I want skipped tasks to remain visible and recoverable, so that I can return when I have the time, permissions, or information.
15. As a workspace creator, I want to dismiss onboarding, so that setup guidance does not block urgent work.
16. As a workspace creator, I want to reopen onboarding from a predictable place later, so that dismissal is reversible.
17. As a returning workspace creator, I want onboarding to resume with accurate task statuses, so that I trust the progress shown.
18. As a returning workspace creator, I do not want onboarding to keep reappearing after I fully complete it, so that it does not become noise.
19. As a user without permission to invite teammates, I want the invite task to explain what I can do next, so that I am not confused by an unavailable action.
20. As a user without permission to manage integrations, I want the integration task to explain why it is unavailable, so that I can request help or continue with other setup work.
21. As an admin, I want invitation and integration actions to respect workspace roles and permissions, so that onboarding never bypasses product security boundaries.
22. As a teammate who joins after being invited, I want the workspace’s setup progress to reflect shared completion accurately, so that the creator is not asked to redo shared setup.
23. As a user, I want my personal dismissal preference to stay separate from shared workspace progress, so that my choice does not hide onboarding for everyone else.
24. As a keyboard user, I want every onboarding action to be operable without a mouse, so that I can complete setup with my preferred input method.
25. As a screen reader user, I want progress and result updates to be announced without disruptive focus jumps, so that I can follow onboarding state changes.
26. As a user with low vision or motor limitations, I want visible focus and adequately sized controls, so that onboarding controls are easy to find and activate.
27. As a mobile or small-screen user, I want onboarding to remain usable without obscuring my workspace, so that setup guidance does not create friction.
28. As a privacy-conscious user, I want onboarding measurement to avoid unnecessary personal data, so that my teammates’ information and integration secrets are not exposed.
29. As a product manager, I want to measure starts, completions, skips, dismissals, and time-to-value, so that I can evaluate whether onboarding improves activation.
30. As a support teammate, I want common onboarding failures and blockers to be observable, so that I can diagnose why new workspaces stall.
31. As an operator, I want onboarding to launch behind rollout control, so that the team can validate behavior before broad release.
32. As an existing workspace user, I want the first rollout to avoid changing long-lived workspaces unexpectedly, so that the launch focuses on net-new activation.
33. As a product team, I want v1 to improve guidance around current capabilities instead of introducing a new integration marketplace, so that scope stays focused.
34. As a product team, I want completion to mean the workspace reached all three setup outcomes, so that activation metrics remain meaningful.
35. As a stakeholder, I want assumptions created by the missing target repository to be explicit, so that engineering validates them before implementation.

## Implementation Decisions

- Use a non-blocking, resumable onboarding checklist rather than a mandatory wizard. Citation: GOV.UK Design System task-list guidance. Reason: the official guidance says task lists fit multi-session, flexible-order tasks better than a strict step flow.
- Do not use a linear progress indicator as the primary container for the three setup outcomes. Citation: IBM Carbon progress-indicator guidance. Reason: Carbon recommends progress indicators for linear step sequences and specifically warns against them when users may complete tasks in any order.
- Show onboarding immediately after workspace creation and keep it reopenable from a persistent product location until fully completed or intentionally dismissed. Citation: Existing repository pattern - multi-step workflows are resumable, stateful, and explicitly revisitable rather than single-pass. Reason: the requested setup tasks may span more than one session.
- Keep the core scope to three outcomes only: invite teammates, connect one existing supported integration, and complete one product-defined first useful setup action. Citation: Existing repository pattern - PRD workflow keeps scope tied to the source request and avoids unapproved expansion. Reason: this preserves focus on activation rather than turning onboarding into a broad setup center.
- Treat the first useful setup action as a configurable product-defined activation event that uses the real product surface. Citation: Existing repository pattern - explicit assumptions are preferred over invented domain detail when the target application is unavailable. Reason: the repository provided for this benchmark does not reveal the product’s actual activation action.
- Store shared task completion at the workspace level while keeping dismiss/reopen preferences user-specific. Citation: Existing repository pattern - durable workflow progress is separated from per-user session behavior. Reason: invite and integration completion are shared workspace facts, but hiding guidance is a personal UX choice.
- Show permission-aware disabled or alternate states instead of hiding unavailable tasks. Citation: Existing repository pattern - shared security guidance requires authorization checks and ownership/role validation on protected actions. Reason: hiding tasks makes progress confusing, while showing unauthorized actions as active creates poor UX and security ambiguity.
- Reuse existing invite and integration entry points in v1 instead of creating new provider flows. Citation: Existing repository pattern - requirements work should avoid expanding implementation scope without evidence. Reason: this change is about guidance to activation, not a new platform capability.
- Require visible labels, concise instructions, and minimal but clear helper text for invite and integration inputs. Citation: W3C WCAG 2.2 Labels or Instructions. Reason: onboarding asks users to make decisions and enter data, so the product must communicate expected actions clearly.
- Require text-based, item-specific errors for user-correctable failures. Citation: W3C WCAG 2.2 Error Identification. Reason: invite errors, validation failures, and integration failures must clearly identify what went wrong and what the user can do next.
- Announce asynchronous progress, success, and error changes without unnecessary focus movement. Citation: W3C WCAG 2.2 Status Messages. Reason: invite sending, integration connection, and task completion often update dynamically and need to be perceivable to assistive technologies.
- Ensure onboarding controls meet minimum target-size expectations and remain keyboard-operable with visible focus. Citation: W3C WCAG 2.2 Target Size Minimum plus existing repository accessibility guidance. Reason: onboarding depends on clickable actions and should be easy to use across input methods.
- For integration connections, require existing secure authorization-code flows with PKCE, redirect URI validation, CSRF/state protection, and least-privilege scopes. Citation: IETF RFC 9700 OAuth 2.0 Security BCP plus existing repository security guidance. Reason: onboarding should not weaken integration security to improve activation.
- Instrument onboarding with privacy-safe events such as shown, task_started, task_completed, task_skipped, dismissed, reopened, and fully_completed. Citation: Google Analytics guidance to avoid sending PII plus existing repository emphasis on durable, reviewable workflow state. Reason: the product needs activation measurement without sending teammate emails, tokens, or secrets.
- Roll out to newly created workspaces behind feature-flag or equivalent control before broader exposure. Citation: Existing repository pattern - staged workflow gates are used before advancing broader rollout. Reason: first-run experience changes should be validated carefully before full release.

## Tech Stack

- Preserve the target application’s existing web/application stack rather than introducing a new platform for onboarding.
- Preserve the target application’s current authentication, invitation, integration, persistence, analytics, and rollout infrastructure wherever those capabilities already exist.
- Concrete framework, language, and version details are intentionally blocked until the actual product repository is identified, because the repository supplied for this benchmark is a skills repository rather than the product codebase.

## Commands

- Build: Use the target application’s existing build command unchanged.
- Test: Use the target application’s existing unit, integration, and end-to-end test commands unchanged.
- Lint/Typecheck: Use the target application’s existing verification commands unchanged.
- Dev: Use the target application’s existing local development run command unchanged.
- Note: Exact executable commands cannot be stated authoritatively until the target application repository is provided.

## Project Structure

- Reuse the target application’s existing surfaces for workspace creation, invitations, integrations, onboarding entry points, analytics, and tests.
- Keep onboarding guidance adjacent to the real invite, integration, and activation flows instead of creating parallel one-off product paths.
- Final source and test directory placement is intentionally omitted until the target application repository is available.

## Code Style

- Follow the target application’s existing naming, formatting, accessibility, and validation conventions.
- Favor short action-first labels, explicit status text, and human-readable error messages over terse internal terminology.
- Keep business truth in shared product state, not only in local UI state, so that onboarding reflects real completion.
- Keep event naming bounded, stable, and privacy-safe.

## Testing Decisions

Good tests for this feature should verify external behavior and user-visible outcomes rather than implementation details.

- Test that a newly created workspace shows onboarding with the three required setup outcomes at the correct first-run moment. Prior art: existing repository testing guidance prefers observable behavior. Reason: the core requirement is what the user sees and can do.
- Test that invite onboarding covers success, validation failure, permission denial, resend/retry, and recoverable error states. Prior art: existing repository testing guidance covers happy-path, validation, and authorization boundaries. Reason: invitations combine user input, protected actions, and visible state changes.
- Test that the integration task covers connect start, cancellation, callback success, callback failure, and already-connected states. Prior art: existing repository testing guidance says to mock external systems at boundaries. Reason: integrations depend on external providers and must still present predictable product behavior.
- Test that the first useful setup action completes only when the real product action succeeds, not when a checklist item is manually toggled. Prior art: existing repository planning guidance values real user-visible outcomes. Reason: completion should represent actual activation.
- Test that completion, skip, dismiss, and reopen behavior persists correctly across reloads and later sessions. Prior art: existing repository workflows are resumable and stateful. Reason: resumability is a primary product requirement.
- Test workspace-level shared completion separately from user-level dismissal preferences. Prior art: existing repository patterns distinguish durable shared progress from per-user execution context. Reason: shared setup should not be repeated, while dismissal remains personal.
- Test permission-aware rendering for owners/admins/members or equivalent product roles. Prior art: existing repository security guidance requires authz checks for protected actions. Reason: onboarding must not expose misleading or unauthorized actions.
- Test keyboard operation, visible focus, target size, labels, instructions, and text error rendering. Prior art: existing repository accessibility guidance plus W3C WCAG 2.2 references. Reason: onboarding is interactive and must be accessible by default.
- Test status announcements for async invite sending, integration progress, and task completion. Prior art: W3C WCAG 2.2 Status Messages. Reason: important dynamic state changes must be announced without disruptive focus shifts.
- Test analytics emission for shown, started, completed, skipped, dismissed, reopened, and fully completed events, and verify that raw emails, tokens, and secrets never enter analytics payloads. Prior art: Google Analytics privacy guidance plus existing repository security guidance. Reason: activation measurement must remain privacy-safe.
- Test rollout gating so the feature can be enabled for internal/beta/new-workspace cohorts before general release. Prior art: existing repository workflows use gates before wider progression. Reason: staged rollout lowers launch risk.

## Boundaries

- Always: validate user input, enforce role/permission checks, preserve accessibility requirements, and run the target application’s existing tests before shipping.
- Ask first: database schema changes, new dependencies, new integration providers, analytics taxonomy changes, and changes to invitation or auth infrastructure.
- Never: block workspace access behind mandatory onboarding, expose secrets or tokens in telemetry, silently invent product-specific behavior without validation, or remove security/accessibility checks for speed.

## Success Criteria

- New-workspace onboarding is shown at the intended first-run moment for the rollout cohort.
- Users can complete the invite task using the existing invitation flow from onboarding.
- Users can connect at least one already-supported integration from onboarding using the existing secure connection flow.
- Users can complete the product-defined first useful setup action from the real product surface.
- Task states visibly distinguish at least incomplete, completed, and any necessary permission-blocked or in-progress states.
- Users can skip or dismiss onboarding without losing workspace access, and can later reopen it from a clear location.
- Completion, skip, dismiss, and reopen states persist according to the workspace-level vs. user-level scoping decision.
- Keyboard-only and assistive-technology users can complete the onboarding flow successfully.
- Analytics can report onboarding funnel progression and time-to-value without capturing PII or secrets.
- Initial rollout can be limited to newly created workspaces and evaluated before broader release.

## Out of Scope

- Rebuilding the workspace-creation flow itself.
- Adding new integration providers, a marketplace, or provider-specific custom setup programs.
- Billing, seat management, SSO configuration, or enterprise provisioning changes unless they are already part of existing invitation/integration permissions.
- Lifecycle email campaigns, marketing nurture flows, or off-product onboarding programs.
- Forcing all users to complete onboarding before using the workspace.
- Migrating every existing workspace into the new experience during the first rollout.
- Inventing a universal first useful setup action for every product domain; the action must be mapped in the target application context.
- Implementation work itself, including code, schema, or deployment changes, within this PRD issue.

## Further Notes

- Accepted assumption: this is a web-style workspace product where the workspace creator is the primary activation actor.
- Accepted assumption: onboarding is non-blocking, dismissible, resumable, and reopenable.
- Accepted assumption: the first release reuses existing invitation and integration capabilities rather than adding new providers.
- Accepted assumption: onboarding is considered fully complete only after all three setup outcomes succeed.
- Accepted assumption: shared setup completion is workspace-scoped, while dismissal/reopen preferences are user-scoped.
- Accepted assumption: the first useful setup action will be defined in the target application as the activation event most correlated with early value.
- Limitation: the repository supplied for this benchmark is not the target application, so concrete stack details, command lines, project paths, and existing product APIs could not be validated here.
- Follow-up required before implementation: confirm the target product repository, supported integrations, role model, rollout mechanism, analytics platform, and exact first useful setup action.
