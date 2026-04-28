# Research Summary

## Scope

Because the current repository is not the target application, targeted research was required before making implementation decisions. I ran three parallel research threads:

1. accessibility guidance for search, forms, status messages, and dialog behavior
2. email-alert subscription, unsubscribe, and deliverability guidance
3. durable web guidance for representing saved-search state in URLs and history

## Thread 1: Accessibility Guidance

### Primary sources

- WAI-ARIA APG search landmark: <https://www.w3.org/WAI/ARIA/apg/patterns/landmarks/examples/search.html>
- WAI Forms Tutorial — labels: <https://www.w3.org/WAI/tutorials/forms/labels/>
- WCAG 2.2 Error Identification: <https://www.w3.org/WAI/WCAG22/Understanding/error-identification>
- WAI Forms Tutorial — notifications: <https://www.w3.org/WAI/tutorials/forms/notifications/>
- WCAG 2.2 Status Messages: <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>
- WCAG 2.2 On Input: <https://www.w3.org/WAI/WCAG22/Understanding/on-input.html>
- WAI-ARIA APG modal dialog: <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>
- WAI-ARIA APG combobox: <https://www.w3.org/WAI/ARIA/apg/patterns/combobox/>

### Findings that affected the PRD

- Search and alert-management controls need explicit, programmatically associated labels.
- Validation cannot rely on browser-default behavior alone; errors should be text-based and easy to recover from.
- Save/update/pause/delete confirmations should be announced as status messages without unexpectedly moving focus.
- Changing cadence or toggle values should not auto-submit or cause unexpected context changes.
- If saved-search creation uses a modal, it must satisfy focus-management rules.
- If custom search suggestions are used, they must follow combobox keyboard and assistive-technology expectations.

### Decisions supported

- accessible account-area management UX
- explicit save actions instead of auto-submit-on-change
- status and error messaging requirements
- keyboard/focus requirements for modals and custom search suggestions
- accessibility-focused testing requirements

## Thread 2: Email Subscription And Unsubscribe Guidance

### Primary sources

- Gmail sender guidelines: <https://support.google.com/mail/answer/81126?hl=en>
- Google FAQ on sender requirements / unsubscribe timing: <https://support.google.com/a/answer/14229414?hl=en>
- Yahoo sender best practices: <https://postmaster.yahooinc.com/best-practices/>
- FTC CAN-SPAM compliance guide: <https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business>
- ICO PECR electronic mail guidance: <https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/>
- RFC 2369 (List-Unsubscribe): <https://www.rfc-editor.org/rfc/rfc2369.txt>
- RFC 8058 (One-Click Unsubscribe): <https://www.rfc-editor.org/rfc/rfc8058.txt>

### Findings that affected the PRD

- Each saved-search alert should behave like a separately manageable subscription.
- Users need login-free unsubscribe from the email itself in addition to account-area management.
- One-click unsubscribe should use standards-based headers and secure opaque tokens.
- Expected cadence should be explicit at signup and editable later.
- Suppression needs to happen quickly after opt-out; testing should verify that future sends stop promptly.
- Deliverability monitoring matters: unsubscribes, complaints, bounces, and sender reputation are part of launch risk.

### Decisions supported

- per-alert unsubscribe behavior
- account-area management plus email-level unsubscribe
- cadence selection and editing requirements
- observability and rollout gating around sender health
- testing around suppression after opt-out

## Thread 3: Search State, Deep Links, And Navigation Guidance

### Primary sources

- MDN `<form>`: <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form>
- MDN GET method: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/GET>
- MDN URLSearchParams: <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams>
- MDN URLSearchParams.getAll: <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams/getAll>
- MDN URLSearchParams.sort: <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams/sort>
- MDN History API guide: <https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API>
- MDN pushState: <https://developer.mozilla.org/en-US/docs/Web/API/History/pushState>
- MDN replaceState: <https://developer.mozilla.org/en-US/docs/Web/API/History/replaceState>
- MDN popstate: <https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event>
- RFC 9110 URI-length note: <https://www.rfc-editor.org/rfc/rfc9110.html#name-length-requirements>

### Findings that affected the PRD

- A saved search should be represented by canonical, serializable search criteria rather than opaque UI state.
- Alert emails should deep-link back to the same search state that was saved.
- Multi-select filters should be modeled in a way that can round-trip cleanly.
- Canonicalization matters for duplicate detection and stable comparisons.
- Back/forward and reload behavior should be part of the product requirements, not left implicit.
- Query state must stay compact and durable because URI length limits vary across environments.

### Decisions supported

- canonical saved-search definition
- deep-link behavior in alert emails
- duplicate-prevention strategy for equivalent searches
- navigation and restoration expectations
- testing for round-trip serialization and back/forward behavior

## Overall Research Outcome

The official research gave enough evidence to write a durable PRD even without a target-app codebase. The strongest support landed in four areas:

1. accessibility requirements for search and account-management flows
2. email unsubscribe and deliverability requirements
3. saved-search state representation and deep-link behavior
4. rollout/testing expectations for a recurring notification feature

No source provided target-app-specific implementation details, so the final PRD intentionally stays at the level of product requirements, data responsibilities, user-visible behavior, and testable outcomes.
