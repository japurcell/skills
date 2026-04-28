# Research Summary

This repository does not contain the target application, so implementation decisions in the PRD rely primarily on official research plus explicit assumptions.

## Research targets

1. Onboarding checklist and activation guidance
2. Accessibility requirements for multi-step onboarding, dialogs, progress, and errors
3. Integration connection and OAuth security requirements

## Official-source findings

### 1. Keep first-run onboarding short, action-led, and resumable

- **Finding:** Initial onboarding should present a short checklist of the highest-value actions, not a long setup wall.
- **Sources:**
  - Intercom checklist best practices — https://www.intercom.com/help/en/articles/6899972-checklist-best-practices
  - Intercom checklists explained — https://www.intercom.com/help/en/articles/6612245-checklists-explained
  - Intercom design your checklist — https://www.intercom.com/help/en/articles/6661022-design-your-checklist
- **Date/version context:** Intercom help articles cited by the research agent were current in 2025–2026.
- **Supports:** A non-blocking checklist with a limited number of steps, verb-first labels, visible progress, and resume behavior.
- **PRD impact:** The onboarding experience should guide users through the three requested outcomes without becoming a mandatory wizard.

### 2. Measure activation through real behavior, not only checklist UI interaction

- **Finding:** Good onboarding measurement should track the funnel from display to real step completion, including time-to-value.
- **Sources:**
  - Intercom measuring engagement with checklists — https://www.intercom.com/help/en/articles/6890704-measuring-and-driving-engagement-with-checklists
  - Google Analytics 4 events guide — https://developers.google.com/analytics/devguides/collection/ga4/events
  - Google Analytics recommended events reference — https://developers.google.com/analytics/devguides/collection/ga4/reference/events
- **Date/version context:** GA4 docs are current live documentation; the research agent noted current references and tutorial events.
- **Supports:** Events such as onboarding_shown, step_started, step_completed, step_skipped, dismissed, reopened, and completed, plus time-to-first-invite / time-to-first-integration / time-to-first-useful-action.
- **PRD impact:** Success criteria and testing decisions should require analytics for activation lift without storing sensitive raw values.

### 3. Use explicit, privacy-safe event payloads

- **Finding:** Measurement is necessary, but analytics payloads should avoid sensitive or unbounded values.
- **Sources:**
  - Google Analytics collection limits — https://support.google.com/analytics/answer/9267744
  - Google Analytics events guide — https://developers.google.com/analytics/devguides/collection/ga4/events
- **Date/version context:** Current Google Analytics help and developer docs.
- **Supports:** Bounded event names/parameters and exclusion of teammate emails, OAuth codes, tokens, secrets, or raw integration payloads.
- **PRD impact:** Privacy-safe instrumentation is a requirement, not just an implementation preference.

### 4. Step navigation, dialog behavior, and status updates must be accessible

- **Finding:** Multi-step onboarding and related dialogs need semantic progress indication, correct focus management, and non-disruptive status announcements.
- **Sources:**
  - WAI-ARIA 1.2 `aria-current="step"` — https://www.w3.org/TR/wai-aria-1.2/#aria-current
  - WAI-ARIA APG modal dialog pattern — https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
  - WCAG 2.2 status messages — https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
  - MDN ARIA progressbar role — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/progressbar_role
- **Date/version context:** WAI-ARIA 1.2 Recommendation published 2023-06-06; WCAG 2.2 and MDN guidance are current references.
- **Supports:** Semantic step indicators, proper modal behavior, visible and screen-reader-friendly progress/status, and async feedback without unwanted focus jumps.
- **PRD impact:** Accessibility requirements must be explicit in implementation and testing decisions.

### 5. Errors must identify the problem and suggest the next fix when safe

- **Finding:** Invite and integration failures must be shown in text, tied to the right field or action, and include corrective guidance when it can be given safely.
- **Sources:**
  - WCAG 2.2 error identification — https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html
  - WCAG 2.2 error suggestion — https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html
  - WCAG 2.2 labels or instructions — https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html
- **Date/version context:** WCAG 2.2 understanding documents.
- **Supports:** Text errors, clear instructions, accessible invite forms, retry guidance, and useful failure states.
- **PRD impact:** Error handling must be user-correctable and testable.

### 6. OAuth-based integration setup should use modern best practices

- **Finding:** Integration onboarding must not use obsolete OAuth patterns and must protect callbacks and tokens.
- **Sources:**
  - OAuth 2.0 Security Best Current Practice RFC 9700 — https://www.rfc-editor.org/rfc/rfc9700
  - Proof Key for Code Exchange RFC 7636 — https://www.rfc-editor.org/rfc/rfc7636
  - OAuth 2.0 Authorization Server Issuer Identification RFC 9207 — https://www.rfc-editor.org/rfc/rfc9207
  - Google OAuth best practices — https://developers.google.com/identity/protocols/oauth2/resources/best-practices
- **Date/version context:** RFC 9700 published January 2025; RFC 7636 September 2015; RFC 9207 March 2022; Google best-practices page was current and updated recently per agent research.
- **Supports:** Authorization code flow with PKCE, exact redirect URI matching, CSRF protection through state, issuer validation where relevant, and avoiding implicit flow.
- **PRD impact:** Security constraints belong in the PRD because integration onboarding introduces real risk.

### 7. Request minimum scopes and handle admin-consent blockers explicitly

- **Finding:** Integration flows should ask only for the scopes needed now and should model cases where the user cannot grant consent themselves.
- **Sources:**
  - Google OAuth best practices — https://developers.google.com/identity/protocols/oauth2/resources/best-practices
  - Microsoft Entra app access / API permissions quickstart — https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-configure-app-access-web-apis
  - Microsoft admin consent guidance — https://learn.microsoft.com/en-us/entra/identity-platform/v2-admin-consent
- **Date/version context:** Microsoft docs cited by the agent carried 2025 update dates; Google guidance is current.
- **Supports:** Least-privilege scopes, in-context explanations of why permissions are requested, explicit states such as needs_admin or pending_admin, and clear recovery paths.
- **PRD impact:** Permission-aware onboarding and partial-progress recovery must be requirements.

## Synthesis for the PRD

Based on the research, the PRD should recommend:

1. a non-blocking, resumable checklist rather than a mandatory wizard,
2. exactly the three requested high-value outcomes in the initial scope,
3. accessible step/status/error behavior,
4. privacy-safe activation analytics,
5. permission-aware invite and integration states,
6. secure OAuth/integration handling,
7. and a product-defined first useful setup action rather than a guessed domain action.

## Limitations

- No target application repository was available, so there was no product-specific codebase evidence for the live onboarding domain.
- Intercom sources are official vendor guidance, but not universal standards; they are used to support product-shape recommendations, not security-critical requirements.
- Product-specific decisions such as the actual first useful action, exact integrations in scope, and role model still require confirmation in the real application repository.
