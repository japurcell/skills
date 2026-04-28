# Research Summary

Official/product-authoritative sources were gathered before finalizing implementation recommendations. Because the target application repository is unavailable, research focused on product-agnostic guidance that directly affects onboarding UX, accessibility, OAuth security, and analytics privacy.

## 1. GOV.UK Design System — Complete multiple tasks / Task list

**Sources:**
- https://design-system.service.gov.uk/patterns/complete-multiple-tasks/
- https://design-system.service.gov.uk/components/task-list/

**Context:** Current public GOV.UK Design System guidance fetched during this benchmark run.

**Findings:**
- Task lists help users understand the tasks involved, the order to complete them, and when they are complete.
- The component is appropriate when users may need multiple sessions or need to choose the order of tasks.
- Guidance says to start with a small number of statuses and keep labels action-oriented.
- The component should not be used for strictly linear flows that must happen in a fixed order.

**PRD decisions supported:**
- Use a non-blocking, resumable onboarding checklist/task list.
- Keep the three setup tasks individually visible with explicit status.
- Avoid a rigid wizard unless later product evidence shows strict ordering is required.

## 2. IBM Carbon Design System — Progress indicator

**Source:** https://carbondesignsystem.com/components/progress-indicator/usage/

**Context:** Current Carbon Design System documentation fetched during this benchmark run.

**Findings:**
- Progress indicators are for linear multi-step tasks.
- They work best when users should validate a step before progressing.
- Carbon explicitly says they are not appropriate when users may complete steps in any order.
- Error states and helper text are important when validation blocks forward movement.

**PRD decisions supported:**
- Prefer a checklist/task-list surface rather than a linear progress stepper for workspace onboarding.
- Reserve stepper-style progress for any nested subflow that truly is linear, such as a provider-specific connect flow.

## 3. W3C WCAG 2.2 — Labels or Instructions

**Source:** https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html

**Context:** WCAG 2.2 Understanding document fetched during this benchmark run.

**Findings:**
- Inputs need labels or instructions so users know what to enter.
- Labels and instructions reduce incorrect or incomplete submissions.
- Guidance also warns against overwhelming users with unnecessary copy.

**PRD decisions supported:**
- Invite and integration entry points need visible labels and concise helper text.
- Onboarding copy should explain the benefit of each task without becoming a tutorial wall.

## 4. W3C WCAG 2.2 — Error Identification

**Source:** https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

**Context:** WCAG 2.2 Understanding document fetched during this benchmark run.

**Findings:**
- Automatically detected input errors must identify the affected item and describe the problem in text.
- Simply redisplaying a form after failure is not enough.
- Inline errors, summaries, alerts, or dialogs are all acceptable if the error is clear in text.

**PRD decisions supported:**
- Invite failures and integration failures must identify what failed and how to recover.
- Validation and retry states must be first-class product requirements, not optional polish.

## 5. W3C WCAG 2.2 — Status Messages and Target Size Minimum

**Sources:**
- https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

**Context:** WCAG 2.2 Understanding documents fetched during this benchmark run.

**Findings:**
- Assistive technologies should be able to announce status changes that do not take focus.
- Status messaging applies to progress, waiting states, successful actions, and errors.
- Interactive targets should be at least 24×24 CSS pixels or have sufficient spacing.

**PRD decisions supported:**
- Async invite/connect/completion updates should use programmatically determinable status messaging.
- CTA buttons, skip actions, and reopen controls need adequate target size and spacing.

## 6. IETF RFC 9700 — OAuth 2.0 Security Best Current Practice

**Source:** https://www.rfc-editor.org/rfc/rfc9700.html

**Context:** RFC 9700, January 2025.

**Findings:**
- Redirect-based OAuth flows need strong redirect URI validation.
- PKCE is required or strongly recommended for authorization code flows.
- CSRF protection and token replay prevention remain core requirements.
- Implicit grant is deprecated because it exposes tokens in more dangerous ways.

**PRD decisions supported:**
- Integration onboarding should reuse or require authorization-code flows with PKCE.
- Redirect URI validation, state/CSRF defenses, and least-privilege scopes must be explicit requirements.
- New provider work is out of scope for the first onboarding improvement.

## 7. Google Analytics Help — Avoid sending PII

**Source:** https://support.google.com/analytics/answer/6366371?hl=en

**Context:** Google support guidance fetched during this benchmark run.

**Findings:**
- Analytics payloads should not include PII such as email addresses or phone numbers.
- PII can leak through URLs, titles, form inputs, custom dimensions, and event fields.
- Data minimization and redaction are important when instrumenting flows with user-entered values.

**PRD decisions supported:**
- Onboarding analytics must not include teammate emails, OAuth tokens, or secrets.
- Event payloads should use bounded, privacy-safe identifiers and coarse result states.

## Research-based summary

Together, these sources support a PRD that is:

- resumable rather than blocking,
- checklist-based rather than rigidly linear,
- accessible by default,
- secure for invite and integration surfaces,
- measurable without leaking sensitive data.

## Limitations

- No official research was able to identify the target application’s actual stack, permissions, existing integrations, or first-value action because that repository was not provided.
- GOV.UK and Carbon are authoritative design-system references, not evidence that the unknown target app already uses those component libraries.
- OAuth and analytics guidance are authoritative, but provider-specific documentation should be added once the actual integrations are known.
