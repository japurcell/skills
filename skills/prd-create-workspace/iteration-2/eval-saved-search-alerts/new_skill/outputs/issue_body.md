# PRD: Saved searches with email alerts

## Objective

Build a web feature that lets signed-in users save a search, choose how often they want email updates, and manage those alerts from their account area. The goal is to reduce repeated manual searching, give users clear control over alert frequency and lifecycle, and deliver relevant updates without creating notification fatigue. Success means users can reliably create, edit, pause, resume, delete, and unsubscribe from saved-search alerts, and every core flow is accessible, understandable, and safe to roll out.

## User Stories

1. As a signed-in user, I want to save my current search from the search results experience, so that I do not have to rebuild the same query later.
2. As a signed-in user, I want to give a saved search a clear name, so that I can recognize it later in my account area.
3. As a signed-in user, I want to choose a digest frequency when saving a search, so that the alert cadence matches how often I want updates.
4. As a signed-in user, I want the product to tell me when an equivalent alert already exists, so that I do not accidentally create duplicate alerts for the same search intent.
5. As a signed-in user, I want a clear confirmation when a saved-search alert is created, so that I know the action succeeded.
6. As a signed-in user, I want a dedicated account-area list of my saved-search alerts, so that I can review everything I am subscribed to in one place.
7. As a signed-in user, I want to edit an alert’s name and frequency from my account area, so that I can keep alerts useful as my needs change.
8. As a signed-in user, I want to pause an alert without deleting it, so that I can temporarily stop emails without losing the saved search.
9. As a signed-in user, I want to resume a paused alert, so that I can restart updates without recreating the search.
10. As a signed-in user, I want to delete an alert permanently, so that I can remove searches I no longer care about.
11. As a signed-in user, I want alert emails to arrive only when there are new matching results since the previous successful send, so that I receive signal instead of repeated noise.
12. As a signed-in user, I want each alert email to link back to the same search criteria I originally saved, so that I can immediately review the relevant results.
13. As a signed-in user, I want every alert email to include unsubscribe for that specific alert, so that I can stop unwanted mail without signing in first.
14. As a signed-in user, I want alert management actions to show clear validation and recovery guidance, so that I can fix mistakes like missing names or unsupported settings.
15. As a keyboard or assistive-technology user, I want the save and manage-alert flows to be fully accessible, so that I can use the feature without blocked controls, hidden context changes, or silent status updates.
16. As a signed-in user, I want the product to avoid sending an email when there are no new results for my saved search, so that the feature remains trustworthy and low-noise.
17. As a signed-in user, I want equivalent alerts to be treated consistently across save, edit, pause, resume, and delete flows, so that alert behavior is predictable.
18. As a privacy-conscious user, I want alert emails and alert links to reveal only what is necessary to return me to the product, so that my activity is not exposed more than needed.
19. As a support or operations stakeholder, I want alert delivery health, unsubscribes, and failure patterns to be observable, so that launch issues can be detected and addressed quickly.
20. As a product team, I want the feature to support staged rollout, so that user confusion, accessibility issues, and sender-reputation problems can be caught before broad release.
21. As an existing user who does not opt in, I want my normal search experience to remain unchanged, so that this feature is additive rather than disruptive.
22. As a signed-in user on a future session, I want my saved alerts to remain manageable from my account area, so that the feature behaves like a durable preference rather than a one-time action.

## Implementation Decisions

- A saved-search alert must be defined by canonical, serializable search criteria that can round-trip through a durable web URL. Citation: MDN GET and URLSearchParams guidance, <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/GET> and <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams>. Reason: the saved search needs a stable representation for deep links, duplicate detection, reloads, and predictable user-visible behavior.
- Alert emails must deep-link back to the exact saved search state rather than a generic destination. Citation: MDN History API and form guidance, <https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API> and <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form>. Reason: saved searches are only useful if users can return directly to the same search intent that generated the alert.
- Equivalent saved searches should be canonicalized and treated as the same alert definition for create/update purposes. Citation: MDN URLSearchParams sorting and repeated-parameter guidance, <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams/sort> and <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams/getAll>. Reason: canonical comparison reduces duplicate alerts and keeps user-facing alert management predictable.
- V1 should offer user-editable daily and weekly digests, and the product should send only when new matching results exist since the previous successful send. Citation: Gmail sender guidelines, Google sender FAQ, and ICO electronic mail guidance, <https://support.google.com/mail/answer/81126?hl=en>, <https://support.google.com/a/answer/14229414?hl=en>, and <https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/>. Reason: explicit cadence and ongoing user control reduce ambiguity, over-mailing, and deliverability risk while still satisfying the prompt’s frequency requirement.
- The account-area management experience should allow users to view, edit, pause, resume, and delete alerts without unexpected auto-save behavior. Citation: WCAG 2.2 On Input and WAI forms guidance, <https://www.w3.org/WAI/WCAG22/Understanding/on-input.html> and <https://www.w3.org/WAI/tutorials/forms/labels/>. Reason: recurring preferences should be intentionally changed, clearly labeled, and easy to recover from.
- Save, update, pause, resume, and delete actions must provide text-based validation and accessible status/error messaging. Citation: WCAG 2.2 Error Identification, WCAG 2.2 Status Messages, and WAI forms notifications guidance, <https://www.w3.org/WAI/WCAG22/Understanding/error-identification>, <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>, and <https://www.w3.org/WAI/tutorials/forms/notifications/>. Reason: this feature introduces recoverable form states and background-affecting preference changes that users must be able to understand confidently.
- If the save or edit flow uses a modal, it must behave as a true modal dialog with correct focus entry, trapping, dismissal, and focus return; otherwise the flow should use an inline or page-level form. Citation: WAI-ARIA APG modal dialog pattern, <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>. Reason: alert creation is a decision point that must not trap or disorient keyboard and assistive-technology users.
- The search experience should expose a clear search landmark and prefer native controls; any custom suggestion UI must satisfy combobox interaction requirements. Citation: WAI-ARIA APG search landmark and combobox patterns, <https://www.w3.org/WAI/ARIA/apg/patterns/landmarks/examples/search.html> and <https://www.w3.org/WAI/ARIA/apg/patterns/combobox/>. Reason: users need a discoverable and accessible entry point to the search they are being asked to save.
- Every alert email must include per-alert login-free unsubscribe in addition to account-area management. Citation: RFC 2369, RFC 8058, Gmail sender guidelines, Yahoo sender best practices, and FTC CAN-SPAM guidance, <https://www.rfc-editor.org/rfc/rfc2369.txt>, <https://www.rfc-editor.org/rfc/rfc8058.txt>, <https://support.google.com/mail/answer/81126?hl=en>, <https://postmaster.yahooinc.com/best-practices/>, and <https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business>. Reason: per-alert, login-free unsubscribe improves user trust and aligns the feature with current sender and compliance expectations.
- One-click unsubscribe should use secure opaque tokens and must not depend on user session cookies or interactive sign-in to suppress future mail. Citation: RFC 8058, <https://www.rfc-editor.org/rfc/rfc8058.txt>. Reason: unsubscribe must work safely from the email itself and remain valid in logged-out contexts.
- Delivery rollout should be staged and monitored for send success, unsubscribe volume, bounce rate, and complaint signals before broad release. Citation: Gmail sender guidelines and Yahoo sender best practices, <https://support.google.com/mail/answer/81126?hl=en> and <https://postmaster.yahooinc.com/best-practices/>. Reason: recurring email features introduce sender-reputation risk that should be measured before the product assumes general availability.

## Testing Decisions

- Good tests for this feature should verify external behavior and user-visible outcomes rather than implementation details. Prior art: Existing codebase testing guidance emphasizes accessible-role UI tests, API validation/auth tests, and end-to-end user journeys. Reason: the core value of this feature is whether users can create, manage, receive, and stop alerts successfully.
- Test the save-search creation flow through user interactions a real user would perform, including naming an alert, choosing cadence, receiving confirmation, and handling duplicate-alert cases. Prior art: Existing codebase testing guidance favors UI tests that query by accessible labels and buttons instead of internal component structure. Reason: save flow correctness is a visible product outcome.
- Test account-area management for list visibility, edit, pause, resume, and delete behavior, including empty states and recovery from validation errors. Prior art: Existing codebase testing guidance covers behavior-focused UI tests and explicit validation assertions. Reason: the account area is the long-term control surface named in the prompt.
- Test API or integration boundaries for authentication, authorization, invalid inputs, duplicate detection, and idempotent unsubscribe or pause behavior. Prior art: Existing codebase testing guidance includes success, validation-failure, and unauthenticated-request cases for API boundaries. Reason: recurring alerts create security- and correctness-sensitive state transitions.
- Test delivery behavior externally: when a due alert has new matches, one email is sent; when there are no new matches, none is sent; when an alert is paused, deleted, or unsubscribed, future sends stop. Prior art: Existing codebase testing guidance emphasizes boundary testing and observable outputs. Reason: scheduler correctness matters only insofar as the user-visible email behavior is correct.
- Test alert email links end-to-end so that the result link restores the intended search state and the unsubscribe action suppresses future mail without requiring sign-in. Prior art: Existing codebase testing guidance includes end-to-end user-flow coverage. Reason: email entry points are first-class user surfaces for this feature.
- Test accessibility outcomes for labels, keyboard navigation, error identification, status messages, search landmark discoverability, and any modal focus management. Prior art: Existing codebase accessibility guidance highlights semantic controls, live regions, alerts, and dialog behavior. Reason: accessibility failures would block core save and management flows for affected users.

## Success Criteria

- Signed-in users can create a saved-search alert from the search flow, choose a supported cadence, and receive an explicit success confirmation.
- Signed-in users can see all of their saved-search alerts in a dedicated account-area view and can edit, pause, resume, or delete each one without rediscovering the original search page.
- Equivalent saved searches are not silently duplicated; users are guided to update or reuse the existing alert instead.
- Alert emails are sent only for due alerts with new matching results and always link back to the intended search state.
- Every alert email includes a working per-alert unsubscribe path that suppresses future sends for that alert without requiring sign-in.
- Users who pause, delete, or unsubscribe from an alert stop receiving future emails for that alert before the next eligible delivery window.
- Core save and manage-alert flows are operable by keyboard, expose understandable labels and errors, and announce non-disruptive status updates.
- Initial rollout can be evaluated with observable delivery health, unsubscribe behavior, and failure rates before the feature is exposed broadly.

## Out of Scope

- Real-time or instant alerting in v1
- SMS, push, in-app digest, or non-email notification channels
- Team-shared, workspace-wide, or admin-managed saved-search alerts
- Multiple recipient addresses or sending alerts to arbitrary external email addresses
- Complex rule builders, boolean alert logic, or cross-search alert bundles
- Marketing or promotional email reuse beyond the saved-search alert use case
- Historical backfill emails for old results that predate alert creation unless separately defined later
- Broad notification-center redesign beyond the surfaces needed to save and manage these alerts

## Further Notes

- This PRD is based on explicit assumptions and official guidance because the current repository context does not expose the target application’s actual search, account, email, or persistence implementation.
- Accepted assumptions for this draft: v1 is user-only; alerts are based on canonical saved search state; cadence is limited to daily and weekly; delivery is only for new matches; alerts go to the primary verified account email; management is available both at creation time and in the account area; equivalent searches are deduplicated; per-alert login-free unsubscribe is required; pause/resume is supported; rollout is staged.
- Before implementation planning, the target application team should reconcile this PRD with any real existing search model, account-area information architecture, email provider capabilities, consent requirements, and data-retention rules.
- If the target application already has notification preferences or search deep-link conventions, those should refine the implementation plan without changing the user-visible commitments captured here.
