## Problem Statement

New workspace creators arrive in an empty workspace without enough guidance to turn that workspace into a useful, collaborative environment. They may not know whether to invite teammates first, connect the tools their team depends on, or perform the first setup action that proves the workspace is ready for real work. When that path is unclear, new workspaces are more likely to stall before activation, and users may abandon setup or rely on support instead of reaching value quickly.

## Solution

When a new workspace is created, show the creator a non-blocking, resumable onboarding task list that guides them through three high-value setup outcomes: inviting teammates, connecting an available integration, and completing the first useful setup action for that workspace. The experience should make progress visible, preserve completion across sessions, adapt to permissions, allow users to skip or dismiss steps without blocking access, and provide a discoverable way to resume setup later.

## User Stories

1. As a workspace creator, I want onboarding to appear after workspace creation, so that I know what to do next.
2. As a workspace creator, I want to see a short list of setup steps, so that I can understand the path to a useful workspace.
3. As a workspace creator, I want the setup steps to include inviting teammates, so that my workspace can become collaborative quickly.
4. As a workspace creator, I want to invite one or more teammates from onboarding, so that I do not need to search settings for the invite flow.
5. As a workspace creator, I want clear invite success and failure feedback, so that I know whether teammate invitations were sent.
6. As a workspace creator, I want onboarding to explain why connecting an integration is valuable, so that I can choose whether it matters for my team.
7. As a workspace creator, I want to connect at least one supported integration from onboarding, so that my workspace can work with the tools my team already uses.
8. As a workspace creator, I want integration setup to show loading, success, cancellation, and failure states, so that I can recover without losing context.
9. As a workspace creator, I want the first useful setup action to be specific to the product area or workspace type, so that onboarding does not feel generic.
10. As a workspace creator, I want the first useful setup action to be completed in the normal product surface when possible, so that I learn the real workflow rather than a disconnected tutorial.
11. As a workspace creator, I want completed steps to remain completed after reloads and new sessions, so that I do not repeat setup work.
12. As a workspace creator, I want skipped steps to remain available, so that I can return when I have the right information or permissions.
13. As a workspace creator, I want to dismiss onboarding, so that I can use the workspace immediately if I already know what to do.
14. As a workspace creator, I want to reopen onboarding from a discoverable location, so that dismissal does not permanently hide setup help.
15. As a workspace creator, I want onboarding to be non-blocking, so that setup guidance does not prevent urgent workspace use.
16. As a workspace creator, I want visible progress, so that I know what is complete and what remains.
17. As a workspace creator, I want step labels and hints to be clear, so that I understand what information is required before I act.
18. As a workspace creator, I want errors to describe what went wrong and how to proceed, so that I can fix user-correctable failures.
19. As a user without invite permission, I want the invite step to explain that an admin must invite teammates, so that I understand why the action is unavailable.
20. As a user without integration permission, I want the integration step to offer a permission-aware alternative, so that I can request help or continue with other setup work.
21. As an admin, I want onboarding actions to respect workspace roles and permissions, so that users cannot invite teammates or connect tools they are not authorized to manage.
22. As a teammate who joins through an invite, I want the workspace to reflect that collaboration setup has progressed, so that the creator is not prompted to repeat a completed step.
23. As a user, I want onboarding state to be scoped appropriately between the workspace and my own dismissal preferences, so that shared setup progress is accurate while my personal experience is respected.
24. As a user using keyboard navigation, I want every onboarding control to be operable without a mouse, so that I can complete setup with my preferred input method.
25. As a screen reader user, I want progress updates and action results to be announced without unnecessary focus jumps, so that I understand onboarding state changes.
26. As a user with low vision or motor limitations, I want visible focus indicators and sufficiently sized action targets, so that onboarding controls are easy to find and activate.
27. As a user on a small screen, I want onboarding to remain usable without obscuring core workspace content, so that setup guidance does not create friction.
28. As a user, I want analytics and tracking to avoid unnecessary personal data, so that onboarding measurement does not expose teammate emails or integration secrets.
29. As a product manager, I want to measure step starts, completions, skips, dismissals, and time-to-value, so that we can evaluate whether onboarding improves activation.
30. As a support teammate, I want onboarding failure states and common blockers to be observable, so that support can diagnose why new workspaces fail to activate.
31. As an operator, I want onboarding to ship behind a controlled rollout, so that we can validate behavior and reduce risk before broad release.
32. As a product team, I want the initial release to use existing invite and integration capabilities, so that this PRD improves guidance without requiring a new integration marketplace.
33. As a returning workspace creator, I want onboarding not to reappear after completion, so that completed setup does not become noise.
34. As an existing workspace user, I want existing workspaces to be unaffected during the initial rollout, so that the launch focuses on newly created workspaces.
35. As a workspace creator, I want concise copy that prioritizes the next best action, so that onboarding feels helpful rather than overwhelming.

## Implementation Decisions

- Use a non-blocking, resumable task-list pattern rather than a mandatory wizard. Citation: GOV.UK Design System task list component, https://design-system.service.gov.uk/components/task-list/. Reason: the official component guidance says task lists help users identify completed and incomplete tasks and are appropriate when users may not complete all tasks in one sitting or need to choose order.
- Show onboarding immediately after new workspace creation and keep it available from a persistent resume location. Citation: Existing codebase pattern - repository workflows use explicit phases, gates, durable artifacts, and resume points for multi-step work. Reason: onboarding is also a multi-step process that should preserve progress and let users return without losing context.
- Include three primary setup outcomes: invite teammates, connect one supported integration, and complete one product-defined first useful setup action. Citation: Existing codebase pattern - the PRD workflow treats the source feature description as the product input to frame scope before exploration and decisions. Reason: preserving the requested outcomes keeps the PRD aligned with the activation path this issue is meant to define.
- Make the first useful setup action configurable by product area or workspace type instead of hard-coding one domain action in this PRD. Citation: Existing codebase pattern - planning guidance favors vertical slices that deliver user-visible value while keeping domain-specific details explicit. Reason: the target application is not present in this repository, so the durable requirement is configurability plus a product-selected action before implementation.
- Scope shared step completion to the workspace while keeping dismissal and reminder preferences user-specific. Citation: Existing codebase pattern - workflow state separates durable shared progress from per-run execution context. Reason: invite and integration completion are workspace facts, while dismissal is a personal UX preference.
- Preserve permission-aware states for invite and integration actions. Citation: Existing security guidance - authorization and ownership checks are required for protected actions. Reason: inviting teammates and managing integrations can affect workspace membership, data access, billing, and external systems.
- Reuse existing invite and integration entry points for the first release instead of introducing new providers or custom connection flows. Citation: Existing codebase pattern - PRD and planning workflows explicitly separate requirements from implementation and avoid expanding scope without evidence. Reason: this keeps the onboarding improvement focused on guidance and activation rather than a broad integrations program.
- For OAuth-based integrations, require authorization-code flows with PKCE, exact redirect URI validation, CSRF protection, and no implicit grant for browser flows. Citation: IETF OAuth 2.0 Security Best Current Practice RFC 9700, https://www.rfc-editor.org/rfc/rfc9700.html. Reason: integration onboarding can introduce token-handling risk, and this source defines current best practices for redirect-based OAuth flows.
- If GitHub-style integrations are part of the product, prefer fine-grained app permissions where available and include state and PKCE in authorization. Citation: GitHub OAuth app authorization documentation, https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps. Reason: the vendor documentation recommends state for CSRF protection, PKCE for flow security, and notes that GitHub Apps provide fine-grained permissions and short-lived tokens.
- Provide visible labels, concise instructions, and validation guidance for invite forms and integration configuration fields. Citation: W3C WCAG 2.2 Understanding Labels or Instructions, https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html. Reason: onboarding asks users for inputs such as emails and configuration choices; labels and instructions reduce confusion and prevent errors.
- Present user-correctable errors in text and identify the affected item. Citation: W3C WCAG 2.2 Understanding Error Identification, https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html. Reason: invite and integration failures must be perceivable and actionable for all users.
- Announce asynchronous progress and completion updates without unnecessary focus changes. Citation: W3C WCAG 2.2 Understanding Status Messages, https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html. Reason: onboarding progress, invite sending, and integration connection states change dynamically and should be communicated to assistive technologies.
- Ensure every onboarding action is keyboard-operable and has visible focus and adequate target size. Citation: W3C WCAG 2.2 keyboard, focus appearance, and target size guidance, https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html, https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html, and https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html. Reason: onboarding includes buttons, links, checklist controls, and forms that must be usable by keyboard, low-vision, and motor-impaired users.
- Instrument onboarding with start, step-start, step-complete, step-skip, dismiss, reopen, and complete events, while avoiding sensitive raw values. Citation: Google Analytics event setup and recommended onboarding events, https://developers.google.com/analytics/devguides/collection/ga4/events and https://developers.google.com/analytics/devguides/collection/ga4/reference/events. Reason: the official guidance treats events as the way to measure interactions and includes tutorial_begin and tutorial_complete as onboarding funnel events.
- Limit analytics payloads to allowed, privacy-reviewed identifiers and bounded parameters. Citation: Google Analytics collection limits, https://support.google.com/analytics/answer/9267744. Reason: analytics event names and parameters have practical limits, and onboarding should not encode teammate emails, token values, or unbounded integration metadata.
- Ship behind a feature flag or equivalent rollout control for newly created workspaces first. Citation: Existing codebase pattern - deterministic workflows use gates and validation before advancing phases. Reason: a staged release allows validation of activation, accessibility, security, and support outcomes before broader exposure.

## Testing Decisions

Good tests for this feature should verify external behavior and user-visible outcomes rather than implementation details.

- Test that a new workspace creator sees onboarding with the three required setup outcomes immediately after workspace creation. Prior art: Existing testing guidance favors user-visible behavior and the lowest test level that captures the behavior. Reason: the core requirement is observable guidance, not a particular component structure.
- Test invite-step behavior for success, validation errors, permission denial, and retry. Prior art: Existing API and component testing patterns cover successful creation, validation failure, and authorization failure. Reason: teammate invitations combine user input, protected actions, and visible completion state.
- Test integration-step behavior for provider selection, authorization start, cancellation, callback success, callback failure, and already-connected states. Prior art: Existing integration-testing guidance treats external services as boundaries to be mocked while preserving application behavior. Reason: integration onboarding depends on external systems and must handle recovery states predictably.
- Test first-useful-action completion through the selected product action rather than a simulated checklist toggle. Prior art: Existing planning guidance favors vertical slices that produce real user-visible value. Reason: onboarding should mark completion when the user actually reaches value.
- Test that completed, skipped, dismissed, and reopened states persist across reloads and sessions according to the workspace/user scoping decision. Prior art: Existing workflow patterns rely on durable state and resume behavior. Reason: resumability is a primary product requirement.
- Test permission-aware variants for workspace owners, admins, members, and users who cannot invite teammates or manage integrations. Prior art: Existing security guidance requires authorization and ownership checks for protected operations. Reason: onboarding must not expose unauthorized actions or misleading calls to action.
- Test keyboard navigation, focus order, visible focus, target size, labels, instructions, and text error descriptions. Prior art: W3C WCAG 2.2 guidance on keyboard operation, focus appearance, target size, labels, and error identification. Reason: onboarding is an interactive flow and must be accessible by default.
- Test dynamic status announcements for invite submission, integration connection progress, and step completion. Prior art: W3C WCAG 2.2 status message guidance. Reason: asynchronous onboarding updates should be announced without taking focus unnecessarily.
- Test analytics emission for onboarding shown, step started, step completed, step skipped, onboarding dismissed, onboarding reopened, and onboarding completed. Prior art: Google Analytics event guidance and recommended onboarding events. Reason: activation impact cannot be evaluated without reliable, privacy-safe event measurement.
- Test that analytics events do not include raw teammate emails, access tokens, refresh tokens, authorization codes, secrets, or unapproved integration metadata. Prior art: Existing security guidance treats sensitive data and external integrations as high-risk. Reason: onboarding measurement should not create privacy or credential-exposure risk.
- Test rollout gating so the feature can be enabled for internal, beta, or newly created workspaces without affecting existing workspaces unexpectedly. Prior art: Existing workflow patterns use gates before broader progression. Reason: rollout control is needed to evaluate activation metrics and mitigate launch risk.

## Out of Scope

- Rebuilding the workspace creation flow itself.
- Creating new integration providers, a full integration marketplace, or provider-specific setup experiences beyond linking to existing supported entry points.
- Building lifecycle email campaigns, marketing automation, or cross-channel onboarding reminders.
- Forcing users to complete onboarding before accessing the workspace.
- Migrating all existing workspaces into the new onboarding experience during the initial release.
- Defining the product-specific first useful setup action for every workspace type; this PRD requires configurability and an initial product-selected action.
- Changing billing, seat management, SSO, or enterprise provisioning flows unless they already affect invite or integration permissions.
- Implementing code, database migrations, API changes, or UI designs as part of the PRD issue itself.
- Capturing sensitive analytics such as teammate email addresses, OAuth tokens, authorization codes, secrets, or raw integration payloads.

## Further Notes

- Assumption accepted for this offline PRD: the primary user is a workspace creator with owner or admin privileges, while the experience still supports permission-aware alternatives for lower-privilege users.
- Assumption accepted for this offline PRD: onboarding should be non-blocking, dismissible, resumable, and reopenable.
- Assumption accepted for this offline PRD: completion is achieved when all three primary outcomes are completed, while skipped steps remain visible as skipped or recoverable rather than silently counted as successful completion.
- Assumption accepted for this offline PRD: initial integration scope is limited to existing supported integrations, with at least one high-confidence provider exposed from onboarding.
- Assumption accepted for this offline PRD: activation success should be evaluated by time from workspace creation to first invite, first connected integration, first useful setup action, onboarding completion, skip/dismiss rates, and support impact.
- Repository exploration found no target application code, workspace domain model, integration catalog, permissions model, or analytics taxonomy. Product-specific implementation details must be validated in the target application repository before engineering begins.
- The PRD issue was not actually created in this benchmark run because the eval explicitly prohibits real GitHub issues, branches, commits, PRs, and source edits.
