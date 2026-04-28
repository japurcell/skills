# PRD: New Workspace Onboarding Guidance

## Objective

Improve activation for newly created workspaces by guiding the workspace creator through three high-value outcomes immediately after creation: inviting teammates, connecting an existing supported integration, and completing the first useful setup action. Success means new workspace creators can understand what to do next, make visible progress without being blocked from normal product use, and reach a collaborative, functional workspace state more quickly with accessible, permission-aware, and measurable onboarding.

## User Stories

1. As a workspace creator, I want onboarding to appear right after workspace creation so that I know what to do next.
2. As a workspace creator, I want the onboarding surface to show a short list of high-value setup steps so that the path to activation feels clear.
3. As a workspace creator, I want onboarding to be non-blocking so that I can enter the product immediately if I need to.
4. As a workspace creator, I want onboarding to be dismissible and resumable so that setup help remains available without becoming a trap.
5. As a workspace creator, I want the onboarding steps to include inviting teammates so that the workspace can become collaborative quickly.
6. As a workspace creator, I want to send one or more teammate invites from onboarding so that I do not need to search the product for the invite flow.
7. As a workspace creator, I want invite outcomes to show clear success, pending, failure, and retry states so that I know whether collaboration setup progressed.
8. As a workspace creator, I want onboarding to explain why connecting an integration is useful so that I can decide whether to do it now.
9. As a workspace creator, I want to connect at least one supported integration from onboarding so that the workspace can work with tools my team already uses.
10. As a workspace creator, I want integration setup to handle cancellation, consent denial, admin-consent blockers, callback failure, and reconnect paths so that I can recover without losing context.
11. As a workspace creator, I want the first useful setup action to feel product-specific rather than generic so that onboarding leads to real value.
12. As a workspace creator, I want the first useful setup action to happen in the normal product surface when possible so that I learn the real workflow.
13. As a workspace creator, I want step progress to persist across reloads and later sessions so that I do not repeat work.
14. As a workspace creator, I want skipped steps to stay recoverable so that I can finish them later when I have permission, time, or context.
15. As a workspace creator, I want a clear way to reopen onboarding later so that dismissing it does not permanently hide setup help.
16. As a workspace creator, I want progress to be visible and understandable so that I always know what is complete, blocked, skipped, or remaining.
17. As a workspace creator, I want onboarding copy to be concise and action-led so that the setup path feels manageable.
18. As a workspace creator, I want labels and instructions to explain what information is needed before I act so that I can avoid preventable errors.
19. As a workspace creator, I want user-correctable errors to identify the specific problem and next step so that I can recover quickly.
20. As a workspace creator, I want onboarding not to steal focus unexpectedly during async actions so that status updates are informative rather than disruptive.
21. As a workspace creator using only a keyboard, I want every onboarding control to be operable with visible focus so that I can complete setup accessibly.
22. As a screen reader user, I want step progress and async results to be announced appropriately so that I understand what changed.
23. As a user with low vision or motor limitations, I want usable targets, visible focus, and understandable progress indicators so that onboarding remains practical to complete.
24. As a user without permission to invite teammates, I want the invite step to explain why it is unavailable and what to do next so that I am not blocked by confusion.
25. As a user without permission to connect integrations, I want the integration step to offer alternate guidance so that I can continue useful setup work.
26. As an admin or owner, I want onboarding actions to respect membership and integration permissions so that protected actions remain secure.
27. As an invited teammate, I want successful invite progress to count toward the workspace's onboarding state so that the creator is not asked to repeat a finished step.
28. As a returning workspace creator, I want completed onboarding not to keep resurfacing as noise so that the experience respects my progress.
29. As a product manager, I want onboarding instrumentation for shown, started, completed, skipped, dismissed, reopened, and time-to-value outcomes so that I can measure activation impact.
30. As a support teammate, I want common blockers such as invite failure, admin-consent required, or incomplete setup to be observable so that I can help new workspaces reach value.
31. As an operator, I want the feature to launch behind rollout control for newly created workspaces so that risk can be managed before broader release.
32. As a privacy-conscious team, I want onboarding measurement to avoid raw emails, tokens, or secrets so that activation instrumentation does not create new exposure risk.
33. As a product team, I want the first release to rely on existing supported invite and integration capabilities so that onboarding scope stays focused on guidance and activation.
34. As an existing workspace user, I want the initial rollout to avoid changing legacy workspaces unexpectedly so that launch risk stays contained.

## Implementation Decisions

- Use a non-blocking, dismissible, resumable checklist rather than a mandatory wizard. Citation: Official vendor guidance from Intercom checklist best practices, https://www.intercom.com/help/en/articles/6899972-checklist-best-practices. Reason: the guidance supports short, action-led onboarding checklists that users can work through progressively instead of forcing a high-friction linear flow.
- Keep the initial scope to exactly three outcomes: invite teammates, connect one existing supported integration, and complete one first useful setup action. Citation: Existing codebase pattern - the governing PRD workflow treats the user request as the scope anchor and discourages uncontrolled expansion before evidence exists. Reason: this keeps the PRD aligned with the benchmark request and prevents unrelated setup work from diluting activation.
- Make the first useful setup action product-defined and configurable by product area or workspace type rather than hard-coding a guessed domain action in this PRD. Citation: Existing codebase pattern - this repository's requirements workflows explicitly surface assumptions instead of silently inventing missing product context. Reason: the target product repository is unavailable here, so configurability is the most durable requirement.
- Show onboarding immediately after workspace creation and provide a persistent way to reopen it later. Citation: Existing codebase pattern - repository workflows model multi-step work as explicit, durable, resumable progress rather than one-shot execution. Reason: onboarding is also multi-step and should remain recoverable across sessions.
- Store step completion as workspace-level progress while keeping dismiss/reopen preferences user-specific. Citation: Existing codebase pattern - the available repository distinguishes durable shared state from per-user or per-run context. Reason: invite and integration completion are shared workspace facts, while hiding or reopening guidance is a personal experience choice.
- Keep permission-aware states visible instead of hiding blocked steps entirely. Citation: Official accessibility guidance for labels, instructions, and clear error handling from WCAG 2.2, https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html and https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html. Reason: users should understand why an action is unavailable and what alternate path exists.
- Represent current step/progress semantically and announce dynamic updates without unnecessary focus changes. Citation: WAI-ARIA 1.2 `aria-current`, https://www.w3.org/TR/wai-aria-1.2/#aria-current, and WCAG 2.2 status messages, https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html. Reason: onboarding includes progress updates and async outcomes that must be perceivable to assistive technologies.
- Any invite or integration dialog used during onboarding must follow modal dialog focus-management rules. Citation: WAI-ARIA Authoring Practices Guide modal dialog pattern, https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/. Reason: onboarding frequently involves modal actions and must preserve keyboard and screen-reader usability.
- Invite and setup forms must use explicit labels, instructions, text errors, and actionable recovery suggestions where it is safe to provide them. Citation: WCAG 2.2 labels or instructions, error identification, and error suggestion guidance, https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html, https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html, and https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html. Reason: onboarding relies on user-correctable inputs and should minimize abandonment from avoidable confusion.
- Limit the initial integration step to existing supported integrations and at least one real connection path. Citation: Existing codebase pattern - the available repository separates requirements work from implementation expansion and avoids inventing unsupported capabilities. Reason: this PRD is about improving onboarding guidance, not launching a new integrations program.
- Require modern OAuth protections for redirect-based integration setup, including authorization code flow with PKCE, exact redirect URI handling, state-based CSRF protection, and avoiding deprecated implicit flow. Citation: OAuth 2.0 Security Best Current Practice RFC 9700, https://www.rfc-editor.org/rfc/rfc9700, and PKCE RFC 7636, https://www.rfc-editor.org/rfc/rfc7636. Reason: integration onboarding introduces token and redirect risk that must be constrained at the requirements level.
- Request the minimum integration scopes needed for the current onboarding action and defer optional permissions until later product moments. Citation: Google OAuth best practices, https://developers.google.com/identity/protocols/oauth2/resources/best-practices. Reason: least-privilege consent improves trust, reduces unnecessary friction, and lowers security exposure.
- Model admin-consent blockers and partial connection states explicitly rather than treating every failed integration attempt as a generic error. Citation: Microsoft Entra admin consent guidance, https://learn.microsoft.com/en-us/entra/identity-platform/v2-admin-consent. Reason: some users cannot authorize integrations themselves, and the onboarding flow should support recovery instead of dead-ending.
- Instrument onboarding with privacy-safe events for shown, step_started, step_completed, step_skipped, dismissed, reopened, and completed, plus time-to-value measures. Citation: Google Analytics 4 event guidance, https://developers.google.com/analytics/devguides/collection/ga4/events. Reason: activation improvement cannot be evaluated without measurable, bounded event data.
- Exclude raw teammate emails, access tokens, refresh tokens, authorization codes, secrets, or unbounded integration payloads from analytics. Citation: Google Analytics collection limits, https://support.google.com/analytics/answer/9267744. Reason: onboarding measurement should not introduce privacy or credential exposure risk.
- Ship behind rollout control for newly created workspaces first. Citation: Existing codebase pattern - the repository's workflows consistently use explicit gates and validation before advancing broader phases. Reason: first-run onboarding affects activation-critical product behavior and should be introduced in a controlled manner.

## Testing Decisions

Good tests for this feature should verify external behavior and user-visible outcomes rather than implementation details.

- Test that a newly created workspace creator sees onboarding immediately with the three required outcomes visible and understandable. Prior art: Existing codebase testing guidance emphasizes behavior-first verification. Reason: the essential requirement is that users see actionable guidance, not how the UI is composed.
- Test invite behavior for success, validation error, permission denial, resend/retry, and pending states. Prior art: Existing codebase testing guidance plus WCAG error-identification guidance. Reason: invite setup combines protected actions with user-correctable input.
- Test integration behavior for provider selection, authorization start, cancel, callback success, consent denial, admin-consent required, reconnect, and already-connected states. Prior art: OAuth security guidance and behavior-first testing guidance. Reason: the integration step crosses an external boundary and must support recovery paths.
- Test that the first useful setup action is marked complete only when the user completes the actual product-defined action, not when they merely click a checklist item. Prior art: Existing codebase planning/workflow patterns favor real user-visible completion over superficial state toggles. Reason: onboarding should measure value reached, not checklist gaming.
- Test persistence of completed, skipped, dismissed, and reopened states across reloads and later sessions according to the workspace/user scoping decision. Prior art: Existing codebase patterns favor durable progress and resumability. Reason: resumability is a core product promise in this PRD.
- Test permission-aware variants for owners/admins, users who cannot invite teammates, and users who cannot manage integrations. Prior art: Existing security guidance requires authorization checks for protected actions. Reason: onboarding must not mislead users about what they can do.
- Test keyboard navigation, focus order, visible focus, dialog focus trapping, step semantics, and status announcements. Prior art: WAI-ARIA dialog guidance, WAI-ARIA `aria-current`, and WCAG status-message guidance. Reason: onboarding is interactive and must be accessible by default.
- Test text labels, instructions, error identification, and safe error suggestions for invite and setup forms. Prior art: WCAG labels/instructions, error identification, and error suggestion guidance. Reason: accessible error recovery is a product requirement.
- Test progress and async feedback for invite sending, integration connection, and setup completion using accessible status announcements rather than focus-stealing patterns. Prior art: WCAG status-message guidance and progressbar semantics guidance. Reason: setup includes async operations that should remain understandable without disorienting users.
- Test analytics emission for shown, started, completed, skipped, dismissed, reopened, and completed outcomes, as well as time-to-first-invite, time-to-first-integration, and time-to-first-useful-action. Prior art: GA4 event guidance. Reason: launch success depends on measurable activation improvement.
- Test that analytics payloads never contain raw invite email addresses, OAuth artifacts, secrets, or unapproved metadata. Prior art: existing security guidance plus GA collection constraints. Reason: measurement must remain privacy-safe.
- Test rollout control so the onboarding experience can be enabled for new workspaces without unintentionally changing the experience for existing workspaces. Prior art: existing codebase workflow gates. Reason: controlled release is part of the product requirement.

## Success Criteria

- Newly created workspace creators are shown a clear onboarding experience immediately after creation or at first entry.
- The onboarding experience visibly guides users through inviting teammates, connecting an existing supported integration, and completing one product-defined first useful setup action.
- Onboarding remains non-blocking, dismissible, and resumable from a persistent entry point.
- Invite, integration, and setup actions show understandable success, pending, blocked, and recovery states.
- Users without required permissions see clear alternate guidance instead of silent failure or confusing omission.
- Keyboard-only and assistive-technology users can operate the onboarding experience successfully.
- Step completion persists correctly across reloads and later sessions.
- Activation analytics are available for the core onboarding funnel and time-to-value outcomes without logging raw sensitive values.
- The feature can be rolled out to newly created workspaces in a controlled manner before broader release.
- Product and support teams can identify common blockers such as invite failure, admin-consent required, or incomplete first-useful-action completion.

## Out of Scope

- Rebuilding the workspace creation flow itself.
- Creating new integration providers, a full marketplace, or provider-specific connection experiences beyond existing supported entry points.
- Requiring onboarding completion before normal workspace access.
- Launching lifecycle email campaigns, nurture messaging, or cross-channel onboarding automations.
- Defining the exact first useful setup action for every product area inside this PRD; the requirement is that the action be product-defined and configurable.
- Reworking billing, seat management, SSO, enterprise provisioning, or unrelated admin flows unless they directly determine onboarding permission states.
- Migrating all existing workspaces into this experience for the first release.
- Implementing code, schema changes, final designs, or operational runbooks in this PRD issue.
- Capturing teammate emails, OAuth artifacts, tokens, secrets, or raw integration payloads in onboarding analytics.

## Further Notes

- Accepted assumption: the primary actor is the workspace creator, usually with owner/admin capability, while lower-privilege users still need permission-aware onboarding states.
- Accepted assumption: onboarding should be non-blocking, dismissible, resumable, and reopenable.
- Accepted assumption: the initial release should cover exactly the three requested outcomes.
- Accepted assumption: the first useful setup action must be selected by the product team based on product area or workspace type before engineering begins.
- Accepted assumption: the integration step should use existing supported integrations only for the initial release.
- Accepted assumption: onboarding completion requires all three primary outcomes to succeed; skipped items remain recoverable and do not count as completed success.
- Important limitation: repository exploration found no target application code or trustworthy product prior art for the actual workspace domain, integration catalog, permission model, or analytics taxonomy. These details must be validated in the real application repository before implementation starts.
- Important limitation: this issue body was prepared in offline benchmark mode, so no live GitHub issue was created.
