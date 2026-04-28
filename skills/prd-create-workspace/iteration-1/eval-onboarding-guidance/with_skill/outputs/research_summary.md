# Targeted Web Research Summary

Research was performed inline with official/source web references because the skill requires current authoritative guidance before recommending implementation decisions. The target application stack was unavailable, so research focused on product-agnostic UX, accessibility, OAuth/security, and analytics sources that directly affect onboarding requirements.

## Source 1: GOV.UK Design System task list component

**Link:** https://design-system.service.gov.uk/components/task-list/

**Date/version context:** GOV.UK Design System public component documentation, fetched during this eval run.

**Findings:**

- A task list displays all tasks a user needs to do and helps users identify which are done and which still need to be done.
- The component supports task titles, optional hints, links, and required status text/tags.
- The guidance says to use a task list when users may not complete all tasks in one sitting or need to choose the order of completion.
- The guidance says to simplify the service first and not use a task list for long services that must be completed in a strict order.
- It also warns that HTML options must be sanitized to protect against cross-site scripting when custom HTML is used.

**Decisions supported:**

- Use a non-blocking, resumable checklist/task-list pattern rather than a mandatory wizard.
- Show explicit completion states for invite, integration, and first useful action steps.
- Allow users to complete steps in flexible order and resume setup later.
- Keep onboarding concise and do not expand it into a long, complex service unless evidence supports that need.

## Source 2: W3C WCAG 2.2 Recommendation

**Link:** https://www.w3.org/TR/WCAG22/

**Date/version context:** W3C Recommendation; WCAG 2.2 extends WCAG 2.1 and W3C advises using the most current version when developing or updating accessibility policies.

**Findings:**

- WCAG 2.2 provides testable success criteria for making web content more accessible across devices.
- Following the guidelines often improves usability for users in general, not only users with disabilities.
- WCAG 2.2 is recommended by W3C as the current web accessibility standard.

**Decisions supported:**

- Treat accessibility as a first-class requirement for onboarding rather than a post-implementation audit.
- Include keyboard, focus, target size, labels, errors, and status announcement tests in the PRD.

## Source 3: W3C WCAG 2.2 Understanding Keyboard

**Link:** https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html

**Date/version context:** WCAG 2.2 Understanding document, fetched during this eval run.

**Findings:**

- All functionality should be operable through a keyboard interface except path-dependent movement.
- Keyboard accessibility benefits blind users, low-vision users, users with mobility impairments, and users of alternative input devices.
- Common pointer actions should have keyboard equivalents.

**Decisions supported:**

- Require every onboarding control, including checklist links, invite submission, integration actions, skip/dismiss, and reopen controls, to be keyboard-operable.
- Include keyboard-only journey tests for the complete onboarding flow.

## Source 4: W3C WCAG 2.2 Understanding Labels or Instructions

**Link:** https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html

**Date/version context:** WCAG 2.2 Understanding document, fetched during this eval run.

**Findings:**

- Labels or instructions must be provided when content requires user input.
- The intent is to identify controls and expected data so users know how to respond.
- Labels and instructions help prevent incomplete or incorrect form submissions.
- Too much information can be harmful, so instructions should provide enough information without clutter.

**Decisions supported:**

- Require visible labels and concise instructions for teammate email input, invite link controls, integration provider choices, and configuration fields.
- Require action-oriented copy that explains why each setup step matters without overwhelming users.

## Source 5: W3C WCAG 2.2 Understanding Error Identification

**Link:** https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

**Date/version context:** WCAG 2.2 Understanding document, fetched during this eval run.

**Findings:**

- When input errors are automatically detected, the affected item must be identified and the error described in text.
- It is not sufficient to redisplay a form without indicating that submission failed.
- Helpful error descriptions can also suggest how to fix the problem.
- Errors may be presented inline, in a list, alert, or dialog; the key requirement is text or text alternative.

**Decisions supported:**

- Require invite and integration errors to identify the failed item and describe the recovery path.
- Require tests for validation, permission, provider cancellation, and retry states.

## Source 6: W3C WCAG 2.2 Understanding Status Messages

**Link:** https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html

**Date/version context:** WCAG 2.2 Understanding document, fetched during this eval run.

**Findings:**

- Status messages should be programmatically determinable so assistive technologies can announce changes without moving focus.
- Status messages include success/results of actions, waiting states, progress, and errors that do not change context.
- Examples include progress bars, form submission success, invalid entry notices, and dynamic completion text.

**Decisions supported:**

- Require progress, invite sending, integration connection, and step completion updates to be announced without unnecessary focus changes.
- Include accessibility tests for asynchronous onboarding status changes.

## Source 7: W3C WCAG 2.2 Understanding Focus Appearance and Target Size

**Links:**

- https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

**Date/version context:** WCAG 2.2 Understanding documents, fetched during this eval run.

**Findings:**

- Focus indicators should be large and contrasting enough to be easy to see.
- Target size guidance requires pointer targets to be at least 24 by 24 CSS pixels or have sufficient spacing, with exceptions.
- Target size helps users with dexterity limitations and improves touchscreen usability.

**Decisions supported:**

- Require visible focus and sufficiently sized controls for step CTAs, skip/dismiss controls, integration buttons, and reopen links.
- Include UI/accessibility acceptance criteria for focus visibility and target size.

## Source 8: IETF OAuth 2.0 Security Best Current Practice RFC 9700

**Link:** https://www.rfc-editor.org/rfc/rfc9700.html

**Date/version context:** RFC 9700, OAuth 2.0 Security BCP, January 2025.

**Findings:**

- Redirect-based flows should use exact redirect URI matching and avoid open redirectors.
- Clients must prevent CSRF; PKCE can provide CSRF protection in supported flows, otherwise one-time state values bound to the user agent are required.
- Public clients must use PKCE for authorization code flows, and PKCE is recommended for confidential clients.
- Clients should avoid implicit grant and use authorization code flows because exposing access tokens in authorization responses increases leakage/replay risk.

**Decisions supported:**

- Require secure OAuth behavior for integration connection flows introduced or surfaced by onboarding.
- Keep onboarding integration scope limited to existing secure providers unless security review confirms new flows.
- Include tests or review gates for redirect validation, state/CSRF, PKCE, and token-handling behavior.

## Source 9: GitHub OAuth app authorization documentation

**Link:** https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps

**Date/version context:** GitHub Docs, fetched during this eval run.

**Findings:**

- GitHub notes that GitHub Apps can provide fine-grained permissions and short-lived tokens compared with OAuth Apps.
- GitHub OAuth supports web application flow and device flow.
- The authorization request strongly recommends `state` for CSRF protection and PKCE `code_challenge`.
- The token exchange strongly recommends redirect URI and PKCE `code_verifier`.
- If returned state does not match, the client should abort.

**Decisions supported:**

- If a GitHub integration is in scope, prefer fine-grained app permissions where feasible.
- Require `state`, PKCE, and redirect URI validation for GitHub-style integration flows.
- Ensure integration onboarding communicates permission scopes clearly.

## Source 10: Google Analytics 4 event setup and recommended events

**Links:**

- https://developers.google.com/analytics/devguides/collection/ga4/events
- https://developers.google.com/analytics/devguides/collection/ga4/reference/events
- https://support.google.com/analytics/answer/9267744

**Date/version context:** Google event setup page fetched with page note `Last updated 2026-03-18 UTC`; support limits page fetched during this eval run.

**Findings:**

- Events measure user interactions and are used to create business reports.
- GA4 supports recommended and custom events beyond automatic collection.
- Recommended onboarding-related events include `tutorial_begin` and `tutorial_complete`, intended for measuring onboarding funnel completion.
- Events can include optional parameters, but collection limits constrain event names, parameter counts, and value lengths.
- DebugView and Realtime reports can be used to confirm events are sent.

**Decisions supported:**

- Instrument onboarding shown, step started, step completed, step skipped, dismissed, reopened, and completed events.
- Include completion funnels and time-to-first-useful-action metrics.
- Keep event names and parameters bounded and avoid raw PII/secrets in analytics payloads.

## Research limitations

- The target product stack and analytics vendor are unknown, so research intentionally used general web standards and vendor documentation rather than framework-specific implementation docs.
- GOV.UK task list guidance is a strong official design-system source for task-list behavior, but it is not evidence that the target product already uses GOV.UK components.
- GitHub OAuth documentation is relevant only if GitHub-style integrations are part of the product; RFC 9700 is the broader OAuth security source.
- Product-specific integration provider documentation should be added once the actual integration catalog is known.
